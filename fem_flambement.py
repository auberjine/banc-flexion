# -*- coding: utf-8 -*-
"""
FLAMBEMENT HORS PLAN du flanc (CalculiX *BUCKLE). La membrure basse est en
compression : a 8 mm de tole, c'est elle qui peut voiler hors de son plan.

Le flanc seul est maille (grossierement : le flambement n'a pas besoin des
angles) et charge comme dans fem_flanc.py, puis on lui impose u_z = 0 la ou
QUELQUE CHOSE le tient hors plan, et on cherche le facteur de charge critique.

Deux hypotheses d'appui, la seconde plus optimiste :

  diaphragmes  : bossages (la poutre et ses patins font diaphragme) et pieds a
                 mi-bois. Les entretoises tubulaires ne sont PAS comptees : c est
                 la borne BASSE, qui neglige la raideur de flexion des tubes.
  entretoises  : en plus, tous les trous d'entretoise et la mortaise de
                 traverse tiennent en z. C est le mode ANTISYMETRIQUE (les deux
                 flancs en sens contraire), ou les tubes travaillent en effort
                 normal : borne HAUTE.

Entre les deux, le mode symetrique reel est celui de fem_flamb3.py, ou chaque
tube est un ressort de rotation 6EI/L : c est LUI le facteur a retenir.

Chaque hypothese est calculee couche (pieds sous la membrure basse) et debout
(pieds dans les chants d'extremite). Des entretoises supplementaires se
testent depuis la ligne de commande, en coordonnees (x, z) du flanc :

    python fem_flambement.py               # 4 cas
    python fem_flambement.py 0:20 -120:20  # + deux appuis a essayer
    python fem_flambement.py --seul 250:436 -250:436   # ces appuis seuls, sur les diaphragmes

Un appui supplementaire est un DIAPHRAGME (plaque a mi-bois qui traverse les
deux flancs), pas un tube : voir le resultat, un tube ne tient pas le mode
symetrique ou les deux flancs penchent du meme cote.

out/fem_flanc.json est sauve et restaure : ce script ne laisse rien derriere lui.
Resultat : out/flambement.json et out/flambement.txt.
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
TRAVAIL = os.path.join(HERE, "out", "flamb")
JSON = os.path.join(HERE, "out", "fem_flanc.json")
MAILLE = os.environ.get("BANC_MAILLE_FLAMB", "9")
N_MODES = 4
SEUL = "--seul" in sys.argv       # avec des appuis supplementaires : ne calculer qu eux

import params as par
import parts

sys.path.insert(0, HERE)
from fem_run import lire_noeuds


# ------------------------------------------------------------- appuis en z

def noeuds_pieds_couche(noeuds):
    """Parois des encoches de pied sous la membrure basse."""
    w = par.PIED_E / 2.0 + par.PIED_JEU / 2.0 + 0.5
    out = []
    for nid, (x, y, z) in noeuds.items():
        if y <= par.PIED_CROIX_FLANC + 0.5 and min(abs(x - par.PIED_X_POS), abs(x + par.PIED_X_POS)) <= w:
            out.append(nid)
    return out


def noeuds_entretoises_hautes(noeuds):
    """Parois des encoches d entretoise haute dans le chant haut : un diaphragme aussi."""
    if not getattr(par, "ENTR_HAUT", False):
        return []
    w = par.PIED_E / 2.0 + par.PIED_JEU / 2.0 + 0.5
    out = []
    for nid, (x, y, z) in noeuds.items():
        if y >= par.H_FLANC - par.ENTR_HAUT_CROIX_FLANC - 0.5 and            min(abs(x - par.ENTR_HAUT_X), abs(x + par.ENTR_HAUT_X)) <= w:
            out.append(nid)
    return out


def noeuds_pieds_debout(noeuds):
    """Parois des deux encoches de coin de l about x = -L/2, a 45 degres."""
    w = par.PIED_E / 2.0 + par.PIED_JEU / 2.0 + 0.5
    ang = math.radians(par.PIED_DEBOUT_ANGLE)
    ca, sa = math.cos(ang), math.sin(ang)
    x0 = -par.L_FLANC / 2.0
    out = []
    for nid, (x, y, z) in noeuds.items():
        for (z0, sz) in ((0.0, 1.0), (par.H_FLANC, -1.0)):
            dx, dy = x - x0, y - z0
            t = dx * ca + sz * dy * sa                # le long de l encoche
            u = abs(-dx * sa + sz * dy * ca)          # a cote
            if 4.0 <= t <= par.PIED_DEBOUT_PROF + 0.5 and u <= w:
                out.append(nid)
                break
    return out


def noeuds_trous(noeuds, centres, rayon):
    """Couronne d'appui d'une entretoise autour de chaque trou."""
    out = []
    r2 = rayon * rayon
    for nid, (x, y, z) in noeuds.items():
        for (cx, cz) in centres:
            if (x - cx) ** 2 + (y - cz) ** 2 <= r2:
                out.append(nid)
                break
    return out


def noeuds_mortaise(noeuds):
    out = []
    for nid, (x, y, z) in noeuds.items():
        if abs(x) <= par.TRAVERSE_LX / 2.0 + 0.5 and par.Z_TAB0 - 0.5 <= y <= par.Z_TAB1 + 0.5:
            out.append(nid)
    return out


def trous_entretoises():
    """Trous d'entretoise qui traversent les DEUX flancs (pas les taraudages de chape)."""
    return [(x, z) for (x, z, d, nom) in parts.flanc_trous() if d > 10.0]


