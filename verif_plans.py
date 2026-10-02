# -*- coding: utf-8 -*-
"""
Controle de lisibilite des planches SVG : textes qui se chevauchent, textes
qui sortent de la feuille, textes traverses par un trait de dessin. Et un
controle de completude : chaque piece du modele doit etre nommee sur au moins
une planche, sinon elle existe en DXF et en 3D mais personne ne la fabrique.

    python verif_plans.py

Purement 2D, sans FreeCAD. La largeur d'un texte est estimee par les chasses
d'Helvetica (gras ignore) : assez pour attraper une superposition, pas pour
garantir un millimetre pres. Tout trait compte, traits fins de cote compris,
contre la boite orientee de chaque texte.
"""

import os
import re
import sys
import math

import parts as P

HERE = os.path.dirname(os.path.abspath(__file__))
PLANS = os.path.join(HERE, "out", "plans")
LARGEUR_CAR = 0.55          # fraction de la hauteur, Helvetica, hors table
# chasses d'Helvetica (AFM Adobe, millimes de corps), caracteres 32 a 126 :
# une note longue en minuscules fait 15 % de moins que 0,55 par caractere,
# assez pour inventer un trait qui la traverse.
CHASSE = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278,
          556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556,
          1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
          667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
          333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
          556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]


def largeur(s, h):
    """Largeur d'encre estimee d'un texte de corps h, en mm."""
    return h * sum(CHASSE[ord(c) - 32] / 1000.0 if 32 <= ord(c) <= 126 else LARGEUR_CAR
                   for c in s)
MARGE = 8.0                 # mm de bord de feuille
RECOUVREMENT_MAX = 0.4      # mm2 de recouvrement tolere entre deux textes

# On capture la balise entiere puis chaque attribut separement : une seule
# expression avec un groupe optionnel pour le transform le laissait avaler par
# le [^>]* qui suit, et TOUS les textes tournes etaient lus a 0 degre -- fausses
# alertes sur les cotes verticales, et vrais recouvrements manques.
RE_TEXT = re.compile(r'<text ([^>]*)>(.*?)</text>', re.S)
RE_ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')
RE_SIZE = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')
RE_NUM = re.compile(r'[-+]?\d*\.?\d+(?:e[-+]?\d+)?')


def _deesc(s):
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"'))


def textes(svg):
    """(x0, y0, x1, y1, contenu, angle, cadre) de chaque texte. (x0..y1) est la
    boite englobante sur la feuille, qui sert aux recouvrements de textes ;
    cadre = (x, y, bx0, by0, bx1, by1) est la boite ORIENTEE : ancre (x, y) et
    boite d'encre dans le repere du texte non tourne, autour de cette ancre."""
    out = []
    for m in RE_TEXT.finditer(svg):
        at = dict(RE_ATTR.findall(m.group(1)))
        x, y, h = float(at["x"]), float(at["y"]), float(at["font-size"])
        anchor = at.get("text-anchor", "start")
        mr = re.match(r'rotate\(([-\d.]+)', at.get("transform", ""))
        ang = mr.group(1) if mr else None
        s = _deesc(m.group(2))
        w = largeur(s, h)
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
        cadre = (x, y, x0, y0, x1, y1)
        a = float(ang) if ang else 0.0
        if abs(a) > 0.01:
            # boite englobante du rectangle tourne autour de l'ancre (x, y),
            # comme le fait rotate(a x y) du SVG
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            xs, ys = [], []
            for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
                dx, dy = px - x, py - y
                xs.append(x + dx * ca - dy * sa)
                ys.append(y + dx * sa + dy * ca)
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        out.append((x0, y0, x1, y1, s, a, cadre))
    return out


def _arc(p0, rx, ry, phi, grand, sens, p1, n_par_rad=12):
    """Echantillonne un arc elliptique SVG (parametrage par extremites,
    SVG 1.1 annexe F.6) en points, p0 exclu, p1 compris."""
    if rx < 1e-9 or ry < 1e-9 or (abs(p0[0] - p1[0]) < 1e-9 and abs(p0[1] - p1[1]) < 1e-9):
        return [p1]
    rx, ry = abs(rx), abs(ry)
    cp, sp = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (p0[0] - p1[0]) / 2.0, (p0[1] - p1[1]) / 2.0
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = (x1p / rx) ** 2 + (y1p / ry) ** 2
    if lam > 1.0:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den > 0 else 0.0
    if grand == sens:
        co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (p0[0] + p1[0]) / 2.0
    cy = sp * cxp + cp * cyp + (p0[1] + p1[1]) / 2.0
    t0 = math.atan2((y1p - cyp) / ry, (x1p - cxp) / rx)
    t1 = math.atan2((-y1p - cyp) / ry, (-x1p - cxp) / rx)
    dt = t1 - t0
    if sens and dt < 0:
        dt += 2 * math.pi
    elif not sens and dt > 0:
        dt -= 2 * math.pi
    n = max(2, int(abs(dt) * n_par_rad) + 1)
    pts = []
    for i in range(1, n + 1):
        t = t0 + dt * i / n
        ex, ey = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + cp * ex - sp * ey, cy + sp * ex + cp * ey))
    pts[-1] = p1
    return pts


