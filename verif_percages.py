# -*- coding: utf-8 -*-
"""
Controle des ligaments de toutes les pieces planes : distance de chaque percage
aux autres percages et au contour exterieur. Tourne sous le Python systeme, sans
FreeCAD, parce que le probleme est purement 2D.

    python verif_percages.py

Regle retenue : un ligament d'acier doit valoir au moins l'epaisseur de la tole
(EP_FLANC sur les flancs). En dessous de MIN_DUR la piece est refusee, entre
MIN_DUR et MIN_MOU elle est signalee. Les fentes des percages et les encoches
ouvertes du contour exterieur doivent valoir MIN_FENTE fois l'epaisseur, sans
quoi le laser ne degage pas la chute.

Chaque piece est controlee finie ET, si elle en a un, sur son profil de
decoupe (PartSpec.dxf_profile).
"""

import math
import sys

import geom2d as G
import params as p
import parts as P

MIN_DUR = 0.8          # x epaisseur : en dessous, faute
MIN_MOU = 1.0          # x epaisseur : en dessous, avertissement
MIN_FENTE = 0.5        # x epaisseur : largeur de fente coupable au laser
PROF_ENCOCHE = 3.0     # mm : en dessous, une encoche du contour est un degagement, pas une fente
N_ECH = 16             # points par quart d'arc


# ------------------------------------------------------------- distances 2D

def seg_seg(a0, a1, b0, b1):
    """Distance minimale entre deux segments de droite."""
    ux, uy = a1[0] - a0[0], a1[1] - a0[1]
    vx, vy = b1[0] - b0[0], b1[1] - b0[1]
    wx, wy = a0[0] - b0[0], a0[1] - b0[1]
    a = ux * ux + uy * uy
    b = ux * vx + uy * vy
    c = vx * vx + vy * vy
    d = ux * wx + uy * wy
    e = vx * wx + vy * wy
    den = a * c - b * b
    if den < 1e-12:
        s = 0.0
        t = (e / c) if c > 1e-12 else 0.0
    else:
        s = (b * e - c * d) / den
        t = (a * e - b * d) / den
    s = max(0.0, min(1.0, s))
    t = max(0.0, min(1.0, t))
    # reprojection apres saturation
    for _ in range(2):
        if c > 1e-12:
            t = max(0.0, min(1.0, (e + b * s) / c))
        if a > 1e-12:
            s = max(0.0, min(1.0, (b * t - d) / a))
    px = a0[0] + s * ux - (b0[0] + t * vx)
    py = a0[1] + s * uy - (b0[1] + t * vy)
    return math.hypot(px, py), (a0[0] + s * ux, a0[1] + s * uy)


def poly_dist(pa, pb):
    """Distance minimale entre deux polygones fermes, et le point ou elle a lieu."""
    best, pos = 1e18, None
    for i in range(len(pa)):
        a0, a1 = pa[i], pa[(i + 1) % len(pa)]
        for j in range(len(pb)):
            b0, b1 = pb[j], pb[(j + 1) % len(pb)]
            d, q = seg_seg(a0, a1, b0, b1)
            if d < best:
                best, pos = d, q
    return best, pos


def dans(pt, poly):
    """Point dans un polygone ferme, par lancer de rayon."""
    x, y = pt
    dedans = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            xi = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if xi > x:
                dedans = not dedans
    return dedans


