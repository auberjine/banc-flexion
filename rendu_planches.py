# -*- coding: utf-8 -*-
"""
Rend les planches SVG en PNG pour les relire a l'oeil (et pour les agents).

    python rendu_planches.py [dossier_sortie]

Ecrit <dossier>/0X_nom.png en 3200 x 2264 px (A3 420 x 297 mm, soit 7,619 px
par mm de feuille). Dossier par defaut : out/rendus. Il faut un navigateur
Chromium sans interface (voir outils.py : Edge sous Windows, chromium ou
google-chrome sous Linux).
"""

import glob
import os
import subprocess
import sys

import outils

HERE = os.path.dirname(os.path.abspath(__file__))
PX_PAR_MM = 3200.0 / 420.0


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out", "rendus")
    os.makedirs(sortie, exist_ok=True)
    nav = outils.navigateur()
    if not nav:
        raise SystemExit("aucun navigateur Chromium trouve : definir BANC_NAVIGATEUR")
    svgs = sorted(glob.glob(os.path.join(HERE, "out", "plans", "0*.svg")))
    if not svgs:
        raise SystemExit("aucune planche : lancer d'abord python plans.py")
    for f in svgs:
        png = os.path.join(sortie, os.path.splitext(os.path.basename(f))[0] + ".png")
        url = "file:///" + os.path.abspath(f).replace(os.sep, "/").lstrip("/")
        subprocess.run([nav] + outils.options_navigateur()
                       + ["--force-device-scale-factor=2", "--window-size=1600,1132",
                          "--screenshot=" + png, url],
                       capture_output=True, text=True, timeout=120)
        print(("  %s" if os.path.isfile(png) else "  ECHEC %s") % png)


if __name__ == "__main__":
    main()
