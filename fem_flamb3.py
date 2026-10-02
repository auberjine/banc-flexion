# -*- coding: utf-8 -*-
"""
FLAMBEMENT HORS PLAN, mode SYMETRIQUE : les liaisons entre flancs en RESSORTS.

Quand les deux flancs penchent du meme cote, rien de ce qui les relie n'est
ancre : tube, plaque a mi-bois ou plaque de dessus suivent en bloc. Ce qu'une
liaison oppose alors, c'est sa raideur de flexion entre les deux flancs, dont
les deux bouts tournent du meme angle : M = 6 E I theta / L a chaque bout,
sans aucun effort tranchant. Un flanc seul suffit donc, avec a chaque
liaison un corps rigide sur la couronne de contact et un ressort de rotation
de 6 E I / L sur ses deux axes de flexion (rien en torsion : les deux bouts
tournent ensemble). Les pieds, eux, sont tenus par le sol : u_z = 0.

Variantes :
  tubes    les six entretoises tubulaires 20 x 4,5 seulement
  mibois   + deux plaques verticales 340 x 20 x 8 a mi-bois dans le chant haut
  plaque   + une plaque de DESSUS PLAQUE_L x 76 x 8 posee sur le chant haut,
             tenons-mortaises a PLAQUE_X ; chaque tenon porte sa part de plaque

Le mode ANTISYMETRIQUE (flancs en sens contraire) est celui de fem_flambement.py
avec les tubes tenus en z : il est bien plus haut. Le facteur a retenir est le
plus petit des deux. Maillage grossier (9 mm). Resultat : out/flambement3.json.

    python fem_flamb3.py                  # remaille puis calcule
    python fem_flamb3.py --sans-maillage  # reprend out/flamb/base.inp
"""

import io
import os
import sys
import json
import math
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
import outils
CCX = outils.CCX
BASE = os.path.join(HERE, "out", "flamb", "base.inp")
TRAVAIL = os.path.join(HERE, "out", "flamb3")
N_MODES = 4
E = 210000.0

import params as par
import parts

sys.path.insert(0, HERE)
from fem_run import lire_noeuds
import fem_flambement as F1

PLAQUE_L = float(os.environ.get("BANC_PLAQUE_L", "600"))
PLAQUE_X = tuple(float(v) for v in os.environ.get("BANC_PLAQUE_X", "-250,0,250").split(","))
L_LIAISON = par.ECART_FLANCS + par.EP_FLANC       # d un plan moyen de flanc a l autre


def anneau(noeuds, cx, cy, r0, r1):
    r02, r12 = r0 * r0, r1 * r1
    return [nid for nid, (x, y, z) in noeuds.items() if r02 <= (x - cx) ** 2 + (y - cy) ** 2 <= r12]


def bord_haut(noeuds, cx, demi):
    return [nid for nid, (x, y, z) in noeuds.items() if y >= par.H_FLANC - 0.5 and abs(x - cx) <= demi]


