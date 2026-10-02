# -*- coding: utf-8 -*-
"""
Controle de lisibilite des planches SVG : textes qui se chevauchent, textes
qui sortent de la feuille, textes traverses par un trait de dessin. Et un
controle de completude : chaque piece du modele doit etre nommee sur au moins
une planche, sinon elle existe en DXF et en 3D mais personne ne la fabrique.

    python verif_plans.py

Purement 2D, sans FreeCAD. La largeur d'un texte est estimee a 0,55 fois sa
hauteur par caractere, ce qui est la moyenne d'Helvetica : c'est assez pour
attraper une superposition, pas pour garantir un millimetre pres.
"""

import os
import re
import sys
import math

import parts as P

HERE = os.path.dirname(os.path.abspath(__file__))
PLANS = os.path.join(HERE, "out", "plans")
LARGEUR_CAR = 0.55          # fraction de la hauteur, Helvetica
MARGE = 8.0                 # mm de bord de feuille
RECOUVREMENT_MAX = 0.4      # mm2 de recouvrement tolere entre deux textes

# On capture la balise entiere puis chaque attribut separement : une seule
# expression avec un groupe optionnel pour le transform le laissait avaler par
# le [^>]* qui suit, et TOUS les textes tournes etaient lus a 0 degre -- fausses
# alertes sur les cotes verticales, et vrais recouvrements manques.
RE_TEXT = re.compile(r'<text ([^>]*)>(.*?)</text>', re.S)
RE_ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')
RE_LINE = re.compile(
    r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"[^>]*?'
    r'stroke-width="([\d.]+)"')
RE_SIZE = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')
RE_PATH = re.compile(r'<path d="([^"]+)"[^>]*?stroke-width="([\d.]+)"')
RE_NUM = re.compile(r'[-+]?\d*\.?\d+(?:e[-+]?\d+)?')


def _deesc(s):
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"'))


def textes(svg):
    """(x0, y0, x1, y1, contenu, angle) de chaque texte, boite estimee."""
    out = []
    for m in RE_TEXT.finditer(svg):
        at = dict(RE_ATTR.findall(m.group(1)))
        x, y, h = float(at["x"]), float(at["y"]), float(at["font-size"])
        anchor = at.get("text-anchor", "start")
        mr = re.match(r'rotate\(([-\d.]+)', at.get("transform", ""))
        ang = mr.group(1) if mr else None
        s = _deesc(m.group(2))
        w = LARGEUR_CAR * h * len(s)
        if anchor == "middle":
            x0, x1 = x - w / 2.0, x + w / 2.0
        elif anchor == "end":
            x0, x1 = x - w, x
        else:
            x0, x1 = x, x + w
        # ligne de base a y ; Helvetica encre de 0,72 h au dessus a 0,21 h en
        # dessous. Prendre toute la hauteur h faisait se toucher les deux lignes
        # d'une meme note, espacees de 3,6 pour 3 de corps.
        y0, y1 = y - 0.75 * h, y + 0.22 * h
        a = float(ang) if ang else 0.0
        if abs(abs(a) - 90.0) < 1.0:
            # texte vertical : la boite tourne autour de l'ancre (x, y)
            cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            hw, hh = (x1 - x0) / 2.0, (y1 - y0) / 2.0
            dx, dy = cx - x, cy - y
            if a > 0:
                ncx, ncy = x - dy, y + dx
            else:
                ncx, ncy = x + dy, y - dx
            x0, x1, y0, y1 = ncx - hh, ncx + hh, ncy - hw, ncy + hw
        elif abs(a) > 1.0:
            # autre angle : on prend la boite englobante du rectangle tourne
            cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            ca, sa = abs(math.cos(math.radians(a))), abs(math.sin(math.radians(a)))
            hw = ((x1 - x0) * ca + (y1 - y0) * sa) / 2.0
            hh = ((x1 - x0) * sa + (y1 - y0) * ca) / 2.0
            x0, x1, y0, y1 = cx - hw, cx + hw, cy - hh, cy + hh
        out.append((x0, y0, x1, y1, s, a))
    return out


