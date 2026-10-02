# -*- coding: utf-8 -*-
"""
Geometrie 2D partagee entre le modele 3D FreeCAD, l'export DXF et les plans SVG.

Un contour est une liste de segments, chacun etant :
    ('L', (x0,z0), (x1,z1))                        segment de droite
    ('A', (xc,zc), r, a0, a1, ccw)                 arc, angles en radians

Aucune dependance a FreeCAD : ce module tourne aussi sous le Python systeme.
"""

import math

TOL = 1e-9


# ---------------------------------------------------------------- vecteurs

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, k):
    return (a[0] * k, a[1] * k)


def norm(a):
    return math.hypot(a[0], a[1])


def unit(a):
    n = norm(a)
    if n < TOL:
        raise ValueError("vecteur nul")
    return (a[0] / n, a[1] / n)


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def ang(a):
    return math.atan2(a[1], a[0])


def pt_on_arc(c, r, a):
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


# ---------------------------------------------------------------- segments

def seg_start(s):
    if s[0] == 'L':
        return s[1]
    return pt_on_arc(s[1], s[2], s[3])


def seg_end(s):
    if s[0] == 'L':
        return s[2]
    return pt_on_arc(s[1], s[2], s[4])


def arc_sweep(a0, a1, ccw):
    """Amplitude signee de l'arc, dans [0, 2pi)."""
    d = (a1 - a0) % (2 * math.pi) if ccw else (a0 - a1) % (2 * math.pi)
    return d


def seg_length(s):
    if s[0] == 'L':
        return norm(sub(s[2], s[1]))
    return s[2] * arc_sweep(s[3], s[4], s[5])


def sample(s, n=24):
    """Echantillonne un segment en points, pour le maillage et le trace."""
    if s[0] == 'L':
        return [s[1], s[2]]
    _, c, r, a0, a1, ccw = s
    d = arc_sweep(a0, a1, ccw)
    k = max(2, int(math.ceil(n * d / (math.pi / 2))))
    out = []
    for i in range(k + 1):
        t = d * i / k
        a = a0 + t if ccw else a0 - t
        out.append(pt_on_arc(c, r, a))
    return out


def polyline(segs, n=24):
    """Contour echantillonne en une liste de points fermee (sans doublon final)."""
    pts = []
    for s in segs:
        for p in sample(s, n):
            if not pts or norm(sub(p, pts[-1])) > 1e-7:
                pts.append(p)
    if len(pts) > 1 and norm(sub(pts[0], pts[-1])) < 1e-7:
        pts.pop()
    return pts


def area(segs):
    """Aire algebrique du contour (positive si sens trigonometrique)."""
    pts = polyline(segs, 64)
    a = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        a += x0 * y1 - x1 * y0
    return a / 2.0


def bbox(segs):
    pts = polyline(segs, 64)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def check_closed(segs, tol=1e-6):
    """Verifie que les segments s'enchainent et que le contour est ferme."""
    errs = []
    for i in range(len(segs)):
        e = seg_end(segs[i])
        s = seg_start(segs[(i + 1) % len(segs)])
        d = norm(sub(e, s))
        if d > tol:
            errs.append((i, d, e, s))
    return errs


# ---------------------------------------------------------------- contours

