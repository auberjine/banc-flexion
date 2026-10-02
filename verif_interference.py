# -*- coding: utf-8 -*-
"""Controle d'interference sur l'assemblage, avec avancement.

    <freecadcmd> verif_interference.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import FreeCAD as App

def p(*a):
    print(*a); sys.stdout.flush()

ATTENDUS = {("coin", "vis"),            # tige engagee dans son taraudage
            ("flanc", "pied"),          # nodes des encoches : 0,1 de serrage par joue, voulu
            ("coulisseau", "guide")}    # vis de guidage dans le sien

# Pieces qui DOIVENT se toucher. Un jeu ici n'est pas une interference, donc
# rien ne le signalait : le coin est reste 5,9 mm au dessus du coulisseau
# pendant deux versions, la chaine d'effort ouverte, sans qu'aucun controle ne
# bronche. La liste suit l'effort du coin jusqu'aux appuis.
CONTACTS = [
    ("plaquette_haute", "traverse"),
    ("coin", "plaquette_haute"),
    ("coin", "plaquette_basse"),
    ("plaquette_basse", "coulisseau"),
    ("guide", "coulisseau"),
    ("coulisseau", "pile_belleville"),
    ("pile_belleville", "poussoir"),
    ("poussoir", "patin_charge"),
    ("pied", "flanc"),
    ("pied", "crochet"),
    ("patin_charge", "poutre"),
    ("poutre", "plat_renfort"),
    ("plat_renfort", "patin_appui"),
    ("patin_appui", "flanc"),
    ("entretoise_vis", "flanc"),
    ("entretoise_vis", "support"),
]
JEU_MAX = 0.01                 # mm : au dela, les pieces ne se touchent plus

def main():
    doc = App.openDocument(os.path.join(HERE, "out", "fcstd", "banc.FCStd"))
    objs = [o for o in doc.Objects if hasattr(o, "Shape")]
    p("%d corps dans l'assemblage" % len(objs))
    bad = 0
    n = 0
    for i in range(len(objs)):
        for j in range(i + 1, len(objs)):
            a, b = objs[i].Shape, objs[j].Shape
            if not a.BoundBox.intersect(b.BoundBox):
                continue
            paire = tuple(sorted((objs[i].Name.rsplit("_", 1)[0],
                                  objs[j].Name.rsplit("_", 1)[0])))
            n += 1
            try:
                v = a.common(b).Volume
            except Exception as e:
                p("  !! %s / %s : %s" % (objs[i].Name, objs[j].Name, e))
                continue
            if v > 1.0:
                if paire in ATTENDUS:
                    p("  (engrenement) %-18s / %-18s : %.0f mm3"
                      % (objs[i].Name, objs[j].Name, v))
                else:
                    p("  INTERFERENCE  %-18s / %-18s : %.0f mm3"
                      % (objs[i].Name, objs[j].Name, v))
                    bad += 1
    p("%d paires testees, %d interference(s) reelle(s)" % (n, bad))

    # ---- contacts obligatoires
    par_nom = {}
    for o in objs:
        par_nom.setdefault(o.Name.rsplit("_", 1)[0], []).append(o)
    manque = 0
    for (a, b) in CONTACTS:
        if a not in par_nom or b not in par_nom:
            p("  ABSENT      %s / %s" % (a, b))
            manque += 1
            continue
        d = min(x.Shape.distToShape(y.Shape)[0]
                for x in par_nom[a] for y in par_nom[b])
        if d > JEU_MAX:
            p("  PAS DE CONTACT %-16s / %-16s : %.3f mm" % (a, b, d))
            manque += 1
    p("%d contacts verifies, %d rompu(s)" % (len(CONTACTS), manque))
    bad += manque

main()
