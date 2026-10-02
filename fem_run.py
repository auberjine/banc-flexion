# -*- coding: utf-8 -*-
"""
Complete le fichier CalculiX ecrit par FreeCAD (bloc de charge vide), lance le
calcul et depouille le .frd.

    python fem_run.py

Le maillage, le materiau et les appuis viennent de fem_flanc.py. Ici on ajoute
la charge de 6 kN vers le haut sur les deux trous de traverse, on resout, et on
sort la contrainte de von Mises et les points chauds.
"""

import os
import re
import math
import json
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TRAVAIL = os.path.join(HERE, "out", "fem")
INP = os.path.join(TRAVAIL, "maillage.inp")
import outils
CCX = outils.CCX

import params as par

CHARGE = 6000.0            # N vers le haut, sur un flanc

# La traverse n'est plus boulonnee : ses tenons prennent appui sur l'ARETE
# SUPERIEURE de la mortaise. La charge s'applique donc sur cette arete, et non
# plus sur le pourtour de deux trous. Le maillage est dans le plan (x, y) du
# fichier CalculiX, ou y porte le z du modele.
CIBLE_Z = par.Z_TAB1 + par.TRAVERSE_JEU / 2.0
# Demi largeur de l'arete DROITE, conges exclus. Le jeu valant deux fois le
# rayon, elle fait exactement la largeur du paquet de tenons. Charger au dela
# reviendrait a poser la charge sur le conge lui-meme et a y fabriquer une
# concentration qui n'existe pas : 139 MPa au lieu de 120 pour un Kt de 10 sur
# un R2, ce qui n'a aucun sens.
CIBLE_X = par.TRAVERSE_LX / 2.0


# ------------------------------------------------------------- .inp

def lire_noeuds(lignes):
    noeuds = {}
    dedans = False
    for L in lignes:
        s = L.strip()
        if s.upper().startswith("*NODE"):
            dedans = True
            continue
        if dedans and s.startswith("*"):
            break
        if dedans and s:
            m = s.split(",")
            if len(m) >= 4:
                noeuds[int(m[0])] = (float(m[1]), float(m[2]), float(m[3]))
    return noeuds


def noeuds_charge(noeuds):
    """Noeuds de l'arete superieure de la mortaise de traverse."""
    out = []
    for nid, (x, y, z) in noeuds.items():
        if abs(y - CIBLE_Z) < 0.25 and abs(x) < CIBLE_X - 0.25:
            out.append(nid)
    return sorted(out)


def deja_injecte(lignes):
    """
    Le .inp a-t-il DEJA recu une charge ? Injecter deux fois laisserait deux
    jeux de *NSET,NSET=charge_noeud : CalculiX les cumule et la charge est
    doublee sans un mot. C'est arrive, et le resultat etait faux d'un facteur
    entier sans que rien ne le signale.
    """
    return sum(1 for L in lignes
               if L.strip().upper().startswith("*NSET") and "charge_noeud" in L)


def injecte(lignes, ids, f_par_noeud):
    out = []
    i = 0
    fait = False
    while i < len(lignes):
        L = lignes[i]
        if not fait and L.strip().upper().startswith("*CLOAD"):
            out.append("*NSET,NSET=charge_noeud\n")
            for j in range(0, len(ids), 12):
                out.append(",".join(str(k) for k in ids[j:j + 12]) + ",\n")
            out.append("*CLOAD\n")
            out.append("charge_noeud,2,%.6f\n" % f_par_noeud)
            i += 1
            while i < len(lignes) and not lignes[i].strip().startswith("*"):
                i += 1
            fait = True
            continue
        out.append(L)
        i += 1
    if not fait:
        raise RuntimeError("bloc *CLOAD introuvable")
    return out


# ------------------------------------------------------------- .frd

def lire_frd(path):
    """Retourne (deplacements, contraintes) indexes par numero de noeud."""
    dep, con = {}, {}
    bloc = None
    with open(path) as f:
        for L in f:
            if L.startswith(" -4"):
                nom = L[5:13].strip()
                bloc = {"DISP": "D", "STRESS": "S"}.get(nom)
                continue
            if L.startswith(" -3"):
                bloc = None
                continue
            if bloc and L.startswith(" -1"):
                nid = int(L[3:13])
                vals = []
                k = 13
                while k + 12 <= len(L.rstrip("\n")):
                    t = L[k:k + 12].strip()
                    if t:
                        vals.append(float(t))
                    k += 12
                if bloc == "D" and len(vals) >= 3:
                    dep[nid] = vals[:3]
                elif bloc == "S" and len(vals) >= 6:
                    con[nid] = vals[:6]
    return dep, con