def lignes(svg):
    """Segments (x1, y1, x2, y2, largeur) des <line> ET des <path> polygonaux.
    Les arcs d'un path sont pris par leurs extremites : assez pour reperer un
    contour qui passe sous un texte, pas pour le suivre au millimetre."""
    out = [tuple(float(v) for v in m.groups()) for m in RE_LINE.finditer(svg)]
    for m in RE_PATH.finditer(svg):
        d, w = m.group(1), float(m.group(2))
        pts, cur, start = [], None, None
        for cmd in re.finditer(r'([MLAZmlaz])([^MLAZmlaz]*)', d):
            c, nums = cmd.group(1).upper(), [float(x) for x in RE_NUM.findall(cmd.group(2))]
            if c == 'M' and len(nums) >= 2:
                cur = start = (nums[0], nums[1])
            elif c == 'L' and len(nums) >= 2 and cur:
                nxt = (nums[0], nums[1]); out.append((cur[0], cur[1], nxt[0], nxt[1], w)); cur = nxt
            elif c == 'A' and len(nums) >= 7 and cur:
                nxt = (nums[5], nums[6]); out.append((cur[0], cur[1], nxt[0], nxt[1], w)); cur = nxt
            elif c == 'Z' and cur and start:
                out.append((cur[0], cur[1], start[0], start[1], w)); cur = start
    return out


def recouvrement(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if (w > 0 and h > 0) else 0.0


def seg_coupe_boite(x1, y1, x2, y2, b, marge=0.3):
    """Le segment traverse-t-il la boite (reduite d'une marge) ?"""
    bx0, by0, bx1, by1 = b[0] + marge, b[1] + marge, b[2] - marge, b[3] - marge
    if bx1 <= bx0 or by1 <= by0:
        return False
    # Liang-Barsky
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - bx0), (dx, bx1 - x1), (-dy, y1 - by0), (dy, by1 - y1)):
        if abs(p) < 1e-12:
            if q < 0:
                return False
            continue
        t = q / p
        if p < 0:
            if t > t1:
                return False
            t0 = max(t0, t)
        else:
            if t < t0:
                return False
            t1 = min(t1, t)
    return t0 <= t1


def controle_feuille(path):
    svg = open(path, encoding="utf-8").read()
    W, H = (float(v) for v in RE_SIZE.search(svg).groups())
    tx = textes(svg)
    li = lignes(svg)
    fautes = []

    for b in tx:
        if b[0] < MARGE or b[2] > W - MARGE or b[1] < MARGE or b[3] > H - MARGE:
            fautes.append("hors feuille : '%s' (%.0f..%.0f, %.0f..%.0f)"
                          % (b[4][:40], b[0], b[2], b[1], b[3]))

    for i in range(len(tx)):
        for j in range(i + 1, len(tx)):
            r = recouvrement(tx[i], tx[j])
            if r > RECOUVREMENT_MAX:
                fautes.append("textes superposes (%.1f mm2) : '%s' / '%s'"
                              % (r, tx[i][4][:32], tx[j][4][:32]))

    # un trait de dessin qui traverse un texte : on ne compte que les traits
    # forts et moyens, les traits fins de cote portent legitimement leur texte
    for (x1, y1, x2, y2, w) in li:
        if w < 0.3:
            continue
        for b in tx:
            if seg_coupe_boite(x1, y1, x2, y2, b):
                fautes.append("trait a travers '%s'  (segment %.0f,%.0f -> %.0f,%.0f  w %.2f)"
                              % (b[4][:40], x1, y1, x2, y2, w))
                break
    return len(tx), fautes


def controle_completude():
    """Chaque piece du modele nommee sur au moins une planche."""
    corpus = ""
    for f in sorted(os.listdir(PLANS)):
        if f.endswith(".svg"):
            corpus += open(os.path.join(PLANS, f), encoding="utf-8").read().lower()
    corpus = _deesc(corpus)
    absentes = []
    for s in P.all_parts():
        if s.name == "poutre":
            continue
        cles = [s.name.lower().replace("_", " "), s.designation.lower()]
        # un mot cle par piece, le plus discriminant de sa designation
        mots = [m for m in re.split(r"[ ,']", s.designation.lower()) if len(m) > 4]
        if not any(c in corpus for c in cles) and not any(m in corpus for m in mots[:1]):
            absentes.append("%s (%s)" % (s.name, s.designation))
    return absentes


def main():
    total = 0
    n_textes = 0
    for f in sorted(os.listdir(PLANS)):
        if not f.endswith(".svg"):
            continue
        n, fautes = controle_feuille(os.path.join(PLANS, f))
        n_textes += n
        print("%-22s %3d textes  %2d faute(s)" % (f, n, len(fautes)))
        for x in fautes:
            print("      " + x)
        total += len(fautes)
    print()
    abs_ = controle_completude()
    for a in abs_:
        print("PIECE SANS PLANCHE : " + a)
    total += len(abs_)
    print("%d textes controles, %d faute(s)" % (n_textes, total))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
