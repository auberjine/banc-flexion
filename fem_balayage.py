# -*- coding: utf-8 -*-
"""
Balayage d un parametre par le calcul EF du flanc : pour chaque valeur, on
reecrit la ligne dans params.py, on remaille (fem_flanc.py), on resout
(fem_run.py), on releve le resultat. A la fin, params.py et out/fem_flanc.json
sont RESTAURES tels qu ils etaient : le balayage ne laisse rien derriere lui.

    python fem_balayage.py R_FEN_BAS 10 14 18 22 26

Chaque point coute un maillage et une resolution, plusieurs minutes.
"""

import io
import os
import re
import sys
import json
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
import outils
FREECAD = outils.FREECAD
PARAMS = os.path.join(HERE, "params.py")
JSON = os.path.join(HERE, "out", "fem_flanc.json")


def ligne_param(src, nom):
    m = re.search(r"^%s = ([^#\n]+)(#.*)?$" % re.escape(nom), src, re.M)
    if not m:
        raise SystemExit("parametre %s introuvable" % nom)
    return m


def main(nom, valeurs):
    orig = io.open(PARAMS, encoding="utf-8").read()
    sauve = JSON + ".balayage"
    if os.path.isfile(JSON):
        shutil.copy(JSON, sauve)
    resultats = []
    try:
        for v in valeurs:
            m = ligne_param(orig, nom)
            neuf = orig[:m.start(1)] + ("%g " % v) + orig[m.end(1):]
            io.open(PARAMS, "w", encoding="utf-8", newline="\r\n").write(neuf)
            print("=== %s = %g" % (nom, v)); sys.stdout.flush()
            r1 = subprocess.run([FREECAD, "fem_flanc.py"], cwd=HERE, capture_output=True, text=True)
            if "ECHEC" in r1.stdout or "Traceback" in r1.stdout + r1.stderr:
                print("   maillage en echec"); resultats.append((v, None)); continue
            r2 = subprocess.run([sys.executable, "fem_run.py"], cwd=HERE, capture_output=True, text=True)
            if not os.path.isfile(JSON) or "ECHEC" in r2.stdout:
                print("   resolution en echec"); resultats.append((v, None)); continue
            d = json.load(io.open(JSON, encoding="utf-8"))
            chaud = d["points_chauds"][0]
            print("   von Mises %.1f MPa  coef %.2f  fleche %.3f  point chaud (%d, %d)"
                  % (d["von_mises_max"], d["coef_securite"], d["fleche_max"], chaud["x"], chaud["z"]))
            sys.stdout.flush()
            resultats.append((v, d))
    finally:
        io.open(PARAMS, "w", encoding="utf-8", newline="\r\n").write(orig)
        if os.path.isfile(sauve):
            shutil.move(sauve, JSON)
        print("params.py et fem_flanc.json restaures")
    print()
    print("%-8s %10s %8s %8s" % (nom, "von Mises", "coef", "fleche"))
    for v, d in resultats:
        if d is None:
            print("%-8g %10s" % (v, "echec"))
        else:
            print("%-8g %10.1f %8.2f %8.3f" % (v, d["von_mises_max"], d["coef_securite"], d["fleche_max"]))
    json.dump([(v, None if d is None else dict(vm=d["von_mises_max"], coef=d["coef_securite"],
                                                fleche=d["fleche_max"]))
               for v, d in resultats],
              io.open(os.path.join(HERE, "out", "balayage_%s.json" % nom), "w"), indent=1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], [float(x) for x in sys.argv[2:]])