def von_mises(s):
    sxx, syy, szz, sxy, syz, szx = s
    return math.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2)
                     + 3.0 * (sxy ** 2 + syz ** 2 + szx ** 2))


# ------------------------------------------------------------- main

def main():
    lignes = open(INP).readlines()
    n_deja = deja_injecte(lignes)
    if n_deja:
        print("ECHEC : %s porte deja %d jeu(x) de charge." % (os.path.basename(INP), n_deja))
        print("        Relancer fem_flanc.py pour regenerer un maillage propre.")
        return 1
    noeuds = lire_noeuds(lignes)
    ids = noeuds_charge(noeuds)
    print("noeuds du maillage : %d" % len(noeuds))
    print("noeuds charges     : %d sur l arete de mortaise" % len(ids))
    if len(ids) < 20:
        print("ECHEC : trop peu de noeuds reperes")
        return 1

    f = CHARGE / len(ids)
    neuf = injecte(lignes, ids, f)
    open(INP, "w").writelines(neuf)
    print("charge injectee    : %.3f N par noeud, %.0f N au total" % (f, f * len(ids)))

    print("resolution CalculiX...")
    r = subprocess.run([CCX, "-i", "maillage"], cwd=TRAVAIL,
                       capture_output=True, text=True)
    fin = r.stdout.strip().splitlines()[-6:]
    for L in fin:
        print("   " + L)

    frd = os.path.join(TRAVAIL, "maillage.frd")
    dep, con = lire_frd(frd)
    print("resultats : %d deplacements, %d tenseurs" % (len(dep), len(con)))
    if not con:
        print("ECHEC : pas de contraintes dans le .frd")
        return 1

    vm = dict((nid, von_mises(s)) for nid, s in con.items())
    vals = sorted(vm.values())
    vmax = vals[-1]
    dmax = max(math.sqrt(sum(v * v for v in d)) for d in dep.values())

    print("")
    print("=" * 62)
    print("von Mises maxi         %8.1f MPa" % vmax)
    print("99,9e centile          %8.1f MPa" % vals[int(0.999 * len(vals))])
    print("99e centile            %8.1f MPa" % vals[int(0.99 * len(vals))])
    print("95e centile            %8.1f MPa" % vals[int(0.95 * len(vals))])
    print("coefficient sur %-7s %8.2f" % (par.NUANCE_TOLE, par.RE_TOLE / vmax))
    print("fleche maxi            %8.3f mm" % dmax)
    print("=" * 62)

    # points chauds regroupes par zone de 30 mm
    zones = {}
    for nid, v in sorted(vm.items(), key=lambda t: -t[1])[:1500]:
        x, y, _z = noeuds[nid]
        cle = (int(round(x / 30.0) * 30), int(round(y / 30.0) * 30))
        if cle not in zones or zones[cle] < v:
            zones[cle] = v
    tri = sorted(zones.items(), key=lambda t: -t[1])[:16]
    print("")
    print("points chauds (x, z, von Mises) :")
    for (cle, v) in tri:
        print("   x %6d   z %6d   %7.1f MPa" % (cle[0], cle[1], v))

    out = dict(charge_N=CHARGE, noeuds_charges=len(ids),
               von_mises_max=round(vmax, 1),
               centile_999=round(vals[int(0.999 * len(vals))], 1),
               centile_99=round(vals[int(0.99 * len(vals))], 1),
               coef_securite=round(par.RE_TOLE / vmax, 2),
               fleche_max=round(dmax, 3), noeuds=len(noeuds),
               points_chauds=[dict(x=k[0], z=k[1], mpa=round(v, 1)) for k, v in tri])
    json.dump(out, open(os.path.join(HERE, "out", "fem_flanc.json"), "w"), indent=1)
    print("\nresultat ecrit dans out/fem_flanc.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
