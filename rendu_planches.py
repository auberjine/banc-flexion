# -*- coding: utf-8 -*-
"""
Rend les planches SVG en PNG pour les relire a l'oeil (et pour les agents).

    python rendu_planches.py [dossier_sortie]

Ecrit <dossier>/0X_nom.png en 3200 x 2262 px (A3 420 x 297 mm, soit 7,619 px
par mm de feuille). Dossier par defaut : out/rendus. Il faut un navigateur
Chromium sans interface et Pillow (voir outils.py : Edge sous Windows, chromium ou
google-chrome sous Linux).
"""

import glob
import os
import subprocess
import sys
import tempfile

from PIL import Image

import outils

HERE = os.path.dirname(os.path.abspath(__file__))
PX_PAR_MM = 3200.0 / 420.0
# Chromium sans interface recent retranche de --window-size la hauteur d'un
# cadre de fenetre : a 1600 x 1132 la capture s'arretait a 274 mm de feuille,
# sans le bas du cartouche. On pose donc la planche a sa taille exacte dans
# une page plus haute, puis on recadre.
MARGE_FENETRE = 200


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out", "rendus")
    os.makedirs(sortie, exist_ok=True)
    nav = outils.navigateur()
    if not nav:
        raise SystemExit("aucun navigateur Chromium trouve : definir BANC_NAVIGATEUR")
    svgs = sorted(glob.glob(os.path.join(HERE, "out", "plans", "0*.svg")))
    if not svgs:
        raise SystemExit("aucune planche : lancer d'abord python plans.py")
    tmp = tempfile.mkdtemp(prefix="rendu_")
    w, h = 1600, int(round(1600 * 297.0 / 420.0))
    for f in svgs:
        png = os.path.join(sortie, os.path.splitext(os.path.basename(f))[0] + ".png")
        if os.path.isfile(png):
            os.remove(png)
        url_svg = "file:///" + os.path.abspath(f).replace(os.sep, "/").lstrip("/")
        page = os.path.join(tmp, "planche.html")
        with open(page, "w", encoding="utf-8") as fh:
            fh.write('<!doctype html><html><body style="margin:0;background:#fff">'
                     '<img src="%s" style="display:block;width:%dpx;height:%dpx">'
                     '</body></html>' % (url_svg, w, h))
        url = "file:///" + os.path.abspath(page).replace(os.sep, "/").lstrip("/")
        brut = os.path.join(tmp, "brut.png")
        subprocess.run([nav] + outils.options_navigateur()
                       + ["--force-device-scale-factor=2", "--allow-file-access-from-files",
                          "--window-size=%d,%d" % (w, h + MARGE_FENETRE),
                          "--screenshot=" + brut, url],
                       capture_output=True, text=True, timeout=120)
        if os.path.isfile(brut):
            Image.open(brut).crop((0, 0, 2 * w, 2 * h)).save(png)
            os.remove(brut)
        print(("  %s" if os.path.isfile(png) else "  ECHEC %s") % png)

if __name__ == "__main__":
    main()