# ------------------------------------------------------------- .inp

def decoupe_inp(texte):
    """Retourne (avant le step, corps du step sans *STATIC ni sorties)."""
    lignes = texte.splitlines()
    i_step = next(i for i, L in enumerate(lignes) if L.strip().upper().startswith("*STEP"))
    avant = lignes[:i_step]
    corps = []
    for L in lignes[i_step + 1:]:
        u = L.strip().upper()
        if u.startswith("*STATIC") or u.startswith("*STEP"):
            continue
        if u.startswith("*NODE FILE") or u.startswith("*EL FILE") or u.startswith("*NODE PRINT") \
           or u.startswith("*EL PRINT") or u.startswith("*END STEP"):
            break
        corps.append(L)
    return avant, corps


def ecrit_inp(nom, avant, corps, jeux):
    """jeux : liste de (nom_nset, [ids]) tenus en z (dof 3)."""
    out = list(avant)
    for nom_set, ids in jeux:
        out.append("*NSET,NSET=%s" % nom_set)
        for j in range(0, len(ids), 12):
            out.append(",".join(str(k) for k in ids[j:j + 12]) + ",")
    out.append("*STEP")
    out.append("*BUCKLE")
    out.append("%d" % N_MODES)
    out.extend(corps)
    if jeux:
        out.append("*BOUNDARY")
        for nom_set, ids in jeux:
            out.append("%s,3,3,0.0" % nom_set)
    out.append("*NODE FILE")
    out.append("U")
    out.append("*END STEP")
    path = os.path.join(TRAVAIL, nom + ".inp")
    io.open(path, "w", encoding="ascii", newline="\n").write("\n".join(out) + "\n")
    return path


# ------------------------------------------------------------- resultats

def lire_facteurs(dat):
    vals = []
    dedans = False
    for L in io.open(dat, encoding="latin-1"):
        if "B U C K L I N G   F A C T O R" in L:
            dedans = True
            continue
        if dedans:
            m = re.match(r"\s*(\d+)\s+([-+0-9.Ee]+)\s*$", L)
            if m:
                vals.append(float(m.group(2)))
            elif vals and L.strip() == "":
                pass
    return vals


def lire_modes(frd):
    """Liste des blocs DISP du .frd : un dict noeud -> (ux, uy, uz) par mode."""
    modes = []
    cur = None
    for L in io.open(frd, encoding="latin-1"):
        if L.startswith(" -4"):
            if L[5:13].strip() == "DISP":
                cur = {}
                modes.append(cur)
            else:
                cur = None
            continue
        if L.startswith(" -3"):
            cur = None
            continue
        if cur is not None and L.startswith(" -1"):
            nid = int(L[3:13])
            vals = []
            k = 13
            s = L.rstrip("\n")
            while k + 12 <= len(s):
                t = s[k:k + 12].strip()
                if t:
                    vals.append(float(t))
                k += 12
            if len(vals) >= 3:
                cur[nid] = vals[:3]
    return modes


def decrit_mode(mode, noeuds):
    """Ou le flanc sort de son plan : zones de 40 mm ou |uz| depasse la moitie du maxi."""
    umax = max(abs(v[2]) for v in mode.values()) or 1.0
    zones = {}
    for nid, v in mode.items():
        a = abs(v[2]) / umax
        if a < 0.5:
            continue
        x, y, _z = noeuds[nid]
        cle = (int(round(x / 40.0) * 40), int(round(y / 40.0) * 40))
        zones[cle] = max(zones.get(cle, 0.0), a)
    tri = sorted(zones.items(), key=lambda t: -t[1])[:8]
    return [dict(x=k[0], z=k[1], amp=round(v, 2)) for k, v in tri]


# ------------------------------------------------------------- main