class Liaisons(object):
    """Corps rigides + ressorts de rotation, ajoutes au .inp du flanc seul."""

    def __init__(self, noeuds, premier_element):
        self.prochain = max(noeuds) + 1
        # CalculiX dimensionne ses tableaux sur le PLUS GRAND numero d element :
        # un ressort numerote 9 000 000 fait echouer l allocation memoire
        self.element = premier_element
        self.blocs = []           # (nset_nom, ids, ref, rot, kx, ky)

    def ajoute(self, nom, ids, kx, ky):
        if not ids:
            raise SystemExit("liaison %s : couronne vide" % nom)
        ref = self.prochain
        rot = self.prochain + 1
        self.prochain += 2
        self.blocs.append(("%s%d" % (nom, len(self.blocs)), sorted(ids), ref, rot, kx, ky))

    def lignes(self, noeuds):
        out = []
        w = out.append
        # noeuds de reference et de rotation : au barycentre de la couronne
        for nom, ids, ref, rot, kx, ky in self.blocs:
            cx = sum(noeuds[i][0] for i in ids) / len(ids)
            cy = sum(noeuds[i][1] for i in ids) / len(ids)
            cz = sum(noeuds[i][2] for i in ids) / len(ids)
            w("*NODE")
            w("%d, %.6f, %.6f, %.6f" % (ref, cx, cy, cz))
            w("%d, %.6f, %.6f, %.6f" % (rot, cx, cy, cz))
        for nom, ids, ref, rot, kx, ky in self.blocs:
            w("*NSET, NSET=%s" % nom)
            for j in range(0, len(ids), 12):
                w(", ".join(str(k) for k in ids[j:j + 12]) + ",")
            w("*RIGID BODY, NSET=%s, REF NODE=%d, ROT NODE=%d" % (nom, ref, rot))
        k = 0
        for nom, ids, ref, rot, kx, ky in self.blocs:
            for dof, kk in ((1, kx), (2, ky)):
                if kk <= 0:
                    continue
                els = "%sr%d" % (nom, dof)
                w("*ELEMENT, TYPE=SPRING1, ELSET=%s" % els)
                w("%d, %d" % (self.element + k, rot))
                w("*SPRING, ELSET=%s" % els)
                w("%d" % dof)
                w("%.6e" % kk)
                k += 1
        return out


def ecrit_inp(nom, avant, corps, noeuds, jeux_z, liaisons):
    out = list(avant)
    out.extend(liaisons.lignes(noeuds))
    for nom_set, ids in jeux_z:
        out.append("*NSET,NSET=%s" % nom_set)
        for j in range(0, len(ids), 12):
            out.append(",".join(str(k) for k in ids[j:j + 12]) + ",")
    out.append("*STEP")
    out.append("*BUCKLE")
    out.append("%d" % N_MODES)
    out.extend(corps)
    if jeux_z:
        out.append("*BOUNDARY")
        for nom_set, ids in jeux_z:
            out.append("%s,3,3,0.0" % nom_set)
    out.append("*NODE FILE")
    out.append("U")
    out.append("*END STEP")
    path = os.path.join(TRAVAIL, nom + ".inp")
    io.open(path, "w", encoding="ascii", newline="\n").write("\n".join(out) + "\n")
    return path


def k_rot(I):
    return 6.0 * E * I / L_LIAISON


