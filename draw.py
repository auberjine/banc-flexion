# -*- coding: utf-8 -*-
"""
Generation des plans de fabrication en SVG, format A3 paysage, cotation ISO.

Repere modele : x et z en millimetres, z vers le haut.
Repere feuille : millimetres, y vers le bas (convention SVG).
"""

import math
import geom2d as G

A3 = (420.0, 297.0)
MARGE = 10.0

TRAIT_FORT = 0.5
TRAIT_FIN = 0.18
TRAIT_AXE = 0.18
H_TEXTE = 3.2
H_TITRE = 5.0
FLECHE = 2.6


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def fmt(v, dec=1):
    s = ("%." + str(dec) + "f") % v
    if s.endswith(".0"):
        s = s[:-2]
    return s.replace(".", ",")


def edition():
    """(indice, date) d'edition pris dans params (INDICE_REVISION, DATE_EDITION),
    ("", "") si params ne les donne pas : draw.py reste utilisable seul."""
    try:
        import params as p
    except ImportError:
        return "", ""
    return getattr(p, "INDICE_REVISION", ""), getattr(p, "DATE_EDITION", "")


class Sheet(object):

    def __init__(self, titre, repere, matiere, brut, qte, echelle_txt,
                 notes=None, taille=A3, indice=None, date=None):
        self.w, self.h = taille
        self.titre = titre
        self.repere = repere
        self.matiere = matiere
        self.brut = brut
        self.qte = qte
        self.echelle_txt = echelle_txt
        self.notes = notes or []
        self.body = []
        # indice de revision et date d'edition : par defaut ceux de params, pour
        # que toutes les planches d'une generation portent les memes
        ind, dat = edition()
        self.indice = ind if indice is None else indice
        self.date = dat if date is None else date

    # ---------------------------------------------------------- primitives

    def _p(self, s):
        self.body.append(s)

    def line(self, x0, y0, x1, y1, w=TRAIT_FORT, dash=None, color="#000"):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self._p('<line x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f" stroke="%s" '
                'stroke-width="%.3f" stroke-linecap="round"%s/>'
                % (x0, y0, x1, y1, color, w, d))

    def path(self, d, w=TRAIT_FORT, dash=None, fill="none", color="#000"):
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        self._p('<path d="%s" fill="%s" stroke="%s" stroke-width="%.3f" '
                'stroke-linecap="round" stroke-linejoin="round"%s/>'
                % (d, fill, color, w, da))

    def text(self, x, y, s, h=H_TEXTE, anchor="middle", color="#000",
             weight="normal", angle=None):
        tr = ' transform="rotate(%.2f %.3f %.3f)"' % (angle, x, y) if angle else ''
        self._p('<text x="%.3f" y="%.3f" font-family="Helvetica,Arial,sans-serif" '
                'font-size="%.2f" fill="%s" text-anchor="%s" font-weight="%s"%s>%s</text>'
                % (x, y, h, color, anchor, weight, tr, esc(s)))

    def rect(self, x, y, w, h, sw=TRAIT_FORT, fill="none"):
        self._p('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="%s" '
                'stroke="#000" stroke-width="%.3f"/>' % (x, y, w, h, fill, sw))

    def motif(self, nom, angle=45.0, pas=1.5, w=0.13):
        """Ajout du 02/10/2026. Definit une fois le motif de hachures 'nom'
        (traits fins paralleles, inclines de angle degres, espaces de pas mm) ;
        View.zone(..., motif=nom) le remplit. Le nom doit etre unique dans tout
        plans.html, ou les SVG des planches sont mis bout a bout."""
        deja = getattr(self, "_motifs", None)
        if deja is None:
            deja = self._motifs = set()
        if nom not in deja:
            deja.add(nom)
            self._p('<defs><pattern id="%s" patternUnits="userSpaceOnUse" width="%.3f" '
                    'height="%.3f" patternTransform="rotate(%.2f)"><line x1="%.3f" y1="0" '
                    'x2="%.3f" y2="%.3f" stroke="#000" stroke-width="%.3f"/></pattern></defs>'
                    % (nom, pas, pas, angle, pas / 2.0, pas / 2.0, pas, w))
        return nom

    # ---------------------------------------------------------- cartouche

    def cartouche(self):
        bw, bh = 185.0, 36.0
        x0 = self.w - MARGE - bw
        y0 = self.h - MARGE - bh
        self.rect(MARGE, MARGE, self.w - 2 * MARGE, self.h - 2 * MARGE, 0.7)
        self.rect(x0, y0, bw, bh, 0.7)
        self.line(x0, y0 + 12, x0 + bw, y0 + 12, 0.35)
        self.line(x0, y0 + 24, x0 + bw, y0 + 24, 0.35)
        self.line(x0 + 120, y0, x0 + 120, y0 + 12, 0.35)
        self.line(x0 + 60, y0 + 12, x0 + 60, y0 + 36, 0.35)
        self.line(x0 + 120, y0 + 12, x0 + 120, y0 + 36, 0.35)

        # le titre ne doit jamais courir sous le repere : on le retrecit s il
        # depasse la case, au lieu de compter sur la brievete de l auteur
        h = min(H_TITRE, 116.0 / (0.55 * max(1, len(self.titre))))
        self.text(x0 + 4, y0 + 8.5, self.titre, h, "start", weight="bold")
        # case du repere coupee en deux : repere a gauche, indice et date a
        # droite. Le repere se retrecit comme le titre s'il deborde sa demi-case.
        rep = "rep. " + self.repere
        if self.indice or self.date:
            self.line(x0 + 160, y0, x0 + 160, y0 + 12, 0.35)
            hr = min(4.0, 34.0 / (0.55 * max(1, len(rep))))
            self.text(x0 + 172.5, y0 + 5.2, "indice " + self.indice, 3.0, "middle")
            self.text(x0 + 172.5, y0 + 10.0, self.date, 2.8, "middle")
        else:
            hr = 4.0
        self.text(x0 + 124, y0 + 8.5, rep, hr, "start")
        self.text(x0 + 4, y0 + 17, "matiere", 2.4, "start", "#555")
        self.text(x0 + 4, y0 + 22, self.matiere, H_TEXTE, "start")
        self.text(x0 + 64, y0 + 17, "brut", 2.4, "start", "#555")
        self.text(x0 + 64, y0 + 22, self.brut, H_TEXTE, "start")
        self.text(x0 + 124, y0 + 17, "quantite", 2.4, "start", "#555")
        self.text(x0 + 124, y0 + 22, str(self.qte), H_TEXTE, "start")
        self.text(x0 + 4, y0 + 29, "echelle", 2.4, "start", "#555")
        self.text(x0 + 4, y0 + 34, self.echelle_txt, H_TEXTE, "start")
        self.text(x0 + 64, y0 + 29, "cotes en mm", 2.4, "start", "#555")
        self.text(x0 + 64, y0 + 34, "tol. generale ISO 2768-m", H_TEXTE, "start")
        self.text(x0 + 124, y0 + 29, "banc de flexion", 2.4, "start", "#555")
        self.text(x0 + 124, y0 + 34, "poutrelle 103x107x840", H_TEXTE, "start")

        y = self.h - MARGE - bh - 4
        for n in reversed(self.notes):
            self.text(self.w - MARGE - 2, y, n, 2.8, "end", "#000")
            y -= 3.8

    def dumps(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="%gmm" height="%gmm" '
                'viewBox="0 0 %g %g">\n<rect width="%g" height="%g" fill="#fff"/>\n%s\n</svg>\n'
                % (self.w, self.h, self.w, self.h, self.w, self.h,
                   "\n".join(self.body)))

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.dumps())
        return path