def main(extra):
    if not os.path.isdir(TRAVAIL):
        os.makedirs(TRAVAIL)
    sauve = JSON + ".flamb"
    if os.path.isfile(JSON):
        shutil.copy(JSON, sauve)
    env = dict(os.environ)
    env["BANC_MAILLE"] = MAILLE
    try:
        print("maillage grossier (%s mm) et charge..." % MAILLE)
        sys.stdout.flush()
        r1 = subprocess.run([FREECAD, "fem_flanc.py"], cwd=HERE, capture_output=True, text=True, env=env)
        if "ECHEC" in r1.stdout or "Traceback" in r1.stdout + r1.stderr:
            print(r1.stdout[-2000:])
            raise SystemExit("maillage en echec")
        r2 = subprocess.run([sys.executable, "fem_run.py"], cwd=HERE, capture_output=True, text=True)
        if "ECHEC" in r2.stdout:
            print(r2.stdout[-2000:])
            raise SystemExit("injection de charge en echec")
        shutil.copy(os.path.join(FEM, "maillage.inp"), os.path.join(TRAVAIL, "base.inp"))
    finally:
        if os.path.isfile(sauve):
            shutil.move(sauve, JSON)

    texte = io.open(os.path.join(TRAVAIL, "base.inp"), encoding="latin-1").read()
    noeuds = lire_noeuds(texte.splitlines(True))
    avant, corps = decoupe_inp(texte)
    print("noeuds : %d" % len(noeuds))

    rayon = par.ENTRETOISE_DE / 2.0 + 0.5
    trous = trous_entretoises()
    haut = [("entretoises_hautes", noeuds_entretoises_hautes(noeuds))] if getattr(par, "ENTR_HAUT", False) else []
    jeux_base = {
        "couche": [("pieds_couche", noeuds_pieds_couche(noeuds))] + haut,
        "debout": [("pieds_debout", noeuds_pieds_debout(noeuds))] + haut,
    }
    jeu_entr = [("entretoises", noeuds_trous(noeuds, trous, rayon)),
                ("mortaise", noeuds_mortaise(noeuds))]
    jeu_extra = [("entretoises_sup", noeuds_trous(noeuds, extra, rayon))] if extra else []

    cas = []
    for pos in ("couche", "debout"):
        if not (extra and SEUL):
            cas.append(("diaphragmes_" + pos, jeux_base[pos]))
            cas.append(("entretoises_" + pos, jeux_base[pos] + jeu_entr))
        if extra:
            # les appuis supplementaires s'ajoutent aux seuls diaphragmes : c'est
            # l'hypothese basse qu'ils doivent relever, pas l'hypothese haute
            cas.append(("supplement_" + pos, jeux_base[pos] + jeu_extra))

    resultats = []
    lignes = ["flambement hors plan du flanc, tole %g mm, charge %.0f N par flanc, maille %s mm"
              % (par.EP_FLANC, 2.0 * 6000.0, MAILLE), ""]
    for nom, jeux in cas:
        for ns, ids in jeux:
            if not ids:
                raise SystemExit("jeu %s vide dans le cas %s" % (ns, nom))
        ecrit_inp(nom, avant, corps, jeux)
        print("cas %-22s appuis z : %s" % (nom, ", ".join("%s(%d)" % (ns, len(ids)) for ns, ids in jeux)))
        sys.stdout.flush()
        r = subprocess.run([CCX, "-i", nom], cwd=TRAVAIL, capture_output=True, text=True)
        dat = os.path.join(TRAVAIL, nom + ".dat")
        frd = os.path.join(TRAVAIL, nom + ".frd")
        if not os.path.isfile(dat):
            print(r.stdout[-1500:])
            raise SystemExit("ccx en echec")
        facteurs = lire_facteurs(dat)
        if not facteurs:
            print(r.stdout[-1500:])
            raise SystemExit("pas de facteur de flambement dans %s" % dat)
        modes = lire_modes(frd)
        zones = decrit_mode(modes[0], noeuds) if modes else []
        print("   facteurs : %s" % "  ".join("%.2f" % f for f in facteurs))
        print("   mode 1 : " + "  ".join("(%d, %d) %.2f" % (z["x"], z["z"], z["amp"]) for z in zones[:5]))
        sys.stdout.flush()
        resultats.append(dict(cas=nom, facteurs=[round(f, 3) for f in facteurs],
                              appuis=dict((ns, len(ids)) for ns, ids in jeux), mode1=zones))
        lignes.append("%-22s facteur critique %6.2f   (modes suivants %s)"
                      % (nom, facteurs[0], " ".join("%.2f" % f for f in facteurs[1:])))
        lignes.append("   sort du plan vers : " + "  ".join("(%d, %d)" % (z["x"], z["z"]) for z in zones[:5]))
    nom_json = "flambement_sup.json" if (extra and SEUL) else "flambement.json"
    json.dump(dict(maille=MAILLE, noeuds=len(noeuds), extra=extra, cas=resultats),
              io.open(os.path.join(HERE, "out", nom_json), "w"), indent=1)
    io.open(os.path.join(HERE, "out", nom_json.replace(".json", ".txt")), "w", encoding="utf-8").write("\n".join(lignes) + "\n")
    print("\n" + "\n".join(lignes))
    return 0


if __name__ == "__main__":
    extra = []
    for a in sys.argv[1:]:
        if a.startswith("--"):
            continue
        x, z = a.split(":")
        extra.append((float(x), float(z)))
    raise SystemExit(main(extra))
