# -*- coding: utf-8 -*-
"""
Reconstruit tout le livrable a partir de params.py.

    python make.py

Enchaine : controle des cotes, controle des ligaments, modele 3D FreeCAD (FCStd,
STEP, STL, projection), DXF de decoupe, plans A3, lisibilite des planches, PDF
des planches (Edge), visionneuse 3D, nomenclature, specification, controle
d'interference. Le calcul elements finis se lance a part (fem_flanc.py puis
fem_run.py), il prend plusieurs minutes.
"""

import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
import outils
FREECAD = outils.FREECAD


def etape(titre, cmd, shell=False, attendus=()):
    """Lance une etape. Elle est en echec si son code de retour n'est pas nul,
    OU si l'un des textes `attendus` manque a sa sortie : params.py et
    verif_interference.py (sous freecadcmd) rendent 0 meme quand ils trouvent
    un probleme, seul leur bilan imprime le dit."""
    print("\n" + "=" * 70)
    print(">>> " + titre)
    print("=" * 70)
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, shell=shell)
    sortie = (r.stdout or "") + (r.stderr or "")
    garder = []
    for L in sortie.splitlines():
        s = L.strip()
        if not s or s.startswith("Recompute") or "%)" in s or s.startswith("***"):
            continue
        if s.startswith("FreeCAD 1.0") or s.startswith("(C) 2001") or s.startswith("FreeCAD is free"):
            continue
        if s.startswith("saving") or s.startswith("** WorkSession") or s.startswith("Step File"):
            continue
        garder.append(L)
    print("\n".join(garder[-40:]))
    if r.returncode != 0:
        print("!! code de retour", r.returncode)
        return r.returncode
    manquent = [a for a in attendus if a not in sortie]
    if manquent:
        print("!! bilan attendu absent : " + " ; ".join(a.strip() for a in manquent))
        return 1
    return 0


def main():
    codes = []
    codes.append(etape("controle des cotes", [sys.executable, "params.py"],
                       attendus=("\n0 probleme(s)",)))
    codes.append(etape("controle des ligaments de percage",
                       [sys.executable, "verif_percages.py"], attendus=("\n0 faute(s)",)))
    codes.append(etape("modele 3D, STEP, STL, projection", [FREECAD, "build_freecad.py"]))
    codes.append(etape("DXF de decoupe", [sys.executable, "export_dxf.py"]))
    codes.append(etape("plans A3", [sys.executable, "plans.py"]))
    codes.append(etape("lisibilite des planches", [sys.executable, "verif_plans.py"],
                       attendus=("textes controles, 0 faute(s)",)))
    # le PDF n est pas produit par plans.py : sans cette etape il reste celui d avant
    edge = outils.navigateur()
    if edge:
        html = os.path.join(HERE, "out", "plans", "plans.html")
        pdf = os.path.join(HERE, "out", "plans", "plans.pdf")
        c = etape("PDF des planches (navigateur)", [edge] + outils.options_navigateur()
                  + ["--no-pdf-header-footer", "--print-to-pdf=" + pdf, html])
        # un PDF ouvert dans une visionneuse est verrouille : Edge n'y ecrit
        # pas, sans toujours le dire. On juge sur la date du fichier.
        if c == 0 and (not os.path.isfile(pdf) or os.path.getmtime(pdf) < os.path.getmtime(html)):
            # verrouille par un lecteur : on ecrit le PDF a cote, au nom de
            # l'indice, plutot que de laisser un PDF perime sans en avoir d'autre
            import params as _p
            secours = os.path.join(HERE, "out", "plans", "plans_indice%s.pdf" % _p.INDICE_REVISION)
            c = etape("PDF des planches, a cote (plans.pdf est ouvert)", [edge] + outils.options_navigateur()
                      + ["--no-pdf-header-footer", "--print-to-pdf=" + secours, html])
            if c == 0 and os.path.isfile(secours) and os.path.getmtime(secours) >= os.path.getmtime(html):
                print("!! %s est ouvert ailleurs et n'a pas ete reecrit : PDF a jour dans %s"
                      % (pdf, os.path.basename(secours)))
            else:
                print("!! PDF des planches non regenere (%s ouvert ?)" % pdf)
                c = 1
        codes.append(c)
    else:
        print("\n!! aucun navigateur Chromium (Edge, Chrome, Chromium) : PDF des planches NON regenere ; voir outils.py")
        codes.append(1)
    codes.append(etape("visionneuse 3D", [sys.executable, "viewer3d.py"]))
    codes.append(etape("nomenclature", [sys.executable, "nomenclature.py"]))
    codes.append(etape("nomenclature Excel", [sys.executable, "nomenclature_xlsx.py"]))
    codes.append(etape("specification", [sys.executable, "spec.py"]))
    codes.append(etape("controle d interference", [FREECAD, "verif_interference.py"],
                       attendus=(" 0 interference(s) reelle(s)", " 0 rompu(s)")))

    print("\n" + "=" * 70)
    print("termine, %d etape(s) en echec" % sum(1 for c in codes if c != 0))
    print("=" * 70)
    for racine, _d, fichiers in os.walk(os.path.join(HERE, "out")):
        n = len(fichiers)
        if n:
            print("  %-28s %3d fichier(s)" % (os.path.relpath(racine, HERE), n))


if __name__ == "__main__":
    main()