def main():
    if not os.path.isdir(TRAVAIL):
        os.makedirs(TRAVAIL)
    if "--sans-maillage" not in sys.argv or not os.path.isfile(BASE):
        # fem_flambement sait mailler et charger ; on lui emprunte son maillage
        r = subprocess.run([sys.executable, "fem_flambement.py", "--seul", "0:0"], cwd=HERE,
                           capture_output=True, text=True)
        if not os.path.isfile(BASE):
            print(r.stdout[-2000:]); raise SystemExit("pas de maillage")
    texte = io.open(BASE, encoding="latin-1").read()
    noeuds = lire_noeuds(texte.splitlines(True))
    avant, corps = F1.decoupe_inp(texte)
    import re as _re
    premier_element = max(int(m.group(1)) for m in _re.finditer(r"^(\d+),", texte, _re.M)) + 1
    print("noeuds : %d" % len(noeuds))

    I_tube = math.pi * (par.ENTRETOISE_DE ** 4 - par.ENTRETOISE_DI ** 4) / 64.0
    k_tube = k_rot(I_tube)
    h_mb = getattr(par, "ENTR_HAUT_H", 20.0)
    I_mb_x = par.EP_FLANC * h_mb ** 3 / 12.0                     # plaque verticale, flexion dans son plan
    I_mb_y = h_mb * par.EP_FLANC ** 3 / 12.0                     # et a plat
    lx = PLAQUE_L / len(PLAQUE_X)
    I_pl_x = lx * par.EP_FLANC ** 3 / 12.0                       # plaque de dessus, a plat
    I_pl_y = par.EP_FLANC * lx ** 3 / 12.0                       # dans son plan

    def tubes(li):
        for (x, z, d, nom) in parts.flanc_trous():
            if "entretoise" in nom:
                li.ajoute("tube", anneau(noeuds, x, z, par.ENTRETOISE_DI / 2.0 - 0.3, par.ENTRETOISE_DE / 2.0 + 0.5),
                          k_tube, k_tube)

    def mibois(li):
        ids = F1.noeuds_entretoises_hautes(noeuds)
        for xt in (-par.PIED_X_POS, par.PIED_X_POS):
            li.ajoute("mibois", [i for i in ids if abs(noeuds[i][0] - xt) < 20.0], k_rot(I_mb_x), k_rot(I_mb_y))

    def plaque(li):
        for xt in PLAQUE_X:
            li.ajoute("plaque", bord_haut(noeuds, xt, 12.0), k_rot(I_pl_x), k_rot(I_pl_y))

    print("raideurs 6EI/L (N.mm/rad) : tube %.2e   mi-bois %.2e / %.2e   plaque par tenon %.2e / %.2e"
          % (k_tube, k_rot(I_mb_x), k_rot(I_mb_y), k_rot(I_pl_x), k_rot(I_pl_y)))
    variantes = [("tubes", [tubes]), ("plaque", [tubes, plaque])]
    if getattr(par, "ENTR_HAUT", False):
        variantes.insert(1, ("mibois", [tubes, mibois]))
    positions = {"couche": F1.noeuds_pieds_couche(noeuds), "debout": F1.noeuds_pieds_debout(noeuds)}

    resultats = []
    lignes = ["flambement hors plan, mode symetrique, liaisons en ressorts 6EI/L, tole %g mm, plaque %g (%s)"
              % (par.EP_FLANC, PLAQUE_L, ",".join("%g" % v for v in PLAQUE_X)), ""]
    for pos, ids_pieds in positions.items():
        if not ids_pieds:
            raise SystemExit("pieds %s : aucun noeud" % pos)
        for nom, fs in variantes:
            li = Liaisons(noeuds, premier_element)
            for fn in fs:
                fn(li)
            cas = "%s_%s" % (nom, pos)
            ecrit_inp(cas, avant, corps, noeuds, [("pieds", sorted(ids_pieds))], li)
            print("cas %-14s %d liaisons" % (cas, len(li.blocs))); sys.stdout.flush()
            r = subprocess.run([CCX, "-i", cas], cwd=TRAVAIL, capture_output=True, text=True)
            dat = os.path.join(TRAVAIL, cas + ".dat")
            fac = F1.lire_facteurs(dat) if os.path.isfile(dat) else []
            if not fac:
                print(r.stdout[-2500:]); raise SystemExit("ccx en echec sur %s" % cas)
            modes = F1.lire_modes(os.path.join(TRAVAIL, cas + ".frd"))
            zz = F1.decrit_mode(modes[0], noeuds) if modes else []
            print("   facteurs : %s   vers %s" % ("  ".join("%.2f" % v for v in fac),
                                                 "  ".join("(%d, %d)" % (q["x"], q["z"]) for q in zz[:4])))
            sys.stdout.flush()
            resultats.append(dict(cas=cas, facteurs=[round(v, 3) for v in fac], mode1=zz))
            lignes.append("%-14s facteur critique %6.2f   vers %s"
                          % (cas, fac[0], "  ".join("(%d, %d)" % (q["x"], q["z"]) for q in zz[:4])))
    json.dump(dict(plaque_L=PLAQUE_L, plaque_X=PLAQUE_X, noeuds=len(noeuds), cas=resultats,
                   date_calcul=outils.aujourdhui(), empreinte=outils.empreinte_modele()),
              io.open(os.path.join(HERE, "out", "flambement3.json"), "w"), indent=1)
    io.open(os.path.join(HERE, "out", "flambement3.txt"), "w", encoding="utf-8").write("\n".join(lignes) + "\n")
    print("\n" + "\n".join(lignes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
