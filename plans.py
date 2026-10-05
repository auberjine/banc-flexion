# -*- coding: utf-8 -*-
"""
Plans de fabrication : un SVG A3 par piece, plus une page d'assemblage.

    python plans.py

Les plans sont construits a partir des MEMES profils que le 3D et les DXF.
"""

import os
import math
import geom2d as G
import params as p
import parts as P
import draw as D
import json
import outils

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "plans")
if not os.path.isdir(OUT):
    os.makedirs(OUT)

LETTRES = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def centre(segs_list):
    xs, zs = [], []
    for segs in segs_list:
        x0, z0, x1, z1 = G.bbox(segs)
        xs += [x0, x1]
        zs += [z0, z1]
    return (min(xs) + max(xs)) / 2.0, (min(zs) + max(zs)) / 2.0, \
           max(xs) - min(xs), max(zs) - min(zs)


def masse(nom, defaut=0.0):
    """Masse d'une piece, lue dans le modele construit."""
    try:
        d = json.load(open(os.path.join(HERE, "out", "masses.json")))
    except Exception:
        return defaut
    if nom == "cadre":
        return d["cadre_kg"]
    for it in d["pieces"]:
        if it["nom"] == nom:
            return it["masse_kg"]
    return defaut


def rect(x0, z0, x1, z1, r=0.0):
    return G.rounded_rect(x0, z0, x1, z1, r) if r > 0 else G.rounded_rect(x0, z0, x1, z1, 0.001)


# ============================================================ flanc

# Aides de la planche 01 (02/10/2026). Elles n'utilisent que l'interface
# publique de draw.View et ne changent rien aux autres planches.

def f01_pm(x, dec=1):
    """Abscisse d'un element symetrique : 0 sur l'axe, +/-x sinon."""
    return "0" if abs(x) < 0.01 else "+/-" + D.fmt(abs(x), dec)


def f01_chemin(v, segs, w=D.TRAIT_FORT, dash=None):
    """Trace OUVERT d'une suite continue de segments (View.contour la ferme)."""
    d = v.d_of(segs)
    if d.endswith(" Z"):
        d = d[:-2]
    v.s.path(d, w, dash)


def f01_decoupe(segs, x0, z0, x1, z1):
    """Segments d'un contour restreints au rectangle (x0, z0)-(x1, z1) : les
    droites sont coupees au bord, les arcs gardes s'ils sont entierement
    dedans. Sert aux vues de detail : un contour entier trace a 2:1 sous un
    masque sortirait de la vue pour le controle de lisibilite."""
    out = []
    for sg in segs:
        a, b = G.seg_start(sg), G.seg_end(sg)
        if sg[0] == 'A':
            if all(x0 <= q[0] <= x1 and z0 <= q[1] <= z1 for q in (a, b)):
                out.append(sg)
            continue
        dx, dz = b[0] - a[0], b[1] - a[1]
        t0, t1 = 0.0, 1.0
        dehors = False
        for pp, qq in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dz, a[1] - z0), (dz, z1 - a[1])):
            if abs(pp) < 1e-12:
                if qq < 0:
                    dehors = True
                continue
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
        if not dehors and t1 - t0 > 1e-9:
            out.append(('L', (a[0] + dx * t0, a[1] + dz * t0), (a[0] + dx * t1, a[1] + dz * t1)))
    return out


def f01_cote_alignee(v, p0, p1, off, texte, att=(True, True), dt=0.0, dedans=True):
    """Cote parallele a p0-p1 (modele). Ligne de cote decalee de off mm de
    feuille (off > 0 : a gauche du sens p0 -> p1 tel qu'on le voit sur la
    feuille). Lignes d'attache perpendiculaires, ISO 129-1 : 1 mm de jour a
    l'arete, 2 mm au-dela de la ligne de cote."""
    a, b = v.P(p0), v.P(p1)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = uy, -ux
    sg = 1.0 if off >= 0 else -1.0
    for q, ok in ((a, att[0]), (b, att[1])):
        if ok:
            v.s.line(q[0] + nx * sg * v.ECART_ATTACHE, q[1] + ny * sg * v.ECART_ATTACHE,
                     q[0] + nx * (off + sg * v.DEPASSE_ATTACHE), q[1] + ny * (off + sg * v.DEPASSE_ATTACHE),
                     D.TRAIT_FIN)
    v._cote_iso((a[0] + nx * off, a[1] + ny * off), (b[0] + nx * off, b[1] + ny * off),
                texte, dt, dedans)


def f01_cote_angle(v, c, a0, a1, r, texte, dr=1.5):
    """Cote angulaire : arc fin de rayon r (mm de feuille) centre en c
    (modele), de a0 a a1 degres (modele, sens trigonometrique), fleches aux
    deux bouts, texte horizontal a l'exterieur de l'arc, sur sa bissectrice."""
    cs = v.P(c)
    A0, A1 = math.radians(a0), math.radians(a1)
    q0 = (cs[0] + r * math.cos(A0), cs[1] - r * math.sin(A0))
    q1 = (cs[0] + r * math.cos(A1), cs[1] - r * math.sin(A1))
    v.s.path("M %.3f %.3f A %.3f %.3f 0 %d 0 %.3f %.3f"
             % (q0[0], q0[1], r, r, 1 if A1 - A0 > math.pi else 0, q1[0], q1[1]), D.TRAIT_FIN)
    v._fleche(q0, -math.sin(A0), -math.cos(A0))
    v._fleche(q1, math.sin(A1), math.cos(A1))
    am = (A0 + A1) / 2.0
    ca, sa = math.cos(am), math.sin(am)
    tx, ty = cs[0] + (r + dr) * ca, cs[1] - (r + dr) * sa
    an = "start" if ca > 0.35 else ("end" if ca < -0.35 else "middle")
    ty += 0.75 * D.H_TEXTE if sa < -0.35 else (0.0 if sa > 0.35 else 0.36 * D.H_TEXTE)
    v.s.text(tx, ty, texte, D.H_TEXTE, an)


def f01_rayon_creux(v, c, r, a_deg, texte, lg=4.0, palier=0.0):
    """Rayon d'un conge CONCAVE (centre du cote du vide) : ligne du point de
    l'arc vers le centre, prolongee de lg mm, fleche sur l'arc, texte au bout."""
    a = math.radians(a_deg)
    q = v.P((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    cs = v.P(c)
    L = math.hypot(cs[0] - q[0], cs[1] - q[1])
    ux, uy = (cs[0] - q[0]) / L, (cs[1] - q[1]) / L
    e = (cs[0] + ux * lg, cs[1] + uy * lg)
    v.s.line(q[0], q[1], e[0], e[1], D.TRAIT_FIN)
    v._fleche(q, ux, uy)
    if palier:
        v.s.line(e[0], e[1], e[0] + palier, e[1], D.TRAIT_FIN)
        an = "start" if palier > 0 else "end"
        v.s.text(e[0] + palier + (1.0 if palier > 0 else -1.0), e[1] + 1.1, texte, D.H_TEXTE, an)
    else:
        v.s.text(e[0], e[1] - 1.2, texte, D.H_TEXTE, "middle")


def f01_appel(v, c, r, lettre, ang, dl=3.5):
    """Appel de detail (ISO 128-1) : cercle fin de rayon r (mm de feuille)
    autour du point c (modele), lettre a l'exterieur, vers ang (degres
    feuille, 0 a droite, 90 en haut)."""
    cs = v.P(c)
    v.s._p('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="none" stroke="#000" stroke-width="%.3f"/>'
           % (cs[0], cs[1], r, D.TRAIT_FIN))
    a = math.radians(ang)
    v.s.text(cs[0] + (r + dl) * math.cos(a), cs[1] - (r + dl) * math.sin(a) + 1.3, lettre, 3.6,
             "middle", weight="bold")


def plan_flanc():
    outer = P.flanc_contour()
    fen = P.flanc_fenetre()
    trous = P.flanc_trous()
    lums = P.flanc_lumieres()
    fente = P.flanc_fente_coin()
    mort = P.flanc_mortaise()
    grav = P.flanc_gravure()
    aj_h = P.ajour_cercles(1)
    ajours = []
    for cote in (-1, 1):
        ajours += P.ajour_cercles(cote)
    bas = P.ajour_membrure_basse()
    spec = dict((sp.name, sp) for sp in P.all_parts())["flanc"]
    _, _, bm, bn = P.ligne_bielle(1)        # arete de bielle : tete de montant -> aisselle
    pente = math.degrees(P.bielle_angle())
    a_enc = math.radians(p.PIED_DEBOUT_ANGLE)
    w2 = p.ENCOCHE_FLANC_B / 2.0             # encoches du flanc : elles recoivent un pied S355
    r_bouche = min(sg[2] for sg in outer if sg[0] == 'A')     # bouches des encoches
    # graduation : un trait par kN, dans l'ordre de parts.flanc_gravure
    gx0 = grav[0][0][1][0]                                     # depart commun des traits
    g_long = [g[0][2][0] - g[0][1][0] for g in grav]           # 8 aux kN pairs, 4,5 impairs
    g_z = [g[0][1][1] for g in grav]
    x_lum = p.GUIDE_X + p.LUMIERE_B / 2.0                      # bord exterieur de la lumiere
    # lettres des details : hors de la plage A..E des percages
    DX, DY, DZ, DW = "X", "Y", "Z", "W"
    m = masse("flanc")
    if p.RE_S355_CHAUD <= p.RE_TOLE_CHAUD:
        mou = "patin S355"
    else:
        mou = "flanc %s" % p.NUANCE_TOLE

    notes = ["Decoupe et gravure laser d'apres flanc.dxf : calque DECOUPE coupe, GRAVURE marque"
             " sans traverser (detail %s)." % DY,
             "Matiere : %s." % p.EXIGENCE_TOLE,
             "Encoches et mortaise taillees sur la tole S355 REELLE des pieds et de la traverse"
             " (EP_TOLE_REELLE_S355 = %s) : encoches %s = tole + jeu %s ;"
             % (P.fr(p.EP_TOLE_REELLE_S355, 2), D.fmt(p.ENCOCHE_FLANC_B), D.fmt(p.PIED_JEU)),
             "mortaise %s = %d x tole + jeu %s."
             % (D.fmt(p.TRAVERSE_LX_REEL + p.TRAVERSE_JEU_X), p.TRAVERSE_N, D.fmt(p.TRAVERSE_JEU_X)),
             p.NOTE_TOLE_REELLE[0].upper() + p.NOTE_TOLE_REELLE[1:] + ".",
             "Aretes cassees %s x 45 deg sur les deux faces, bossages compris (ils ne sont pas repris)."
             % D.fmt(p.CHANFREIN),
             "Contour symetrique en X, graduation d'un seul cote : deux flancs identiques, face gravee"
             " a l'exterieur ;",
             "le second, tourne de 180 deg autour de Z, a sa graduation le long de la lumiere -X.",
             "Planeite 0,5 sur %s, ne pas redresser a chaud ; sommets des bossages coplanaires a 0,3."
             % D.fmt(p.L_FLANC)]
    if m > 0:
        notes.append("Masse : %s kg." % D.fmt(m, 1))
    s = D.Sheet("FLANC EN TREILLIS", "01", spec.material, spec.stock, spec.qty,
                "1:4  -  details 1,5:1 et 2:1", notes=notes)
    s.cartouche()

    # ------------------------------------------------ vue de face, 1:4
    v = D.View(s, 0.25, 0.0, p.H_FLANC / 2.0, 145.0, 78.0)
    s.text(25.0, 17.0, "VUE DE LA FACE GRAVEE  (1:4)", 3.6, "start", weight="bold")
    v.contour(outer, D.TRAIT_FORT)
    v.contour(fen, D.TRAIT_FORT)
    for lu in lums:
        v.contour(lu, D.TRAIT_FORT)
    v.contour(fente, D.TRAIT_FORT)
    v.contour(mort, D.TRAIT_FORT)
    for (cx, cz, r) in ajours + bas:
        v.contour(G.circle(cx, cz, r), D.TRAIT_FORT)
    for (x, z, d, _r) in trous:
        v.contour(G.circle(x, z, d / 2.0), D.TRAIT_FORT)
        v.croix((x, z), 2.2)
    for g in grav:
        f01_chemin(v, g, D.TRAIT_FIN)
    v.axe((0.0, 0.0), (0.0, p.H_FLANC), ext=2.5)

    def z_de_y(vv, y):
        return vv.cz - (y - vv.oy) / vv.k

    y0 = v.P((0.0, 0.0))[1]
    # entraxe des encoches du chant bas : porte par leurs axes, prolonges
    # jusqu'au-dela de sa ligne de cote
    for sx in (-1.0, 1.0):
        v.axe((sx * p.PIED_X_POS, p.PIED_CROIX_FLANC + 2.0), (sx * p.PIED_X_POS, z_de_y(v, y0 + 9.0)),
              ext=0.0)
    v.cote_hx(-p.PIED_X_POS, p.PIED_X_POS, None, None, 0.0, dt=-22.0, zl=z_de_y(v, y0 + 7.0))
    v.cote_hx(-p.X_APPUI, p.X_APPUI, p.Z_BOSSAGE, p.Z_BOSSAGE, 0.0,
              texte="%s +/-0,3" % D.fmt(2.0 * p.X_APPUI), zl=z_de_y(v, y0 + 14.0))
    v.cote_hx(-p.L_FLANC / 2.0, p.L_FLANC / 2.0, 0.0, 0.0, 0.0, zl=z_de_y(v, y0 + 21.0))
    v.cote_vx(0.0, p.H_FLANC, -p.L_FLANC / 2.0, -p.L_FLANC / 2.0, -7.0)

    # bulles des percages, decalages choisis un par un sur le rendu
    OFFS = {"A": (12.0, -4.0), "B": (12.0, 4.0), "C": (8.0, -6.0), "D": (0.0, -9.0), "E": (8.5, -1.0)}
    lignes = []
    i = 0
    for (x, z, d, role) in trous:
        if x < -0.01:
            continue
        nb = sum(1 for (x2, z2, _d2, _r2) in trous if abs(abs(x2) - abs(x)) < 0.01 and abs(z2 - z) < 0.01)
        lettre = LETTRES[i]
        lignes.append((lettre, str(nb), f01_pm(x), D.fmt(z, 1), D.fmt(d, 1), role))
        dx, dy = OFFS.get(lettre, (8.0, -8.0))
        v.bulle((x, z), lettre, dx, dy, r=3.1, fin="point")
        i += 1

    # appels de detail
    f01_appel(v, (p.X_APPUI, p.Z_BOSSAGE - 2.0), 8.5, DX, 135.0)
    f01_appel(v, ((x_lum + gx0 + max(g_long)) / 2.0, (min(g_z) + max(g_z)) / 2.0), 5.5, DY, -20.0)
    f01_appel(v, (p.L_FLANC / 2.0 - 14.0 * math.cos(a_enc), p.H_FLANC - 14.0 * math.sin(a_enc)),
              6.5, DZ, 30.0)
    f01_appel(v, (-p.PIED_X_POS, p.PIED_CROIX_FLANC / 2.0), 4.5, DW, 225.0, 4.5)

    # ------------------------------------------------ detail X : bossage, 1,5:1
    KX, XD, YD = 1.5, 342.0, 40.0
    s.text(XD, 16.5, "DETAIL %s  (1,5:1)" % DX, 3.6, "middle", weight="bold")
    s.text(XD, 21.0, "bossage d'appui, 2 ex.", 2.8, "middle")
    bd, xb0, xb1 = G.crown(0.0, 0.0, p.BOSSAGE_RELIEF, p.BOSSAGE_R, p.BOSSAGE_CONGE, True)
    xg, xd = xb0 - 3.0, xb1 + 2.0
    zb = -10.0
    v2 = D.View(s, KX, 0.0, 0.0, XD, YD)
    f01_chemin(v2, [('L', (xg, 0.0), (xb0, 0.0))] + bd + [('L', (xb1, 0.0), (xd, 0.0))])
    v2.rupture((xg, 0.0), (xg, zb))
    v2.rupture((xg, zb), (xd, zb))
    v2.rupture((xd, zb), (xd, 0.0))
    v2.axe((0.0, -4.0), (0.0, p.BOSSAGE_RELIEF + 4.0))
    v2.rayon((0.0, p.BOSSAGE_RELIEF - p.BOSSAGE_R), p.BOSSAGE_R, 97.0, "R" + D.fmt(p.BOSSAGE_R), 9)
    # conge gauche : centre au-dessus de l'arete, arc entre la droite et le bombe
    cg = (xb0, p.BOSSAGE_CONGE)
    a_cg = 0.5 * math.degrees(bd[0][3] + bd[0][4])       # milieu de l'arc du conge
    f01_rayon_creux(v2, cg, p.BOSSAGE_CONGE, a_cg, "R" + D.fmt(p.BOSSAGE_CONGE), lg=3.0)
    v2.cote_vx(0.0, p.BOSSAGE_RELIEF, xd, 0.0, 7.0, texte=D.fmt(p.BOSSAGE_RELIEF, 1), dt=6.5)
    v2.cote_hx(xb0, xb1, 0.0, 0.0, 0.0, texte="(%s)" % D.fmt(p.largeur_bossage(), 1), dt=-22.0, zl=-5.5)
    f_appui = p.CHARGE_DIM / 4.0
    s.text(XD, 60.0, "Bombe R%s choisi pour le contact, %s kN par bossage :"
           % (D.fmt(p.BOSSAGE_R), D.fmt(f_appui / 1000.0, 1)), 2.8, "middle")
    s.text(XD, 63.8, "Hertz %.0f MPa sur %s portants (%s - 2 x %s d'aretes cassees),"
           % (p.hertz_appui(), D.fmt(p.hertz_largeur(), 1), D.fmt(p.EP_FLANC), D.fmt(p.CHANFREIN)),
           2.8, "middle")
    s.text(XD, 67.6, "limite %.0f MPa (%s a 150 C), coefficient %s."
           % (p.HERTZ_LIM, mou, D.fmt(p.hertz_coef(), 2)), 2.8, "middle")

    # ------------------------------------------------ detail Y : graduation, 2:1
    KY = 2.0
    z_ch = p.LUMIERE_Z1 + 4.0                       # ligne des cotes, au-dessus de la lumiere
    v3 = D.View(s, KY, p.GUIDE_X, z_ch, 300.0, 84.0)
    s.text(311.0, 75.5, "DETAIL %s  (2:1)  graduation" % DY, 3.6, "middle", weight="bold")
    zc = p.Z_GUIDE - p.GUIDE_TETE_D / 2.0 - 0.6       # vue arretee sous la tete de guide
    for sg in f01_decoupe(lums[1], p.GUIDE_X - 20.0, zc, p.GUIDE_X + 20.0, 300.0):
        f01_chemin(v3, [sg])
    v3.rupture((p.GUIDE_X - 9.0, zc), (gx0 + max(g_long) + 2.5, zc))
    v3.axe((p.GUIDE_X, zc), (p.GUIDE_X, p.LUMIERE_Z1 + 5.0), ext=0.0)
    v3.contour(G.circle(p.GUIDE_X, p.Z_GUIDE, p.GUIDE_TETE_D / 2.0), D.TRAIT_FIN,
               dash="6 1.2 0.8 1.2 0.8 1.2")
    for g in grav:
        f01_chemin(v3, g, 0.25)
    v3.cote_hx(p.GUIDE_X, gx0, None, g_z[0], 0.0, zl=z_ch)
    v3.cote_hx(gx0, gx0 + g_long[0], g_z[0], g_z[0], 0.0, zl=z_ch)
    for k in (0, 6, 12):
        q = v3.P((gx0 + g_long[k], g_z[k]))
        s.text(q[0] + 1.5, q[1] + 1.0, "%d kN" % k, 2.8, "start")
    xn = 352.0
    for j, t in enumerate(["Traits graves, sans chiffres,",
                           "de %s aux kN impairs." % D.fmt(g_long[1]),
                           "Zero : tangente haute de la",
                           "tete de guide (trait mixte),",
                           "pile libre, Z %s." % D.fmt(g_z[0], 2),
                           "Z de chaque trait : tableau",
                           "GRADUATION."]):
        s.text(xn, 96.0 + 4.0 * j, t, 2.8, "start")

    # ------------------------------------------------ detail Z : encoche de coin, 2:1
    c0 = (p.L_FLANC / 2.0, p.H_FLANC)               # coin vif fictif, haut droit
    dd = (-math.cos(a_enc), -math.sin(a_enc))       # axe de l'encoche, vers la matiere
    nn = (math.sin(a_enc), -math.cos(a_enc))        # normale, cote du chant de 440
    v4 = D.View(s, 2.0, c0[0], c0[1], 346.0, 146.0)
    s.text(316.0, 134.5, "DETAIL %s  (2:1)" % DZ, 3.6, "middle", weight="bold")
    s.text(316.0, 139.0, "encoche de coin, 4 ex. symetriques", 2.8, "middle")
    xz0, zz0 = c0[0] - 30.0, c0[1] - 26.0
    for sg in f01_decoupe(outer, xz0, zz0, c0[0] + 1.0, c0[1] + 1.0):
        f01_chemin(v4, [sg])
    v4.rupture((xz0, c0[1]), (xz0, zz0))
    v4.rupture((xz0, zz0), (c0[0], zz0))
    # chants prolonges jusqu'au coin vif fictif (trait fin)
    xb_h = max(G.seg_start(sg)[0] for sg in outer
               if sg[0] == 'L' and abs(G.seg_start(sg)[1] - c0[1]) < 1e-6 and abs(G.seg_end(sg)[1] - c0[1]) < 1e-6)
    zb_v = max(G.seg_end(sg)[1] for sg in outer
               if sg[0] == 'L' and abs(G.seg_start(sg)[0] - c0[0]) < 1e-6 and abs(G.seg_end(sg)[0] - c0[0]) < 1e-6)
    f01_chemin(v4, [('L', (xb_h, c0[1]), (c0[0] + 1.5, c0[1]))], D.TRAIT_FIN)
    f01_chemin(v4, [('L', (c0[0], zb_v), (c0[0], c0[1] + 1.5))], D.TRAIT_FIN)
    t_enc = p.PIED_DEBOUT_PROF
    v4.axe(c0, (c0[0] + dd[0] * (t_enc + 3.0), c0[1] + dd[1] * (t_enc + 3.0)), ext=0.0)
    f01_cote_angle(v4, c0, 180.0, 180.0 + p.PIED_DEBOUT_ANGLE, 32.0,
                   "%s deg" % D.fmt(p.PIED_DEBOUT_ANGLE))
    fond = (c0[0] + dd[0] * t_enc, c0[1] + dd[1] * t_enc)
    OFF_P = 15.0                                    # ligne de la profondeur, cote du chant de 440
    f01_cote_alignee(v4, c0, fond, OFF_P, D.fmt(t_enc), att=(True, False))
    # attache du fond : elle part du sommet de la poche de degagement, sur la
    # ligne du fond prolongee
    q = v4.P((fond[0] + nn[0] * (w2 + p.PIED_R), fond[1] + nn[1] * (w2 + p.PIED_R)))
    b_ = v4.P(fond)
    L_ = math.hypot(q[0] - b_[0], q[1] - b_[1])
    nx_, ny_ = (q[0] - b_[0]) / L_, (q[1] - b_[1]) / L_
    s.line(q[0] + nx_ * v4.ECART_ATTACHE, q[1] + ny_ * v4.ECART_ATTACHE,
           b_[0] + nx_ * (OFF_P + v4.DEPASSE_ATTACHE), b_[1] + ny_ * (OFF_P + v4.DEPASSE_ATTACHE), D.TRAIT_FIN)
    # largeur, en travers de l'encoche
    tl = 22.0
    j1 = (c0[0] + dd[0] * tl - nn[0] * w2, c0[1] + dd[1] * tl - nn[1] * w2)
    j2 = (c0[0] + dd[0] * tl + nn[0] * w2, c0[1] + dd[1] * tl + nn[1] * w2)
    v4._cote_iso(v4.P(j1), v4.P(j2), D.fmt(p.ENCOCHE_FLANC_B), dt=4.0)

    # ------------------------------------------------ detail W : encoche du chant bas, 2:1
    xw = -p.PIED_X_POS
    v5 = D.View(s, 2.0, xw, 0.0, 378.0, 176.0)
    s.text(378.0, 134.5, "DETAIL %s  (2:1)" % DW, 3.6, "middle", weight="bold")
    s.text(378.0, 139.0, "encoche du chant bas, 2 ex.", 2.8, "middle")
    zw1 = p.PIED_CROIX_FLANC + 5.0
    for sg in f01_decoupe(outer, xw - 9.0, -1.0, xw + 11.0, zw1):
        f01_chemin(v5, [sg])
    v5.rupture((xw - 9.0, 0.0), (xw - 9.0, zw1))
    v5.rupture((xw - 9.0, zw1), (xw + 11.0, zw1))
    v5.rupture((xw + 11.0, zw1), (xw + 11.0, 0.0))
    v5.axe((xw, -0.5), (xw, p.PIED_CROIX_FLANC + 3.0), ext=0.0)
    v5.cote_hx(xw - w2, xw + w2, 0.0, 0.0, 0.0, texte=D.fmt(p.ENCOCHE_FLANC_B), zl=-4.0)
    v5.cote_vx(0.0, p.PIED_CROIX_FLANC, None, xw + w2 + p.PIED_R, 6.0, texte=D.fmt(p.PIED_CROIX_FLANC))
    yn = 203.0
    s.text(346.0, yn, "Details %s et %s : angles du fond degages par une poche carree de %s"
           % (DZ, DW, D.fmt(p.PIED_R * math.sqrt(2.0))), 2.8, "middle")
    s.text(346.0, yn + 4.0, "tournee a 45 deg, centree sur l'angle vif (3 traits) ; bouches R%s."
           % D.fmt(r_bouche), 2.8, "middle")

    # ------------------------------------------------ tableaux
    D.table(s, 13.0, 170.0, "PERCAGES  (X depuis l'axe, Z depuis le chant bas)",
            ["rep", "nb", "X", "Z", "diam", "fonction"], lignes, [9, 8, 19, 15, 11, 44], 4.4)

    lig2 = []
    for (cx, cz, r) in aj_h:
        lig2.append(("2", f01_pm(cx), D.fmt(cz, 1), D.fmt(2 * r, 1)))
    for (cx, cz, r) in bas:
        if cx < -0.01:
            continue
        lig2.append(("1" if abs(cx) < 0.01 else "2", f01_pm(cx), D.fmt(cz, 1), D.fmt(2 * r, 1)))
    D.table(s, 140.0, 170.0, "AJOURS  (meme origine)", ["nb", "X", "Z", "diam"], lig2, [9, 19, 15, 13], 4.4)

    lig3 = [("angle bas", "2", f01_pm(p.X_FENETRE), D.fmt(p.Z_MEMB_BASSE, 1), "R" + D.fmt(p.R_FEN_BAS)),
            ("tete de montant", "2", f01_pm(bm[0]), D.fmt(bm[1], 1), "R" + D.fmt(p.R_FEN_MONTANT)),
            ("aisselle de noeud", "2", f01_pm(bn[0]), D.fmt(bn[1], 1), "R" + D.fmt(p.R_FEN_NOEUD)),
            ("angle bas du noeud", "2", f01_pm(p.X_NOEUD), D.fmt(p.Z_NOEUD_BAS, 1),
             "R" + D.fmt(p.R_FEN_NOEUD_BAS))]
    yf = D.table(s, 13.0, 208.0, "FENETRE  (sommets en coins vifs fictifs)",
                 ["sommet", "nb", "X", "Z", "conge"], lig3, [36, 8, 19, 15, 14], 4.4)
    s.text(13.0, yf + 4.0, "Sommets relies par des droites ; arete de bielle a %s deg ;"
           % D.fmt(pente, 2), 2.8, "start")
    s.text(13.0, yf + 8.0, "bossages d'appui : cote %s et detail %s." % (D.fmt(2.0 * p.X_APPUI), DX),
           2.8, "start")

    def bte(segs):
        x0, z0, x1, z1 = G.bbox(segs)
        return (x0 + x1) / 2.0, z0, z1, x1 - x0

    lig4 = []
    for nom, segs, nb, ang in (("fente du coin", fente, 1, "R" + D.fmt(p.FENTE_COIN_R)),
                               ("lumiere oblongue", lums[1], 2, "R" + D.fmt(p.LUMIERE_B / 2.0)),
                               ("mortaise de traverse", mort, 1, "R" + D.fmt(p.TRAVERSE_R_MORT))):
        xc, z0, z1, lx = bte(segs)
        lig4.append((nom, str(nb), f01_pm(xc), "%s a %s" % (D.fmt(z0, 1), D.fmt(z1, 1)),
                     D.fmt(lx, 1), ang))
    D.table(s, 13.0, yf + 22.0, "DECOUPES INTERIEURES  (X de l'axe de la decoupe)",
            ["decoupe", "nb", "X", "Z bas a haut", "largeur", "angles"], lig4, [33, 8, 15, 27, 16, 13], 4.4)

    lig5 = []
    n2 = (len(g_z) + 1) // 2
    for k in range(n2):
        a = ("%d" % k, D.fmt(g_z[k], 2))
        b = ("%d" % (k + n2), D.fmt(g_z[k + n2], 2)) if k + n2 < len(g_z) else ("", "")
        lig5.append(a + b)
    D.table(s, 140.0, 219.0, "GRADUATION  (detail %s)" % DY, ["kN", "Z", "kN", "Z"], lig5, [9, 16, 9, 16], 4.4)

    return s.save(os.path.join(OUT, "01_flanc.svg"))


# ============================================================ tete de charge

# Aides de la planche 02 (02/10/2026). Elles n'utilisent que l'interface
# publique de draw.View (cote_hx, cote_vx, _cote_iso, renvoi, rupture, rayon)
# et ne changent rien aux autres planches.

C02_CACHE = "3 1"          # trait interrompu fin (ISO 128 type 02)


def c02_poly(v, pts, w=D.TRAIT_FORT, dash=None, ferme=False):
    """Ligne brisee par les points modele pts, ouverte sauf si ferme."""
    q = [v.P(a) for a in pts]
    d = " ".join(("M " if i == 0 else "L ") + "%.3f %.3f" % a for i, a in enumerate(q))
    v.s.path(d + (" Z" if ferme else ""), w, dash)


def c02_chemin(v, segs, w=D.TRAIT_FORT, dash=None):
    """Trace OUVERT d'une suite de segments (View.contour la ferme)."""
    d = v.d_of(segs)
    if d.endswith(" Z"):
        d = d[:-2]
    v.s.path(d, w, dash)


def c02_decoupe(segs, x0, z0, x1, z1):
    """Segments d'un contour restreints au rectangle (x0, z0)-(x1, z1) : les
    droites sont coupees au bord, les arcs gardes s'ils sont entierement
    dedans (vues de detail)."""
    out = []
    for sg in segs:
        a, b = G.seg_start(sg), G.seg_end(sg)
        if sg[0] == 'A':
            if all(x0 <= q[0] <= x1 and z0 <= q[1] <= z1 for q in (a, b)):
                out.append(sg)
            continue
        dx, dz = b[0] - a[0], b[1] - a[1]
        t0, t1 = 0.0, 1.0
        dehors = False
        for pp, qq in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dz, a[1] - z0), (dz, z1 - a[1])):
            if abs(pp) < 1e-12:
                if qq < 0:
                    dehors = True
                continue
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
        if not dehors and t1 - t0 > 1e-9:
            out.append(('L', (a[0] + dx * t0, a[1] + dz * t0), (a[0] + dx * t1, a[1] + dz * t1)))
    return out


