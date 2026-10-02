# -*- coding: utf-8 -*-
"""
FLAMBEMENT HORS PLAN, modele a DEUX FLANCS relies par des poutres.

fem_flambement.py impose u_z = 0 la ou une piece traverse le flanc : c'est
supposer cette piece ANCREE. Or rien ne l'est : quand les deux flancs penchent
du meme cote, un tube, une plaque a mi-bois ou une plaque de dessus suivent en
bloc. Ce qu'ils opposent au mouvement, c'est leur raideur de FLEXION entre les
deux flancs (cadre vierendeel), rien de plus. Ici on maille les deux flancs,
on tend entre eux chaque liaison sous forme d'une poutre B32 encastree dans
le flanc par un corps rigide sur la couronne de contact, et on cherche le
facteur critique. Seuls les pieds (plaques profondes, et le sol) tiennent en z.

Liaisons tendues :
  tubes     les six entretoises tubulaires 20 x 4,5 (toujours presentes)
  mibois    + deux plaques verticales 340 x 20 x 8 a mi-bois dans le chant haut
  plaque    + une plaque de DESSUS 600 x 76 x 8 posee sur le chant haut,
              tenons-mortaises a x = 0 et +/- 250 (trois poutres 200 x 8)

chacune couchee et debout. Maillage grossier (9 mm), comme fem_flambement.py.
Resultat : out/flambement2.json et out/flambement2.txt.
"""

import io
import os
import re
import sys
import json
import math
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
import outils
FREECAD = outils.FREECAD
CCX = outils.CCX
FEM = os.path.join(HERE, "out", "fem")
TRAVAIL = os.path.join(HERE, "out", "flamb2")
JSON = os.path.join(HERE, "out", "fem_flanc.json")
MAILLE = os.environ.get("BANC_MAILLE_FLAMB", "9")
N_MODES = 4

import params as par
import parts

sys.path.insert(0, HERE)
from fem_run import lire_noeuds
from fem_flambement import (noeuds_pieds_couche, noeuds_pieds_debout, noeuds_entretoises_hautes,
                            trous_entretoises, lire_facteurs, lire_modes)

DZ = par.ECART_FLANCS + par.EP_FLANC        # decalage du second flanc
Z1 = par.EP_FLANC                           # face interieure du flanc 1
Z2 = par.ECART_FLANCS + par.EP_FLANC        # face interieure du flanc 2
PLAQUE_L = 600.0
PLAQUE_X = (-250.0, 0.0, 250.0)


# ------------------------------------------------------------- lecture du .inp

def lire_inp(texte):
    lignes = texte.splitlines()
    noeuds = lire_noeuds([L + "\n" for L in lignes])
    elems = []
    nsets = {}
    f_noeud = None
    mode = None
    cle = None
    for L in lignes:
        s = L.strip()
        u = s.upper()
        if u.startswith("*ELEMENT"):
            mode = "elem"; continue
        if u.startswith("*NSET"):
            m = re.search(r"NSET=([^,\s]+)", s, re.I)
            cle = m.group(1); nsets.setdefault(cle, []); mode = "nset"; continue
        if u.startswith("*CLOAD"):
            mode = "cload"; continue
        if s.startswith("*"):
            mode = None; continue
        if not s:
            continue
        if mode == "elem":
            elems.append([int(t) for t in s.rstrip(",").split(",") if t.strip()])
        elif mode == "nset":
            nsets[cle].extend(int(t) for t in s.rstrip(",").split(",") if t.strip())
        elif mode == "cload" and f_noeud is None and s.lower().startswith("charge_noeud"):
            f_noeud = float(s.split(",")[2])
    # les elements quadratiques sont ecrits sur deux lignes : recoller
    fixes = []
    cur = []
    for e in elems:
        cur.extend(e)
        if len(cur) >= 11:
            fixes.append(cur[:11]); cur = cur[11:]
    return noeuds, fixes, nsets, f_noeud


def anneau(noeuds, cx, cy, z_face, r0, r1):
    out = []
    for nid, (x, y, z) in noeuds.items():
        if abs(z - z_face) < 0.05 and r0 * r0 <= (x - cx) ** 2 + (y - cy) ** 2 <= r1 * r1:
            out.append(nid)
    return out


def bord_haut(noeuds, cx, demi):
    return [nid for nid, (x, y, z) in noeuds.items()
            if y >= par.H_FLANC - 0.5 and abs(x - cx) <= demi]