class View(object):
    """Vue : transforme les coordonnees modele (x,z) en coordonnees feuille."""

    def __init__(self, sheet, scale, cx, cz, ox, oy, label=None, label_dy=-46.0):
        self.s = sheet
        self.k = scale
        self.cx, self.cz = cx, cz
        self.ox, self.oy = ox, oy
        if label:
            sheet.text(ox, oy + label_dy, label, 3.6, "middle", weight="bold")

    def P(self, p):
        return (self.ox + self.k * (p[0] - self.cx),
                self.oy - self.k * (p[1] - self.cz))

    # ------------------------------------------------------------ geometrie

    def d_of(self, segs):
        d = []
        for i, sg in enumerate(segs):
            a = self.P(G.seg_start(sg))
            if i == 0:
                d.append("M %.3f %.3f" % a)
            if sg[0] == 'L':
                b = self.P(sg[2])
                d.append("L %.3f %.3f" % b)
            else:
                _, c, r, a0, a1, ccw = sg
                b = self.P(G.seg_end(sg))
                rr = r * self.k
                sweep = 0 if ccw else 1          # y inverse -> balayage inverse
                large = 1 if G.arc_sweep(a0, a1, ccw) > math.pi else 0
                d.append("A %.3f %.3f 0 %d %d %.3f %.3f" % (rr, rr, large, sweep, b[0], b[1]))
        d.append("Z")
        return " ".join(d)

    def contour(self, segs, w=TRAIT_FORT, dash=None, fill="none", color="#000"):
        self.s.path(self.d_of(segs), w, dash, fill, color)

    def contours(self, lst, **kw):
        for c in lst:
            self.contour(c, **kw)

    def axe(self, p0, p1, ext=3.0):
        a, b = self.P(p0), self.P(p1)
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L < 1e-6:
            return
        ux, uy = dx / L, dy / L
        self.s.line(a[0] - ux * ext, a[1] - uy * ext, b[0] + ux * ext, b[1] + uy * ext,
                    TRAIT_AXE, "6 1.5 1 1.5", "#000")

    def croix(self, p, r=2.5):
        a = self.P(p)
        self.s.line(a[0] - r, a[1], a[0] + r, a[1], TRAIT_AXE, "4 1 0.8 1")
        self.s.line(a[0], a[1] - r, a[0], a[1] + r, TRAIT_AXE, "4 1 0.8 1")

    # ------------------------------------------------------------ cotation

    def _fleche(self, p, ux, uy):
        w = FLECHE * 0.28
        x1, y1 = p[0] + ux * FLECHE, p[1] + uy * FLECHE
        self.s._p('<path d="M %.3f %.3f L %.3f %.3f L %.3f %.3f Z" fill="#000"/>'
                  % (p[0], p[1], x1 - uy * w, y1 + ux * w, x1 + uy * w, y1 - ux * w))

    def _ligne_cote(self, a, b, texte, dedans=True):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-6:
            return
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        if dedans and L > 3 * FLECHE:
            self.s.line(a[0], a[1], b[0], b[1], TRAIT_FIN)
            self._fleche(a, ux, uy)
            self._fleche(b, -ux, -uy)
        else:
            self.s.line(a[0] - ux * 7, a[1] - uy * 7, b[0] + ux * 7, b[1] + uy * 7, TRAIT_FIN)
            self._fleche(a, -ux, -uy)
            self._fleche(b, ux, uy)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ang = math.degrees(math.atan2(uy, ux))
        if ang > 90 or ang < -90:
            ang += 180
        off = 1.6
        nx, ny = -uy, ux
        if ny > 0:
            nx, ny = -nx, -ny
        self.s.text(mx + nx * off, my + ny * off, texte, H_TEXTE, "middle", angle=ang)

    def cote_h(self, x0, x1, z, dz=10.0, texte=None, zref=None):
        """Cote horizontale, ligne de cote a dz mm au dessus (dz<0 : en dessous)."""
        zr = z if zref is None else zref
        pa, pb = self.P((x0, zr)), self.P((x1, zr))
        ya = pa[1] - dz
        self.s.line(pa[0], pa[1] - math.copysign(1.5, dz), pa[0], ya + math.copysign(2, dz), TRAIT_FIN)
        self.s.line(pb[0], pb[1] - math.copysign(1.5, dz), pb[0], ya + math.copysign(2, dz), TRAIT_FIN)
        self._ligne_cote((pa[0], ya), (pb[0], ya), texte or fmt(abs(x1 - x0)))

    def cote_v(self, z0, z1, x, dx=10.0, texte=None, xref=None):
        xr = x if xref is None else xref
        pa, pb = self.P((xr, z0)), self.P((xr, z1))
        xa = pa[0] + dx
        self.s.line(pa[0] + math.copysign(1.5, dx), pa[1], xa - math.copysign(2, dx), pa[1], TRAIT_FIN)
        self.s.line(pb[0] + math.copysign(1.5, dx), pb[1], xa - math.copysign(2, dx), pb[1], TRAIT_FIN)
        self._ligne_cote((xa, pa[1]), (xa, pb[1]), texte or fmt(abs(z1 - z0)))

    def repere_lettre(self, p, lettre, dx=0, dy=-6):
        a = self.P(p)
        self.s._p('<circle cx="%.3f" cy="%.3f" r="3.1" fill="#fff" stroke="#000" '
                  'stroke-width="0.25"/>' % (a[0] + dx, a[1] + dy))
        self.s.text(a[0] + dx, a[1] + dy + 1.2, lettre, 3.0, "middle")
        self.s.line(a[0], a[1], a[0] + dx, a[1] + dy + 3.1, TRAIT_FIN)

    def note(self, p, texte, dx=14, dy=-10, anchor=None):
        a = self.P(p)
        b = (a[0] + dx, a[1] + dy)
        self.s.line(a[0], a[1], b[0], b[1], TRAIT_FIN)
        ln = 6.0 if dx >= 0 else -6.0
        self.s.line(b[0], b[1], b[0] + ln, b[1], TRAIT_FIN)
        an = anchor or ("start" if dx >= 0 else "end")
        off = 1.0 if dx >= 0 else -1.0
        lines = texte.split("\n")
        for i, t in enumerate(lines):
            self.s.text(b[0] + ln + off, b[1] - 1.0 + i * 3.6, t, H_TEXTE, an)

    def rayon(self, c, r, a_deg, texte=None, lg=12):
        a = math.radians(a_deg)
        pc = self.P(c)
        pr = (pc[0] + r * self.k * math.cos(a), pc[1] - r * self.k * math.sin(a))
        pe = (pr[0] + lg * math.cos(a), pr[1] - lg * math.sin(a))
        self.s.line(pr[0], pr[1], pe[0], pe[1], TRAIT_FIN)
        ux = (pr[0] - pe[0]) / max(1e-6, math.hypot(pr[0] - pe[0], pr[1] - pe[1]))
        uy = (pr[1] - pe[1]) / max(1e-6, math.hypot(pr[0] - pe[0], pr[1] - pe[1]))
        self._fleche(pr, ux, uy)
        an = "start" if math.cos(a) >= 0 else "end"
        self.s.text(pe[0] + (1.2 if an == "start" else -1.2), pe[1] - 1.0,
                    texte or ("R" + fmt(r)), H_TEXTE, an)

    # ============================================================ ajouts ISO
    # Ajoutes le 02/10/2026 pour la planche d'ensemble. Rien de ce qui precede
    # n'est modifie : les planches qui appellent cote_h, cote_v ou note gardent
    # exactement leur rendu. Ce que ces variantes font de plus :
    #  - le texte d'une cote est pose du cote ou pointe le HAUT des lettres, donc
    #    a gauche d'une cote verticale lue de bas en haut : _ligne_cote le posait
    #    du mauvais cote et la ligne barrait les chiffres ;
    #  - les lignes d'attache partent a ECART_ATTACHE de l'arete et DEPASSENT la
    #    ligne de cote de DEPASSE_ATTACHE (ISO 129-1), au lieu de s'arreter 2 mm
    #    avant elle ;
    #  - chaque bout a son propre point d'attache, ou aucun quand la ligne de
    #    cote s'appuie sur un axe deja trace ;
    #  - le texte peut glisser le long de sa ligne (dt, mm de feuille) ;
    #  - lignes de repere terminees selon ISO 128-22 (point dans un contour,
    #    fleche sur un trait), bulles de repere, zones hachurees ou masquantes,
    #    decoupe d'un groupe de traits, trace de plan de coupe, trait de rupture.

    ECART_ATTACHE = 1.0
    DEPASSE_ATTACHE = 2.0

    def _cote_iso(self, a, b, texte, dt=0.0, dedans=True, queue=7.0):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-6:
            return
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        if dedans and L > 3 * FLECHE:
            self.s.line(a[0], a[1], b[0], b[1], TRAIT_FIN)
            self._fleche(a, ux, uy)
            self._fleche(b, -ux, -uy)
        else:
            self.s.line(a[0] - ux * queue, a[1] - uy * queue, b[0] + ux * queue, b[1] + uy * queue,
                        TRAIT_FIN)
            self._fleche(a, -ux, -uy)
            self._fleche(b, ux, uy)
        ang = math.degrees(math.atan2(uy, ux))
        ang = ((ang + 90.0) % 180.0) - 90.0        # lu du bas ou de la droite
        r = math.radians(ang)
        nx, ny = math.sin(r), -math.cos(r)         # vers le haut des lettres
        tx, ty = math.cos(r), math.sin(r)          # sens de lecture
        mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
        off = 1.6
        self.s.text(mx + nx * off + tx * dt, my + ny * off + ty * dt, texte, H_TEXTE,
                    "middle", angle=ang if abs(ang) > 0.01 else None)

    def cote_hx(self, x0, x1, z0, z1, dz, texte=None, dt=0.0, dedans=True, zl=None, queue=7.0):
        """Cote horizontale ISO. (x0, z0) et (x1, z1) : points d'attache, en
        coordonnees modele ; z None : pas de ligne d'attache a ce bout (la ligne
        de cote s'appuie sur un axe ou un trait deja trace). La ligne de cote
        est a dz mm de feuille au-dessus du plus haut point d'attache (dz > 0)
        ou au-dessous du plus bas (dz < 0), ou a la cote modele zl si elle est
        donnee. Cote trop courte pour ses fleches : fleches dehors, ligne
        prolongee de 'queue' mm. Renvoie l'ordonnee feuille de la ligne."""
        if zl is not None:
            yl = self.P((0.0, zl))[1]
        else:
            ys = [self.P((0.0, z))[1] for z in (z0, z1) if z is not None]
            yl = (min(ys) - dz) if dz > 0 else (max(ys) - dz)
        xa, xb = self.P((x0, 0.0))[0], self.P((x1, 0.0))[0]
        for x, z in ((xa, z0), (xb, z1)):
            if z is None:
                continue
            y = self.P((0.0, z))[1]
            sg = 1.0 if yl > y else -1.0
            self.s.line(x, y + sg * self.ECART_ATTACHE, x, yl + sg * self.DEPASSE_ATTACHE, TRAIT_FIN)
        self._cote_iso((xa, yl), (xb, yl), texte or fmt(abs(x1 - x0)), dt, dedans, queue)
        return yl

    def cote_vx(self, z0, z1, x0, x1, dx, texte=None, dt=0.0, dedans=True, xl=None, queue=7.0):
        """Cote verticale ISO, lue de bas en haut, texte a GAUCHE de sa ligne.
        (x0, z0) et (x1, z1) : points d'attache modele ; x None : pas de ligne
        d'attache a ce bout. Ligne a dx mm de feuille a droite du point le plus
        a droite (dx > 0) ou a gauche du plus a gauche (dx < 0), ou a l'abscisse
        modele xl si elle est donnee. Renvoie l'abscisse feuille de la ligne."""
        if xl is not None:
            xs_l = self.P((xl, 0.0))[0]
        else:
            xs = [self.P((x, 0.0))[0] for x in (x0, x1) if x is not None]
            xs_l = (max(xs) + dx) if dx > 0 else (min(xs) + dx)
        ya, yb = self.P((0.0, z0))[1], self.P((0.0, z1))[1]
        for x, y in ((x0, ya), (x1, yb)):
            if x is None:
                continue
            xf = self.P((x, 0.0))[0]
            sg = 1.0 if xs_l > xf else -1.0
            self.s.line(xf + sg * self.ECART_ATTACHE, y, xs_l + sg * self.DEPASSE_ATTACHE, y, TRAIT_FIN)
        bas, haut = ((xs_l, ya), (xs_l, yb)) if ya >= yb else ((xs_l, yb), (xs_l, ya))
        self._cote_iso(bas, haut, texte or fmt(abs(z1 - z0)), dt, dedans, queue)
        return xs_l

    def _fin_repere(self, a, b, fin):
        """Terminaison ISO 128-22 d'une ligne de repere qui va de a vers b."""
        if fin == "point":
            self.s._p('<circle cx="%.3f" cy="%.3f" r="0.55" fill="#000"/>' % a)
        elif fin == "fleche":
            L = max(1e-6, math.hypot(b[0] - a[0], b[1] - a[1]))
            self._fleche(a, (b[0] - a[0]) / L, (b[1] - a[1]) / L)

    def renvoi(self, p, texte, dx=14.0, dy=-10.0, fin="point", palier=6.0, h=H_TEXTE):
        """Ligne de repere et texte, comme note(), terminee par un point (elle
        finit dans un contour) ou une fleche (elle finit sur un trait)."""
        a = self.P(p)
        b = (a[0] + dx, a[1] + dy)
        self.s.line(a[0], a[1], b[0], b[1], TRAIT_FIN)
        self._fin_repere(a, b, fin)
        ln = palier if dx >= 0 else -palier
        self.s.line(b[0], b[1], b[0] + ln, b[1], TRAIT_FIN)
        an = "start" if dx >= 0 else "end"
        off = 1.0 if dx >= 0 else -1.0
        for i, t in enumerate(texte.split("\n")):
            self.s.text(b[0] + ln + off, b[1] + 1.0 + i * 3.6 - 1.8 * (len(texte.split("\n")) - 1),
                        t, h, an)

    def bulle(self, p, rep, dx, dy, r=3.6, fin="point", h=3.0):
        """Bulle de repere : ligne de repere depuis p (modele), cercle de rayon r
        (mm de feuille) centre a (dx, dy) de p, repere au centre."""
        a = self.P(p)
        c = (a[0] + dx, a[1] + dy)
        d = math.hypot(dx, dy)
        if d > r:
            e = (c[0] - dx / d * r, c[1] - dy / d * r)
            self.s.line(a[0], a[1], e[0], e[1], TRAIT_FIN)
            self._fin_repere(a, e, fin)
        self.s._p('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="#fff" stroke="#000" '
                  'stroke-width="0.25"/>' % (c[0], c[1], r))
        self.s.text(c[0], c[1] + 0.36 * h, rep, h, "middle")
        return c

    def zone(self, contours, motif=None, w=TRAIT_FORT, fond="#fff", dash=None):
        """Region bordee d'un trait w : contour exterieur et trous (regle
        evenodd). Le fond (blanc par defaut) masque ce qui a ete dessine avant ;
        motif : nom d'un motif de hachures defini par Sheet.motif()."""
        d = " ".join(self.d_of(c) for c in contours)
        if fond:
            self.s._p('<path d="%s" fill="%s" fill-rule="evenodd" stroke="none"/>' % (d, fond))
        fill = ("url(#%s)" % motif) if motif else "none"
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        if w > 0:
            self.s._p('<path d="%s" fill="%s" fill-rule="evenodd" stroke="#000" '
                      'stroke-width="%.3f" stroke-linecap="round" stroke-linejoin="round"%s/>'
                      % (d, fill, w, da))
        elif motif:
            self.s._p('<path d="%s" fill="%s" fill-rule="evenodd" stroke="none"/>' % (d, fill))

    def clip_debut(self, nom, contours):
        """Ce qui suit, jusqu'a clip_fin(), n'est visible qu'a l'interieur des
        contours (regle evenodd : un contour dans un autre fait un trou)."""
        d = " ".join(self.d_of(c) for c in contours)
        self.s._p('<defs><clipPath id="%s"><path d="%s" clip-rule="evenodd"/></clipPath></defs>'
                  '<g clip-path="url(#%s)">' % (nom, d, nom))

    def clip_fin(self):
        self.s._p('</g>')

    def trace_coupe(self, p0, p1, lettre, sens, lg=5.0, fl=7.0):
        """Trace d'un plan de coupe (ISO 128-44) : p0, p1 (modele), bouts de la
        trace hors de la piece ; trait mixte fin entre eux, epaissi sur lg mm
        aux deux bouts ; fleches de fl mm dans le sens de vue 'sens' (vecteur
        unitaire de feuille), lettre au bout de chaque fleche."""
        a, b = self.P(p0), self.P(p1)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-6:
            return
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        self.s.line(a[0], a[1], b[0], b[1], TRAIT_AXE, "6 1.5 1 1.5")
        for e, sg in ((a, 1.0), (b, -1.0)):
            self.s.line(e[0], e[1], e[0] + sg * ux * lg, e[1] + sg * uy * lg, 0.7)
            t = (e[0] + sens[0] * fl, e[1] + sens[1] * fl)
            self.s.line(e[0], e[1], t[0], t[1], TRAIT_FIN)
            self._fleche(t, -sens[0], -sens[1])
            self.s.text(t[0] + sens[0] * 3.0, t[1] + sens[1] * 3.0 + 1.5, lettre, 4.0,
                        "middle", weight="bold")

    def rupture(self, p0, p1, amp=1.5, w=TRAIT_FIN):
        """Trait de rupture fin : droit, avec un zigzag au milieu."""
        a, b = self.P(p0), self.P(p1)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-6:
            return
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        nx, ny = -uy, ux
        m = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        pts = [a, (m[0] - ux * 1.6, m[1] - uy * 1.6),
               (m[0] - ux * 0.5 + nx * amp, m[1] - uy * 0.5 + ny * amp),
               (m[0] + ux * 0.5 - nx * amp, m[1] + uy * 0.5 - ny * amp),
               (m[0] + ux * 1.6, m[1] + uy * 1.6), b]
        self.s.path(" ".join(("M " if i == 0 else "L ") + "%.3f %.3f" % q
                             for i, q in enumerate(pts)), w)


def table(sheet, x, y, titre, entetes, lignes, largeurs, h=4.6):
    """Petit tableau (nomenclature de percages)."""
    W = sum(largeurs)
    sheet.text(x, y - 1.5, titre, 3.2, "start", weight="bold")
    sheet.rect(x, y, W, h * (len(lignes) + 1), 0.35)
    sheet.line(x, y + h, x + W, y + h, 0.35)
    cx = x
    for w in largeurs[:-1]:
        cx += w
        sheet.line(cx, y, cx, y + h * (len(lignes) + 1), 0.25)
    cx = x
    for i, e in enumerate(entetes):
        sheet.text(cx + largeurs[i] / 2, y + h - 1.5, e, 2.7, "middle", weight="bold")
        cx += largeurs[i]
    for r, ligne in enumerate(lignes):
        cx = x
        for i, cell in enumerate(ligne):
            sheet.text(cx + largeurs[i] / 2, y + h * (r + 2) - 1.5, str(cell), 2.7, "middle")
            cx += largeurs[i]
    return y + h * (len(lignes) + 1)