def c02_axe(v, p0, p1, e0=2.0, e1=2.0):
    """Trait d'axe de p0 a p1 (modele), prolonge de e0 / e1 mm de feuille."""
    a, b = v.P(p0), v.P(p1)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    if L < 1e-6:
        return
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    v.s.line(a[0] - ux * e0, a[1] - uy * e0, b[0] + ux * e1, b[1] + uy * e1,
             D.TRAIT_AXE, "6 1.5 1 1.5")


def c02_cercle(v, c, r, w=D.TRAIT_FORT, dash=None):
    q = v.P(c)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    v.s._p('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="none" stroke="#000" stroke-width="%.3f"%s/>'
           % (q[0], q[1], r * v.k, w, da))


def c02_arc(v, c, r, a0, a1, w=D.TRAIT_FIN):
    """Arc de cercle de a0 a a1 degres (modele, sens trigonometrique)."""
    q = v.P(c)
    rr = r * v.k
    A0, A1 = math.radians(a0), math.radians(a1)
    p0 = (q[0] + rr * math.cos(A0), q[1] - rr * math.sin(A0))
    p1 = (q[0] + rr * math.cos(A1), q[1] - rr * math.sin(A1))
    v.s.path("M %.3f %.3f A %.3f %.3f 0 %d 0 %.3f %.3f"
             % (p0[0], p0[1], rr, rr, 1 if A1 - A0 > math.pi else 0, p1[0], p1[1]), w)


def c02_taraudage_bout(v, c, d_fond, d_nom):
    """Taraudage vu en bout (ISO 6410) : cercle du fond de filet en trait
    fort, cercle nominal aux trois quarts en trait fin."""
    c02_cercle(v, c, d_fond / 2.0, D.TRAIT_FORT)
    c02_arc(v, c, d_nom / 2.0, 100.0, 370.0, D.TRAIT_FIN)


def c02_cote_alignee(v, p0, p1, off, texte, att=(True, True), dt=0.0):
    """Cote parallele a p0-p1 (modele), ligne decalee de off mm de feuille
    (off > 0 : a gauche du sens p0 -> p1 vu sur la feuille). Lignes d'attache
    perpendiculaires : 1 mm de jour a l'arete, 2 mm au-dela de la ligne."""
    a, b = v.P(p0), v.P(p1)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = uy, -ux
    sg = 1.0 if off >= 0 else -1.0
    for q, ok in ((a, att[0]), (b, att[1])):
        if ok:
            v.s.line(q[0] + nx * sg * v.ECART_ATTACHE, q[1] + ny * sg * v.ECART_ATTACHE,
                     q[0] + nx * (off + sg * v.DEPASSE_ATTACHE), q[1] + ny * (off + sg * v.DEPASSE_ATTACHE),
                     D.TRAIT_FIN)
    v._cote_iso((a[0] + nx * off, a[1] + ny * off), (b[0] + nx * off, b[1] + ny * off), texte, dt)


def c02_cote_texte_h(v, p0, p1, texte, gauche=True):
    """Ligne de cote de p0 a p1 (modele), fleches dedans, texte HORIZONTAL a
    cote de son milieu (a gauche par defaut) : pour une ligne presque
    verticale inclinee, ou un texte tourne ne se lirait ni du bas ni de la
    droite (ISO 129-1)."""
    a, b = v.P(p0), v.P(p1)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    v.s.line(a[0], a[1], b[0], b[1], D.TRAIT_FIN)
    v._fleche(a, ux, uy)
    v._fleche(b, -ux, -uy)
    mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
    if gauche:
        v.s.text(mx - 1.5, my + 1.15, texte, D.H_TEXTE, "end")
    else:
        v.s.text(mx + 1.5, my + 1.15, texte, D.H_TEXTE, "start")


def c02_cote_angle(v, c, a0, a1, r, texte, dr=1.5):
    """Cote angulaire : arc fin de rayon r (mm de feuille) centre en c
    (modele), de a0 a a1 degres (modele, sens trigonometrique), fleches aux
    deux bouts, texte horizontal a l'exterieur de l'arc, sur sa bissectrice."""
    cs = v.P(c)
    A0, A1 = math.radians(a0), math.radians(a1)
    q0 = (cs[0] + r * math.cos(A0), cs[1] - r * math.sin(A0))
    q1 = (cs[0] + r * math.cos(A1), cs[1] - r * math.sin(A1))
    v.s.path("M %.3f %.3f A %.3f %.3f 0 %d 0 %.3f %.3f"
             % (q0[0], q0[1], r, r, 1 if A1 - A0 > math.pi else 0, q1[0], q1[1]), D.TRAIT_FIN)
    v._fleche(q0, -math.sin(A0), -math.cos(A0))
    v._fleche(q1, math.sin(A1), math.cos(A1))
    am = (A0 + A1) / 2.0
    ca, sa = math.cos(am), math.sin(am)
    tx, ty = cs[0] + (r + dr) * ca, cs[1] - (r + dr) * sa
    an = "start" if ca > 0.35 else ("end" if ca < -0.35 else "middle")
    ty += 0.75 * D.H_TEXTE if sa < -0.35 else (0.0 if sa > 0.35 else 0.36 * D.H_TEXTE)
    v.s.text(tx, ty, texte, D.H_TEXTE, an)