# ------------------------------------------------------------- ecriture

class Modele(object):
    def __init__(self, noeuds, elems, nsets, f_noeud):
        self.noeuds = noeuds
        self.elems = elems
        self.nsets = nsets
        self.f = f_noeud
        self.off = max(noeuds) + 1
        self.eoff = max(e[0] for e in elems) + 1
        self.prochain = 2 * self.off + 1
        self.extra_noeuds = []          # (id, x, y, z)
        self.poutres = []               # (elset, [n1, n2, n3])
        self.sections = []              # (elset, type, dims)
        self.rigides = []               # (nset_nom, ids, ref, rot)
        self.nsets_z = []               # (nom, ids) tenus en z
        self.n_liaisons = 0

    def noeud(self, x, y, z):
        nid = self.prochain
        self.prochain += 1
        self.extra_noeuds.append((nid, x, y, z))
        return nid

    def liaison(self, nom, ids1, ids2, x, y, za, zb, section):
        """Poutre entre les deux flancs, encastree par corps rigide dans ids1 (flanc 1) et ids2 (flanc 2)."""
        if not ids1 or not ids2:
            raise SystemExit("liaison %s : couronne vide (%d, %d)" % (nom, len(ids1), len(ids2)))
        a = self.noeud(x, y, za)
        m = self.noeud(x, y, (za + zb) / 2.0)
        b = self.noeud(x, y, zb)
        ra = self.noeud(x, y, za)
        rb = self.noeud(x, y, zb)
        k = self.n_liaisons
        self.n_liaisons += 1
        elset = "L%d" % k
        self.poutres.append((elset, [a, m, b]))
        self.sections.append((elset, section))
        self.rigides.append(("R%da" % k, sorted(ids1), a, ra))
        self.rigides.append(("R%db" % k, sorted([i + self.off for i in ids2]), b, rb))

    def ecrit(self, path, nsets_z):
        o = []
        w = o.append
        w("*NODE, NSET=Nall")
        for nid, (x, y, z) in self.noeuds.items():
            w("%d, %.6f, %.6f, %.6f" % (nid, x, y, z))
        for nid, (x, y, z) in self.noeuds.items():
            w("%d, %.6f, %.6f, %.6f" % (nid + self.off, x, y, z + DZ))
        for (nid, x, y, z) in self.extra_noeuds:
            w("%d, %.6f, %.6f, %.6f" % (nid, x, y, z))
        w("*ELEMENT, TYPE=C3D10, ELSET=Etole")
        for e in self.elems:
            w(", ".join(str(t) for t in e))
        for e in self.elems:
            w(", ".join(str(e[0] + self.eoff if i == 0 else t + self.off) for i, t in enumerate(e)))
        for k, (elset, nn) in enumerate(self.poutres):
            typ = self.sections[k][1][0]
            # CalculiX : la section PIPE n existe que pour les B32R
            w("*ELEMENT, TYPE=%s, ELSET=%s" % ("B32R" if typ == "PIPE" else "B32", elset))
            w("%d, %d, %d, %d" % (2 * self.eoff + k, nn[0], nn[1], nn[2]))
        w("*MATERIAL, NAME=acier")
        w("*ELASTIC")
        w("210000., 0.3")
        w("*SOLID SECTION, ELSET=Etole, MATERIAL=acier")
        for elset, (typ, dims) in self.sections:
            w("*BEAM SECTION, ELSET=%s, MATERIAL=acier, SECTION=%s" % (elset, typ))
            w("%s" % dims)
            w("1., 0., 0.")
        # jeux de noeuds
        def nset(nom, ids):
            w("*NSET, NSET=%s" % nom)
            for j in range(0, len(ids), 12):
                w(", ".join(str(k) for k in ids[j:j + 12]) + ",")
        for nom in ("appui_gauche", "appui_droit", "blocage_x", "charge_noeud"):
            ids = self.nsets[nom]
            nset(nom + "1", ids)
            nset(nom + "2", [i + self.off for i in ids])
        for nom, ids in nsets_z:
            nset(nom, ids)
        for nom, ids, ref, rot in self.rigides:
            nset(nom, ids)
            w("*RIGID BODY, NSET=%s, REF NODE=%d, ROT NODE=%d" % (nom, ref, rot))
        # Le corps rigide ne porte que la TRANSLATION sur le noeud de reference ;
        # sa rotation vit dans les ddl 1-3 du noeud de rotation. Sans ces trois
        # equations, la poutre serait ARTICULEE sur la couronne et tournerait
        # librement : facteurs a 1,00 et modes de mecanisme. On encastre.
        for nom, ids, ref, rot in self.rigides:
            for i in (1, 2, 3):
                w("*EQUATION")
                w("2")
                w("%d, %d, 1., %d, %d, -1." % (ref, i + 3, rot, i))
        w("*BOUNDARY")
        for k in "12":
            w("appui_gauche%s, 2, 2, 0." % k)
            w("appui_droit%s, 2, 2, 0." % k)
            w("blocage_x%s, 1, 1, 0." % k)
        for nom, ids in nsets_z:
            w("%s, 3, 3, 0." % nom)
        w("*STEP")
        w("*BUCKLE")
        w("%d" % N_MODES)
        w("*CLOAD")
        w("charge_noeud1, 2, %.6f" % self.f)
        w("charge_noeud2, 2, %.6f" % self.f)
        w("*NODE FILE")
        w("U")
        w("*END STEP")
        io.open(path, "w", encoding="ascii", newline="\n").write("\n".join(o) + "\n")


