# -*- coding: utf-8 -*-
"""
Ecriture DXF R12 ASCII : LINE, ARC, CIRCLE, TEXT.
R12 est le format le plus surement lu par les decoupeurs laser et jet d'eau.
Les arcs sont exacts, pas de polyligne approchee.
"""

import math


def _g(code, value):
    if isinstance(value, float):
        return "%d\n%.6f\n" % (code, value)
    return "%d\n%s\n" % (code, value)


class Dxf(object):

    def __init__(self):
        self.entities = []
        self.layers = set(["0"])

    # -- entites

    def line(self, p0, p1, layer="DECOUPE"):
        self.layers.add(layer)
        self.entities.append(
            "0\nLINE\n8\n%s\n" % layer
            + _g(10, float(p0[0])) + _g(20, float(p0[1])) + _g(30, 0.0)
            + _g(11, float(p1[0])) + _g(21, float(p1[1])) + _g(31, 0.0))

    def arc(self, c, r, a0_deg, a1_deg, layer="DECOUPE"):
        """DXF : l'arc va TOUJOURS de a0 a a1 dans le sens trigonometrique."""
        self.layers.add(layer)
        self.entities.append(
            "0\nARC\n8\n%s\n" % layer
            + _g(10, float(c[0])) + _g(20, float(c[1])) + _g(30, 0.0)
            + _g(40, float(r))
            + _g(50, float(a0_deg % 360.0)) + _g(51, float(a1_deg % 360.0)))

    def circle(self, c, r, layer="DECOUPE"):
        self.layers.add(layer)
        self.entities.append(
            "0\nCIRCLE\n8\n%s\n" % layer
            + _g(10, float(c[0])) + _g(20, float(c[1])) + _g(30, 0.0)
            + _g(40, float(r)))

    def text(self, p, h, s, layer="TEXTE"):
        self.layers.add(layer)
        self.entities.append(
            "0\nTEXT\n8\n%s\n" % layer
            + _g(10, float(p[0])) + _g(20, float(p[1])) + _g(30, 0.0)
            + _g(40, float(h)) + _g(1, s))

    # -- contours issus de geom2d

    def contour(self, segs, layer="DECOUPE"):
        for s in segs:
            if s[0] == 'L':
                self.line(s[1], s[2], layer)
            else:
                _, c, r, a0, a1, ccw = s
                d0, d1 = math.degrees(a0), math.degrees(a1)
                if ccw:
                    self.arc(c, r, d0, d1, layer)
                else:
                    self.arc(c, r, d1, d0, layer)

    def contours(self, list_of_segs, layer="DECOUPE"):
        for segs in list_of_segs:
            self.contour(segs, layer)

    # -- fichier

    def dumps(self):
        out = []
        out.append("0\nSECTION\n2\nHEADER\n")
        out.append(_g(9, "$ACADVER") + _g(1, "AC1009"))
        out.append(_g(9, "$INSUNITS") + "70\n4\n")          # 4 = millimetres
        out.append(_g(9, "$MEASUREMENT") + "70\n1\n")       # 1 = metrique
        out.append("0\nENDSEC\n")
        out.append("0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n")
        out.append("70\n%d\n" % len(self.layers))
        for i, name in enumerate(sorted(self.layers)):
            color = {"DECOUPE": 7, "TEXTE": 3, "GRAVURE": 1}.get(name, 7)
            out.append("0\nLAYER\n2\n%s\n70\n0\n62\n%d\n6\nCONTINUOUS\n" % (name, color))
        out.append("0\nENDTAB\n0\nENDSEC\n")
        out.append("0\nSECTION\n2\nENTITIES\n")
        out.extend(self.entities)
        out.append("0\nENDSEC\n0\nEOF\n")
        return "".join(out)

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.dumps())
        return path