class Contour(object):
    """
    Contour ferme construit par une suite d'elements :

      add(x, z, r=0)        sommet, avec conge de rayon r
      arc_to(x, z, r, ccw)  arc depuis le point courant
      raw(segments)         bloc de segments deja construit (bossage, col...)

    Les elements consecutifs sont relies par des segments de droite.
    Les conges ne s'appliquent qu'aux sommets encadres par deux droites.
    """

    def __init__(self, name=""):
        self.name = name
        self.items = []

    def add(self, x, z, r=0.0, relief=False):
        """
        Sommet, avec conge de rayon r. Si relief vaut 'diag', c'est un degagement
        a decoupes droites (relief_diag). Si relief est vrai, ce n'est pas un conge
        mais un DEGAGEMENT : on perce un disque de rayon r centre sur le sommet
        au lieu d'arrondir l'angle. C'est ce qu'il faut partout ou une piece
        conjuguee doit venir en appui dans l'angle -- pied de tenon, coin de
        mortaise. Un conge y ajouterait de la matiere et empecherait l'appui ;
        le degagement, lui, ouvre l'angle.
        """
        p = (float(x), float(z))
        self.items.append(dict(kind='v', start=p, end=p, r=float(r),
                               relief=relief, segs=[]))
        return self

    def add_many(self, pts):
        for p in pts:
            self.add(p[0], p[1], p[2] if len(p) > 2 else 0.0)
        return self

    def raw(self, segs):
        segs = list(segs)
        self.items.append(dict(kind='s', start=seg_start(segs[0]),
                               end=seg_end(segs[-1]), r=0.0, segs=segs))
        return self

    def arc_to(self, x, z, r, ccw=True):
        p = (float(x), float(z))
        prev = self.items[-1]['end']
        return self.raw([arc_through(prev, p, r, ccw)])

    def build(self):
        n = len(self.items)
        if n < 2:
            raise ValueError("%s : contour vide" % self.name)

        chain = []
        fillets = []          # (indice dans chain, rayon, numero de sommet)
        for i in range(n):
            prev_end = self.items[i - 1]['end']
            cur = self.items[i]
            chain.append(('L', prev_end, cur['start']))
            if cur['kind'] == 'v' and cur['r'] > TOL:
                fillets.append((len(chain) - 1, cur['r'], i, cur.get('relief', False)))
            for s in cur['segs']:
                chain.append(s)

        m = len(chain)
        inserted = {}
        for k, r, ivert, rel in fillets:
            a = chain[k]
            b = chain[(k + 1) % m]
            if a[0] != 'L' or b[0] != 'L':
                raise ValueError("%s sommet %d : conge entre un arc et une droite, "
                                 "non gere" % (self.name, ivert))
            f = (relief_diag if rel == 'diag' else relief_ll) if rel else fillet_ll
            segs = f(a, b, r, self.name, ivert)      # premier et dernier remplacent a et b,
            chain[k] = segs[0]                       # ce qu'il y a entre s'insere : un arc
            chain[(k + 1) % m] = segs[-1]            # pour un conge, trois traits pour un
            inserted[k] = list(segs[1:-1])           # degagement droit

        res = []
        for k in range(m):
            if chain[k][0] == 'A' or seg_length(chain[k]) > 1e-7:
                res.append(chain[k])
            if k in inserted:
                res.extend(inserted[k])
        errs = check_closed(res, 1e-6)
        if errs:
            raise ValueError("%s : contour non ferme, %d discontinuites (max %.4g mm)"
                             % (self.name, len(errs), max(e[1] for e in errs)))
        return res


def arc_through(p0, p1, r, ccw):
    """Arc de rayon r reliant p0 a p1, dans le sens demande, le plus court."""
    d = sub(p1, p0)
    L = norm(d)
    if L < TOL:
        raise ValueError("arc de longueur nulle")
    if r < L / 2 - 1e-9:
        raise ValueError("rayon %.3f trop petit pour une corde de %.3f" % (r, L))
    r = max(r, L / 2)
    h = math.sqrt(max(0.0, r * r - (L / 2) ** 2))
    mid = mul(add(p0, p1), 0.5)
    nvec = unit((-d[1], d[0]))
    c = add(mid, mul(nvec, h if ccw else -h))
    a0 = ang(sub(p0, c))
    a1 = ang(sub(p1, c))
    return ('A', c, r, a0, a1, ccw)


def fillet_ll(a, b, r, name="", idx=-1):
    """
    Conge de rayon r entre deux segments de droite consecutifs a puis b.
    Retourne (a_raccourci, arc, b_raccourci).
    """
    p = a[2]                       # sommet commun
    d0 = unit(sub(a[1], p))        # direction sortant vers l'amont
    d1 = unit(sub(b[2], p))        # direction sortant vers l'aval
    cosang = max(-1.0, min(1.0, dot(d0, d1)))
    theta = math.acos(cosang)      # angle entre les deux directions sortantes
    if theta < 1e-6 or abs(theta - math.pi) < 1e-9:
        raise ValueError("%s sommet %d : angle degenere (%.4f rad)" % (name, idx, theta))
    t = r / math.tan(theta / 2.0)  # recul le long de chaque cote
    la = norm(sub(a[1], p))
    lb = norm(sub(b[2], p))
    if t > la - 1e-6 or t > lb - 1e-6:
        raise ValueError(
            "%s sommet %d : conge R%.2f trop grand (recul %.2f pour cotes %.2f et %.2f)"
            % (name, idx, r, t, la, lb))
    ta = add(p, mul(d0, t))
    tb = add(p, mul(d1, t))
    bis = unit(add(d0, d1))
    c = add(p, mul(bis, r / math.sin(theta / 2.0)))
    a0 = ang(sub(ta, c))
    a1 = ang(sub(tb, c))
    ccw = cross(sub(ta, c), sub(tb, c)) > 0
    return (('L', a[1], ta), ('A', c, r, a0, a1, ccw), ('L', tb, b[2]))


# ---------------------------------------------------------------- bossage