def c02_rayon_creux(v, c, r, a_deg, texte, lg=4.0, palier=0.0):
    """Rayon d'un arc CONCAVE (centre du cote du vide) : ligne du point de
    l'arc vers le centre, prolongee de lg mm, fleche sur l'arc, texte au bout
    (apres un palier horizontal de palier mm s'il est non nul)."""
    a = math.radians(a_deg)
    q = v.P((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    cs = v.P(c)
    L = math.hypot(cs[0] - q[0], cs[1] - q[1])
    ux, uy = (cs[0] - q[0]) / L, (cs[1] - q[1]) / L
    e = (cs[0] + ux * lg, cs[1] + uy * lg)
    v.s.line(q[0], q[1], e[0], e[1], D.TRAIT_FIN)
    v._fleche(q, ux, uy)
    if palier:
        v.s.line(e[0], e[1], e[0] + palier, e[1], D.TRAIT_FIN)
        an = "start" if palier > 0 else "end"
        v.s.text(e[0] + palier + (1.0 if palier > 0 else -1.0), e[1] + 1.1, texte, D.H_TEXTE, an)
    else:
        v.s.text(e[0], e[1] - 1.2, texte, D.H_TEXTE, "middle")


def c02_appel(v, c, r, lettre, ang, dl=3.5):
    """Appel de detail (ISO 128) : cercle fin de rayon r (mm de feuille) autour
    du point c (modele), lettre a l'exterieur vers ang (degres feuille)."""
    cs = v.P(c)
    v.s._p('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="none" stroke="#000" stroke-width="%.3f"/>'
           % (cs[0], cs[1], r, D.TRAIT_FIN))
    a = math.radians(ang)
    v.s.text(cs[0] + (r + dl) * math.cos(a), cs[1] - (r + dl) * math.sin(a) + 1.3, lettre, 3.6,
             "middle", weight="bold")


def c02_titre(s, x, y, titre, sous=None):
    """Titre de piece en gras, ligne de matiere / quantite / brut dessous."""
    s.text(x, y, titre, 3.6, "middle", weight="bold")
    if sous:
        s.text(x, y + 4.6, sous, 2.8, "middle")


def plan_coulisseau():
    import nomenclature as N            # les reperes de NOMENCLATURE.md font foi
    SP = dict((q.name, q) for q in P.all_parts())
    R = N.REPERES
    sc, sp, so = SP["coulisseau"], SP["poussoir"], SP["coin"]
    rep_c, rep_p, rep_o = R["coulisseau"], R["poussoir"], R["coin"]
    vg = [t[0] for t in N.visserie() if "oupille" in t[1]]
    vg = vg[0] if vg else "V?"
    f = D.fmt

    # ---------------------------------------------------------------- valeurs
    b2 = p.POUSSOIR_B / 2.0                  # demi-largeur du coulisseau (selon y)
    L2 = p.COULISSEAU_L / 2.0
    tg = p.COIN_TAN
    H = p.COULISSEAU_H                       # bord epais, cote chape
    hb = p.COULISSEAU_E - b2 * tg            # bord mince
    prof, _ = P.coulisseau_profile()
    rc = [sg[2] for sg in prof if sg[0] == 'A'][0]          # angles verticaux, lus sur le contour
    ra = p.ALESAGE_D / 2.0
    gx, gz = p.GUIDE_X, p.GUIDE_Z
    coin, _ = P.coin_profile()
    r1 = min(sg[2] for sg in coin if sg[0] == 'A')        # angles des rebords, lus sur le contour
    zt, zr = p.Z_COIN_HAUT, p.Z_COIN_HAUT + p.PLAQ_REBORD_H
    w, wb, hr = p.PLAQ_REBORD_L, p.PLAQ_REBORD_L_BAS, p.PLAQ_REBORD_H
    Y0, Y1 = p.COIN_Y0, p.COIN_Y1
    a_c = math.radians(p.COIN_ANGLE)
    sa_, ca_ = math.sin(a_c), math.cos(a_c)

    def zb(y):
        """Dessous du coin : plan du siege de la plaque basse."""
        return zt - p.COIN_T_BOUT_MINCE - (Y1 - y) * tg

    d1_vis = p.VIS_D - 1.082532 * p.VIS_PAS  # diametre du fond de filet femelle (ISO 724)
    logement = p.PLAQ_L + 2.0 * p.PLAQ_JEU   # 100,4 entre rebords
    psi, rho, marge = p.filet_marge()
    # filet trapezoidal Tr16x4 (ISO 2904 : pas 4, d2 14, flanc 15 deg) au meme frottement
    tr_psi = math.degrees(math.atan(4.0 / (math.pi * 14.0)))
    tr_rho = math.degrees(math.atan(p.VIS_MU_MIN / math.cos(math.radians(15.0))))
    dz_t, df_t = p.coin_par_tour()
    p_haut, p_bas = p.pressions_plaquettes()

    notes = [
        "Aretes vives non cotees cassees %s x 45 deg." % f(p.CHANFREIN),
        "%s : pente fraisee Ra 1,6, planeite 0,05 (la plaque basse %s y glisse) ; bord EPAIS (%s)"
        " cote chape." % (rep_c, R["plaquette_basse"], f(H)),
        "%s : logements centres sur la longueur, sieges plans a 0,05 ; %s, %s et %s depuis les"
        " plans des sieges prolonges."
        % (rep_o, f(p.COIN_T_BOUT_EPAIS), f(p.COIN_T_BOUT_MINCE), f(p.COIN_VIS_SOUS)),
        "%s : pente du dessous (%s deg, celle du coulisseau) ; faces interieures des rebords du"
        " dessous NORMALES a la pente ; angles R%s." % (rep_o, f(p.COIN_ANGLE), f(r1)),
        "%s : plaques du commerce %s %g x %g x %g (%s, %s) tenues par les rebords, points de"
        " silicone HT." % (rep_o, p.PLAQ_REF.split()[0], p.PLAQ_B, p.PLAQ_L, p.PLAQ_EP,
                           R["plaquette_haute"], R["plaquette_basse"]),
        "%s : commande %s kN, couple %s N.m a %s kN ; un tour de vis : %s mm de coulisseau,"
        " environ %.0f N."
        % (rep_o, f(p.coin_effort() / 1000.0), f(p.coin_couple()), f(p.CHARGE_DIM / 1000.0),
           f(dz_t, 3), df_t),
        "%s : autobloquant seulement si mu > %s : on n y compte pas, c est le filet M%g x %g qui"
        " tient la charge" % (rep_o, f(p.coin_mu_autoblocage(), 3), p.VIS_D, p.VIS_PAS),
        "(helice %s deg, frottement %s deg a mu %s : marge x%s ; un Tr16x4 tomberait a x%s,"
        " reversible)."
        % (f(psi, 2), f(rho, 2), f(p.VIS_MU_MIN, 2), f(marge, 2), f(tr_rho / tr_psi, 2)),
        "%s : flancs du filet a %s MPa ; pate cuivre (haute temperature) dans le taraudage."
        % (rep_o, f(p.pression_filet())),
        "%s : %d plateaux identiques empiles, decoupe laser (%s.dxf) ; le patin de charge"
        " %s colle fait fond." % (rep_p, sp.qty, sp.name, R["patin_charge"]),
        "%s : goupilles %s %g m6 libres dans les trous de passage, serrees dans le patin de"
        " charge %s (%g H7)." % (rep_p, vg, p.POUSSOIR_GOUPILLE_D, R["patin_charge"],
                                  p.POUSSOIR_GOUPILLE_D),
        "SENS DE MONTAGE : bout EPAIS du coin du cote oppose a la chape.",
    ]
    s = D.Sheet("COULISSEAU, COIN ET POUSSOIR", "02",
                "%s / %s / %s" % (sc.material, sp.material, so.material),
                "voir sous les titres",
                "%d + %d + %d (%s, %s, %s)" % (sc.qty, sp.qty, so.qty, rep_c, rep_p, rep_o),
                "1:1  -  details 4:1", notes=notes)
    s.cartouche()

    # ======================================================== coulisseau 02a
    XF, YF, XS, YT = 165.0, 76.0, 57.0, 119.0
    c02_titre(s, 124.0, 17.0, "%s  COULISSEAU A TETE INCLINEE  (1:1)" % rep_c,
              "%s, %d ex., brut %s" % (sc.material, sc.qty, sc.stock))

    def zdessus(y):
        return p.COULISSEAU_E + y * tg

    # ------------------------------------------------ vue de face (depuis -y)
    vf = D.View(s, 1.0, 0.0, 0.0, XF, YF)
    s.text(XF, 35.0, "vue de face", 2.8, "middle")
    n = 12
    ts = [math.radians(90.0 * i / n) for i in range(n + 1)]
    loin = [(L2 - rc + rc * math.cos(t), zdessus(b2 - rc + rc * math.sin(t))) for t in ts]
    pres = [(L2 - rc + rc * math.cos(t), zdessus(-(b2 - rc) - rc * math.sin(t))) for t in ts]
    c02_poly(vf, [(-L2, 0.0), (L2, 0.0)] + loin + [(-x, z) for (x, z) in reversed(loin)],
             ferme=True)
    c02_poly(vf, [(-x, z) for (x, z) in pres] + list(reversed(pres)))
    c02_poly(vf, [(-ra, 0.0), (-ra, p.ALESAGE_P_COUL), (ra, p.ALESAGE_P_COUL), (ra, 0.0)],
             D.TRAIT_FIN, C02_CACHE)
    c02_axe(vf, (0.0, 0.0), (0.0, p.ALESAGE_P_COUL), 0.0, 2.0)
    for sx in (-1.0, 1.0):
        c02_taraudage_bout(vf, (sx * gx, gz), p.GUIDE_TARAUD_D, p.GUIDE_VIS_D)
        c02_axe(vf, (sx * gx, 0.0), (sx * gx, gz + p.GUIDE_VIS_D / 2.0), 0.0, 2.0)
        if sx > 0:
            c02_axe(vf, (gx - p.GUIDE_VIS_D / 2.0, gz), (L2, gz), 2.0, 0.0)
        else:
            c02_axe(vf, (-gx - p.GUIDE_VIS_D / 2.0, gz), (-gx + p.GUIDE_VIS_D / 2.0, gz), 2.0, 2.0)
    vf.cote_vx(0.0, gz, L2, L2, 9.0)
    vf.cote_hx(-gx, gx, 0.0, 0.0, 0.0, zl=-7.0)

    # ------------------------------------------------ vue de droite (depuis +x)
    vs = D.View(s, 1.0, 0.0, 0.0, XS, YF)
    s.text(XS, 35.0, "vue de droite", 2.8, "middle")
    c02_poly(vs, [(-b2, 0.0), (b2, 0.0), (b2, H), (-b2, hb)], ferme=True)
    c02_poly(vs, [(-ra, 0.0), (-ra, p.ALESAGE_P_COUL), (ra, p.ALESAGE_P_COUL), (ra, 0.0)],
             D.TRAIT_FIN, C02_CACHE)
    c02_axe(vs, (0.0, 0.0), (0.0, p.ALESAGE_P_COUL), 0.0, 2.0)
    vs.cote_vx(0.0, H, b2, b2, 7.0)
    vs.cote_vx(0.0, hb, -b2, -b2, -7.0, texte="(%s)" % f(hb))
    c02_poly(vs, [(b2 - 1.0, H), (b2 - 42.0, H)], D.TRAIT_FIN)
    c02_cote_angle(vs, (b2, H), 180.0, 180.0 + p.COIN_ANGLE, 38.0, "%s deg" % f(p.COIN_ANGLE))

    # ------------------------------------------------ vue de dessus
    vt = D.View(s, 1.0, 0.0, 0.0, XF, YT)
    s.text(XF, 164.0, "vue de dessus", 2.8, "middle")
    vt.contour(prof)
    vt.contour(G.circle(0.0, 0.0, ra), D.TRAIT_FIN, dash=C02_CACHE)
    c02_axe(vt, (-L2, 0.0), (L2, 0.0), 2.5, 2.5)
    c02_axe(vt, (0.0, -b2), (0.0, b2), 2.5, 2.5)
    rn, rf = p.GUIDE_VIS_D / 2.0, p.GUIDE_TARAUD_D / 2.0
    cone = rf / math.tan(math.radians(59.0))
    for sx in (-1.0, 1.0):
        xg = sx * gx
        for sy in (-1.0, 1.0):
            yf_ = sy * (b2 - p.GUIDE_TARAUD_P)          # fin du filet
            yp_ = sy * (b2 - p.GUIDE_PERCAGE_P)         # fond de l'avant-trou
            for e in (-1.0, 1.0):
                c02_poly(vt, [(xg + e * rn, sy * b2), (xg + e * rn, yf_)], D.TRAIT_FIN, C02_CACHE)
                c02_poly(vt, [(xg + e * rf, sy * b2), (xg + e * rf, yp_), (xg, yp_ - sy * cone)],
                         D.TRAIT_FIN, C02_CACHE)
            c02_poly(vt, [(xg - rn, yf_), (xg + rn, yf_)], D.TRAIT_FIN, C02_CACHE)
            c02_axe(vt, (xg, sy * b2), (xg, yp_ - sy * cone), 2.0, 1.0)
    vt.cote_hx(-L2, L2, -(b2 - rc), -(b2 - rc), 0.0, zl=-b2 - 9.0)
    vt.cote_vx(-b2, b2, L2 - rc, L2 - rc, 0.0, xl=L2 + 9.0)
    vt.rayon((-(L2 - rc), b2 - rc), rc, 135.0, "4 x R%s" % f(rc), 10)
    vt.renvoi((-gx - rn, b2 - 8.0),
              "%d x M%g prof. %s" % (SP["guide"].qty, p.GUIDE_VIS_D, f(p.GUIDE_TARAUD_P)) + chr(10)
              + "avant-trou %s prof. %s" % (f(p.GUIDE_TARAUD_D), f(p.GUIDE_PERCAGE_P)),
              -20.0, -4.0, fin="fleche")
    a5 = math.radians(170.0)
    vt.renvoi((ra * math.cos(a5), ra * math.sin(a5)),
              "alesage %s prof. %s" % (f(p.ALESAGE_D), f(p.ALESAGE_P_COUL)) + chr(10)
              + "a fond plat, par dessous", -50.0, -5.0, fin="fleche")

    # ======================================================== coin 02c
    XC, YC = 315.0, 46.0
    c02_titre(s, XC, 17.0, "%s  COIN DE COMMANDE, epaisseur %s  (1:1)" % (rep_o, f(p.COIN_B)),
              "%s, %d ex., brut %s" % (so.material, so.qty, so.stock))
    vc = D.View(s, 1.0, (Y0 + Y1) / 2.0, zt, XC, YC)
    vc.contour(coin)
    # taraudage M16 puis passage, en traits interrompus
    yt_ = Y0 + p.COIN_TARAUD_L
    for e in (-1.0, 1.0):
        c02_poly(vc, [(Y0, p.Z_VIS + e * p.VIS_D / 2.0), (yt_, p.Z_VIS + e * p.VIS_D / 2.0)],
                 D.TRAIT_FIN, C02_CACHE)
        c02_poly(vc, [(Y0, p.Z_VIS + e * d1_vis / 2.0), (yt_, p.Z_VIS + e * d1_vis / 2.0)],
                 D.TRAIT_FIN, C02_CACHE)
        c02_poly(vc, [(yt_, p.Z_VIS + e * p.VIS_PASSAGE_D / 2.0), (Y1, p.Z_VIS + e * p.VIS_PASSAGE_D / 2.0)],
                 D.TRAIT_FIN, C02_CACHE)
    c02_poly(vc, [(yt_, p.Z_VIS - p.VIS_PASSAGE_D / 2.0), (yt_, p.Z_VIS + p.VIS_PASSAGE_D / 2.0)],
             D.TRAIT_FIN, C02_CACHE)
    c02_axe(vc, (Y0, p.Z_VIS), (Y1, p.Z_VIS), 3.0, 0.0)
    # cotes
    vc.cote_hx(Y0 + w, Y1 - w, zr, zr, 7.0, texte="%s +0,2/0" % f(logement))
    vc.cote_hx(Y0, Y1, zr, zr, 14.0)
    vc.cote_vx(zt - p.COIN_T_BOUT_EPAIS, zt, Y0, Y0, -7.0, texte=f(p.COIN_T_BOUT_EPAIS))
    vc.cote_vx(p.Z_VIS, zt, Y1, Y1, 7.0, texte=f(p.COIN_VIS_SOUS))
    vc.cote_vx(zt - p.COIN_T_BOUT_MINCE, zt, Y1, Y1, 14.0, texte=f(p.COIN_T_BOUT_MINCE), dt=7.0)
    y0b, y1b = Y0 + wb, Y1 - wb
    c02_cote_alignee(vc, (y0b + hr * sa_, zb(y0b) - hr * ca_), (y1b + hr * sa_, zb(y1b) - hr * ca_),
                     -8.0, "%s +0,2/0" % f(logement))
    vc.renvoi((Y0 + 4.5, p.Z_VIS - p.VIS_D / 2.0),
              "M%g x %g prof. %s depuis le bout EPAIS, centre" % (p.VIS_D, p.VIS_PAS, f(p.COIN_TARAUD_L))
              + chr(10) + "sur l epaisseur ; passage %s debouchant" % f(p.VIS_PASSAGE_D),
              0.0, 48.0, fin="fleche")
    c02_appel(vc, (Y1 - w / 2.0 - 1.0, zt + 1.5), 5.0, "B", 35.0)
    c02_appel(vc, (Y1 - wb / 2.0 - 1.0, zb(Y1 - wb / 2.0 - 1.0) - 1.0), 5.0, "C", -30.0)

    # ------------------------------------------------ detail B : rebord du dessus, 4:1
    KD = 4.0
    XB, XCD, YD = 286.0, 364.0, 132.0
    s.text(XB, YD, "DETAIL B  (4:1)", 3.6, "middle", weight="bold")
    s.text(XB, YD + 4.5, "rebords du dessus, 2 ex.", 2.8, "middle")
    s.text(XB, YD + 8.3, "largeur (%s) ; degagement centre sur l angle" % f(w, 2), 2.8, "middle")
    vb = D.View(s, KD, Y1 - 8.0, zt, XB, YD + 30.0)
    yb0, zb0 = Y1 - 15.5, zt - 3.0
    for sg in c02_decoupe(coin, yb0, zb0, Y1 + 1.0, zr + 1.0):
        c02_chemin(vb, [sg])
    vb.rupture((yb0, zt), (yb0, zb0))
    vb.rupture((yb0, zb0), (Y1, zb0))
    vb.cote_vx(zt, zr, None, Y1 - w, 0.0, xl=Y1 - w - 6.0, texte=f(hr))
    c02_rayon_creux(vb, (Y1 - w, zt), p.PLAQ_REBORD_R, -45.0, "R%s" % f(p.PLAQ_REBORD_R),
                    lg=5.0, palier=-5.0)
    vb.rayon((Y1 - r1, zr - r1), r1, 45.0, "R%s" % f(r1), 6)

    # ------------------------------------------------ detail C : rebord du dessous, 4:1
    s.text(XCD, YD, "DETAIL C  (4:1)", 3.6, "middle", weight="bold")
    s.text(XCD, YD + 4.5, "rebords du dessous, 2 ex.", 2.8, "middle")
    s.text(XCD, YD + 8.3, "largeur (%s) en projection ; degagement R%s comme B" % (f(wb, 2), f(p.PLAQ_REBORD_R)), 2.8, "middle")
    yc = Y1 - 6.0
    vd = D.View(s, KD, yc, zb(yc), XCD + 2.0, YD + 32.0)
    yd0 = Y1 - 13.0
    zd1 = zb(Y1) + 3.5
    for sg in c02_decoupe(coin, yd0, zb(Y1) - 8.0, Y1 + 1.0, zd1):
        c02_chemin(vd, [sg])
    vd.rupture((yd0, zb(yd0)), (yd0, zd1))
    vd.rupture((yd0, zd1), (Y1, zd1))
    # hauteur 3 le long de la face interieure (normale a la pente), decalee de
    # 2 mm vers le logement : fleche haute sur le siege, attache basse sur la
    # face du rebord prolongee
    t_ = (-ca_, -sa_)                                 # le long de la pente, vers le logement
    cs_ = (y1b, zb(y1b))
    cb = (y1b + hr * sa_, zb(y1b) - hr * ca_)
    pt_ = (cs_[0] + 2.0 * t_[0], cs_[1] + 2.0 * t_[1])
    pb_ = (cb[0] + 2.0 * t_[0], cb[1] + 2.0 * t_[1])
    qa, qb = vd.P(cb), vd.P(pb_)
    L_ = math.hypot(qb[0] - qa[0], qb[1] - qa[1])
    ux_, uy_ = (qb[0] - qa[0]) / L_, (qb[1] - qa[1]) / L_
    s.line(qa[0] + ux_ * 1.0, qa[1] + uy_ * 1.0, qb[0] + ux_ * 2.0, qb[1] + uy_ * 2.0, D.TRAIT_FIN)
    c02_cote_texte_h(vd, pb_, pt_, f(hr))

    # ======================================================== poussoir 02b
    XP, YP = 80.0, 222.0
    c02_titre(s, XP, 180.0, "%s  PLATEAU DE POUSSOIR, %d empiles  (1:1)" % (rep_p, sp.qty),
              "%s, %d ex., brut %s" % (sp.material, sp.qty, sp.stock))
    vp = D.View(s, 1.0, 0.0, 0.0, XP, YP)
    po, ptrous = P.poussoir_profile()
    rp = [sg[2] for sg in po if sg[0] == 'A'][0]
    Lp2, Bp2 = p.POUSSOIR_L / 2.0, p.POUSSOIR_B / 2.0
    vp.contour(po)
    for h in ptrous:
        vp.contour(h)
    c02_axe(vp, (-Lp2, 0.0), (Lp2, 0.0), 2.5, 2.5)
    c02_axe(vp, (0.0, -ra), (0.0, ra), 3.0, 3.0)
    rg = p.POUSSOIR_GOUPILLE_PASSAGE / 2.0
    for sx in (-1.0, 1.0):
        c02_axe(vp, (sx * p.POUSSOIR_GOUPILLE_X, -Bp2), (sx * p.POUSSOIR_GOUPILLE_X, rg), 0.0, 2.5)
    vp.cote_hx(-p.POUSSOIR_GOUPILLE_X, p.POUSSOIR_GOUPILLE_X, -Bp2, -Bp2, 0.0, zl=-Bp2 - 7.0)
    vp.cote_hx(-Lp2, Lp2, -(Bp2 - rp), -(Bp2 - rp), 0.0, zl=-Bp2 - 14.0)
    vp.cote_vx(-Bp2, Bp2, -(Lp2 - rp), -(Lp2 - rp), 0.0, xl=-Lp2 - 7.0)
    a60 = math.radians(60.0)
    vp.renvoi((ra * math.cos(a60), ra * math.sin(a60)), "alesage %s traversant" % f(p.ALESAGE_D),
              54.0, -14.0, fin="fleche")
    a45 = math.radians(-45.0)
    vp.renvoi((p.POUSSOIR_GOUPILLE_X + rg * math.cos(a45), rg * math.sin(a45)),
              "%d x diam. %s (passage)" % (len(P.poussoir_goupilles()), f(p.POUSSOIR_GOUPILLE_PASSAGE)),
              22.0, 10.0, fin="fleche")
    vp.rayon((Lp2 - rp, Bp2 - rp), rp, 45.0, "4 x R%s" % f(rp), 8)

    return s.save(os.path.join(OUT, "02_coulisseau.svg"))


# Aides de la planche 03 (02/10/2026). Elles n'utilisent que l'interface
# publique de draw.View (cote_hx, cote_vx, renvoi, rupture, rayon) et ne
# changent rien aux autres planches.

T03_MIXTE2 = "8 1.2 1 1.2 1 1.2"   # trait mixte fin a deux tirets : piece voisine (ISO 128, 05.1)
T03_TOL_TENON = 0.1                 # +/- sur la hauteur des tenons (decoupe laser fine) : avec la
#                                     mortaise a la tolerance generale, le jeu reste positif


def t03_ligne(v, p0, p1, w=D.TRAIT_FIN, dash=None):
    """Segment ouvert de p0 a p1 (modele)."""
    a, b = v.P(p0), v.P(p1)
    v.s.line(a[0], a[1], b[0], b[1], w, dash)


def t03_axe(v, p0, p1, e0=2.0, e1=2.0):
    """Trait d'axe de p0 a p1 (modele), prolonge de e0 / e1 mm de feuille."""
    a, b = v.P(p0), v.P(p1)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    if L < 1e-6:
        return
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    v.s.line(a[0] - ux * e0, a[1] - uy * e0, b[0] + ux * e1, b[1] + uy * e1,
             D.TRAIT_AXE, "6 1.5 1 1.5")


def t03_chemin(v, segs, w=D.TRAIT_FORT, dash=None):
    """Trace OUVERT d'une suite de segments (View.contour la ferme)."""
    d = v.d_of(segs)
    if d.endswith(" Z"):
        d = d[:-2]
    v.s.path(d, w, dash)


def t03_decoupe(segs, x0, z0, x1, z1):
    """Segments d'un contour restreints au rectangle (x0, z0)-(x1, z1) : les
    droites sont coupees au bord, les arcs gardes s'ils sont entierement
    dedans (vue de detail)."""
    out = []
    for sg in segs:
        a, b = G.seg_start(sg), G.seg_end(sg)
        if sg[0] == 'A':
            if all(x0 <= q[0] <= x1 and z0 <= q[1] <= z1 for q in (a, b)):
                out.append(sg)
            continue
        dx, dz = b[0] - a[0], b[1] - a[1]
        t0, t1 = 0.0, 1.0
        dehors = False
        for pp, qq in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dz, a[1] - z0), (dz, z1 - a[1])):
            if abs(pp) < 1e-12:
                if qq < 0:
                    dehors = True
                continue
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
        if not dehors and t1 - t0 > 1e-9:
            out.append(('L', (a[0] + dx * t0, a[1] + dz * t0), (a[0] + dx * t1, a[1] + dz * t1)))
    return out


def t03_appel(v, c, r, lettre, ang, dl=3.5):
    """Appel de detail (ISO 128) : cercle fin de rayon r (mm de feuille) autour
    du point c (modele), lettre a l'exterieur vers ang (degres feuille)."""
    cs = v.P(c)
    v.s._p('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="none" stroke="#000" stroke-width="%.3f"/>'
           % (cs[0], cs[1], r, D.TRAIT_FIN))
    a = math.radians(ang)
    v.s.text(cs[0] + (r + dl) * math.cos(a), cs[1] - (r + dl) * math.sin(a) + 1.3, lettre, 3.6,
             "middle", weight="bold")