# ------------------------------------------------------------- resultats

def caractere(mode, noeuds, off):
    """+1 : les deux flancs penchent du meme cote ; -1 : en sens contraire."""
    num = den1 = den2 = 0.0
    for nid in noeuds:
        a = mode.get(nid); b = mode.get(nid + off)
        if a is None or b is None:
            continue
        num += a[2] * b[2]; den1 += a[2] ** 2; den2 += b[2] ** 2
    return num / math.sqrt(den1 * den2) if den1 > 0 and den2 > 0 else 0.0


def zones(mode, noeuds):
    umax = max(abs(v[2]) for nid, v in mode.items() if nid in noeuds) or 1.0
    z = {}
    for nid, v in mode.items():
        if nid not in noeuds:
            continue
        a = abs(v[2]) / umax
        if a < 0.5:
            continue
        x, y, _ = noeuds[nid]
        cle = (int(round(x / 40.0) * 40), int(round(y / 40.0) * 40))
        z[cle] = max(z.get(cle, 0.0), a)
    return sorted(z.items(), key=lambda t: -t[1])[:6]


# ------------------------------------------------------------- main

def maille():
    if not os.path.isdir(TRAVAIL):
        os.makedirs(TRAVAIL)
    sauve = JSON + ".flamb2"
    if os.path.isfile(JSON):
        shutil.copy(JSON, sauve)
    env = dict(os.environ)
    env["BANC_MAILLE"] = MAILLE
    try:
        print("maillage grossier (%s mm) et charge..." % MAILLE); sys.stdout.flush()
        r1 = subprocess.run([FREECAD, "fem_flanc.py"], cwd=HERE, capture_output=True, text=True, env=env)
        if "ECHEC" in r1.stdout or "Traceback" in r1.stdout + r1.stderr:
            print(r1.stdout[-2000:]); raise SystemExit("maillage en echec")
        r2 = subprocess.run([sys.executable, "fem_run.py"], cwd=HERE, capture_output=True, text=True)
        if "ECHEC" in r2.stdout:
            print(r2.stdout[-2000:]); raise SystemExit("injection de charge en echec")
        shutil.copy(os.path.join(FEM, "maillage.inp"), os.path.join(TRAVAIL, "base.inp"))
    finally:
        if os.path.isfile(sauve):
            shutil.move(sauve, JSON)


