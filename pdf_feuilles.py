# -*- coding: utf-8 -*-
"""
Un PDF par feuille de plan, decoupe dans le PDF de toutes les planches.

    python pdf_feuilles.py

Lit out/plans/plans.pdf (ou plans_indice<X>.pdf s'il est plus recent : c'est
la copie que make.py ecrit quand plans.pdf est ouvert ailleurs) et ecrit
out/plans/pdf/<repere>_<piece>.pdf, une page chacun, au nom de la feuille SVG.
Les pages sont dans l'ordre de plans.html, qui est celui des SVG tries par nom.
Il faut pypdf (pip install pypdf).
"""

import glob
import os
import sys

from pypdf import PdfReader, PdfWriter

HERE = os.path.dirname(os.path.abspath(__file__))
PLANS = os.path.join(HERE, "out", "plans")
SORTIE = os.path.join(PLANS, "pdf")


def main():
    sources = [f for f in [os.path.join(PLANS, "plans.pdf")]
               + glob.glob(os.path.join(PLANS, "plans_indice*.pdf")) if os.path.isfile(f)]
    if not sources:
        raise SystemExit("aucun PDF des planches : lancer make.py")
    source = max(sources, key=os.path.getmtime)
    svgs = sorted(f for f in os.listdir(PLANS) if f.endswith(".svg"))
    pages = PdfReader(source).pages
    if len(pages) != len(svgs):
        raise SystemExit("%s a %d pages pour %d feuilles SVG : PDF perime, relancer make.py"
                         % (os.path.basename(source), len(pages), len(svgs)))
    os.makedirs(SORTIE, exist_ok=True)
    for vieux in glob.glob(os.path.join(SORTIE, "*.pdf")):   # feuilles disparues
        try:
            os.remove(vieux)
        except PermissionError:
            pass
    echecs = 0
    for nom, page in zip(svgs, pages):
        w = PdfWriter()
        w.add_page(page)
        cible = os.path.join(SORTIE, os.path.splitext(nom)[0] + ".pdf")
        try:
            with open(cible, "wb") as fh:
                w.write(fh)
        except PermissionError:
            print("!! %s est ouvert ailleurs : non reecrit" % os.path.basename(cible))
            echecs += 1
    print("%d PDF de feuille ecrits dans out/plans/pdf (depuis %s), %d echec(s)"
          % (len(svgs) - echecs, os.path.basename(source), echecs))
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