def t03_rayon_trou(v, c, r, a_deg, texte, lg=8.0):
    """Rayon d'un angle de TROU (centre dans le vide) : fleche posee de
    l'exterieur sur l'arc, pointe vers le centre, ligne de repere radiale
    dans la matiere, texte au bout. A 2:1, un R2 ne loge pas la fleche."""
    a = math.radians(a_deg)
    q = v.P((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    ux, uy = math.cos(a), -math.sin(a)                  # vers l'exterieur, sur la feuille
    e = (q[0] + ux * lg, q[1] + uy * lg)
    v.s.line(q[0], q[1], e[0], e[1], D.TRAIT_FIN)
    v._fleche(q, ux, uy)
    an = "start" if ux >= 0 else "end"
    v.s.text(e[0] + (1.0 if ux >= 0 else -1.0), e[1] - 1.0, texte, D.H_TEXTE, an)


def t03_titre(s, x, y, titre, sous=None):
    """Titre de vue en gras, une ligne d'explication dessous."""
    s.text(x, y, titre, 3.6, "middle", weight="bold")
    if sous:
        s.text(x, y + 4.6, sous, 2.8, "middle")


def plan_traverse():
    import nomenclature as N            # les reperes de NOMENCLATURE.md font foi
    SP = dict((q.name, q) for q in P.all_parts())
    R = N.REPERES
    st = SP["traverse"]
    f = D.fmt
    vis = [t[0] for t in N.visserie()
           if "M10 x %g" % p.TRAVERSE_TIRANT_L in t[1] and "ige" in t[1]]
    vis = vis[0] if vis else "V?"

    # ---------------------------------------------------------------- valeurs
    outer, trous = P.traverse_profile()                 # piece FINIE (le DXF est le brut)
    ra = min(sg[2] for sg in outer if sg[0] == 'A')     # angles du contour, lus sur le contour
    yb = p.ECART_FLANCS / 2.0 - p.TRAVERSE_JEU_Y / 2.0  # epaulement, comme parts.traverse_profile
    yt = p.Y_FLANC_EXT + p.TRAVERSE_TAB_DEP             # bout de tenon
    z0, z1 = p.Z_TRAVERSE_BAS, p.Z_TRAVERSE_HAUT
    ta, tb = p.Z_TAB0, p.Z_TAB1
    zh, rh = p.TRAVERSE_TIRANT_Z, p.TRAVERSE_TIRANT_D / 2.0
    rp = p.TRAVERSE_R_PIED
    lx, ly, entraxe = p.appui_tenon()
    sig_t, hn = p.flexion_tenon()
    sig_p, _ = p.flexion_traverse()
    p_haut, _ = p.pressions_plaquettes()
    n_joints = int(round((p.PLAQ_B - p.portee_coin()) / (2.0 * p.CHANFREIN)))

    notes = [
        "Matiere : %s ; chant fraise frottant sur le bronze-graphite : admis a %s MPa et a cette vitesse."
        % (p.EXIGENCE_TOLE_COURANTE, f(p.pressions_plaquettes()[0])),
        "Decoupe laser d apres %s.dxf (calque DECOUPE) : le DXF est le BRUT, chant du bas descendu"
        " de %s (%s de haut au lieu de %s)."
        % (st.name, f(p.TRAVERSE_SUREP), f(p.TRAVERSE_H + p.TRAVERSE_SUREP), f(p.TRAVERSE_H)),
        "CHANT DU BAS FRAISE EN PAQUET : les %d plaques serrees sur le tirant %s, paquet retourne et"
        " pose sur les faces HAUTES des" % (st.qty, vis),
        "%d tenons (2 cales de plus de %s sous les tenons, la coiffe passe entre), fraise a %s de ces"
        " faces." % (2 * st.qty, f(p.TRAVERSE_COIFFE), f(tb - z0)),
        "Chant fraise : planeite 0,05 sur le paquet, Ra 1,6 ; c est le plan de glissement de la plaque"
        " de bronze %s, sans rectification." % R["plaquette_haute"],
        "Aretes cassees %s x 45 deg sur les deux faces APRES le fraisage (rainure en V de %s a chaque"
        " joint, reserve de graisse)," % (f(p.CHANFREIN), f(2.0 * p.CHANFREIN)),
        "puis paquet resserre sur %s, chants fraises poses sur un marbre." % vis,
        "Angles du contour non cotes : R%s ; pieds de tenon : detail A." % f(ra),
        "Les tenons portent par leur face HAUTE sur l arete superieure de la mortaise du flanc : pas de"
        " vis de traverse.",
    ]
    s = D.Sheet("TRAVERSE  -  PLAQUES A TENONS", R["traverse"], st.material, st.stock,
                "%d plaques identiques" % st.qty, "2:1  -  detail 10:1", notes=notes)
    s.cartouche()

    # ======================================================== plaque, 2:1
    k = 2.0
    XV, YV = 115.0, 114.0
    t03_titre(s, XV, 20.0, "%s  PLAQUE DE TRAVERSE, VUE SELON X  (2:1)" % R["traverse"],
              "ep. %s, %d plaques identiques serrees en paquet" % (f(p.TRAVERSE_EP), st.qty))
    v = D.View(s, k, 0.0, (z0 + z1) / 2.0, XV, YV)
    v.contour(outer)
    for h in trous:
        v.contour(h)
    t03_axe(v, (0.0, z0), (0.0, z1), 3.0, 3.0)
    # axe du trou, prolonge a gauche jusqu'a la ligne de cote du 19
    x19 = -(yb + yt) / 2.0
    t03_axe(v, (-rh, zh), (rh, zh), (-rh - x19) * k + 2.0, 3.0)

    # selon y, au-dessus : epaulements, puis bouts de tenon
    v.cote_hx(-yb, yb, z1, z1, 0.0, zl=z1 + 4.0)
    v.cote_hx(-yt, yt, tb, tb, 0.0, zl=z1 + 8.0)
    # coiffe, dans le creux au-dessus du tenon droit
    v.cote_vx(tb, z1, None, yb, 0.0, xl=(yb + yt) / 2.0)
    # selon z, a droite : chaine (38) + 20 alignee, puis 58 du chant aux faces portantes
    v.cote_vx(z0, ta, None, yt, 0.0, xl=yt + 4.0, texte="(%s)" % f(ta - z0))
    v.cote_vx(ta, tb, None, None, 0.0, xl=yt + 4.0,
              texte="%s +/-%s" % (f(tb - ta), f(T03_TOL_TENON)))
    v.cote_vx(z0, tb, yb, yt, 0.0, xl=yt + 8.0)
    # trou du tirant, a gauche
    v.cote_vx(z0, zh, -yb, None, 0.0, xl=x19)
    a240 = math.radians(240.0)
    q = (rh * math.cos(a240), zh + rh * math.sin(a240))
    dh = (q[1] - z0) * k + 10.0                  # descend 10 mm sous le chant
    v.renvoi(q, "diam. %s : passage du tirant %s" % (f(2.0 * rh), vis),
             -dh * math.tan(math.radians(30.0)), dh, fin="fleche")
    v.renvoi((14.0, z0), "chant FRAISE EN PAQUET : plan de glissement", 10.0, 10.0, fin="fleche")
    t03_appel(v, (yb, ta), 5.0, "A", -40.0)

    # ======================================================== mortaise du flanc, 2:1
    mort = P.flanc_mortaise()
    mx0, mz0, mx1, mz1 = G.bbox(mort)
    rm = min(sg[2] for sg in mort if sg[0] == 'A')
    XM, YM = 318.0, 66.0
    t03_titre(s, XM, 20.0, "MORTAISE DU FLANC (rep. %s) ET PAQUET DE TENONS, VUE SELON Y  (2:1)"
              % R["flanc"],
              "vue de reference : la mortaise est definie planche %s (tableau DECOUPES INTERIEURES)"
              % R["flanc"])
    v2 = D.View(s, k, 0.0, (mz0 + mz1) / 2.0, XM, YM)
    v2.contour(mort)
    lxr = p.TRAVERSE_LX_REEL
    for i in range(p.TRAVERSE_N + 1):
        x = -lxr / 2.0 + i * p.EP_TOLE_REELLE_S355
        t03_ligne(v2, (x, ta), (x, tb), D.TRAIT_FIN, T03_MIXTE2)
    t03_axe(v2, (0.0, mz1), (0.0, mz1 + 2.0), 0.0, 0.0)
    t03_axe(v2, (0.0, mz0), (0.0, mz0 - 1.5), 0.0, 0.0)
    # attaches aux angles vifs fictifs, comme sur la plaque : elles ne se croisent pas
    v2.cote_hx(mx0, mx1, mz0, mz0, 0.0, zl=mz0 - 4.0, texte="(%s)" % f(mx1 - mx0), dt=14.0)
    v2.cote_vx(mz0, mz1, mx1, mx1, 0.0, xl=mx1 + 4.0, texte="(%s)" % f(mz1 - mz0))
    t03_rayon_trou(v2, (mx0 + rm, mz1 - rm), rm, 135.0, "(4 x R%s)" % f(rm), 8.0)
    v2.renvoi((lxr / 2.0 - 1.5 * p.EP_TOLE_REELLE_S355, ta + 6.0),
              "%d tenons jointifs :" % p.TRAVERSE_N + chr(10) + "%d x tole reelle" % p.TRAVERSE_N,
              6.0, -40.0, fin="point")
    s.text(XM, 104.0, "Largeur = %d x tole S355 REELLE + 2 x R%s (EP_TOLE_REELLE_S355, MESUREE) : l arete droite porte"
           " sur toute la largeur du paquet." % (p.TRAVERSE_N, f(rm)), 2.8, "middle")

    # ======================================================== detail A, 10:1
    KD = 10.0
    XA, YA = 300.0, 160.0
    t03_titre(s, 325.0, 124.0, "DETAIL A  (10:1)",
              "pied de tenon, 4 par plaque (ici en bas a droite)")
    vA = D.View(s, KD, yb, ta, XA, YA)
    wy0, wy1, wz0, wz1 = yb - 2.5, yb + 3.5, ta - 3.5, ta + 2.5
    for sg in t03_decoupe(outer, wy0, wz0, wy1, wz1):
        t03_chemin(vA, [sg])
    vA.rupture((wy0, wz1), (wy1, wz1))
    vA.rupture((wy0, wz0), (wy0, wz1))
    vA.rupture((wy0, wz0), (yb, wz0))
    vA.rupture((wy1, ta), (wy1, wz1))
    # angle vif fictif : aretes prolongees en trait fin
    t03_ligne(vA, (yb, ta - rp), (yb, ta))
    t03_ligne(vA, (yb + rp, ta), (yb, ta))
    vA.cote_hx(yb, yb + rp, None, ta, 0.0, zl=ta - 2.5)
    for i, t in enumerate(["poche carree tournee a 45 deg,",
                           "centree sur l angle vif fictif :",
                           "3 traits droits, jamais un conge",
                           "(il deborderait de l epaulement)"]):
        s.text(XA + 40.0, YA - 6.0 + 4.0 * i, t, 2.8, "start")

    # ======================================================== calcul et montage
    calc = [
        "Sous %s kN (verification de dimensionnement) :" % f(p.CHARGE_DIM / 1000.0),
        "- matage du tenon sur l arete de mortaise : %s MPa sur %s x %s par flanc (aretes cassees et"
        " degagement deduits) ;" % (f(p.matage_tenon()), f(lx), f(ly)),
        "- racine de tenon : %s MPa sur %s nets ; plaque (%s de haut, percee de %s, appuis a %s) : %s MPa, majorant ;"
        % (f(sig_t), f(hn), f(p.TRAVERSE_H), f(2.0 * rh), f(entraxe), f(sig_p)),
        "- bronze %s : %s MPa sur %s nets (%d joints dans ses %s) ; Re du %s a 150 C : %s MPa."
        % (R["plaquette_haute"], f(p_haut), f(p.portee_coin()), n_joints, f(p.PLAQ_B),
           p.NUANCE_TOLE_COURANTE, f(p.RE_TOLE_COURANTE_CHAUD)),
        "MONTAGE : serrer le paquet sur %s, engager les tenons dans un flanc, chants fraises du cote"
        " du coin, puis presenter le second flanc." % vis,
    ]
    for i, t in enumerate(calc):
        s.text(16.0, 258.0 + 4.6 * i, t, 2.8, "start")
    return s.save(os.path.join(OUT, "03_traverse.svg"))


# ============================================================ pieces collees

# Aides de la planche 04 (02/10/2026). Elles n'utilisent que l'interface
# publique de draw.View (cote_hx, cote_vx, renvoi, rayon, zone, trace_coupe)
# et de draw.Sheet (motif) ; elles ne changent rien aux autres planches.

def p04_ligne(v, p0, p1, w=D.TRAIT_FIN, dash=None):
    """Segment ouvert de p0 a p1 (modele)."""
    a, b = v.P(p0), v.P(p1)
    v.s.line(a[0], a[1], b[0], b[1], w, dash)


def p04_poly(pts):
    """Contour ferme (segments 'L') par ses sommets, en coordonnees modele."""
    return [('L', pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def p04_titre(s, x, y, titre, sous=None):
    """Titre de vue en gras, une ligne d'explication dessous."""
    s.text(x, y, titre, 3.6, "middle", weight="bold")
    if sous:
        s.text(x, y + 4.6, sous, 2.8, "middle")


def plan_patins():
    import nomenclature as N            # les reperes de NOMENCLATURE.md font foi
    SP = dict((q.name, q) for q in P.all_parts())
    R = N.REPERES
    E = N.ETAPE
    f = D.fmt
    sa, sc, sp = SP["patin_appui"], SP["patin_charge"], SP["plat_renfort"]
    goup = [t[0] for t in N.visserie() if "oupille" in t[1]]
    goup = goup[0] if goup else "V?"

    # ---------------------------------------------------------------- valeurs
    la, ba, ea, ra = p.PATIN_L, p.PATIN_B, p.PATIN_E, p.PATIN_R
    rb, rp = p.RAINURE_B, p.RAINURE_P
    lc, bc, rc = p.PATIN_CHARGE_L, p.PATIN_CHARGE_B, p.PATIN_CHARGE_R
    gx, gd = p.POUSSOIR_GOUPILLE_X, p.POUSSOIR_GOUPILLE_D

    def ex(spec):
        return "%s, %d ex." % (spec.material, spec.qty)

    matieres, bruts = [], []
    for q in (sa, sc, sp):
        if q.material not in matieres:
            matieres.append(q.material)
    for q in (sa, sc):                  # deux epaisseurs de patin un jour : les deux bruts
        if q.stock not in bruts:
            bruts.append(q.stock)
    bruts.append("feuillard %s x %s" % (f(p.PLAT_B), f(p.PLAT_E)))

    notes = [
        "Aretes vives des patins cassees %s x 45 deg ; plat ebavure." % f(sa.chanfrein),
        "%s : decoupe laser d apres %s.dxf (calque DECOUPE), PUIS rainure fraisee sur toute la"
        " longueur de la face d appui." % (R["patin_appui"], sa.name),
        "%s : rainure %s = tole REELLE du flanc (EP_TOLE_REELLE_42 = %s) + 2 x %s de jeu : mesurer la"
        " tole 42CrMo4 livree et regenerer ce plan." % (R["patin_appui"], P.fr(rb, 2), P.fr(p.EP_TOLE_REELLE_42, 2),
                                               P.fr(p.RAINURE_JEU, 2)),
        "%s : le fond de rainure porte le bossage, %s kN par patin (4 contacts, 2 par appui) : Hertz %s MPa, limite %s MPa a"
        " 150 C, coefficient %s : %s au minimum."
        % (R["patin_appui"], f(p.CHARGE_DIM / 4000.0), f(p.hertz_appui(), 0), f(p.HERTZ_LIM, 0),
           f(p.hertz_coef(), 2), sa.material),
        "%s : decoupe d apres %s.dxf, avant-trous %s ; PERCER puis ALESER les 2 trous %s H7, ou les"
        " goupilles %s (%s m6) sont serrees." % (R["patin_charge"], sc.name,
                                                f(p.PATIN_CHARGE_AVANT_TROU), f(gd), goup, f(gd)),
        "Collage (NOMENCLATURE.md, ordre de montage) : %s etape %d, %s etape %d, %s etape %d ;"
        " polymeriser sous la precharge (etape %d)."
        % (R["plat_renfort"], E["eprouvette"], R["patin_charge"], E["tete"], R["patin_appui"],
           E["patins"], E["precharge"]),
        "%s : colle par sa face superieure seulement, contre le plat ; rainure SECHE sur le"
        " bossage, qui doit y basculer." % R["patin_appui"],
        "Surfaces a coller : poncer P80 et degraisser a l acetone. Colle Duralco 4420, post-cuisson"
        " selon la notice avant charge.",
        "Un jeu neuf par eprouvette : %d x %s, %d x %s et ses 2 goupilles %s, %d x %s ; il part avec"
        " la poutrelle." % (sa.qty, R["patin_appui"], sc.qty, R["patin_charge"], goup, sp.qty,
                            R["plat_renfort"]),
    ]
    s = D.Sheet("PATINS ET PLATS COLLES", R["patin_appui"][:2], " / ".join(matieres),
                " / ".join(bruts),
                "%d + %d + %d (%s, %s, %s)" % (sa.qty, sc.qty, sp.qty, R["patin_appui"],
                                               R["patin_charge"], R["plat_renfort"]),
                "1:1 - coupe 5:1 - %s 1:5" % R["plat_renfort"], notes=notes)
    s.cartouche()

    # ======================================================== 04a, vue de dessous 1:1
    XA, YA = 100.0, 47.0
    p04_titre(s, XA, 20.0, "%s  PATIN D APPUI RAINURE, VUE DE DESSOUS  (1:1)" % R["patin_appui"],
              "%s, brut %s" % (ex(sa), sa.stock))
    v = D.View(s, 1.0, 0.0, 0.0, XA, YA)
    v.contour(P.patin_appui_profile()[0])
    for sy in (-1.0, 1.0):                      # rainure, debouchante aux deux bouts
        p04_ligne(v, (-la / 2.0, sy * rb / 2.0), (la / 2.0, sy * rb / 2.0), D.TRAIT_FORT)
    v.axe((-la / 2.0, 0.0), (la / 2.0, 0.0))
    # attaches aux angles vifs fictifs : celles de deux cotes voisines ne se croisent pas
    v.cote_hx(-la / 2.0, la / 2.0, -ba / 2.0, -ba / 2.0, 0.0, zl=-ba / 2.0 - 14.0)
    v.cote_vx(-ba / 2.0, ba / 2.0, -la / 2.0, -la / 2.0, 0.0, xl=-la / 2.0 - 10.0)
    v.rayon((la / 2.0 - ra, ba / 2.0 - ra), ra, 45.0, "4 x R%s" % f(ra), 8.0)
    v.trace_coupe((la / 2.0 - 20.0, ba / 2.0 + 6.0), (la / 2.0 - 20.0, -ba / 2.0 - 6.0), "A",
                  (-1.0, 0.0))

    # ======================================================== 04a, coupe A-A 5:1
    k2 = 5.0
    XC, YC = 100.0, 119.0
    p04_titre(s, XC, 82.0, "COUPE A-A  (5:1)", "face collee en haut, rainure cote bossage")
    v2 = D.View(s, k2, 0.0, ea / 2.0, XC, YC)
    sec = p04_poly([(-ba / 2.0, 0.0), (-rb / 2.0, 0.0), (-rb / 2.0, rp), (rb / 2.0, rp),
                    (rb / 2.0, 0.0), (ba / 2.0, 0.0), (ba / 2.0, ea), (-ba / 2.0, ea)])
    # profondeur : cote dans le vide de la rainure, contre le flanc gauche ;
    # fleches dehors, la queue haute entre dans la matiere : hachures interrompues
    q15 = 4.0
    x15 = -rb / 2.0 + 7.0 / k2
    jour = p04_poly([(x15 - 1.0 / k2, rp), (x15 + 1.0 / k2, rp),
                     (x15 + 1.0 / k2, rp + (q15 + 1.0) / k2), (x15 - 1.0 / k2, rp + (q15 + 1.0) / k2)])
    s.motif("p04_h", 45.0, 2.0)
    v2.zone([sec, jour], "p04_h", w=0)
    v2.contour(sec)
    v2.axe((0.0, 0.0), (0.0, ea))
    v2.cote_vx(0.0, rp, -rb / 2.0, None, 0.0, xl=x15, queue=q15)
    v2.cote_hx(-rb / 2.0, rb / 2.0, 0.0, 0.0, -12.0, texte=P.fr(rb, 2))   # 9,75 pour une tole de 8,25
    v2.cote_vx(0.0, ea, ba / 2.0, ba / 2.0, 10.0)

    # ======================================================== 04b, patin de charge 1:1
    XB, YB = 285.0, 92.0
    p04_titre(s, XB, 20.0, "%s  PATIN DE CHARGE, epaisseur %s  (1:1)"
              % (R["patin_charge"], f(p.PATIN_CHARGE_E)),
              "%s, brut %s" % (ex(sc), sc.stock))
    v3 = D.View(s, 1.0, 0.0, 0.0, XB, YB)
    oc, trous = P.patin_charge_profile()        # piece FINIE : trous 8 H7 (le DXF a les avant-trous)
    v3.contour(oc)
    for t in trous:
        v3.contour(t)
    v3.axe((-lc / 2.0, 0.0), (lc / 2.0, 0.0))
    v3.axe((0.0, -bc / 2.0), (0.0, bc / 2.0))
    for sx in (-1.0, 1.0):
        # axe prolonge au-dela de la ligne de cote : il porte l'entraxe, sans
        # attache en trait continu a travers la matiere
        v3.axe((sx * gx, -gd / 2.0 - 2.0), (sx * gx, bc / 2.0 + 12.0), ext=0.0)
    v3.cote_hx(-gx, gx, None, None, 0.0, zl=bc / 2.0 + 10.0)
    v3.cote_hx(-lc / 2.0, lc / 2.0, -bc / 2.0, -bc / 2.0, 0.0, zl=-bc / 2.0 - 10.0)
    v3.cote_vx(-bc / 2.0, bc / 2.0, -lc / 2.0, -lc / 2.0, 0.0, xl=-lc / 2.0 - 10.0)
    v3.rayon((lc / 2.0 - rc, bc / 2.0 - rc), rc, 45.0, "4 x R%s" % f(rc), 8.0)
    a45 = math.radians(45.0)
    v3.renvoi((gx + gd / 2.0 * math.cos(a45), gd / 2.0 * math.sin(a45)),
              "2 x diam. %s H7" % f(gd) + chr(10) + "perces-aleses", 20.0, -20.0, fin="fleche")

    # ======================================================== 04c, plat 1:5
    k4 = 0.2
    XP, YP = 115.0, 187.0
    p04_titre(s, XP, 172.0, "%s  PLAT DE RENFORT  (1:5)" % R["plat_renfort"],
              "%s, piece du commerce : feuillard %s x %s coupe a longueur, angles vifs ; pas de DXF"
              % (ex(sp), f(p.PLAT_B), f(p.PLAT_E)))
    v4 = D.View(s, k4, 0.0, 0.0, XP, YP)
    v4.contour(P.plat_profile()[0])
    v4.cote_hx(-p.PLAT_L / 2.0, p.PLAT_L / 2.0, -p.PLAT_B / 2.0, -p.PLAT_B / 2.0, 0.0,
               zl=-p.PLAT_B / 2.0 - 12.0 / k4)
    bord = p.POUTRE_B / 2.0 - p.Y_FLANC - p.PLAT_B / 2.0
    for i, t in enumerate([
            "colles sous la poutrelle, un dans l axe de chaque flanc : entraxe %s, centres sur"
            " la poutrelle," % f(2.0 * p.Y_FLANC),
            "bord exterieur a %s du bord de la poutrelle (planche 00, coupe A-A)" % f(bord)]):
        s.text(XP, 209.0 + 4.4 * i, t, 2.8, "middle")
    return s.save(os.path.join(OUT, "04_patins.svg"))


# ============================================================ pied

# Aides de la planche 05 (02/10/2026). Elles n'utilisent que l'interface
# publique de draw.View (P, d_of, axe, cote_hx, cote_vx, bulle, rayon, rupture)
# et de draw.Sheet ; elles ne changent rien aux autres planches.

def p05_titre(s, x, y, titre, sous=()):
    """Titre de vue en gras, des lignes d'explication dessous."""
    s.text(x, y, titre, 3.6, "middle", weight="bold")
    for i, t in enumerate(sous):
        s.text(x, y + 4.6 + 4.0 * i, t, 2.8, "middle")


def p05_rogne(sg, y0, z0, y1, z1):
    """Segment vu dans la fenetre [y0, y1] x [z0, z1] : un 'L' coupe aux bords
    (Liang-Barsky), un arc garde entier s'il y est tout entier, None sinon."""
    e = 1e-6
    y0, z0, y1, z1 = y0 - e, z0 - e, y1 + e, z1 + e
    if sg[0] != 'L':
        ok = all(y0 <= q[0] <= y1 and z0 <= q[1] <= z1 for q in G.sample(sg, 8))
        return sg if ok else None
    (ya, za), (yb, zb) = sg[1], sg[2]
    dy, dz = yb - ya, zb - za
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dy, ya - y0), (dy, y1 - ya), (-dz, za - z0), (dz, z1 - za)):
        if abs(pp) < 1e-12:
            if qq < 0.0:
                return None
            continue
        t = qq / pp
        if pp < 0.0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
    if t1 - t0 < 1e-9:
        return None
    return ('L', (ya + t0 * dy, za + t0 * dz), (ya + t1 * dy, za + t1 * dz))


def p05_morceaux(segs, fen):
    """Morceaux d'un contour ferme vus dans la fenetre fen = (y0, z0, y1, z1) :
    listes de segments contigus, a tracer sans fermeture."""
    out = []
    for sg in segs:
        r = p05_rogne(sg, *fen)
        if r is None:
            continue
        if out and G.norm(G.sub(G.seg_end(out[-1][-1]), G.seg_start(r))) < 1e-6:
            out[-1].append(r)
        else:
            out.append([r])
    # contour ferme : le dernier morceau peut se raccorder au premier
    if len(out) > 1 and G.norm(G.sub(G.seg_end(out[-1][-1]), G.seg_start(out[0][0]))) < 1e-6:
        out[0] = out.pop() + out[0]
    return out


def p05_detail(v, segs, fen, ruptures, w=D.TRAIT_FORT):
    """Vue de detail : le contour rogne a la fenetre, trace OUVERT (View.d_of
    sans son 'Z'), et les traits de rupture fins la ou la matiere est coupee."""
    for ch in p05_morceaux(segs, fen):
        d = v.d_of(ch)
        v.s.path(d[:d.rindex(" Z")], w)
    for a, b in ruptures:
        v.rupture(a, b)


def p05_arc(segs, q):
    """(centre, rayon) de l'arc du contour dont le centre est le plus pres de q :
    les conges qui n'ont pas de parametre sont lus sur le profil lui-meme."""
    a = min((sg for sg in segs if sg[0] != 'L'), key=lambda sg: G.norm(G.sub(sg[1], q)))
    return a[1], a[2]


def plan_pied():
    import nomenclature as N            # les reperes de NOMENCLATURE.md font foi
    SP = dict((q.name, q) for q in P.all_parts())
    sp, sc = SP["pied"], SP["crochet"]
    rp, rc = N.REPERES["pied"], N.REPERES["crochet"]
    f, fr = D.fmt, P.fr

    # ---------------------------------------------------------------- valeurs
    outer, ajours = P.pied_profile()
    co, _ = P.crochet_profile()
    y2, h = p.PIED_Y / 2.0, p.PIED_H
    hb, bb = p.PIED_BOSSAGE_H, p.PIED_BOSSAGE_B
    fb, fw, fh = p.PIED_FENTE_BORD, p.PIED_FENTE_B, p.PIED_FENTE_H
    yf, w2 = p.Y_FLANC, p.ENCOCHE_PIED_B / 2.0
    wn = p.EP_TOLE_REELLE_42 / 2.0 - p.PIED_NODE_SERRE    # demi-passage au node : recoit le flanc
    zb = h - p.PIED_CROIX                                   # fond d encoche
    zn1 = zb + (p.PIED_CROIX - p.PIED_NODE_L) / 2.0         # bas du node
    zn2 = zn1 + p.PIED_NODE_L                               # haut du node
    S, H, za, lz = p.CROCHET_S, p.CROCHET_H, p.CROCHET_Z_APPUI, p.CROCHET_LANGUE_Z
    lh, ll, bec, becl = p.CROCHET_LANGUE_H, p.CROCHET_LANGUE_L, p.CROCHET_BEC, p.CROCHET_BEC_L
    yd, db = p.CROCHET_DENT_Y, p.CROCHET_DENT_B / 2.0
    pente = math.tan(math.radians(p.PIED_DEBOUT_ANGLE))
    hd_paroi = p.CROCHET_DENT_H + db * pente     # arete de la dent cote paroi (la plus haute)
    hd_int = p.CROCHET_DENT_H - db * pente       # arete cote interieur
    # conges sans parametre, lus sur les profils
    c6, r6 = p05_arc(outer, (y2, h))                         # angles du chant haut
    c2, r2 = p05_arc(outer, (-y2, 0.0))                      # bout : arete de pose (PIED_COIN_R)
    r_bos = p05_arc(outer, (-y2 + bb, 0.0))[1]               # raccords du bossage
    r_fen = p05_arc(outer, (-y2 + fb, fh))[1]                # fente de calage
    r_ent = p05_arc(outer, (yf + w2, h))[1]                  # entree d encoche
    r_aj = p.PIED_AJOUR_R
    r_cr = p05_arc(co, (S, -H))[1]                           # corps et appui du crochet
    r_lg = p05_arc(co, (-ll, lz[0]))[1]                      # langues
    r_gr = p05_arc(co, (-ll + becl, lz[0] - lh))[1]          # fond de gorge
    r_dt = p05_arc(co, (yd - db, za + hd_paroi))[1]          # haut de la dent
    a_deb = f(p.PIED_DEBOUT_ANGLE, 0)
    confirmer = "confirmees" if p.ETUVE_CONFIRMEE else "A CONFIRMER"

    notes = [
        "Decoupe laser d apres %s.dxf et %s.dxf (calque DECOUPE) ; aretes cassees %s x 45 deg sur les"
        " deux faces." % (sp.name, sc.name, fr(sp.chanfrein, 2)),
        "Matiere : %s." % p.EXIGENCE_TOLE_COURANTE,
        "%s : encoches %s = e + %s et passage aux nodes %s = e - 2 x %s (serrage), e = tole REELLE du flanc"
        " 42CrMo4 (EP_TOLE_REELLE_42 = %s) ;"
        % (rp, fr(p.ENCOCHE_PIED_B, 2), fr(p.PIED_JEU, 2), fr(2.0 * wn, 2), fr(p.PIED_NODE_SERRE, 2),
           fr(p.EP_TOLE_REELLE_42, 2)),
        "%s : fentes de calage %s = e' + 2 x %s, e' = tole REELLE du crochet S355 (EP_TOLE_REELLE_S355 = %s)."
        % (rp, fr(fw, 2), fr(p.PIED_FENTE_JEU, 2), fr(p.EP_TOLE_REELLE_S355, 2)),
        p.NOTE_TOLE_REELLE[0].upper() + p.NOTE_TOLE_REELLE[1:] + ".",
        "%s : 2 sous le chant bas des flancs (couche), 2 en V aux coins de l about a %s deg (debout),"
        " aretes de pose a %s." % (rp, a_deb, f(p.pied_debout_base(), 0)),
        "%s : l encoche (%s) porte fond sur fond dans celle du flanc (%s, planche 01, detail W) ;"
        " plan de pose a %s sous le chant du flanc." % (rp, f(p.PIED_CROIX), f(p.PIED_CROIX_FLANC),
                                                       f(p.PIED_SOL)),
        "%s : fentes de calage a +/- %s de l axe (entraxe %s) : crochets a %s des parois laterales,"
        " colonnes de trous %s." % (rp, fr(p.PIED_FENTE_Y, 2), fr(2.0 * p.PIED_FENTE_Y, 2),
                                    fr(p.ETUVE_Y / 2.0 - p.PIED_FENTE_Y, 2), confirmer),
        "%s : pend par %d langues a bec dans les trous carres de %s (pas %s) de la paroi de %s, qui passe"
        " dans la gorge ; la dent cale le pied." % (rc, p.CROCHET_N_LANGUES, f(p.ETUVE_TROU),
                                                    " / ".join(f(v) for v in p.ETUVE_TROU_PAS),
                                                    f(p.ETUVE_PAROI_E)),
        "%s : angles du corps et de l appui R%s ; langues R%s, fond de gorge R%s ; haut de la dent R%s."
        % (rc, f(r_cr), f(r_lg), f(r_gr), f(r_dt)),
    ]
    s = D.Sheet("PIED ET CROCHET D'ETUVE", rp,
                " / ".join(sorted(set((sp.material, sc.material)))),
                sp.stock if sp.stock == sc.stock else "%s / %s" % (sp.stock, sc.stock),
                "%d + %d (%s, %s)" % (sp.qty, sc.qty, rp, rc), "1:2 - details 2:1 et 5:1",
                notes=notes)
    s.cartouche()
    if not p.ETUVE_CONFIRMEE:
        # au-dessus des notes, en gras : pied et crochet dependent de l etuve
        y_al = s.h - D.MARGE - 36.0 - 4.0 - 3.8 * len(notes) - 2.0
        s.text(s.w - D.MARGE - 2.0, y_al, "ETUVE %s A CONFIRMER : %s" % (f(p.ETUVE_INTERIEUR), p.ALERTE_ETUVE),
               3.2, "end", weight="bold")

    # ======================================================== 05, pied 1:2
    k1 = 0.5
    v = D.View(s, k1, 0.0, 0.0, 155.0, 69.0)
    p05_titre(s, 155.0, 18.0, "%s  PIED A MI-BOIS  (1:2)" % rp,
              ["%s, %d ex., brut %s" % (sp.material, sp.qty, sp.stock)])
    v.contour(outer)
    for aj in ajours:
        v.contour(aj)
    v.axe((0.0, -4.0), (0.0, h + 8.0), ext=0.0)                # symetrie : origine des y
    z68 = h + 8.0 / k1
    for sy in (-1.0, 1.0):                                     # axes des encoches = attaches du 68
        v.axe((sy * yf, zb - 2.0), (sy * yf, z68 + 2.0 / k1), ext=0.0)
    v.cote_hx(-yf, yf, None, None, 0.0, zl=z68)
    v.cote_hx(-p.PIED_FENTE_Y, p.PIED_FENTE_Y, 0.0, 0.0, -10.0, texte="%s  entraxe des fentes (crochets)" % fr(2.0 * p.PIED_FENTE_Y, 1))
    v.cote_hx(-y2, y2, 0.0, 0.0, -18.0)
    v.cote_vx(0.0, h, y2, y2, 10.0)
    v.rayon(c6, r6, 70.0, "2 x R%s" % f(r6), 7.0)
    v.bulle((-y2, 10.0), "A", -9.0, -4.0, fin="fleche")
    v.bulle((yf + w2 + 3.0, h), "B", 10.0, -8.0, fin="fleche")

    # ajours : tableau, origine sur l axe du pied et le plan de pose
    lig = []
    for aj in sorted(ajours, key=lambda c: G.bbox(c)[0]):
        b = G.bbox(aj)
        if b[2] < 0.0:
            continue                                           # le symetrique est sur la ligne +/-
        if b[0] < 0.0:
            lig.append(["central", "1", fr(b[0], 2), fr(b[2], 2), fr(b[1], 2), fr(b[3], 2)])
        else:
            lig.append(["exterieurs", "2", "+/-" + fr(b[0], 2), "+/-" + fr(b[2], 2), fr(b[1], 2),
                        fr(b[3], 2)])
    yt = D.table(s, 20.0, 196.0, "AJOURS DU PIED %s (angles R%s)" % (rp, f(r_aj)),
                 ["ajour", "nb", "y de", "y a", "z de", "z a"], lig, [24, 10, 18, 18, 14, 14])
    s.text(20.0, yt + 4.6, "y depuis l axe du pied, z depuis le plan de pose (dessous des bossages)",
           2.8, "start")

    # ======================================================== detail A : bout du pied, 2:1
    kA = 2.0
    vA = D.View(s, kA, -y2, 0.0, 40.0, 152.0)
    yA1, zA1 = -y2 + bb + 10.0, hb + 5.0
    p05_titre(s, 90.0, 108.0, "DETAIL A  (2:1)",
              ["bout du pied, 2 ex. symetriques",
               "fente : angles R%s ; bossage : R%s ; R%s du bout = arete de pose"
               % (f(r_fen), f(r_bos), f(r2))])
    p05_detail(vA, outer, (-y2, 0.0, yA1, zA1),
               [((-y2, zA1), (yA1, zA1)), ((yA1, hb), (yA1, zA1))])
    vA.cote_hx(-y2, -y2 + fb, 0.0, 0.0, -10.0)                                   # 5
    vA.cote_hx(-y2 + fb, -y2 + fb + fw, 0.0, 0.0, -10.0, texte=fr(fw, 2))        # 8,4
    vA.cote_hx(-y2, -y2 + bb, 0.0, 0.0, -18.0)                                   # 40
    vA.cote_vx(0.0, fh, -y2 + fb + fw, None, 0.0, xl=-y2 + fb + fw / 2.0)       # 7, dans la fente
    vA.cote_vx(0.0, hb, -y2 + bb, None, 0.0, xl=-y2 + bb + 6.0)                 # 8, sous le creux
    vA.rayon(c2, r2, 200.0, "R%s" % f(r2), 8.0)

    # ======================================================== detail B : encoche, 2:1
    kB = 2.0
    vB = D.View(s, kB, yf, h, 195.0, 130.0)
    yB0, yB1, zB0 = yf - 12.0, yf + 12.0, zb - 5.0
    p05_titre(s, 195.0, 108.0, "DETAIL B  (2:1)", ["encoche, 2 ex. : un node par joue"])
    p05_detail(vB, outer, (yB0, zB0, yB1, h),
               [((yB0, zB0), (yB0, h)), ((yB1, zB0), (yB1, h)), ((yB0, zB0), (yB1, zB0))])
    vB.cote_hx(yf - w2, yf + w2, h, h, 8.0, texte=fr(2.0 * w2, 2))                        # 8,4
    vB.cote_hx(yf - wn, yf + wn, None, None, 0.0, zl=(zn1 + zn2) / 2.0, texte=fr(2.0 * wn, 2))   # 7,8
    vB.cote_vx(zb, h, yf + w2 + p.PIED_R, None, 0.0, xl=yf + w2 + 4.0)                   # 20
    vB.cote_vx(zn2, h, yf - wn, None, 0.0, xl=yf - w2 - 4.0)                             # 6
    vB.cote_vx(zn1, zn2, yf - wn, yf - wn, 0.0, xl=yf - w2 - 4.0)                        # 8
    for i, t in enumerate(["angles du fond : poche carree de %s tournee"
                           " a 45 deg," % fr(p.PIED_R * math.sqrt(2.0), 1),
                           "centree sur l angle vif (3 traits) ; entree R%s" % f(r_ent),
                           "nodes : rampes a 45 deg"]):
        s.text(195.0, 186.0 + 4.0 * i, t, 2.8, "middle")

    # ======================================================== 05c, crochet 1:2
    k5 = 0.5
    v5 = D.View(s, k5, 0.0, 0.0, 347.0, 44.0)
    p05_titre(s, 355.0, 18.0, "%s  CROCHET D ETUVE  (1:2)" % rc,
              ["%s, %d ex. ; y = 0 : face interieure de la paroi" % (sc.material, sc.qty),
               "dent a %s de la paroi : etuve de %s %s" % (fr(yd, 1), f(p.ETUVE_INTERIEUR),
                                                           confirmer.replace("ees", "ee"))])
    v5.contour(co)
    v5.cote_hx(-ll, p.CROCHET_CORPS, 0.0, 0.0, 8.0)                       # 21 hors tout en haut
    xg1 = -ll - 10.0 / k5                                                  # chaine des langues
    for i in range(len(lz) - 1):
        v5.cote_vx(lz[i + 1], lz[i], -ll, -ll, 0.0, xl=xg1)
    v5.cote_vx(-H, 0.0, 0.0, -ll, 0.0, xl=xg1 - 8.0 / k5)                 # 127
    v5.cote_vx(-H, za, S, S, 10.0)                                         # 20, appui
    zg1 = -H - 10.0 / k5
    v5.axe((yd, za + hd_paroi + 2.0), (yd, zg1 - 2.0 / k5), ext=0.0)       # axe de la dent
    v5.cote_hx(0.0, yd, -H, None, 0.0, zl=zg1, texte=fr(yd, 1))           # 48,2 : depend de l etuve
    v5.cote_hx(0.0, S, -H, -H, 0.0, zl=zg1 - 8.0 / k5)                    # 60
    v5.bulle((-ll, lz[-1] - lh + 1.0), "D", -7.0, 7.0, fin="fleche")
    v5.bulle((yd + db, za + hd_int / 2.0), "C", 9.0, -9.0, fin="fleche")

    # ======================================================== detail D : langue, 2:1
    kC = 2.0
    zt = lz[1] if len(lz) > 1 else lz[0]
    vC = D.View(s, kC, 0.0, zt, 370.0, 159.0)
    zC0, zC1, yC0, yC1 = zt - lh - bec - 6.0, zt + 6.0, -ll - 5.0, 6.0
    p05_titre(s, 362.0, 134.0, "DETAIL D  (2:1)", ["langue, %d ex. identiques" % p.CROCHET_N_LANGUES])
    p05_detail(vC, co, (yC0, zC0, yC1, zC1),
               [((0.0, zC1), (yC1, zC1)), ((yC1, zC0), (yC1, zC1)), ((0.0, zC0), (yC1, zC0))])
    vC.cote_hx(-ll, 0.0, zt, None, 0.0, zl=zt + 4.0)                                # 9
    vC.cote_vx(zt - lh - bec, zt, -ll, -ll, -8.0)                                   # 12
    vC.cote_vx(zt - lh - bec, zt - lh, -ll + becl, None, 0.0, xl=-1.3)             # 5, dans la gorge
    vC.cote_hx(-ll + becl, 0.0, zt - lh - bec, None, 0.0, zl=zt - lh - bec - 3.5)  # 4, sous le bec

    # ======================================================== detail C : dent, 5:1
    kD = 5.0
    vD = D.View(s, kD, yd, za, 272.0, 168.0)
    yD0, yD1, zD0 = yd - 6.0, yd + 6.0, za - 2.5
    p05_titre(s, 272.0, 108.0, "DETAIL C  (5:1)",
              ["dent de l appui, haute cote paroi",
               "dessus a %s deg, comme le fond de fente du pied en V" % a_deb])
    p05_detail(vD, co, (yD0, zD0, yD1, za + hd_paroi + 2.0),
               [((yD0, zD0), (yD0, za)), ((yD1, zD0), (yD1, za)), ((yD0, zD0), (yD1, zD0))])
    vD.cote_hx(yd - db, yd + db, za + hd_paroi, za + hd_int, 8.0)                          # 6
    vD.cote_vx(za, za + hd_paroi, None, yd - db, 0.0, xl=yd - db - 1.6, texte=fr(hd_paroi, 2))
    vD.cote_vx(za, za + hd_int, None, yd + db, 0.0, xl=yd + db + 1.6, texte=fr(hd_int, 2))

    return s.save(os.path.join(OUT, "05_pied.svg"))


def plan_petites():
    """Planche 06 : tourillon 06a, entretoise de cadre 06b, plaque de frottement
    06c / 06d (piece du commerce, une seule vue : dessus et dessous identiques).
    Reprise du 02/10/2026 : quantites, matieres, bruts et reperes lus dans les
    PartSpec et nomenclature.REPERES ; cotes ISO (cote_hx / cote_vx : texte a
    gauche des cotes verticales, attaches qui depassent la ligne de cote) ;
    aides locales p06_*, qui ne changent rien aux autres planches."""
    import nomenclature as N            # les reperes de NOMENCLATURE.md font foi
    SP = dict((q.name, q) for q in P.all_parts())
    R = N.REPERES
    f = D.fmt
    st, se, sh = SP["tourillon"], SP["entretoise"], SP["plaquette_haute"]
    sb, sv = SP["plaquette_basse"], SP["entretoise_vis"]
    rA, rB, rC, rD = R["tourillon"], R["entretoise"], R["plaquette_haute"], R["plaquette_basse"]

    # ---------------------------------------------------------------- valeurs
    rT, lT, cT = p.TOURILLON_D / 2.0, p.TOURILLON_L, p.TOURILLON_CHANFREIN
    ajust = p06_ajustement(st.stock)                 # "h9" : le brut de la nomenclature fait foi
    de, di, lE = p.ENTRETOISE_DE, p.ENTRETOISE_DI, p.ENTRETOISE_L
    tube = p.ENTRETOISE_BRUT.replace("de precision ", "")          # "tube 20 x 4,5"
    par = p06_parallelisme(se.note)                  # "0,05", lu dans la note de la nomenclature
    n_chape = len(p.TROU_SUPPORT)                    # entretoises traversees par les vis de chape
    n_cadre = se.qty - n_chape                       # les autres, une vis TH chacune
    k2 = 2.0                                         # pieces de revolution au 2:1

    notes = [
        "%s : flottant, il centre la pile de rondelles %s ; rond etire %s NON repris : jeu de %s au moins"
        " dans les diam. %s de la pile et des alesages." % (rA, R["pile_belleville"], ajust,
                                                            f(p.ALESAGE_D - p.TOURILLON_D), f(p.ALESAGE_D)),
        "%s : %d serrees chacune par une V1 (vis TH M10 x %s + ecrou autofreine tout metal), les %d de la"
        " chape par les V9 (vis H M10 x %s)." % (rB, n_cadre, f(p.ENTR_VIS_L), n_chape, f(p.SUPPORT_TIRANT_L)),
        "%s : la longueur %s %s fixe l ecart des flancs : couper les %d en serie. Ne pas confondre avec %s"
        " (meme tube, L %s, planche 07)." % (rB, f(lE), p.ENTRETOISE_TOL, se.qty, R["entretoise_vis"],
                                            f(p.SUPPORT_TUBE_L)),
        "%s / %s : pieces du commerce, rien a fabriquer ; entre les rebords du coin %s (larges de %s dessus"
        " et %s dessous), trous remplis de silicone HT." % (rC, rD, R["coin"], f(p.PLAQ_REBORD_L, 2),
                                                      f(p.PLAQ_REBORD_L_BAS, 2)),
    ]
    s = D.Sheet("TOURILLON, ENTRETOISES, PLAQUES", rA[:2],
                "%s / %s / %s (achat)" % (st.material.split()[0], se.material.split()[0],
                                          p06_famille(sh.material)),
                "rond %s %s / %s" % (f(p.TOURILLON_D), ajust, tube),
                "%d + %d + %d + %d (%s a %s)" % (st.qty, se.qty, sh.qty, sb.qty, rA, rD),
                "2:1 - plaque %s/%s 1:1" % (rC, rD), notes=notes)
    s.cartouche()

    # ======================================================== 06a tourillon, 2:1
    Y_HAUT = 45.0                                # haut des pieces de revolution, sous les titres
    XA, YA = 75.0, Y_HAUT + k2 * lT              # axe ; bas de la piece (z = 0)
    p06_titre(s, XA, 20.0, "%s  TOURILLON  (2:1)" % rA,
              ["%s, %d ex." % (st.material, st.qty), "brut %s" % st.stock])
    v = D.View(s, k2, 0.0, 0.0, XA, YA)
    v.contour(p06_poly([(-rT + cT, 0.0), (rT - cT, 0.0), (rT, cT), (rT, lT - cT),
                        (rT - cT, lT), (-rT + cT, lT), (-rT, lT - cT), (-rT, cT)]))
    for z in (cT, lT - cT):                      # aretes chanfrein / cylindre : aretes vues
        p06_ligne(v, (-rT, z), (rT, z), D.TRAIT_FORT)
    v.axe((0.0, 0.0), (0.0, lT))
    # attaches aux angles vifs fictifs : celles de la longueur et du diametre
    # se rejoignent au coin sans se croiser
    for sx in (-1.0, 1.0):                       # angles vifs fictifs des chanfreins (ISO 129-1)
        for z0, zc in ((0.0, cT), (lT, lT - cT)):
            dz = 1.0 if z0 == 0.0 else -1.0
            p06_ligne(v, (sx * rT, zc), (sx * rT, z0 - dz * 1.0 / k2))
            p06_ligne(v, (sx * (rT - cT), z0), (sx * (rT + 1.0 / k2), z0))
    v.cote_vx(0.0, lT, rT, rT, 0.0, xl=rT + 10.0 / k2)
    v.cote_hx(-rT, rT, 0.0, 0.0, 0.0, zl=-12.0 / k2, texte="diam. %s %s" % (f(p.TOURILLON_D), ajust))
    v.renvoi((-rT + cT / 2.0, lT - cT / 2.0), "%s x 45 deg" % f(cT, 1) + chr(10) + "aux 2 bouts",
             -9.0, -8.0, fin="fleche", palier=4.0)

    # ======================================================== 06b entretoise, coupe 2:1
    XB, YB = 185.0, Y_HAUT + k2 * lE
    p06_titre(s, XB, 20.0, "%s  ENTRETOISE DE CADRE, COUPE AXIALE  (2:1)" % rB,
              ["%s, %d ex." % (se.material, se.qty), "brut %s" % se.stock])
    v2 = D.View(s, k2, 0.0, 0.0, XB, YB)
    s.motif("p06_h", 45.0, 2.0)
    for sg in (-1.0, 1.0):                       # les deux parois coupees
        paroi = p06_poly([(sg * di / 2.0, 0.0), (sg * de / 2.0, 0.0), (sg * de / 2.0, lE),
                          (sg * di / 2.0, lE)])
        v2.zone([paroi], "p06_h", w=0)
        v2.contour(paroi)
    for z in (0.0, lE):                          # bord de l alesage aux deux bouts : arete vue
        p06_ligne(v2, (-di / 2.0, z), (di / 2.0, z), D.TRAIT_FORT)
    v2.axe((0.0, 0.0), (0.0, lE))
    v2.cote_vx(0.0, lE, de / 2.0, de / 2.0, 0.0, xl=de / 2.0 + 10.0 / k2,
               texte="%s %s" % (f(lE), p.ENTRETOISE_TOL))
    v2.cote_hx(-di / 2.0, di / 2.0, 0.0, 0.0, 0.0, zl=-10.0 / k2, texte="diam. %s" % f(di))
    v2.cote_hx(-de / 2.0, de / 2.0, 0.0, 0.0, 0.0, zl=-18.0 / k2, texte="diam. %s" % f(de))
    v2.renvoi(((de + di) / 4.0, lE), "2 faces dressees" + chr(10) + "paralleles a %s" % par,
              12.0, -7.0, fin="fleche", palier=5.0)

    # ======================================================== 06c / 06d plaque, 1:1
    XC, YC = 325.0, 90.0
    o, trous = P.plaquette_haute_profile()       # profil (x : largeur, y : longueur)
    bx0, by0, bx1, by1 = G.bbox(o)
    hl, hb = (by1 - by0) / 2.0, (bx1 - bx0) / 2.0
    yc = (by0 + by1) / 2.0
    rc = p06_rayon_coin(o)
    rt = p.PLAQ_TROU_D / 2.0
    xt = sorted(t[0][1][1] for t in trous)       # centres des trous, le long de la plaque
    p06_titre(s, XC, 20.0, "%s / %s  PLAQUE DE FROTTEMENT  (1:1)" % (rC, rD),
              ["piece du commerce : %s" % p.PLAQ_REF,
               "%s, epaisseur %s" % (sh.material, f(p.PLAQ_EP)),
               "%d dessus (%s) + %d dessous (%s), identiques" % (sh.qty, rC, sb.qty, rD)])
    vp = D.View(s, 1.0, yc, 0.0, XC, YC)         # longueur a l horizontale
    vp.contour([seg_tourne(sg) for sg in o])
    for t in trous:
        vp.contour([seg_tourne(sg) for sg in t])
    vp.axe((yc - hl, 0.0), (yc + hl, 0.0))
    vp.axe((yc, -hb), (yc, hb), ext=2.0)        # symetrie : les trous sont a +/- 35 du milieu
    for x in xt:                                 # axe du trou prolonge jusqu au bord : attache du 70
        vp.axe((x, -rt), (x, hb - 3.0))
    vp.cote_hx(xt[0], xt[-1], hb, hb, 0.0, zl=hb + 10.0)
    for sy in (-1.0, 1.0):                       # angles vifs fictifs des R4 (ISO 129-1)
        for sz in (-1.0, 1.0):
            cy_, cz_ = yc + sy * hl, sz * hb
            p06_ligne(vp, (cy_, cz_ - sz * rc), (cy_, cz_ + sz * 1.0))
            p06_ligne(vp, (cy_ - sy * rc, cz_), (cy_ + sy * 1.0, cz_))
    vp.cote_hx(yc - hl, yc + hl, -hb, -hb, 0.0, zl=-hb - 10.0)
    vp.cote_vx(-hb, hb, yc + hl, yc + hl, 0.0, xl=yc + hl + 10.0)
    a60 = math.radians(60.0)
    vp.renvoi((xt[-1] + rt * math.cos(a60), rt * math.sin(a60)),
              "%d x diam. %s" % (len(trous), f(p.PLAQ_TROU_D)), 6.0, -24.0, fin="fleche", palier=5.0)
    vp.rayon((yc - hl + rc, hb - rc), rc, 135.0, "(4 x R%s)" % f(rc), 8.0)
    return s.save(os.path.join(OUT, "06_petites.svg"))


# Aides de la planche 06 (02/10/2026). Elles n'utilisent que l'interface
# publique de draw.View (P, axe, contour, zone, cote_hx, cote_vx, renvoi,
# rayon) et de draw.Sheet ; elles ne changent rien aux autres planches.

def p06_titre(s, x, y, titre, sous=()):
    """Titre de vue en gras, des lignes d'explication dessous."""
    s.text(x, y, titre, 3.6, "middle", weight="bold")
    for i, t in enumerate(sous):
        s.text(x, y + 4.6 + 4.0 * i, t, 2.8, "middle")


def p06_ligne(v, p0, p1, w=D.TRAIT_FIN, dash=None):
    """Segment ouvert de p0 a p1 (modele)."""
    a, b = v.P(p0), v.P(p1)
    v.s.line(a[0], a[1], b[0], b[1], w, dash)


def p06_poly(pts):
    """Contour ferme (segments 'L') par ses sommets, en coordonnees modele."""
    return [('L', pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def p06_ajustement(texte):
    """Classe de tolerance ISO 286 ecrite dans un brut ('rond etire 25 h9 x 76'
    donne 'h9') : la nomenclature reste la seule source."""
    import re
    m = re.search(r"\b([a-z]{1,2}\d{1,2})\b", texte)
    return m.group(1) if m else ""


def p06_parallelisme(texte):
    """Tolerance de parallelisme ecrite dans une note ('... // 0,05 ...')."""
    import re
    m = re.search(r"//\s*([\d,]+)", texte)
    return m.group(1) if m else "?"


def p06_famille(matiere):
    """Famille d'un alliage ('CuZn25Al5Mn4Fe3-C + graphite' donne 'CuZn') : la
    designation complete ne tient pas dans la case du cartouche."""
    import re
    m = re.match(r"[A-Za-z]+", matiere)
    return m.group(0) if m else matiere


def p06_rayon_coin(segs):
    """Rayon des angles d'un contour, lu sur ses arcs (pas de parametre)."""
    rs = sorted(set(round(sg[2], 3) for sg in segs if sg[0] != 'L'))
    return rs[0] if rs else 0.0


def seg_tourne(sg):
    """Echange les deux coordonnees d un segment : un profil (x, y) se lit en (y, x)."""
    if sg[0] == 'L':
        return ('L', (sg[1][1], sg[1][0]), (sg[2][1], sg[2][0]))
    _t, c, r, a0, a1, ccw = sg
    import math as _m
    return ('A', (c[1], c[0]), r, _m.pi / 2 - a0, _m.pi / 2 - a1, not ccw)


# ============================================================ chape

# Planche 07, reprise du 02/10/2026. Valeurs de norme, pas de conception : elles
# ne servent qu'au dessin de la visserie M10 et des filets, et a l'ordre de
# grandeur de la precharge. ISO 4014 : hauteur de tete H M10 ; ISO 4014 / 4032 :
# surplat M10 ; ISO 7089 : d2 de la rondelle M10 ; ISO 261 : pas du M10 ;
# ISO 724 : diametre a fond de filet d3 = d - 1,2269 P ; couple de serrage
# C = K F d avec K = 0,2 pour une vis zinguee montee a sec.
C07_M10_K = 6.4
C07_M10_S = 16.0
C07_M10_RONDELLE_D = 20.0
C07_M10_PAS = 1.5
C07_K_COUPLE = 0.2


def c07_titre(s, x, y, titre, sous=()):
    """Titre de vue en gras, des lignes d'explication dessous."""
    s.text(x, y, titre, 3.6, "middle", weight="bold")
    for i, t in enumerate(sous):
        s.text(x, y + 4.6 + 4.0 * i, t, 2.8, "middle")


def c07_ligne(v, p0, p1, w=D.TRAIT_FIN, dash=None):
    """Segment ouvert de p0 a p1 (modele)."""
    a, b = v.P(p0), v.P(p1)
    v.s.line(a[0], a[1], b[0], b[1], w, dash)


def c07_rect(x0, y0, x1, y1):
    """Rectangle ferme (segments 'L'), coordonnees modele."""
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return [('L', pts[i], pts[(i + 1) % 4]) for i in range(4)]


def c07_d3(d, pas):
    """Diametre a fond de filet d'un filetage metrique ISO (ISO 724)."""
    return d - 1.2269 * pas


def c07_filet(v, y0, y1, d, pas):
    """Tige filetee vue, d'axe x = 0 du plan (x, y) de la vue, de y0 a y1 :
    sommets en trait fort (contour), fond de filet en trait fin (ISO 6410)."""
    v.contour(c07_rect(-d / 2.0, y0, d / 2.0, y1))
    r3 = c07_d3(d, pas) / 2.0
    for sx in (-1.0, 1.0):
        c07_ligne(v, (sx * r3, y0), (sx * r3, y1))


def c07_arc_pres(segs, pt):
    """Arc du contour dont le centre est le plus proche de pt."""
    arcs = [sg for sg in segs if sg[0] == 'A']
    return min(arcs, key=lambda sg: math.hypot(sg[1][0] - pt[0], sg[1][1] - pt[1]))


def c07_sommet_fictif(v, segs, sommet, dep=1.0):
    """Arete fictive (ISO 129-1) : les deux droites qui encadrent l'arc voisin
    de 'sommet' sont prolongees en trait fin jusqu'a leur intersection. Une
    droite parallele a un axe du repere depasse encore de dep mm de feuille :
    elle se continue dans la ligne d'attache qui part du sommet. Une droite
    biaise s'arrete au sommet, pour ne croiser aucune ligne d'attache."""
    a = c07_arc_pres(segs, sommet)
    for q in (G.seg_start(a), G.seg_end(a)):
        dx, dy = sommet[0] - q[0], sommet[1] - q[1]
        n = math.hypot(dx, dy)
        if n < 1e-9:
            continue
        droit = min(abs(dx), abs(dy)) < 1e-6 * n
        e = (dep if droit else 0.0) / v.k
        c07_ligne(v, q, (sommet[0] + dx / n * e, sommet[1] + dy / n * e))


def c07_court(stock, re_min):
    """Brut de tole tenant dans la case du cartouche : l'exigence de Re passe
    dans la case matiere ('tole 8 mm, cert. 3.1, Re >= 430' donne
    'tole 8 cert.3.1')."""
    t = stock.replace(", Re >= %.0f" % re_min, "").replace(" mm,", "")
    return t.replace("cert. ", "cert.")


def c07_min(t):
    """Designation de la nomenclature, initiale en minuscule (tableau)."""
    return t[:1].lower() + t[1:]


def c07_dec(x):
    """Une decimale, virgule, meme ronde (3,0 et non 3)."""
    return ("%.1f" % x).replace(".", ",")


def plan_chape():
    """Planche 07 : platine de butee (07) et montage de la chape, ou figure
    aussi l'entretoise de butee 07b (tube coupe a longueur, cotee sur la coupe).
    Reprise du 02/10/2026 : tout a l'echelle 1:1 ; quantites, matieres, bruts et
    reperes lus dans les PartSpec, nomenclature.REPERES et nomenclature.visserie ;
    cotes ISO (cote_hx / cote_vx), aretes fictives marquees, bulles de repere
    et tableau des pieces du montage ; aides locales c07_*."""
    import nomenclature as N            # reperes et visserie de NOMENCLATURE.md
    import spec as SPC                  # couple de serrage des M10
    SP = dict((q.name, q) for q in P.all_parts())
    R = N.REPERES
    VS = dict((r[0], r) for r in N.visserie())
    f = D.fmt
    sp, st = SP["support"], SP["entretoise_vis"]
    r07, r07b = R["support"], R["entretoise_vis"]

    # ---------------------------------------------------------------- valeurs
    zv = p.Z_VIS
    b2, e2 = p.SUPPORT_B / 2.0, p.SUPPORT_B_BOUT / 2.0
    xa0, xa1 = p.SUPPORT_X0, p.SUPPORT_X1
    xs = p.SUPPORT_X
    rh = p.D_VIS / 2.0                       # trous des V9
    rb = p.VIS_PASSAGE_D / 2.0               # alesage de la tige
    o, trous = P.support_profile()
    bx0, bz0, bx1, bz1 = G.bbox(o)
    sig, fle, sig_tube = p.platine_contrainte()
    aire = math.pi / 4.0 * (p.ENTRETOISE_DE ** 2 - p.ENTRETOISE_DI ** 2)
    f0 = SPC.COUPLE_M10 * 1000.0 / (C07_K_COUPLE * p.SUPPORT_TIRANT_D)   # precharge d'une V9, N
    sig_pre = (f0 + p.coin_effort() / len(p.TROU_SUPPORT)) / aire
    v9 = p.boulonnerie()[2]
    tube = p.ENTRETOISE_BRUT.replace("de precision ", "")          # "tube 20 x 4,5"
    n_ch = len(p.TROU_SUPPORT)
    nron = p.SUPPORT_RONDELLES_ECROU

    notes = [
        "%s : %s ; meme tole que les flancs, platines imbriquees dans leurs chutes." % (r07, p.EXIGENCE_TOLE),
        "%s : decoupe laser d apres support.dxf, aretes cassees %s x 45 deg ; %s et %s entre aretes fictives (au sommet R%s, la"
        " tole mesure %s)." % (r07, f(p.CHANFREIN), f(p.SUPPORT_B_BOUT), f(p.SUPPORT_B),
                               f(p.SUPPORT_R_CONGE), f(bz1 - bz0, 2)),
        "%s : %s %s, coupe a la longueur cotee, les %d a la meme butee, faces dressees."
        % (r07b, p.ENTRETOISE_BRUT, st.material, st.qty),
        "Commande %s kN : le coin tire la tige, la tete V7 pousse la butee V6 ; platines et %s comprimees ;"
        " V9 : %s N au desserrage." % (f(p.coin_effort() / 1000.0), r07b, f(p.coin_desserrage(), 0)),
        "Platine : %s MPa en flexion, coefficient %s a 20 C et %s a 150 C, fleche %s mm."
        % (f(sig, 0), c07_dec(p.RE_TOLE / sig), c07_dec(p.RE_TOLE_CHAUD / sig), f(fle, 2)),
        "%s : %s MPa chacune sous la commande, %s environ avec la precharge des V9 (%s N.m, K = %s)."
        % (r07b, f(sig_tube), f(sig_pre, 0), f(SPC.COUPLE_M10), f(C07_K_COUPLE)),
        "V9 : tete et 1 rondelle derriere le flanc oppose, %d rondelles et 2 ecrous H cote platines ; le"
        " premier sur le filet (marge %s), %s N.m, puis le contre-ecrou bloque contre lui."
        % (nron, f(v9["marge_filet"]), f(SPC.COUPLE_M10)),
        "V8 : 0,1 a 0,3 de jeu axial, puis contre-bloques. V7 : douille de %s et cliquet, une cle plate bute"
        " sur les V9." % f(p.VIS_TETE_D),
    ]
    s = D.Sheet("PLATINE ET ENTRETOISE DE BUTEE", r07,
                "%s, Re >= %s / %s" % (sp.material, f(p.RE_TOLE), st.material.split()[0]),
                "%s / %s" % (c07_court(sp.stock, p.RE_TOLE), tube),
                "%d + %d (%s, %s)" % (sp.qty, st.qty, r07, r07b), "1:1", notes=notes)
    s.cartouche()

    # ======================================================== 07 platine, 1:1
    XP, YP = 312.0, 78.0
    c07_titre(s, XP, 17.0, "%s  PLATINE DE BUTEE  (1:1)" % r07,
              ["%s, %d ex. identiques, empilees" % (sp.material, sp.qty), "brut %s" % sp.stock])
    v = D.View(s, 1.0, 0.0, zv, XP, YP)
    v.contour(o)
    for t in trous:
        v.contour(t)
    # la hauteur aux sommets : ligne de cote entre l'alesage et le trou de
    # droite, attaches courtes. Dehors, ses attaches couperaient celles du 140
    # et l'axe du trou, qui sert d'attache a l'entraxe. L'axe de symetrie
    # horizontal s'interrompt pour la laisser passer.
    x70 = (rb + xs - rh) / 2.0
    v.axe((xa0, zv), (x70 - 5.0, zv))
    v.axe((x70 + 5.0, zv), (xa1, zv))
    v.axe((0.0, zv - b2), (0.0, zv + b2))
    z104 = zv - b2 - 10.0                    # ligne de cote de l'entraxe
    z140 = z104 - 8.0                        # ligne de cote de la longueur
    for (x, _z) in p.TROU_SUPPORT:           # axes des trous, attaches de l'entraxe
        v.axe((x, zv + rh), (x, z104 + 1.0))
    # aretes fictives : coins des bouts (140 et 40) et sommets (70)
    for q in ((xa0, zv - e2), (xa1, zv - e2), (xa1, zv + e2), (0.0, zv - b2), (0.0, zv + b2)):
        c07_sommet_fictif(v, o, q)
    v.cote_hx(-xs, xs, None, None, 0.0, zl=z104)
    v.cote_hx(xa0, xa1, zv - e2, zv - e2, 0.0, zl=z140)
    v.cote_vx(zv - e2, zv + e2, xa1, xa1, 0.0, xl=xa1 + 10.0)
    v.cote_vx(zv - b2, zv + b2, 0.0, 0.0, 0.0, xl=x70, dt=12.0)
    # rayons : en haut a gauche, ou aucune attache ne passe
    c8 = c07_arc_pres(o, (xa0, zv + e2))
    v.rayon(c8[1], c8[2], 135.0, "4 x R%s" % f(c8[2]), 7.0)
    c12 = c07_arc_pres(o, (0.0, zv + b2))
    v.rayon(c12[1], c12[2], 100.0, "2 x R%s" % f(c12[2]), 9.0)
    # alesage et trous : lignes de repere radiales, textes alignes
    a = math.radians(120.0)
    lg = (b2 + 2.0 - rb * math.sin(a)) / math.sin(a)
    v.renvoi((rb * math.cos(a), zv + rb * math.sin(a)), "diam. %s" % f(p.VIS_PASSAGE_D),
             lg * math.cos(a), -lg * math.sin(a), fin="fleche", palier=5.0)
    a = math.radians(110.0)
    lg = (b2 + 2.0 - rh * math.sin(a)) / math.sin(a)
    v.renvoi((-xs + rh * math.cos(a), zv + rh * math.sin(a)),
             "%d x diam. %s" % (n_ch, f(p.D_VIS)),
             lg * math.cos(a), -lg * math.sin(a), fin="fleche", palier=5.0)

    # ======================================================== montage, coupe 1:1
    # Plan de coupe horizontal par les axes (tige et V9, tous a z = Z_VIS), vu
    # de dessus. Vue : x (long de la platine) horizontal, y (axe de la tige)
    # vertical, vers la butee en haut. Tige, vis, ecrous et rondelles ne sont
    # pas coupes (ISO 128-50) ; flancs, entretoises et platines sont hachures.
    XM, YM = 112.0, 200.0
    c07_titre(s, XM, 17.0, "MONTAGE DE LA CHAPE, COUPE PAR LES AXES  (1:1)",
              ["vue de dessus, butee vers le haut ; coin et tete de charge non representes",
               "jeu des V9 dans leurs trous non represente (trous de %s, vis de %s)"
               % (f(p.D_VIS), f(p.SUPPORT_TIRANT_D))])
    m = D.View(s, 1.0, 0.0, 0.0, XM, YM)
    ep = p.EP_FLANC
    yo, yf = -p.Y_FLANC_EXT, p.Y_FLANC_EXT        # faces exterieures des flancs
    yi, ye = p.COIN_Y_SUPPORT, p.SUPPORT_Y1       # faces des platines
    ron, nron = p.SUPPORT_RONDELLE_E, p.SUPPORT_RONDELLES_ECROU
    ecr = p.SUPPORT_ECROU_M10_H * p.SUPPORT_ECROUS_M10_N
    re_ = p.ENTRETOISE_DE / 2.0
    xf = xa1 + 6.0                                 # flancs rompus un peu au-dela des platines
    fente = p.FENTE_COIN_B / 2.0
    rt = p.SUPPORT_TIRANT_D / 2.0
    rm = rt                                        # trous des V9 dessines au diametre de la vis
    s.motif("c07_hf", 45.0, 2.0)                   # flancs
    s.motif("c07_ht", -45.0, 1.4)                  # entretoises
    s.motif("c07_hp", 45.0, 1.2)                   # platines
    s.motif("c07_hq", -45.0, 1.2)                  # platine du dessus : hachures croisees
    # -- flancs, coupes : trous des V9 et fente du coin ; bouts rompus
    for (ya, yb) in ((yo, yo + ep), (yf - ep, yf)):
        xs_ = [-xf, -xs - rm, -xs + rm, -fente, fente, xs - rm, xs + rm, xf]
        for i in range(0, 8, 2):
            xg, xd = xs_[i], xs_[i + 1]
            m.zone([c07_rect(xg, ya, xd, yb)], "c07_hf", w=0)
            c07_ligne(m, (xg, ya), (xd, ya), D.TRAIT_FORT)
            c07_ligne(m, (xg, yb), (xd, yb), D.TRAIT_FORT)
            for x in (xg, xd):
                if abs(abs(x) - xf) < 1e-9:
                    m.rupture((x, ya), (x, yb), amp=1.2)
                else:
                    c07_ligne(m, (x, ya), (x, yb), D.TRAIT_FORT)
    # -- entretoises de cadre (06b) et de butee (07b), coupees en long
    for sx in (-1.0, 1.0):
        for (ya, yb) in ((yo + ep, yf - ep), (yf, yi)):
            for (u0, u1) in ((-re_, -rm), (rm, re_)):
                parois = c07_rect(sx * xs + u0, ya, sx * xs + u1, yb)
                m.zone([parois], "c07_ht", w=0)
                m.contour(parois)
    # -- platines, coupees : trous des V9 et alesage de la tige
    for i in range(p.SUPPORT_N):
        ya, yb = yi + i * p.SUPPORT_EP, yi + (i + 1) * p.SUPPORT_EP
        xs_ = [xa0, -xs - rm, -xs + rm, -rb, rb, xs - rm, xs + rm, xa1]
        for j in range(0, 8, 2):
            r_ = c07_rect(xs_[j], ya, xs_[j + 1], yb)
            m.zone([r_], "c07_hp" if i == 0 else "c07_hq", w=0)
            m.contour(r_)
    # -- vis de chape V9 (non coupees)
    y_tete = yo - ron                              # dessous de tete
    y_ecr = ye + nron * ron                        # dessous de l'ecrou
    y_bout = y_tete + p.SUPPORT_TIRANT_L
    for sx in (-1.0, 1.0):
        x = sx * xs
        m.contour(c07_rect(x - C07_M10_S / 2.0, y_tete - C07_M10_K, x + C07_M10_S / 2.0, y_tete))
        m.contour(c07_rect(x - C07_M10_RONDELLE_D / 2.0, y_tete, x + C07_M10_RONDELLE_D / 2.0, yo))
        # fut lisse : ses bords sont ceux des trous et des alesages qu'il remplit
        for k in range(nron):
            m.contour(c07_rect(x - C07_M10_RONDELLE_D / 2.0, ye + k * ron,
                               x + C07_M10_RONDELLE_D / 2.0, ye + (k + 1) * ron))
        for k in range(p.SUPPORT_ECROUS_M10_N):     # ecrou serre puis contre-ecrou
            m.contour(c07_rect(x - C07_M10_S / 2.0, y_ecr + k * p.SUPPORT_ECROU_M10_H,
                               x + C07_M10_S / 2.0, y_ecr + (k + 1) * p.SUPPORT_ECROU_M10_H))
        m.contour(c07_rect(x - rt, y_ecr + ecr, x + rt, y_bout))
        r3 = c07_d3(p.SUPPORT_TIRANT_D, C07_M10_PAS) / 2.0
        for sg in (-1.0, 1.0):                     # bout filete vu : fond de filet en trait fin
            c07_ligne(m, (x + sg * r3, y_ecr + ecr), (x + sg * r3, y_bout))
        m.axe((x, y_tete - C07_M10_K), (x, y_bout))
    # -- tige M16 (02d) et son arret axial
    hm = p.SUPPORT_ECROU_H / 2.0                   # un ecrou HM M16
    y_hm = yi - p.SUPPORT_RONDELLE - p.SUPPORT_ECROU_H
    y_tt = ye + p.SUPPORT_BUTEE_H                  # dessous de la tete de manoeuvre
    as_ = p.SUPPORT_RONDELLE / 2.0                 # une rondelle AS 1730
    rv, rbu = p.VIS_TETE_D / 2.0, p.SUPPORT_BUTEE_D / 2.0
    c07_filet(m, p.VIS_Y0, y_hm, p.VIS_D, p.VIS_PAS)
    c07_filet(m, yi, ye, p.VIS_D, p.VIS_PAS)       # vue dans l'alesage des platines
    c07_filet(m, y_tt + p.VIS_TETE_H, p.Y_BOUT_VIS, p.VIS_D, p.VIS_PAS)
    for k in range(2):                             # V8 : deux ecrous HM
        m.contour(c07_rect(-rv, y_hm + k * hm, rv, y_hm + (k + 1) * hm))
    for k in range(2):                             # V5 : deux rondelles AS
        y0_ = yi - p.SUPPORT_RONDELLE + k * as_
        m.contour(c07_rect(-rbu, y0_, rbu, y0_ + as_))
    for (y0_, y1_) in ((ye, ye + as_), (ye + as_, y_tt - as_), (y_tt - as_, y_tt)):   # V6
        m.contour(c07_rect(-rbu, y0_, rbu, y1_))
    y_hh = y_tt + p.VIS_TETE_H - hm                # V7 : ecrou H puis ecrou HM
    m.contour(c07_rect(-rv, y_tt, rv, y_hh))
    m.contour(c07_rect(-rv, y_hh, rv, y_tt + p.VIS_TETE_H))
    m.axe((0.0, p.VIS_Y0), (0.0, p.Y_BOUT_VIS))
    # -- cotes : longueur de l'entretoise 07b (seule cote de cette piece) et
    #    calage de la tete de manoeuvre sur la tige
    m.cote_vx(yf, yi, xf, xa1, 0.0, xl=xf + 8.0,
              texte="%s %s" % (f(p.SUPPORT_TUBE_L), p.SUPPORT_TUBE_TOL))
    m.cote_vx(y_tt + p.VIS_TETE_H, p.Y_BOUT_VIS, rv, p.VIS_D / 2.0, 0.0, xl=rv + 8.0,
              dedans=False, dt=8.0, queue=10.0)
    # -- bulles : colonne a gauche pour les pieces des bords, dans les vides
    #    du montage pour celles de l'axe
    xb = -xf - 12.0
    pts = [
        (R["support"], (xa0 + 6.0, yi + p.SUPPORT_EP / 2.0), xb, yi + p.SUPPORT_EP / 2.0, "point"),
        (R["entretoise_vis"], (-xs - (re_ + rm) / 2.0, (yf + yi) / 2.0), xb, (yf + yi) / 2.0, "point"),
        (R["flanc"], (-xf + 8.0, yf - ep / 2.0), xb, yf - ep - 12.0, "point"),
        (R["entretoise"], (-xs - (re_ + rm) / 2.0, 0.0), xb, 0.0, "point"),
        ("V9", (-xs - C07_M10_S / 2.0 + 2.0, y_tete - C07_M10_K / 2.0), xb, y_tete - C07_M10_K / 2.0,
         "point"),
        (R["vis"], (-p.VIS_D / 2.0, 12.0), -26.0, 12.0, "fleche"),
        ("V8", (rv / 2.0, y_hm + hm / 2.0), 28.0, y_hm - 6.0, "point"),
        ("V5", (rbu, yi - p.SUPPORT_RONDELLE / 2.0), 28.0, yi - 9.0, "fleche"),
        ("V6", (rbu - 1.5, ye + p.SUPPORT_BUTEE_H / 2.0), 28.0, ye + 12.5, "point"),
        ("V7", (-rv / 2.0, y_tt + 8.5), -28.0, y_tt + 8.5, "point"),
    ]
    for (rep, pt, xbul, ybul, fin) in pts:
        m.bulle(pt, rep, xbul - pt[0], -(ybul - pt[1]), fin=fin)

    # ======================================================== pieces du montage
    lignes = [
        (R["flanc"], "flanc (planche %s)" % R["flanc"][:2], SP["flanc"].qty),
        (R["entretoise"], "entretoise de cadre, L %s (planche %s)" % (f(p.ENTRETOISE_L), R["entretoise"][:2]),
         n_ch),
        (r07b, "entretoise de butee, %s (ci-contre)" % tube, st.qty),
        (r07, "platine de butee (ci-dessus)", sp.qty),
        (R["vis"], "tige filetee M%s x %s" % (f(p.VIS_D), f(p.VIS_L)), SP["vis"].qty),
        ("V5", c07_min(VS["V5"][1]), VS["V5"][2]),
        ("V6", c07_min(VS["V6"][1]), VS["V6"][2]),
        ("V7", "ecrou H + ecrou HM M%s, bloques" % f(p.VIS_D), VS["V7"][2]),
        ("V8", c07_min(VS["V8"][1]), VS["V8"][2]),
        ("V9", "vis H M10 x %s + 2 ecrous + %d rondelles" % (f(p.SUPPORT_TIRANT_L), 1 + nron), VS["V9"][2]),
    ]
    larg = (11.0, 74.0, 10.0)
    D.table(s, XP - sum(larg) / 2.0, 150.0, "Pieces du montage", ("rep.", "designation", "qte"),
            [(a_, b_, "%d" % c_) for (a_, b_, c_) in lignes], larg)
    return s.save(os.path.join(OUT, "07_chape.svg"))


# ============================================================ assemblage

# Valeurs de norme, pas de conception : elles ne servent qu'au dessin des
# tetes et des ecrous M10 vus de face (ISO 7089 : d2 de la rondelle M10 ;
# ISO 4014, 4032 et 7042 : surplat M10).
A00_M10_RONDELLE_D = 20.0
A00_M10_S = 16.0
A00_MOYEN = 0.35                        # trait des pieces du banc autres que le flanc
A00_MIXTE2 = "8 1.2 1 1.2 1 1.2"        # trait mixte fin a deux tirets (ISO 128, 05.1)


def a00_ligne(v, pts, w=D.TRAIT_FIN, dash=None):
    """Polyligne ouverte, coordonnees modele."""
    v.s.path(" ".join(("M " if i == 0 else "L ") + "%.3f %.3f" % v.P(q)
                      for i, q in enumerate(pts)), w, dash)


def a00_poly(pts):
    """Contour ferme a partir d'une liste de points."""
    return [('L', pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def a00_hexagone(xc, zc, s):
    """Hexagone de surplat s, plats en haut et en bas."""
    r = s / math.sqrt(3.0)
    return a00_poly([(xc + r * math.cos(math.radians(60.0 * i)),
                      zc + r * math.sin(math.radians(60.0 * i))) for i in range(6)])


def a00_decale(segs, dy):
    """Contour translate de dy selon son premier axe (y dans le plan (y, z))."""
    out = []
    for sg in segs:
        if sg[0] == 'L':
            out.append(('L', (sg[1][0] + dy, sg[1][1]), (sg[2][0] + dy, sg[2][1])))
        else:
            _, c, r, a0, a1, ccw = sg
            out.append(('A', (c[0] + dy, c[1]), r, a0, a1, ccw))
    return out


def a00_intervalles(contours, x0):
    """Intervalles de z ou la verticale x = x0 est dans la matiere : contour
    exterieur et trous, regle pair-impair."""
    zs = []
    for c in contours:
        pts = G.polyline(c, 64)
        for a, b in zip(pts, pts[1:] + pts[:1]):
            if (a[0] - x0) * (b[0] - x0) < 0:
                zs.append(a[1] + (x0 - a[0]) / (b[0] - a[0]) * (b[1] - a[1]))
    zs.sort()
    return [(zs[i], zs[i + 1]) for i in range(0, len(zs) - 1, 2)]


def a00_iso(pt):
    """Projection d'un point 3D comme TechDraw.projectEx dans build_freecad :
    direction (1, 1, 0,55), axe X = (1, -1, 0)/racine 2, Y = direction x X."""
    vx, vy, vz = 1.0, 1.0, 0.55
    n = math.sqrt(vx * vx + vy * vy + vz * vz)
    X = (1.0 / math.sqrt(2.0), -1.0 / math.sqrt(2.0), 0.0)
    Y = ((vy * X[2] - vz * X[1]) / n, (vz * X[0] - vx * X[2]) / n, (vx * X[1] - vy * X[0]) / n)
    return (sum(a * b for a, b in zip(pt, X)), sum(a * b for a, b in zip(pt, Y)))


def a00_bulle_seule(s, c, rep, r=3.6, h=3.0):
    """Bulle sans ligne de repere, centree en c (feuille) : a accoler a une
    autre pour reperer deux pieces coaxiales sur une seule ligne."""
    s._p('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="#fff" stroke="#000" stroke-width="0.25"/>'
         % (c[0], c[1], r))
    s.text(c[0], c[1] + 0.36 * h, rep, h, "middle")


def plan_assemblage():
    import nomenclature as N            # les reperes de NOMENCLATURE.md font foi
    R = N.REPERES
    ez, ex = p.pied_debout_encombrement()
    cpt = p.coin_par_tour()
    m_cadre = masse("cadre", 0.0)
    pile = dict((sp.name, sp) for sp in P.all_parts())["pile_belleville"]
    a_conf = "" if p.ETUVE_CONFIRMEE else " A CONFIRMER"
    notes = [
        "Flexion 3 points, portee %s, capacite %s kN." % (D.fmt(p.PORTEE), D.fmt(p.CHARGE_DIM / 1000.0)),
        "Eprouvette : poutrelle %s x %s x %s, en trait mixte a deux tirets."
        % (D.fmt(p.POUTRE_B), D.fmt(p.POUTRE_H), D.fmt(p.POUTRE_L)),
        "Pile Belleville, %s : %s kN a plat, course %s mm."
        % (pile.stock, D.fmt(p.RESSORT_F_PLAT / 1000.0, 1), D.fmt(p.PILE_COURSE, 1)),
        "Lecture de charge : %s mm de coulisseau a %s kN."
        % (D.fmt(p.PILE_ECRAS_DIM, 2), D.fmt(p.CHARGE_DIM / 1000.0)),
        "Reglage par coin acier a %s deg et tige M%s normale aux flancs :"
        % (D.fmt(p.COIN_ANGLE), D.fmt(p.VIS_D)),
        "%s mm de coulisseau et environ %.0f N par tour de tige." % (D.fmt(cpt[0], 3), cpt[1]),
        "Hors tout couche sur pieds : %s x %s x %s (x, y, z) ; flancs %s."
        % (D.fmt(p.L_FLANC), D.fmt(p.PIED_Y), D.fmt(p.H_FLANC + p.PIED_SOL),
           D.fmt(p.ECART_FLANCS + 2 * p.EP_FLANC)),
        "Debout dans l etuve : %s de haut, %s x %s en plan ; etuve %s x %s x %s%s."
        % (D.fmt(p.L_FLANC + ex, 1), D.fmt(p.H_FLANC + 2.0 * ez, 1), D.fmt(p.PIED_Y),
           D.fmt(p.ETUVE_INTERIEUR), D.fmt(p.ETUVE_Y, 1), D.fmt(p.ETUVE_HAUTEUR), a_conf),
        ("Masse du cadre %s kg. " % D.fmt(m_cadre, 1) if m_cadre > 0 else "")
        + "Reperes : NOMENCLATURE.md (Vn : visserie).",
    ]
    s = D.Sheet("BANC DE FLEXION  -  ENSEMBLE", "00", "voir nomenclature", "-", 1,
                "1:5 sauf indication", notes=notes)
    s.cartouche()
    s.motif("a00_ha", 45.0, 1.5)
    s.motif("a00_hb", -45.0, 1.5)
    s.motif("a00_hc", 45.0, 0.7)
    MOY = A00_MOYEN

    def z_de(vv, y):
        return vv.cz - (y - vv.oy) / vv.k

    def titre(nom, kk):
        return "%s  (1:%s)" % (nom, D.fmt(1.0 / kk, 1))

    def bul(vv, pm, cx_, cy_, rep, fin="point"):
        """Bulle centree en (cx_, cy_) mm de feuille, ligne de repere tiree du
        point modele pm."""
        a_ = vv.P(pm)
        return vv.bulle(pm, rep, cx_ - a_[0], cy_ - a_[1], fin=fin)

    # ================================================== elevation, 1:5
    # vue depuis y < 0 (cote du bout epais du coin) : x a droite, z en haut.
    # Le flanc avant cache tout ce qui est entre les flancs, sauf a travers
    # ses ouvertures (fenetre, lumieres, fente, mortaise, ajours, trous). Sont
    # DEVANT lui : coin, plaques de frottement, patins, plats, patin de charge,
    # bouts des tenons, tetes et ecrous M10, pieds couches. La poutrelle,
    # eprouvette et piece voisine, est en trait mixte a deux tirets.
    k = 0.2
    v = D.View(s, k, 0.0, p.H_FLANC / 2.0, 128.0, 74.0, titre("elevation", k), -56.0)
    outer, trous = P.flanc_profile()
    z_coul = p.Z_COULISSEAU_HAUT - (p.POUSSOIR_B / 2.0) * p.COIN_TAN   # dessus du coulisseau, face y < 0
    v.clip_debut("a00_ouv", trous)
    v.contour(rect(-p.POUSSOIR_L / 2, p.Z_POUSSOIR_BAS, p.POUSSOIR_L / 2, p.Z_POUSSOIR_HAUT, 0), MOY)
    for i in range(1, p.POUSSOIR_N):
        zp = p.Z_POUSSOIR_BAS + i * p.POUSSOIR_EP
        a00_ligne(v, [(-p.POUSSOIR_L / 2, zp), (p.POUSSOIR_L / 2, zp)], MOY)
    v.contour(rect(-p.RESSORT_DE / 2, p.Z_PILE_BAS, p.RESSORT_DE / 2, p.Z_COULISSEAU_BAS, 0), MOY)
    v.contour(rect(-p.COULISSEAU_L / 2, p.Z_COULISSEAU_BAS, p.COULISSEAU_L / 2, z_coul, 0), MOY)
    for sx in (-1, 1):
        v.contour(G.circle(sx * p.GUIDE_X, p.Z_GUIDE, p.GUIDE_TETE_D / 2.0), MOY)
    v.clip_fin()
    v.contour(outer)
    for t in trous:
        v.contour(t)
    # devant le flanc avant
    for sx in (-1, 1):
        xa = sx * p.X_APPUI
        v.zone([rect(xa - p.PATIN_L / 2, p.Z_PATIN_BAS, xa + p.PATIN_L / 2, p.Z_PLAT_BAS, 0)], w=MOY)
    v.zone([rect(-p.PLAT_L / 2, p.Z_PLAT_BAS, p.PLAT_L / 2, p.Z_POUTRE_BAS, 0)], w=MOY)
    v.zone([rect(-p.PATIN_CHARGE_L / 2, p.Z_POUTRE_HAUT, p.PATIN_CHARGE_L / 2,
                 p.Z_PATIN_CHARGE_HAUT, 0)], w=MOY)
    coin, _ = P.coin_profile()
    z_coin_bas = min(G.bbox(coin)[1], p.Z_COULISSEAU_HAUT + p.PLAQ_BAS_Y0 * p.COIN_TAN)
    v.zone([rect(-p.COIN_B / 2, z_coin_bas, p.COIN_B / 2, p.Z_TRAVERSE_BAS, 0)], w=MOY)
    v.contour(G.circle(0.0, p.Z_VIS, p.VIS_D / 2.0), MOY)
    v.zone([rect(-p.TRAVERSE_LX / 2, p.Z_TAB0, p.TRAVERSE_LX / 2, p.Z_TAB1, 0)], w=MOY)
    for i in range(1, p.TRAVERSE_N):
        xt = -p.TRAVERSE_LX / 2 + i * p.TRAVERSE_EP
        a00_ligne(v, [(xt, p.Z_TAB0), (xt, p.Z_TAB1)], D.TRAIT_FIN)
    boulons = [(d["t"][0], d["t"][2]) for d in P._instances_entretoises()]
    for (xb, zb) in boulons:
        v.zone([G.circle(xb, zb, A00_M10_RONDELLE_D / 2.0)], w=MOY)
        v.zone([a00_hexagone(xb, zb, A00_M10_S)], w=MOY)
    for sx in (-1, 1):
        v.zone([rect(sx * p.PIED_X_POS - p.PIED_E / 2, -p.PIED_SOL,
                     sx * p.PIED_X_POS + p.PIED_E / 2, p.PIED_H - p.PIED_SOL, 0)], w=MOY)
    v.contour(rect(-p.POUTRE_L / 2, p.Z_POUTRE_BAS, p.POUTRE_L / 2, p.Z_POUTRE_HAUT, 0),
              D.TRAIT_FIN, dash=A00_MIXTE2)
    # axe d'appui gauche ; l'axe d'appui droit porte la trace de A-A, le plan
    # median celle de B-B
    v.axe((-p.X_APPUI, p.Z_PLAT_BAS + 12.0), (-p.X_APPUI, 0.0), ext=0.0)
    y_haut, y_bas = 24.0, 124.0
    v.trace_coupe((p.X_APPUI, z_de(v, y_haut)), (p.X_APPUI, z_de(v, y_bas)), "A", (-1.0, 0.0))
    v.trace_coupe((0.0, z_de(v, y_haut)), (0.0, z_de(v, y_bas)), "B", (-1.0, 0.0))
    # cotes
    # texte du 750 decale vers la droite : la lettre B de la trace est au-dessus
    # du milieu de la ligne
    v.cote_hx(-p.X_APPUI, p.X_APPUI, 0.0, z_de(v, y_bas), None, zl=z_de(v, 131.0), dt=20.0)
    v.cote_hx(-p.L_FLANC / 2, p.L_FLANC / 2, 0.0, 0.0, None, zl=z_de(v, 138.0))
    v.cote_vx(0.0, p.H_FLANC, -p.L_FLANC / 2, -p.L_FLANC / 2, -8.0)
    v.cote_vx(-p.PIED_SOL, 0.0, -p.PIED_X_POS + p.PIED_E / 2, None, 7.0, queue=3.0)
    # reperes
    iv = a00_intervalles([outer] + trous, -330.0)[-1]           # membrure haute
    v.bulle((-330.0, (iv[0] + iv[1]) / 2.0), R["flanc"], -10.0, 0.0)   # reste dans la membrure
    v.bulle((-p.PIED_X_POS - p.PIED_E / 2, -p.PIED_SOL / 2), R["pied"], -15.0, 2.5)
    xe, ze = max(boulons)                       # entretoise du coin haut droit
    c1 = v.bulle((xe, ze), "V1", 16.0, 5.0)
    a00_bulle_seule(s, (c1[0] + 7.2, c1[1]), R["entretoise"])
    bul(v, (p.SUPPORT_X, p.Z_VIS), 156.0, 70.0, "V9")
    bul(v, (p.GUIDE_X, p.Z_GUIDE), 166.0, 79.0, R["guide"])

    # ================================================== coupe A-A, 1:2
    # plan x = +X_APPUI, vue vers -x : y a droite, z en haut
    v2 = D.View(s, 0.5, 0.0, 50.0, 55.0, 183.0, titre("coupe A-A", 0.5), -33.0)
    z_cut = p.Z_POUTRE_BAS + 44.0
    yf = p.ECART_FLANCS / 2.0
    for sy in (-1, 1):
        y0, y1 = sorted((sy * yf, sy * p.Y_FLANC_EXT))
        v2.zone([rect(y0, 0.0, y1, p.Z_BOSSAGE, 0)], "a00_ha")
        yc, b, r = sy * p.Y_FLANC, p.PATIN_B / 2.0, p.RAINURE_B / 2.0
        z0, zr, z1 = p.Z_PATIN_BAS, p.Z_PATIN_BAS + p.RAINURE_P, p.Z_PLAT_BAS
        v2.zone([a00_poly([(yc - b, z0), (yc - r, z0), (yc - r, zr), (yc + r, zr), (yc + r, z0),
                           (yc + b, z0), (yc + b, z1), (yc - b, z1)])], "a00_hb")
        v2.zone([rect(yc - p.PLAT_B / 2, p.Z_PLAT_BAS, yc + p.PLAT_B / 2, p.Z_POUTRE_BAS, 0)],
                w=D.TRAIT_FIN, fond="#000")
    hb = p.POUTRE_B / 2.0
    a00_ligne(v2, [(-hb, z_cut), (-hb, p.Z_POUTRE_BAS), (hb, p.Z_POUTRE_BAS), (hb, z_cut)],
              D.TRAIT_FIN, A00_MIXTE2)
    v2.rupture((-hb - 3.0, z_cut), (hb + 3.0, z_cut))
    v2.axe((0.0, -6.0), (0.0, z_cut + 4.0), ext=0.0)
    y68 = 223.0
    for sy in (-1, 1):
        v2.axe((sy * p.Y_FLANC, p.Z_POUTRE_BAS + 8.0), (sy * p.Y_FLANC, z_de(v2, y68 + 2.0)), ext=0.0)
    v2.cote_hx(-yf, yf, 0.0, 0.0, -8.0)
    v2.cote_hx(-p.Y_FLANC, p.Y_FLANC, None, None, None, zl=z_de(v2, y68))
    v2.cote_vx(0.0, p.Z_POUTRE_BAS, -p.Y_FLANC_EXT, -hb, -6.0, texte="(%s)" % D.fmt(p.Z_POUTRE_BAS))
    v2.bulle((p.Y_FLANC + 2.0, p.Z_PLAT_BAS + 1.0), R["plat_renfort"], 22.0, -8.0)
    v2.bulle((p.Y_FLANC + p.PATIN_B / 2 - 2.0, p.Z_PATIN_BAS + 3.0), R["patin_appui"], 18.0, 2.0)
    s.text(55.0, 233.0, "Les flancs portent SOUS les plats colles :", 2.9, "middle")
    s.text(55.0, 237.5, "la face laterale de la poutre reste degagee.", 2.9, "middle")
    # le pied couche de x = +PIED_X_POS est au-dela du plan : vue partielle
    s.text(55.0, 242.0, "Pieds %s, au-dela du plan, non figures." % R["pied"], 2.9, "middle")

    # ================================================== coupe B-B, 1:2,5
    # plan median x = 0, vue vers -x : y a droite, z en haut. Hachures pour
    # les pieces coupees ; tige, tourillon, ecrous, rondelles et butee ne se
    # coupent pas. Au-dela du plan : bords des flancs, entretoises de butee,
    # vis H M10 (on n'en voit que le bout).
    kb = 0.4
    v3 = D.View(s, kb, 40.0, 275.0, 184.0, 214.0, titre("coupe B-B", kb), -70.0)
    ob = v3.ox - 172.0                  # les bulles de B-B suivent la vue
    zv = p.Z_VIS
    z_bas, z_haut = p.Z_POUTRE_HAUT - 7.0, p.Z_TRAVERSE_HAUT + 7.0
    # au-dela du plan, du plus loin au plus pres : vis H M10 (x = -52), dont
    # seul le bout depasse de la tete de tige ; entretoise de butee ; bords
    # des flancs, vus par la tranche
    v3.zone([rect(p.Y_BOUT_TIRANT - p.SUPPORT_TIRANT_L, zv - p.SUPPORT_TIRANT_D / 2,
                  p.Y_BOUT_TIRANT, zv + p.SUPPORT_TIRANT_D / 2, 0)], w=MOY)
    v3.zone([rect(p.Y_FLANC_EXT, zv - p.ENTRETOISE_DE / 2, p.COIN_Y_SUPPORT,
                  zv + p.ENTRETOISE_DE / 2, 0)], w=MOY)
    for sy in (-1, 1):
        y0, y1 = sorted((sy * yf, sy * p.Y_FLANC_EXT))
        v3.zone([rect(y0, p.Z_POUTRE_HAUT, y1, z_haut, 0)], w=MOY)
    # coupees dans le plan
    iv_b = a00_intervalles([outer] + trous, 0.0)
    for (za, zb_) in iv_b:
        za, zb_ = max(za, p.Z_POUTRE_HAUT), min(zb_, z_haut)
        if zb_ > za:
            for sy in (-1, 1):
                y0, y1 = sorted((sy * yf, sy * p.Y_FLANC_EXT))
                v3.zone([rect(y0, za, y1, zb_, 0)], "a00_ha")
    v3.zone([rect(-p.PATIN_CHARGE_B / 2, p.Z_POUTRE_HAUT, p.PATIN_CHARGE_B / 2,
                  p.Z_PATIN_CHARGE_HAUT, 0)], "a00_ha")
    ra = p.ALESAGE_D / 2.0
    for i in range(p.POUSSOIR_N):
        zp = p.Z_POUSSOIR_BAS + i * p.POUSSOIR_EP
        mot = "a00_hb" if i % 2 == 0 else "a00_ha"
        v3.zone([rect(-p.POUSSOIR_B / 2, zp, -ra, zp + p.POUSSOIR_EP, 0)], mot)
        v3.zone([rect(ra, zp, p.POUSSOIR_B / 2, zp + p.POUSSOIR_EP, 0)], mot)
    ri_, re_ = p.RESSORT_DI / 2.0, p.RESSORT_DE / 2.0
    for kk in range(p.RESSORT_N):
        z0 = p.Z_PILE_BAS + kk * p.RESSORT_L0
        a, b = (re_, ri_) if kk % 2 == 0 else (ri_, re_)
        for sg in (-1, 1):
            v3.zone([a00_poly([(sg * a, z0), (sg * b, z0 + p.RESSORT_H0),
                               (sg * b, z0 + p.RESSORT_H0 + p.RESSORT_T), (sg * a, z0 + p.RESSORT_T)])],
                    w=D.TRAIT_FIN, fond="#000")
    zc0 = p.Z_COULISSEAU_BAS
    yb2 = p.POUSSOIR_B / 2.0
    v3.zone([a00_poly([(-yb2, zc0), (-ra, zc0), (-ra, zc0 + p.ALESAGE_P_COUL),
                       (ra, zc0 + p.ALESAGE_P_COUL), (ra, zc0), (yb2, zc0),
                       (yb2, p.Z_COULISSEAU_HAUT + yb2 * p.COIN_TAN),
                       (-yb2, p.Z_COULISSEAU_HAUT - yb2 * p.COIN_TAN)])], "a00_ha")
    ang = math.radians(p.COIN_ANGLE)
    nrm = (-math.sin(ang) * p.PLAQ_EP, math.cos(ang) * p.PLAQ_EP)
    q0 = (p.PLAQ_BAS_Y0, p.Z_COULISSEAU_HAUT + p.PLAQ_BAS_Y0 * p.COIN_TAN)
    q1 = (p.PLAQ_BAS_Y1, p.Z_COULISSEAU_HAUT + p.PLAQ_BAS_Y1 * p.COIN_TAN)
    v3.zone([a00_poly([q0, q1, (q1[0] + nrm[0], q1[1] + nrm[1]), (q0[0] + nrm[0], q0[1] + nrm[1])])],
            "a00_hc")
    v3.zone([coin], "a00_hb")
    # taraudage M16 depuis le bout epais, passage au-dela
    yt = p.COIN_Y0 + p.COIN_TARAUD_L
    rp = p.VIS_PASSAGE_D / 2.0
    v3.zone([rect(p.COIN_Y0, zv - p.VIS_D / 2, yt, zv + p.VIS_D / 2, 0)], w=0)
    v3.zone([rect(yt, zv - rp, p.COIN_Y1, zv + rp, 0)], w=0)
    for sg in (-1, 1):
        a00_ligne(v3, [(p.COIN_Y0, zv + sg * p.VIS_D / 2), (yt, zv + sg * p.VIS_D / 2),
                       (yt, zv + sg * rp), (p.COIN_Y1, zv + sg * rp)], MOY)
    v3.zone([rect(p.PLAQ_HAUT_Y0, p.Z_COIN_HAUT, p.PLAQ_HAUT_Y1, p.Z_TRAVERSE_BAS, 0)], "a00_hc")
    tr, th = P.traverse_profile()
    v3.zone([tr] + th, "a00_hb")
    v3.zone([G.circle(0.0, p.TRAVERSE_TIRANT_Z, p.SUPPORT_TIRANT_D / 2.0)], "a00_ha", w=MOY)
    for i in range(p.SUPPORT_N):
        y0 = p.COIN_Y_SUPPORT + i * p.SUPPORT_EP
        mot = "a00_ha" if i % 2 == 0 else "a00_hb"
        v3.zone([rect(y0, p.SUPPORT_Z0, y0 + p.SUPPORT_EP, zv - rp, 0)], mot)
        v3.zone([rect(y0, zv + rp, y0 + p.SUPPORT_EP, p.SUPPORT_Z1, 0)], mot)
    # pieces non coupees, dans le plan
    rt, ct = p.TOURILLON_D / 2.0, p.TOURILLON_CHANFREIN
    z0, z1 = p.Z_TOURILLON_BAS, p.Z_TOURILLON_BAS + p.TOURILLON_L
    v3.zone([a00_poly([(-rt + ct, z0), (rt - ct, z0), (rt, z0 + ct), (rt, z1 - ct), (rt - ct, z1),
                       (-rt + ct, z1), (-rt, z1 - ct), (-rt, z0 + ct)])], w=MOY)
    v3.zone([rect(p.VIS_Y0, zv - p.VIS_D / 2, p.Y_BOUT_VIS, zv + p.VIS_D / 2, 0)], w=MOY)
    yi = p.COIN_Y_SUPPORT
    rb, rtete = p.SUPPORT_BUTEE_D / 2.0, p.VIS_TETE_D / 2.0
    v3.zone([rect(yi - p.SUPPORT_RONDELLE, zv - rb, yi, zv + rb, 0)], w=MOY)
    hm = p.SUPPORT_ECROU_H / 2.0
    for j in range(2):
        y1 = yi - p.SUPPORT_RONDELLE - j * hm
        v3.zone([rect(y1 - hm, zv - rtete, y1, zv + rtete, 0)], w=MOY)
    ye = p.SUPPORT_Y1
    v3.zone([rect(ye, zv - rb, ye + p.SUPPORT_BUTEE_H, zv + rb, 0)], w=MOY)
    y_tete = ye + p.SUPPORT_BUTEE_H
    v3.zone([rect(y_tete, zv - rtete, y_tete + p.VIS_TETE_H, zv + rtete, 0)], w=MOY)
    # coin en fin de course, trait mixte a deux tirets : son enveloppe (dessus
    # des rebords, deux bouts, dessous incline), sans les degagements de pied
    # de rebord qui, en tirets, ne se lisent plus
    zr_ = p.Z_COIN_HAUT + p.PLAQ_REBORD_H

    def z_dessous(y):
        return (p.Z_COIN_HAUT - p.COIN_T_BOUT_MINCE - (p.COIN_Y1 - y) * p.COIN_TAN
                - p.PLAQ_REBORD_DROP)
    yf0, yf1 = p.COIN_Y0 + p.COIN_COURSE, p.COIN_Y1 + p.COIN_COURSE
    v3.contour(a00_poly([(yf0, zr_), (yf1, zr_), (yf1, z_dessous(p.COIN_Y1)),
                         (yf0, z_dessous(p.COIN_Y0))]), D.TRAIT_FIN, dash=A00_MIXTE2)
    # poutrelle (piece voisine), rompue
    a00_ligne(v3, [(-hb, z_bas), (-hb, p.Z_POUTRE_HAUT), (hb, p.Z_POUTRE_HAUT), (hb, z_bas)],
              D.TRAIT_FIN, A00_MIXTE2)
    v3.rupture((-hb - 3.0, z_bas), (hb + 3.0, z_bas))
    for sy in (-1, 1):
        y0, y1 = sorted((sy * yf, sy * p.Y_FLANC_EXT))
        v3.rupture((y0 - 2.0, z_haut), (y1 + 2.0, z_haut))
    # axes
    y_l1, y_l2 = 159.0, 152.0
    v3.axe((0.0, z_bas - 2.0), (0.0, z_de(v3, y_l2 - 2.0)), ext=0.0)
    v3.axe((p.COIN_Y0 - 6.0, zv), (p.Y_BOUT_TIRANT + 4.0, zv), ext=0.0)
    # cotes selon y, depuis le plan median
    v3.cote_hx(p.COIN_Y0, 0.0, p.Z_COIN_HAUT + p.PLAQ_REBORD_H, None, None, zl=z_de(v3, y_l1))
    v3.cote_hx(0.0, p.Y_BOUT_VIS, None, zv + p.VIS_D / 2, None, zl=z_de(v3, y_l1))
    v3.cote_hx(0.0, p.Y_BOUT_TIRANT, None, zv + p.SUPPORT_TIRANT_D / 2, None, zl=z_de(v3, y_l2))
    # reperes
    zpb = lambda y: p.Z_COULISSEAU_HAUT + y * p.COIN_TAN + p.PLAQ_DROP / 2.0   # mi-epaisseur de la plaque basse
    # a gauche
    bul(v3, (-20.0, p.Z_TAB0 + 10.0), ob + 131.0, 172.0, R["traverse"])
    bul(v3, (-55.0, p.Z_COIN_HAUT + p.PLAQ_EP / 2.0), ob + 131.0, 184.0, R["plaquette_haute"])
    bul(v3, (-70.0, zv - 12.0), ob + 111.0, 204.0, R["coin"])
    bul(v3, (-60.0, zpb(-60.0)), ob + 116.0, 228.0, R["plaquette_basse"])
    iv0 = [iv_ for iv_ in iv_b if iv_[1] > p.Z_PATIN_CHARGE_HAUT][0]   # premier flanc coupe
    bul(v3, (-p.Y_FLANC, (iv0[0] + iv0[1]) / 2.0), ob + 111.0, 237.0, R["flanc"])
    bul(v3, (-(p.RESSORT_DI + p.RESSORT_DE) / 4.0, p.Z_PILE_BAS + p.PILE_H_LIBRE / 3.0),
        ob + 111.0, 246.0, R["pile_belleville"])
    bul(v3, (-22.0, p.Z_POUSSOIR_BAS + 12.0), ob + 111.0, 254.0, R["poussoir"])
    bul(v3, (-45.0, p.Z_POUTRE_HAUT + 5.0), ob + 111.0, 262.0, R["patin_charge"])
    # a droite
    bul(v3, (0.0, p.TRAVERSE_TIRANT_Z), ob + 182.0, 166.0, "V2")
    bul(v3, (60.0, zv + 5.0), ob + 182.0, 176.0, R["vis"])
    bul(v3, (70.0, zv + (p.VIS_D + p.ENTRETOISE_DE) / 4.0), ob + 191.0, 176.0, R["entretoise_vis"])
    bul(v3, (yi + p.SUPPORT_EP / 2.0, p.SUPPORT_Z1 - 7.5), ob + 200.0, 176.0, R["support"])
    bul(v3, (ye + p.SUPPORT_BUTEE_H / 2.0, zv + rb - 2.0), ob + 209.0, 176.0, "V6")
    bul(v3, (22.0, p.Z_COULISSEAU_BAS + 15.0), ob + 186.0, 220.0, R["coulisseau"])
    bul(v3, (5.0, p.Z_TOURILLON_BAS + p.TOURILLON_L - 5.0), ob + 186.0, 230.0, R["tourillon"])
    bul(v3, (yi - p.SUPPORT_RONDELLE - hm, zv - rtete + 1.0), ob + 190.0, 240.0, "V8")
    # V5 a la verticale de sa rondelle : sa ligne longe la platine sans y entrer
    pv5 = (yi - p.SUPPORT_RONDELLE / 2.0, zv - rb + 1.0)
    bul(v3, pv5, v3.P(pv5)[0], 240.0, "V5")
    bul(v3, (y_tete + p.VIS_TETE_H / 2.0, zv - rtete + 1.0), ob + 214.0, 240.0, "V7")
    bul(v3, (p.Y_BOUT_TIRANT - 2.0, zv + 3.0), ob + 230.0, 214.0, "V9")
    s.text(124.0, 270.0, "Le coin AVANCE VERS LA CHAPE en chargeant ; repousse vers son bout epais, il TIRE"
           " la tige vers l interieur :", 2.9, "middle")
    s.text(124.0, 274.5, "la tete appuie, par la butee a aiguilles, sur la face exterieure des %d platines ;"
           " monte a l envers, la tige ne retiendrait rien." % p.SUPPORT_N, 2.9, "middle")
    s.text(124.0, 279.0, "Douille sur la tete : %s mm devant le bout de tige dans l etuve de %s%s, %s de"
           " marge pour le decentrage du cadre."
           % (D.fmt(p.DEGAGEMENT_DOUILLE), D.fmt(p.ETUVE_Y, 1), a_conf, D.fmt(p.ETUVE_GARDE)),
           2.9, "middle")
    s.text(124.0, 283.5, "En trait mixte a deux tirets, le coin %s en fin de course : %s depuis le repos."
           % (R["coin"], D.fmt(p.COIN_COURSE, 1)), 2.9, "middle")

    # ================================================== niveaux
    lignes = [
        (R["traverse"], "traverse, %d plaques" % p.TRAVERSE_N, p.Z_TRAVERSE_BAS, p.Z_TRAVERSE_HAUT),
        (R["plaquette_haute"], "plaque de frottement haute", p.Z_COIN_HAUT, p.Z_TRAVERSE_BAS),
        (R["coin"], "coin au repos, a y = 0", p.Z_PLAQ_COUL, p.Z_COIN_HAUT),
        (R["plaquette_basse"], "plaque de frottement basse, y = 0", p.Z_COULISSEAU_HAUT, p.Z_PLAQ_COUL),
        (R["coulisseau"], "coulisseau, a y = 0", p.Z_COULISSEAU_BAS, p.Z_COULISSEAU_HAUT),
        (R["tourillon"], "tourillon", p.Z_TOURILLON_BAS, p.Z_TOURILLON_BAS + p.TOURILLON_L),
        (R["pile_belleville"], "pile Belleville libre (+ cales V4)", p.Z_PILE_BAS, p.Z_COULISSEAU_BAS),
        (R["poussoir"], "poussoir, %d plateaux, goupilles V3" % p.POUSSOIR_N, p.Z_POUSSOIR_BAS, p.Z_POUSSOIR_HAUT),
        (R["patin_charge"], "patin de charge", p.Z_POUTRE_HAUT, p.Z_PATIN_CHARGE_HAUT),
        (R["poutre"], "poutrelle (eprouvette)", p.Z_POUTRE_BAS, p.Z_POUTRE_HAUT),
        (R["plat_renfort"], "plats colles", p.Z_PLAT_BAS, p.Z_POUTRE_BAS),
        (R["patin_appui"], "patins d appui, x = +/- %s" % D.fmt(p.X_APPUI), p.Z_PATIN_BAS, p.Z_PLAT_BAS),
    ]
    D.table(s, 322.0, 152.5, "NIVEAUX (z depuis le chant bas des flancs)",
            ["rep.", "piece", "z bas", "z haut"],
            [(r_, n_, D.fmt(a_, 1), D.fmt(b_, 1)) for (r_, n_, a_, b_) in lignes]
            + [(R["vis"], "tige M%s : axe" % D.fmt(p.VIS_D), D.fmt(zv, 1), "")],
            [10.0, 52.0, 12.0, 12.0], h=4.2)

    # ================================================== perspective
    iso_path = os.path.join(HERE, "out", "iso.json")
    if os.path.isfile(iso_path):
        polys = json.load(open(iso_path))["ensemble"]
        xs = [q[0] for pl in polys for q in pl]
        ys = [q[1] for pl in polys for q in pl]
        cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
        ech = 1.0 / 7.0
        ox, oy = 318.0, 78.0
        s.text(ox, 18.0, "perspective  (sans echelle)", 3.6, "middle", weight="bold")
        # TechDraw.projectEx pose X = (1, -1, 0)/racine 2 : son Y descend en z.
        # On tourne de 180 degres (rotation, pas miroir) pour avoir z vers le haut.
        def pz(q):
            return ox - ech * (q[0] - cx), oy + ech * (q[1] - cy)
        for pl in polys:
            s.path(" ".join(("M " if i == 0 else "L ") + "%.2f %.2f" % pz(q) for i, q in enumerate(pl)),
                   0.22)
        # un crochet d'etuve (en haut, cote y > 0), pour son repere
        xf_, zf_ = p.pied_debout_fente()
        x0c = xf_ - p.CROCHET_Z_APPUI - p.CROCHET_DENT_H
        pc = pz(a00_iso((x0c + p.CROCHET_Z_APPUI - p.CROCHET_BANDE / 2.0, p.PIED_FENTE_Y,
                         p.H_FLANC - p.CROCHET_Z_PAROI - p.CROCHET_S / 2.0)))
        cb = (pc[0] + 14.0, pc[1] - 8.0)
        dd = math.hypot(cb[0] - pc[0], cb[1] - pc[1])
        s.line(pc[0], pc[1], cb[0] - 3.6 * (cb[0] - pc[0]) / dd, cb[1] - 3.6 * (cb[1] - pc[1]) / dd,
               D.TRAIT_FIN)
        s._p('<circle cx="%.3f" cy="%.3f" r="0.55" fill="#000"/>' % pc)
        a00_bulle_seule(s, cb, R["crochet"])
        s.text(ox, 140.0, "Pieds couches, pieds en V et crochets d etuve figures ensemble :", 2.8, "middle")
        s.text(ox, 144.0, "debout, les pieds couches restent sur la paillasse.", 2.8, "middle")
        # la perspective vient du dernier build_freecad : la dater, et le dire
        # si params.py ou parts.py ont change depuis
        # date et empreinte ecrites par build_freecad dans iso.json : les dates
        # de fichiers ne survivent pas a git
        import time
        iso_d = json.load(open(iso_path))
        if iso_d.get("empreinte"):
            perime = iso_d["empreinte"] != outils.empreinte_modele()
            date_iso = iso_d.get("date_calcul", "?")
        else:
            t_iso = os.path.getmtime(iso_path)
            perime = t_iso < max(os.path.getmtime(p.__file__), os.path.getmtime(P.__file__))
            date_iso = time.strftime("%d/%m/%Y", time.localtime(t_iso))
        if perime:
            print("ATTENTION : out/iso.json a ete construit sur d'autres params.py ou parts.py :"
                  " perspective de la planche 00 perimee, relancer build_freecad.py")
        s.text(ox + ech * (max(xs) - min(xs)) / 2.0, 135.0, "modele 3D du %s%s"
               % (date_iso, " : PERIME" if perime else ""),
               2.4, "end")

    return s.save(os.path.join(OUT, "00_assemblage.svg"))


def index_html(fichiers):
    corps = []
    for f in fichiers:
        nom = os.path.basename(f)
        with open(f) as fh:
            svg = fh.read()
        svg = svg.split("?>")[-1]
        corps.append('<div class="page">%s</div>' % svg)
    html = ("<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Banc de flexion - plans</title><style>"
            "@page{size:A3 landscape;margin:0}"
            "body{margin:0;padding:0;background:#fff}"
            ".page{page-break-after:always;width:420mm;height:297mm;overflow:hidden}"
            ".page svg{width:420mm;height:297mm;display:block}"
            "</style></head><body>%s</body></html>" % "".join(corps))
    path = os.path.join(OUT, "plans.html")
    with open(path, "w") as f:
        f.write(html)
    return path


def main():
    fichiers = [plan_assemblage(), plan_flanc(), plan_coulisseau(), plan_traverse(),
                plan_patins(), plan_pied(), plan_petites(), plan_chape()]
    for f in fichiers:
        print("  ", os.path.basename(f))
    print("  ", os.path.basename(index_html(fichiers)))


if __name__ == "__main__":
    main()