def main():
    if "--sans-maillage" not in sys.argv or not os.path.isfile(os.path.join(TRAVAIL, "base.inp")):
        maille()
    texte = io.open(os.path.join(TRAVAIL, "base.inp"), encoding="latin-1").read()
    noeuds, elems, nsets, f = lire_inp(texte)
    print("noeuds %d, elements %d, charge %.3f N par noeud" % (len(noeuds), len(elems), f))

    def tubes(mod):
        # seuls les trous qui recoivent un TUBE : pas les trous de levage ni les tiges de butee
        for (x, y, d, nom) in parts.flanc_trous():
            if "entretoise" not in nom:
                continue
            a1 = anneau(noeuds, x, y, 0.0 + Z1, par.ENTRETOISE_DI / 2.0 - 0.3, par.ENTRETOISE_DE / 2.0 + 0.5)
            # flanc 2 : sa face interieure est la face z = 0 du maillage de base, decalee de DZ
            a2 = anneau(noeuds, x, y, 0.0, par.ENTRETOISE_DI / 2.0 - 0.3, par.ENTRETOISE_DE / 2.0 + 0.5)
            mod.liaison("tube", a1, a2, x, y, Z1, Z2,
                        ("PIPE", "%.3f, %.3f" % (par.ENTRETOISE_DE / 2.0, (par.ENTRETOISE_DE - par.ENTRETOISE_DI) / 2.0)))

    def mibois(mod):
        ids = noeuds_entretoises_hautes(noeuds)
        for xt in (-par.ENTR_HAUT_X, par.ENTR_HAUT_X):
            sel = [i for i in ids if abs(noeuds[i][0] - xt) < 20.0]
            y = par.H_FLANC - par.ENTR_HAUT_CROIX_FLANC / 2.0
            mod.liaison("mibois", sel, sel, xt, y, par.EP_FLANC / 2.0, DZ + par.EP_FLANC / 2.0,
                        ("RECT", "%.3f, %.3f" % (par.EP_FLANC, par.ENTR_HAUT_H)))

    def plaque(mod):
        lx = PLAQUE_L / len(PLAQUE_X)
        for xt in PLAQUE_X:
            sel = bord_haut(noeuds, xt, 12.0)
            y = par.H_FLANC + par.EP_FLANC / 2.0
            mod.liaison("plaque", sel, sel, xt, y, par.EP_FLANC / 2.0, DZ + par.EP_FLANC / 2.0,
                        ("RECT", "%.3f, %.3f" % (lx, par.EP_FLANC)))

    variantes = [("tubes", [tubes]), ("mibois", [tubes, mibois]), ("plaque", [tubes, plaque])]
    positions = {"couche": noeuds_pieds_couche(noeuds), "debout": noeuds_pieds_debout(noeuds)}

    resultats = []
    lignes = ["flambement hors plan, deux flancs relies par des poutres, tole %g mm, %.0f N par flanc, maille %s mm"
              % (par.EP_FLANC, 2.0 * 6000.0, MAILLE), ""]
    for pos, ids_pieds in positions.items():
        for nom, fs in variantes:
            mod = Modele(noeuds, elems, nsets, f)
            for fn in fs:
                fn(mod)
            cas = "%s_%s" % (nom, pos)
            nz = [("pieds1", sorted(ids_pieds)), ("pieds2", sorted(i + mod.off for i in ids_pieds))]
            mod.ecrit(os.path.join(TRAVAIL, cas + ".inp"), nz)
            print("cas %-16s %d liaisons" % (cas, mod.n_liaisons)); sys.stdout.flush()
            r = subprocess.run([CCX, "-i", cas], cwd=TRAVAIL, capture_output=True, text=True)
            dat = os.path.join(TRAVAIL, cas + ".dat")
            fac = lire_facteurs(dat) if os.path.isfile(dat) else []
            if not fac:
                print(r.stdout[-2500:]); raise SystemExit("ccx en echec sur %s" % cas)
            modes = lire_modes(os.path.join(TRAVAIL, cas + ".frd"))
            car = caractere(modes[0], noeuds, mod.off) if modes else 0.0
            zz = zones(modes[0], noeuds) if modes else []
            print("   facteurs : %s   mode 1 %s (%+.2f)  vers %s"
                  % ("  ".join("%.2f" % v for v in fac), "symetrique" if car > 0 else "antisymetrique", car,
                     "  ".join("(%d, %d)" % k for k, _ in zz[:4])))
            sys.stdout.flush()
            resultats.append(dict(cas=cas, facteurs=[round(v, 3) for v in fac], caractere=round(car, 2),
                                  mode1=[dict(x=k[0], z=k[1], amp=round(v, 2)) for k, v in zz]))
            lignes.append("%-16s facteur critique %6.2f  mode %s  vers %s"
                          % (cas, fac[0], "symetrique" if car > 0 else "antisymetrique",
                             "  ".join("(%d, %d)" % k for k, _ in zz[:4])))
    json.dump(dict(maille=MAILLE, noeuds=len(noeuds), cas=resultats),
              io.open(os.path.join(HERE, "out", "flambement2.json"), "w"), indent=1)
    io.open(os.path.join(HERE, "out", "flambement2.txt"), "w", encoding="utf-8").write("\n".join(lignes) + "\n")
    print("\n" + "\n".join(lignes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