def relief_ll(a, b, r, name="", idx=-1):
    """
    DEGAGEMENT d'angle entre deux droites consecutives : un disque de rayon r
    centre sur le sommet, au lieu d'un conge.

    Le contour passe par le GRAND arc, celui qui reste du cote de la matiere.
    Sur un angle rentrant (pied de tenon) cela creuse une lunule qui ouvre
    l'angle sans deborder de l'epaulement ; sur un angle saillant de trou
    (coin de mortaise) cela donne l'os de chien classique, qui laisse entrer un
    tenon a angles vifs.
    """
    p = a[2]                       # sommet commun
    d0 = unit(sub(a[1], p))        # vers l'amont
    d1 = unit(sub(b[2], p))        # vers l'aval
    la = norm(sub(a[1], p))
    lb = norm(sub(b[2], p))
    if r > la - 1e-6 or r > lb - 1e-6:
        raise ValueError("%s sommet %d : degagement R%.2f trop grand pour des "
                         "cotes de %.2f et %.2f" % (name, idx, r, la, lb))
    ta = add(p, mul(d0, r))
    tb = add(p, mul(d1, r))
    a0 = ang(sub(ta, p))
    a1 = ang(sub(tb, p))
    ccw = ((a1 - a0) % (2 * math.pi)) > math.pi
    return (('L', a[1], ta), ('A', p, r, a0, a1, ccw), ('L', tb, b[2]))


def relief_diag(a, b, r, name="", idx=-1):
    """
    DEGAGEMENT d'angle a DECOUPES DROITES : au lieu d'un disque, une petite
    poche carree tournee de 45 degres, ouverte sur l'angle. Le contour quitte
    chaque arete a r du sommet et s'enfonce de r.sqrt(2) dans la matiere, le
    long de la bissectrice ; l'angle vif de la piece conjuguee garde r/sqrt(2)
    de garde sur les trois cotes. Trois traits de laser au lieu d'un arc, et
    une poche qui se lit tout de suite sur le DXF.
    """
    p = a[2]
    d0 = unit(sub(a[1], p))
    d1 = unit(sub(b[2], p))
    la = norm(sub(a[1], p))
    lb = norm(sub(b[2], p))
    if r > la - 1e-6 or r > lb - 1e-6:
        raise ValueError("%s sommet %d : degagement %.2f trop grand pour des "
                         "cotes de %.2f et %.2f" % (name, idx, r, la, lb))
    bis = unit(add(d0, d1))                 # bissectrice cote VIDE
    prof = mul(bis, -r * math.sqrt(2.0))    # on s'enfonce cote matiere
    ta = add(p, mul(d0, r))
    tb = add(p, mul(d1, r))
    b1 = add(ta, prof)
    b2 = add(tb, prof)
    return (('L', a[1], ta), ('L', ta, b1), ('L', b1, b2), ('L', b2, tb), ('L', tb, b[2]))


def rect_degage(x0, z0, x1, z1, r):
    """Rectangle a degagements d'angle : il accepte un tenon a angles vifs."""
    c = Contour("rect degage")
    for (x, z) in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
        c.add(x, z, r, relief=True)
    return c.build()


def crown(xc, z_line, apex, R, r_blend, going_right=True):
    """
    Bossage bombe convexe sur une arete horizontale z = z_line.

    Arc principal de rayon R dont le sommet est a (xc, apex), raccorde de chaque
    cote a la droite z = z_line par un conge concave de rayon r_blend.

    Retourne (segments, x_debut, x_fin) : les segments vont de gauche a droite
    si going_right, l'appelant les insere dans son contour.
    """
    h = apex - z_line
    if h <= 0:
        raise ValueError("bossage de relief nul ou negatif")
    zc = apex - R                                    # centre de l'arc principal
    dz = z_line - zc                                 # > 0
    if dz >= R:
        raise ValueError("le bossage ne recoupe pas la droite")

    # centre du conge : a z_line + r au dessus de la droite, a R + r du centre
    r = r_blend
    disc = (R + r) ** 2 - (dz + r) ** 2
    if disc <= 0:
        raise ValueError("conge de bossage R%.2f impossible" % r)
    dx = math.sqrt(disc)
    cl = (xc - dx, z_line + r)                       # conge gauche
    cr = (xc + dx, z_line + r)                       # conge droit
    cc = (xc, zc)

    # points de tangence avec la droite
    tl_line = (cl[0], z_line)
    tr_line = (cr[0], z_line)
    # points de tangence avec l'arc principal (alignes centre principal -> centre conge)
    ul = unit(sub(cl, cc))
    ur = unit(sub(cr, cc))
    tl_arc = add(cc, mul(ul, R))
    tr_arc = add(cc, mul(ur, R))

    segs = [
        arc_short(cl, r, tl_line, tl_arc),
        arc_short(cc, R, tl_arc, tr_arc),
        arc_short(cr, r, tr_arc, tr_line),
    ]
    if not going_right:
        segs = [reverse_seg(s) for s in reversed(segs)]
        return segs, tr_line[0], tl_line[0]
    return segs, tl_line[0], tr_line[0]