def _proj(pt, a, b):
    """Point de [a, b] le plus proche de pt."""
    ux, uy = b[0] - a[0], b[1] - a[1]
    L2 = ux * ux + uy * uy
    if L2 < 1e-12:
        return a
    t = max(0.0, min(1.0, ((pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy) / L2))
    return (a[0] + t * ux, a[1] + t * uy)


def auto_dist(pa, ecart_mini, matiere_dedans):
    """
    Epaisseur minimale de MATIERE entre deux points d'un MEME contour eloignes
    l'un de l'autre le long de ce contour. C'est ce qui attrape un contour qui
    se pince : une languette trop pres du bord d'en face, une fente qui revient
    sur elle-meme. La comparaison d'un percage a un autre ne le voit pas,
    puisqu'il n'y a la qu'un seul contour.

    Deux precautions, sans lesquelles le controle ne dit rien de juste :
    - l'eloignement est CURVILIGNE et se mesure entre les extremites les plus
      proches des deux segments, sinon deux segments voisins, qui se touchent
      par construction, passent le filtre des qu'ils sont longs ;
    - le milieu du plus court chemin doit tomber DANS LA MATIERE. Deux bords
      separes par du vide -- les deux joues d'une fente, le degagement autour
      d'une languette -- ne sont pas un ligament, et les compter en faisait
      refuser toutes les pieces qui en ont une.
    """
    n = len(pa)
    s = [0.0] * (n + 1)
    for i in range(n):
        a, b = pa[i], pa[(i + 1) % n]
        s[i + 1] = s[i] + math.hypot(b[0] - a[0], b[1] - a[1])
    tot = s[n]
    if tot < 4.0 * ecart_mini:
        return 1e18, None
    best, pos = 1e18, None
    for i in range(n):
        ai, bi = pa[i], pa[(i + 1) % n]
        for j in range(i + 1, n):
            if min(s[j] - s[i + 1], tot - s[j + 1] + s[i]) < ecart_mini:
                continue
            aj, bj = pa[j], pa[(j + 1) % n]
            d, q = seg_seg(ai, bi, aj, bj)
            if d >= best:
                continue
            r = _proj(q, aj, bj)
            if dans(((q[0] + r[0]) / 2.0, (q[1] + r[1]) / 2.0), pa) != matiere_dedans:
                continue
            best, pos = d, q
    return best, pos


def encoches(pa, prof_mini):
    """
    Largeur minimale des ENCOCHES ouvertes du contour exterieur : le vide entre
    deux bords qui se font FACE (directions opposees a 30 degres pres), chacun
    long d'au moins `prof_mini`, le milieu du plus court chemin etant hors de
    la matiere. C'est ce qui attrape l'encoche entre le bec et le corps d'un
    crochet, qu'auto_dist ne voit pas : ses deux joues sont trop proches le
    long du contour pour passer son filtre curviligne.

    Les degagements d'angle (3 traits de r = 1,5, poche de 2,1) et les conges
    echantillonnes ont des cotes plus courtes que `prof_mini` : ils sont
    ignores, ce ne sont pas des fentes a degager.
    """
    n = len(pa)
    segs = []
    for i in range(n):
        a, b = pa[i], pa[(i + 1) % n]
        lg = math.hypot(b[0] - a[0], b[1] - a[1])
        if lg >= prof_mini:
            segs.append((i, a, b, ((b[0] - a[0]) / lg, (b[1] - a[1]) / lg)))
    best, pos = 1e18, None
    for k in range(len(segs)):
        i, ai, bi, ui = segs[k]
        li = math.hypot(bi[0] - ai[0], bi[1] - ai[1])
        for m in range(k + 1, len(segs)):
            j, aj, bj, uj = segs[m]
            if ui[0] * uj[0] + ui[1] * uj[1] > -math.cos(math.radians(30.0)):
                continue                      # pas face a face
            # partie de i qui fait face a j : recouvrement des projections
            ta = (aj[0] - ai[0]) * ui[0] + (aj[1] - ai[1]) * ui[1]
            tb = (bj[0] - ai[0]) * ui[0] + (bj[1] - ai[1]) * ui[1]
            t0, t1 = max(0.0, min(ta, tb)), min(li, max(ta, tb))
            if t1 - t0 < 0.5:
                continue                      # decales : ils ne se font pas face
            d, q = seg_seg(ai, bi, aj, bj)
            if d >= best or d < 1e-9:
                continue
            # le vide se juge au milieu de la partie en regard, pas a un bout,
            # ou le milieu tomberait sur le contour lui-meme
            tm = (t0 + t1) / 2.0
            pm = (ai[0] + ui[0] * tm, ai[1] + ui[1] * tm)
            rm = _proj(pm, aj, bj)
            if dans(((pm[0] + rm[0]) / 2.0, (pm[1] + rm[1]) / 2.0), pa):
                continue                      # c'est de la matiere, pas une encoche
            best, pos = d, q
    return best, pos


def echantillonne(segs):
    return G.polyline(segs, N_ECH)


# ------------------------------------------------------------- controle

def controle(nom, outer, holes, epaisseur, noms=None):
    """Retourne (fautes, avertissements, ligament minimal)."""
    dur = MIN_DUR * epaisseur
    mou = MIN_MOU * epaisseur
    po = echantillonne(outer)
    ph = [echantillonne(h) for h in holes]
    et = noms or ["trou %d" % (i + 1) for i in range(len(holes))]

    fautes, avert = [], []
    mini = 1e18

    for i, h in enumerate(ph):
        d, q = poly_dist(h, po)
        # un percage qui mord le contour : son centre est dehors, ou il le coupe
        cx = sum(u[0] for u in h) / len(h)
        cz = sum(u[1] for u in h) / len(h)
        if not dans((cx, cz), po):
            fautes.append(("%s hors du contour" % et[i], (cx, cz), 0.0))
            continue
        mini = min(mini, d)
        if d < dur:
            fautes.append(("%s a %.1f mm du contour" % (et[i], d), q, d))
        elif d < mou:
            avert.append(("%s a %.1f mm du contour" % (et[i], d), q, d))

    # un contour qui se pince : languette, fente qui revient sur elle-meme
    for et_i, poly, dedans_ok in ([("contour", po, True)]
                                  + [(e, h, False) for e, h in zip(et, ph)]):
        d, q = auto_dist(poly, 6.0 * mou, dedans_ok)
        if d > 1e17:
            continue
        mini = min(mini, d)
        if d < dur:
            fautes.append(("%s se pince a %.1f mm" % (et_i, d), q, d))
        elif d < mou:
            avert.append(("%s se pince a %.1f mm" % (et_i, d), q, d))

    # Et le controle symetrique : la largeur des FENTES, le vide entre deux
    # bords d'un meme percage. Un degagement de languette, les deux joues d'une
    # fente. Trop etroit, le laser ne le coupe pas proprement -- et la languette
    # n'a plus la place de bouger.
    for et_i, h in zip(et, ph):
        d, q = auto_dist(h, 6.0 * mou, True)
        if d > 1e17:
            continue
        if d < MIN_FENTE * epaisseur:
            fautes.append(("%s : fente de %.1f mm seulement" % (et_i, d), q, d))
    # ... et les ENCOCHES ouvertes du contour exterieur (bec de crochet, mi-bois)
    d, q = encoches(po, PROF_ENCOCHE)
    if d < 1e17 and d < MIN_FENTE * epaisseur - 1e-9:
        fautes.append(("contour : encoche de %.1f mm seulement" % d, q, d))

    for i in range(len(ph)):
        for j in range(i + 1, len(ph)):
            d, q = poly_dist(ph[i], ph[j])
            ci = (sum(u[0] for u in ph[i]) / len(ph[i]),
                  sum(u[1] for u in ph[i]) / len(ph[i]))
            if dans(ci, ph[j]) or d < 1e-6:
                fautes.append(("%s et %s se recoupent" % (et[i], et[j]), q, 0.0))
                continue
            mini = min(mini, d)
            if d < dur:
                fautes.append(("%s et %s : ligament %.1f mm" % (et[i], et[j], d), q, d))
            elif d < mou:
                avert.append(("%s et %s : ligament %.1f mm" % (et[i], et[j], d), q, d))

    return fautes, avert, mini


def noms_flanc():
    """Etiquettes des percages du flanc, dans l'ordre de flanc_profile."""
    out = ["fenetre"]
    for cote in (-1, 1):
        for k, _ in enumerate(P.ajour_cercles(cote)):
            out.append("ajour bielle %+d n%d" % (cote, k + 1))
    for k, _ in enumerate(P.ajour_membrure_basse()):
        out.append("ajour membrure basse n%d" % (k + 1))
    out += ["lumiere gauche", "lumiere droite", "fente du coin"]
    for (x, z, d, role) in P.flanc_trous():
        out.append("%s (%+.0f, %.0f)" % (role, x, z))
    return out


def main():
    print("=" * 74)
    print("%-22s %6s %9s %7s %7s" % ("piece", "trous", "ligament", "fautes", "avert"))
    print("=" * 74)
    total_f = 0
    detail = []

    for spec in P.all_parts():
        if not spec.flat and spec.name not in ("coulisseau", "poussoir", "support",
                                               "traverse", "coin"):
            continue
        # la piece finie, et la piece telle que la decoupe le laser quand elle
        # differe (surepaisseur de fraisage, avant-trous) : c'est celle-la que
        # la tole doit tenir a la coupe
        variantes = [(spec.name, spec.profile)]
        if getattr(spec, "dxf_profile", None):
            variantes.append((spec.name + " (DXF)", spec.dxf_profile))
        for nom, prof in variantes:
            outer, holes = prof()
            noms = noms_flanc() if spec.name == "flanc" else None
            f, a, mini = controle(nom, outer, holes, spec.thickness, noms)
            total_f += len(f)
            print("%-22s %6d %9s %7d %7d"
                  % (nom, len(holes), ("%.1f" % mini) if mini < 1e17 else "-",
                     len(f), len(a)))
            detail.append((nom, f, a))

    print("=" * 74)
    for nom, f, a in detail:
        if not f and not a:
            continue
        print("\n%s :" % nom)
        for t, q, d in f:
            print("   FAUTE  %s" % t)
        for t, q, d in a:
            print("   -      %s" % t)

    print("\n%d faute(s)" % total_f)
    return 1 if total_f else 0


if __name__ == "__main__":
    sys.exit(main())