def lignes(svg):
    """Segments (x1, y1, x2, y2, largeur) de TOUT ce qui est trace : <line>,
    <path> (arcs echantillonnes), <circle> (polygone) et <rect> traces. Les
    motifs de hachures et les gabarits de decoupe (<defs>) sont exclus : ils
    ne sont pas a l'echelle de la feuille. Un cercle plein sans trait (point
    de repere) compte aussi : pose sur un texte, il le salit autant."""
    svg = re.sub(r'<defs>.*?</defs>', '', svg, flags=re.S)
    out = []
    for m in re.finditer(r'<line ([^>]*)/?>', svg):
        at = dict(RE_ATTR.findall(m.group(1)))
        if "stroke-width" not in at:
            continue
        out.append((float(at["x1"]), float(at["y1"]), float(at["x2"]), float(at["y2"]),
                    float(at["stroke-width"])))
    for m in re.finditer(r'<path ([^>]*)/?>', svg):
        at = dict(RE_ATTR.findall(m.group(1)))
        if "d" not in at:
            continue
        w = float(at.get("stroke-width", "0"))
        if at.get("stroke", "#000") == "none":
            w = 0.0
        if w <= 0 and at.get("fill", "none") in ("none", "#fff", "white"):
            continue
        cur, start = None, None
        for cmd in re.finditer(r'([MLAZmlaz])([^MLAZmlaz]*)', at["d"]):
            c, nums = cmd.group(1).upper(), [float(x) for x in RE_NUM.findall(cmd.group(2))]
            if c == 'M' and len(nums) >= 2:
                cur = start = (nums[0], nums[1])
                # un M suivi de plusieurs paires vaut M puis L
                for k in range(2, len(nums) - 1, 2):
                    nxt = (nums[k], nums[k + 1]); out.append(cur + nxt + (w,)); cur = nxt
            elif c == 'L' and cur:
                for k in range(0, len(nums) - 1, 2):
                    nxt = (nums[k], nums[k + 1]); out.append(cur + nxt + (w,)); cur = nxt
            elif c == 'A' and cur:
                for k in range(0, len(nums) - 6, 7):
                    a = nums[k:k + 7]
                    for nxt in _arc(cur, a[0], a[1], a[2], int(a[3]), int(a[4]), (a[5], a[6])):
                        out.append(cur + nxt + (w,)); cur = nxt
            elif c == 'Z' and cur and start:
                out.append(cur + start + (w,)); cur = start
    for m in re.finditer(r'<circle ([^>]*)/?>', svg):
        at = dict(RE_ATTR.findall(m.group(1)))
        cx, cy, r = float(at["cx"]), float(at["cy"]), float(at["r"])
        w = float(at.get("stroke-width", "0"))
        if w <= 0 and at.get("fill", "none") in ("none", "#fff", "white"):
            continue
        n = 48
        pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
               for i in range(n + 1)]
        for i in range(n):
            out.append(pts[i] + pts[i + 1] + (w,))
    for m in re.finditer(r'<rect ([^>]*)/?>', svg):
        at = dict(RE_ATTR.findall(m.group(1)))
        if "stroke-width" not in at or "x" not in at:
            continue
        x, y = float(at["x"]), float(at["y"])
        W, H = float(at["width"]), float(at["height"])
        w = float(at["stroke-width"])
        c = [(x, y), (x + W, y), (x + W, y + H), (x, y + H), (x, y)]
        for i in range(4):
            out.append(c[i] + c[i + 1] + (w,))
    return out


def dans_repere_texte(x1, y1, x2, y2, t):
    """Segment ramene dans le repere du texte t non tourne (rotation inverse
    autour de son ancre)."""
    a = t[5]
    if abs(a) <= 0.01:
        return x1, y1, x2, y2
    ax, ay = t[6][0], t[6][1]
    ca, sa = math.cos(math.radians(-a)), math.sin(math.radians(-a))
    def r(px, py):
        dx, dy = px - ax, py - ay
        return ax + dx * ca - dy * sa, ay + dx * sa + dy * ca
    p, q = r(x1, y1), r(x2, y2)
    return p[0], p[1], q[0], q[1]


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

    # un trait qui traverse un texte, traits fins compris : boite ORIENTEE du
    # texte, segment ramene dans le repere du texte. Le trait qui porte le
    # texte (ligne de cote 1,6 sous la ligne de base, ligne de repere 1,0
    # dessous) reste hors de la boite d'encre, il n'a pas a etre excepte.
    # Les boites sont filtrees d'abord par leur englobante.
    for t in tx:
        for (x1, y1, x2, y2, w) in li:
            if max(x1, x2) < t[0] or min(x1, x2) > t[2] or max(y1, y2) < t[1] or min(y1, y2) > t[3]:
                continue
            if seg_coupe_boite(*dans_repere_texte(x1, y1, x2, y2, t), t[6][2:]):
                fautes.append("trait a travers '%s'  (segment %.1f,%.1f -> %.1f,%.1f  w %.2f)"
                              % (t[4][:40], x1, y1, x2, y2, w))
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