def s_curve(x_a, z_hi, z_lo, r, going_right=True):
    """
    Raccordement en S entre deux droites horizontales z_hi et z_lo, par deux arcs
    tangents de meme rayon r. Depart tangent en (x_a, z_hi).
    Retourne (segments, run) ou run est la longueur horizontale consommee.
    """
    delta = z_hi - z_lo
    sgn = 1.0 if delta >= 0 else -1.0
    d = abs(delta)
    if d < 1e-9:
        return [], 0.0
    if r < d / 4.0:
        raise ValueError("rayon de raccordement %.2f trop faible pour un decrochement de %.2f"
                         % (r, d))
    costh = 1.0 - d / (2.0 * r)
    costh = max(-1.0, min(1.0, costh))
    th = math.acos(costh)
    run = 2.0 * r * math.sin(th)
    s = 1.0 if going_right else -1.0

    c1 = (x_a, z_hi - sgn * r)
    p_mid = (x_a + s * r * math.sin(th), z_hi - sgn * d / 2.0)
    c2 = (x_a + s * run, z_lo + sgn * r)
    p_end = (x_a + s * run, z_lo)
    p0 = (x_a, z_hi)
    return [arc_short(c1, r, p0, p_mid), arc_short(c2, r, p_mid, p_end)], run


def notch(x_center, length, z_hi, z_lo, r):
    """
    Gorge symetrique (col de mesure) dans une arete horizontale z_hi, de longueur
    utile `length` au fond z_lo, avec raccordements en S de rayon r.
    Retourne (segments, x_debut, x_fin), parcourus de gauche a droite.
    """
    run = run_of(z_hi, z_lo, r)
    x0 = x_center - length / 2.0 - run
    down, _ = s_curve(x0, z_hi, z_lo, r, True)
    x1 = x0 + run
    x2 = x_center + length / 2.0
    up, _ = s_curve(x2, z_lo, z_hi, r, True)
    segs = list(down) + [('L', (x1, z_lo), (x2, z_lo))] + list(up)
    return segs, x0, x2 + run


def run_of(z_hi, z_lo, r):
    d = abs(z_hi - z_lo)
    costh = max(-1.0, min(1.0, 1.0 - d / (2.0 * r)))
    return 2.0 * r * math.sin(math.acos(costh))


def reverse_seg(s):
    if s[0] == 'L':
        return ('L', s[2], s[1])
    return ('A', s[1], s[2], s[4], s[3], not s[5])


def reverse(segs):
    return [reverse_seg(s) for s in reversed(segs)]


def arc_short(c, r, pa, pb):
    """Arc de centre c passant de pa a pb par le chemin le plus court."""
    a0 = ang(sub(pa, c))
    a1 = ang(sub(pb, c))
    d_ccw = (a1 - a0) % (2 * math.pi)
    return ('A', c, r, a0, a1, d_ccw <= math.pi)


def ensure_ccw(segs):
    """Oriente le contour dans le sens trigonometrique."""
    return segs if area(segs) >= 0 else reverse(segs)


def ensure_cw(segs):
    return segs if area(segs) <= 0 else reverse(segs)


# ---------------------------------------------------------------- primitives

def circle(cx, cz, r):
    """Cercle complet, en deux demi-arcs (robuste pour tous les exports)."""
    return [
        ('A', (cx, cz), r, 0.0, math.pi, True),
        ('A', (cx, cz), r, math.pi, 2 * math.pi, True),
    ]


def rounded_rect(x0, z0, x1, z1, r):
    c = Contour("rect")
    c.add(x0, z0, r).add(x1, z0, r).add(x1, z1, r).add(x0, z1, r)
    return c.build()


def slot(x0, z0, x1, z1):
    """Lumiere oblongue a bouts ronds, axe selon la plus grande dimension."""
    w = abs(x1 - x0)
    h = abs(z1 - z0)
    xa, xb = min(x0, x1), max(x0, x1)
    za, zb = min(z0, z1), max(z0, z1)
    if h >= w:
        r = w / 2.0
        xc = (xa + xb) / 2.0
        return [
            ('L', (xa, za + r), (xa, zb - r)),
            ('A', (xc, zb - r), r, math.pi, 0.0, False),
            ('L', (xb, zb - r), (xb, za + r)),
            ('A', (xc, za + r), r, 0.0, math.pi, False),
        ]
    r = h / 2.0
    zc = (za + zb) / 2.0
    return [
        ('L', (xa + r, za), (xb - r, za)),
        ('A', (xb - r, zc), r, -math.pi / 2, math.pi / 2, True),
        ('L', (xb - r, zb), (xa + r, zb)),
        ('A', (xa + r, zc), r, math.pi / 2, 3 * math.pi / 2, True),
    ]
