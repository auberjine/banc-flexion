# -*- coding: utf-8 -*-
"""
Geometrie de chaque piece du banc, construite a partir de params.py.

Chaque piece est un profil 2D extrude puis place dans le repere global. Les
percages et rainures hors du plan du profil passent par un rappel
`features(solid, Part, Vector)` execute sous FreeCAD.

Le profil d'une piece est sa geometrie FINIE : c'est elle que voient le 3D,
les plans et les calculs. Quand la decoupe laser doit livrer autre chose --
une surepaisseur a fraiser --, la piece porte en plus un `dxf_profile`, que
l'export DXF prend a la place du profil (voir PartSpec).

Ce module ne depend PAS de FreeCAD : il sert aussi aux DXF et aux plans.
"""

import math
import geom2d as G
import params as p


# ============================================================ lignes de bielle

def ligne_bielle(cote):
    """
    (dessus_montant, dessus_noeud, dessous_montant, dessous_noeud) d'une bielle.
    cote : +1 a droite, -1 a gauche.
    """
    s = 1.0 if cote > 0 else -1.0
    a = (s * p.X_FENETRE, p.Z_MEMB_HAUTE)
    b = (s * p.X_NOEUD, p.Z_BIELLE_NOEUD)
    dx = abs(a[0] - b[0])
    dz = abs(a[1] - b[1])
    L = math.hypot(dx, dz)
    dv = p.W_BIELLE * L / dx               # decalage vertical d'une largeur perpendiculaire
    return a, b, (a[0], a[1] - dv), (b[0], b[1] - dv)


def bielle_angle():
    a, b, _, _ = ligne_bielle(1)
    return math.atan2(abs(a[1] - b[1]), abs(a[0] - b[0]))


def profondeur_treillis():
    """
    Bras de levier du treillis : axe de la membrure haute moins axe du noeud.
    Z_MEMB_HAUTE est le DESSOUS de la membrure, son axe est donc plus haut.
    """
    _, b, _, bn = ligne_bielle(1)
    return (p.Z_MEMB_HAUTE + p.W_MEMBRURE / 2.0) - (b[1] + bn[1]) / 2.0


# ============================================================ ajourage

def ajour_cercles(cote):
    """
    Trous ronds decroissants inscrits dans le coin compris entre le dessous de la
    membrure haute et le dessus de bielle. La membrure et la bielle gardent leur
    section pleine : les trous sont tangents a des droites decalees du ligament.
    """
    s = 1.0 if cote > 0 else -1.0
    haut, noeud, _, _ = ligne_bielle(cote)
    dx = abs(haut[0] - noeud[0])
    dz = abs(haut[1] - noeud[1])
    demi = math.atan2(dz, dx) / 2.0
    k = math.sin(demi)
    g = p.AJOUR_LIGAMENT
    d_off = g / k                                   # recul du sommet efficace
    d_max = dx / math.cos(demi)                     # bissectrice jusqu'au flanc du noeud

    d = (d_max - g + k * d_off) / (1.0 + k)
    trous = []
    for _ in range(12):
        r = k * (d - d_off)
        if r < p.AJOUR_RMIN or d <= d_off:
            break
        cx = haut[0] - s * d * math.cos(demi)
        cz = haut[1] - d * math.sin(demi)
        trous.append((cx, cz, r))
        d = (d * (1.0 - k) + g) / (1.0 + k)
    return trous


def ajour_membrure_basse():
    if not p.AJOUR_BASSE:
        return []
    x0 = -(p.X_APPUI - p.AJOUR_BASSE_MARGE)
    n = p.AJOUR_BASSE_N
    pas = (2.0 * abs(x0)) / (n - 1)
    return [(x0 + i * pas, p.AJOUR_BASSE_Z, p.AJOUR_BASSE_R) for i in range(n)]


# ============================================================ flanc

def coin_encoche(c, p0, ua, ub):
    """
    Encoche de pied debout dans un coin du flanc, inclinee de PIED_DEBOUT_ANGLE
    sur le grand cote (l axe x). Le contour arrive au coin le long de ua
    (vecteur unitaire du chant d arrivee, oriente en s eloignant du coin) et
    repart le long de ub. Chaque joue sort sur son chant la ou elle le coupe,
    le fond est a PIED_DEBOUT_PROF du coin vif le long de l encoche, ses angles
    degages. Largeur ENCOCHE_FLANC_B : la tole reelle du pied (S355,
    EP_TOLE_REELLE_S355) plus PIED_JEU.
    """
    w2 = p.ENCOCHE_FLANC_B / 2.0
    ang = math.radians(p.PIED_DEBOUT_ANGLE)
    # direction de l encoche : composante cos sur le chant long (celui des deux
    # qui est selon x), sin sur le chant court, toutes deux vers la matiere
    if abs(ua[0]) > 0.5:
        d = (ua[0] * math.cos(ang), ub[1] * math.sin(ang))
    else:
        d = (ub[0] * math.cos(ang), ua[1] * math.sin(ang))
    n = (-d[1], d[0])
    if n[0] * ua[0] + n[1] * ua[1] < 0:
        n = (-n[0], -n[1])                                 # normale cote chant d arrivee
    t = p.PIED_DEBOUT_PROF

    def bouche(u, v, sn):
        # point ou la joue decalee de sn.w2 coupe le chant de direction u, dont
        # la normale interieure est v : (d.t + sn.n.w2) . v = 0
        tt = -sn * w2 * (n[0] * v[0] + n[1] * v[1]) / (d[0] * v[0] + d[1] * v[1])
        px, pz = d[0] * tt + sn * n[0] * w2, d[1] * tt + sn * n[1] * w2
        m = px * u[0] + pz * u[1]
        return (p0[0] + u[0] * m, p0[1] + u[1] * m)

    ma = bouche(ua, ub, +1.0)
    mb = bouche(ub, ua, -1.0)
    c.add(ma[0], ma[1], 1.0)
    c.add(p0[0] + d[0] * t + n[0] * w2, p0[1] + d[1] * t + n[1] * w2, p.PIED_R, relief='diag')
    c.add(p0[0] + d[0] * t - n[0] * w2, p0[1] + d[1] * t - n[1] * w2, p.PIED_R, relief='diag')
    c.add(mb[0], mb[1], 1.0)


def flanc_contour():
    """
    Rectangle a encoches de mi-bois : deux dans le chant bas pour les pieds de
    la position couchee, une dans chacun des quatre coins, a PIED_DEBOUT_ANGLE
    du grand cote, pour les memes pieds en position debout (le conge de coin
    n existe plus qu en reference EF). Le flanc reste symetrique en x.
    """
    L2 = p.L_FLANC / 2.0
    H = p.H_FLANC
    w2 = p.ENCOCHE_FLANC_B / 2.0       # encoche du flanc : tole REELLE du pied (S355) + PIED_JEU
    d = p.PIED_CROIX_FLANC
    c = G.Contour("flanc contour")

    def coin(p0, ua, ub):
        if p.FLANC_ENCOCHES:
            coin_encoche(c, p0, ua, ub)
        else:
            c.add(p0[0], p0[1], p.R_COIN)

    coin((-L2, 0.0), (0.0, 1.0), (1.0, 0.0))
    # chant bas, de gauche a droite
    for xp in ((-p.PIED_X_POS, p.PIED_X_POS) if p.FLANC_ENCOCHES else ()):
        c.add(xp - w2, 0.0, 1.0)
        c.add(xp - w2, d, p.PIED_R, relief='diag')
        c.add(xp + w2, d, p.PIED_R, relief='diag')
        c.add(xp + w2, 0.0, 1.0)
    coin((L2, 0.0), (-1.0, 0.0), (0.0, 1.0))
    coin((L2, H), (0.0, -1.0), (-1.0, 0.0))
    coin((-L2, H), (1.0, 0.0), (0.0, -1.0))
    return c.build()


def flanc_fenetre():
    """Fenetre basse : loge la poutre, les bossages d'appui y font saillie."""
    bg, _, _ = G.crown(-p.X_APPUI, p.Z_MEMB_BASSE, p.Z_BOSSAGE,
                       p.BOSSAGE_R, p.BOSSAGE_CONGE, True)
    bd, _, _ = G.crown(p.X_APPUI, p.Z_MEMB_BASSE, p.Z_BOSSAGE,
                       p.BOSSAGE_R, p.BOSSAGE_CONGE, True)
    _, _, bas_d_m, bas_d_n = ligne_bielle(+1)
    _, _, bas_g_m, bas_g_n = ligne_bielle(-1)

    c = G.Contour("fenetre")
    c.add(-p.X_FENETRE, p.Z_MEMB_BASSE, p.R_FEN_BAS)
    c.raw(bg)
    c.raw(bd)
    c.add(p.X_FENETRE, p.Z_MEMB_BASSE, p.R_FEN_BAS)
    c.add(bas_d_m[0], bas_d_m[1], p.R_FEN_MONTANT)
    c.add(bas_d_n[0], bas_d_n[1], p.R_FEN_NOEUD)
    c.add(p.X_NOEUD, p.Z_NOEUD_BAS, p.R_FEN_NOEUD_BAS)
    c.add(-p.X_NOEUD, p.Z_NOEUD_BAS, p.R_FEN_NOEUD_BAS)
    c.add(bas_g_n[0], bas_g_n[1], p.R_FEN_NOEUD)
    c.add(bas_g_m[0], bas_g_m[1], p.R_FEN_MONTANT)
    return c.build()


def flanc_trous():
    """Percages du flanc : (x, z, diametre, role)."""
    xc = p.TROU_COIN[0]
    t = []
    for sx in (-1, 1):
        t.append((sx * xc, p.TROU_COIN[1], p.D_VIS, "entretoise basse"))
        t.append((sx * xc, p.TROU_COIN_HAUT_Z, p.D_VIS, "entretoise haute"))
        haut, noeud, bm, bn = ligne_bielle(sx)
        t.append(((haut[0] + noeud[0]) / 2.0,
                  (haut[1] + noeud[1] + bm[1] + bn[1]) / 4.0, p.D_VIS, "entretoise de bielle"))
    # Les deux tirants de la chape, de part et d'autre de la vis, dans le plan
    # de son axe. Ils traversent LES DEUX flancs et une entretoise de cadre entre
    # eux : la commande se monte du cote que l'on veut, en retournant le coin.
    for (x, z) in p.TROU_SUPPORT:
        t.append((x, z, p.D_VIS, "entretoise et tirant de chape"))
    if p.ENTR_SOMMET:
        t.append((0.0, p.Z_ENTR_SOMMET, p.D_VIS, "entretoise de sommet"))
    return t


def flanc_lumieres():
    """Deux lumieres de guidage du coulisseau, de part et d'autre de la fente."""
    return [G.slot(sx * p.GUIDE_X - p.LUMIERE_B / 2.0, p.LUMIERE_Z0,
                   sx * p.GUIDE_X + p.LUMIERE_B / 2.0, p.LUMIERE_Z1)
            for sx in (-1.0, 1.0)]


def flanc_mortaise():
    """
    Mortaise de traverse. Les tenons y prennent appui sur l'arete SUPERIEURE :
    c'est par la que les 12 kN entrent dans le flanc, juste sous la membrure
    haute. Plus aucune vis de traverse.
    """
    jz = p.TRAVERSE_JEU / 2.0
    jx = p.TRAVERSE_JEU_X / 2.0
    r = p.TRAVERSE_R_MORT
    # CONGES et non degagements. Un degagement d'angle ne se justifie que si la
    # piece conjuguee doit venir porter DANS l'angle ; ici le paquet de tenons a
    # 2 mm de jeu par cote, il n'approche jamais des coins. En revanche il porte
    # sur l'arete du haut, et un os de chien y creuserait une entaille juste au
    # bout de la ligne d'appui : le calcul EF l'a chiffree a 209 MPa contre 133.
    # Le jeu valant deux fois le rayon, l'arete droite fait exactement la
    # largeur du paquet. La mortaise est taillee sur le paquet REEL
    # (TRAVERSE_LX_REEL, tole mesuree) : six toles a +0,5 n'entreraient plus
    # dans une mortaise calculee sur la cote nominale.
    lx2 = p.TRAVERSE_LX_REEL / 2.0
    return G.rounded_rect(-lx2 - jx, p.Z_TAB0 - jz, lx2 + jx, p.Z_TAB1 + jz, r)


def flanc_fente_coin():
    """Passage du coin de commande et de sa vis, au centre du noeud."""
    return G.rounded_rect(-p.FENTE_COIN_B / 2.0, p.FENTE_COIN_Z0,
                          p.FENTE_COIN_B / 2.0, p.FENTE_COIN_Z1, p.FENTE_COIN_R)


def flanc_profile():
    outer = flanc_contour()
    holes = [flanc_fenetre()]
    for cote in (-1, 1):
        for (cx, cz, r) in ajour_cercles(cote):
            holes.append(G.circle(cx, cz, r))
    for (cx, cz, r) in ajour_membrure_basse():
        holes.append(G.circle(cx, cz, r))
    for lum in flanc_lumieres():
        holes.append(lum)
    holes.append(flanc_fente_coin())
    holes.append(flanc_mortaise())
    for (x, z, d, _r) in flanc_trous():
        holes.append(G.circle(x, z, d / 2.0))
    return outer, holes


def flanc_gravure():
    """
    Graduation de lecture de charge, gravee le long de la lumiere. La loi des
    rondelles Belleville n'est pas lineaire : les traits ne sont pas equidistants.

    Le zero est le HAUT DE TETE de guide, pile libre : c'est la tangente
    superieure du cylindre qu'on voit dans la lumiere, et elle se lit comme une
    bulle de niveau. Prendre le dessus du coulisseau, invisible entre les
    flancs, mettait la moitie des traits au dessus de la lumiere.
    """
    out = []
    x0 = p.GUIDE_X + p.LUMIERE_B / 2.0 + 2.5
    z_ref = p.Z_GUIDE + p.GUIDE_TETE_D / 2.0
    for i in range(0, 13):
        z = z_ref - p.pile_ecrasement(i * 1000.0)
        lg = 8.0 if i % 2 == 0 else 4.5
        out.append([('L', (x0, z), (x0 + lg, z))])
    return out


# ============================================================ tete de charge

def traverse_profile(brut=False):
    """
    Plaque de traverse, profil dans le plan (y, z), extrude selon x.

    Le CHANT DU BAS est le plan de glissement du coin : les plaques sont
    fraisees ensemble, jointives, et forment une portee continue. Deux tenons
    par plaque s'engagent dans une mortaise du flanc et prennent appui sur son
    arete SUPERIEURE : l'effort monte droit dans la membrure haute, sans une
    seule vis ni un seul taraudage.

    brut=False : la plaque FINIE (3D, plans, calculs).
    brut=True  : la plaque telle que la decoupe le laser, chant du bas abaisse
    de TRAVERSE_SUREP (brut 65 / 39), que le fraisage en paquet ramene a la
    cote finie (64 / 38). Seul ce chant bouge : tenons, coiffe et trou de tirant
    restent a leur place. C'est le profil du DXF (PartSpec.dxf_profile).
    """
    yb = p.ECART_FLANCS / 2.0 - p.TRAVERSE_JEU_Y / 2.0   # epaulement sur la face interieure
    yt = p.Y_FLANC_EXT + p.TRAVERSE_TAB_DEP
    z0, z1 = p.Z_TRAVERSE_BAS, p.Z_TRAVERSE_HAUT
    if brut:
        z0 -= p.TRAVERSE_SUREP
    ta, tb = p.Z_TAB0, p.Z_TAB1
    c = G.Contour("traverse")
    c.add(-yb, z0, 2.0)
    c.add(yb, z0, 2.0)
    for sy in (1.0, -1.0):
        if sy < 0:
            c.add(-yb, z1, 2.0)
        # pied de tenon : DEGAGEMENT et non conge. Un conge deborderait de
        # l'epaulement et viendrait mordre la face interieure du flanc ; le
        # degagement ouvre l'angle et supprime l'amorce de rupture.
        c.add(sy * yb, ta if sy > 0 else tb, p.TRAVERSE_R_PIED, relief='diag')
        c.add(sy * yt, ta if sy > 0 else tb, 2.0)
        c.add(sy * yt, tb if sy > 0 else ta, 2.0)
        c.add(sy * yb, tb if sy > 0 else ta, p.TRAVERSE_R_PIED, relief='diag')
        if sy > 0:
            c.add(yb, z1, 2.0)
    holes = [G.circle(0.0, p.TRAVERSE_TIRANT_Z, p.TRAVERSE_TIRANT_D / 2.0)]
    return c.build(), holes


def coulisseau_profile():
    """
    Vue de dessus : un simple bloc. Les pattes de guidage ont disparu, ce sont
    les tetes des quatre CHC M8 (GUIDE_VIS_D) qui guident maintenant. La piece
    se reduit a un parallelepipede, un plan incline, un alesage et quatre
    taraudages dans les faces laterales.
    """
    return G.rounded_rect(-p.COULISSEAU_L / 2.0, -p.POUSSOIR_B / 2.0,
                          p.COULISSEAU_L / 2.0, p.POUSSOIR_B / 2.0, 4.0), []


def guide_profile():
    """Tete de la vis de guidage, cylindre de GUIDE_TETE_D, extrude selon y."""
    return G.circle(p.GUIDE_X, p.Z_GUIDE, p.GUIDE_TETE_D / 2.0), []


def poussoir_contour():
    return G.rounded_rect(-p.POUSSOIR_L / 2.0, -p.POUSSOIR_B / 2.0,
                          p.POUSSOIR_L / 2.0, p.POUSSOIR_B / 2.0, 4.0)


def poussoir_trous_vis():
    """Les deux trous de passage des vis H M6 du poussoir, a x = +/- POUSSOIR_VIS_X,
    POUSSOIR_VIS_PASSAGE decoupes au laser."""
    return [G.circle(sx * p.POUSSOIR_VIS_X, 0.0, p.POUSSOIR_VIS_PASSAGE / 2.0)
            for sx in (-1.0, 1.0)]


def poussoir_profile():
    """
    Plateau perce : les trois forment l'alesage du tourillon, le patin de
    charge fait fond. Les deux trous de passage (POUSSOIR_VIS_PASSAGE) recoivent
    les vis H M6 qui serrent les trois plateaux en un bloc.
    """
    return (poussoir_contour(),
            [G.circle(0.0, 0.0, p.ALESAGE_D / 2.0)] + poussoir_trous_vis())


def coin_profile():
    """
    Coin de commande, profil dans le plan (y, z), extrude selon x.
    Dessus plat sous la traverse, dessous incline sur la tete du coulisseau.
    Dessine a sa position de REPOS : le bout mince affleure le coulisseau.
    Le bout EPAIS est du cote oppose a la chape : le coin avance vers elle.

    Les DEUX faces portent une plaquette de bronze, chacune tenue entre deux
    REBORDS qui prennent son entrainement dans l'axe de la vis. Leur pied
    garde l'angle de la fraise (conge PLAQ_REBORD_R au plus), sans degagement :
    c'est le logement, plus long de 2.PLAQ_JEU, qui laisse l'angle de la
    plaquette hors du conge.
    """
    zt = p.Z_COIN_HAUT
    zr = zt + p.PLAQ_REBORD_H
    w = p.PLAQ_REBORD_L
    dr = p.PLAQ_REBORD_DROP
    a = math.radians(p.COIN_ANGLE)
    sa, ca = math.sin(a), math.cos(a)

    def zb(y):
        """Dessous du coin, siege de la plaquette basse, avant rebord."""
        return zt - p.COIN_T_BOUT_MINCE - (p.COIN_Y1 - y) * p.COIN_TAN

    # Pieds des rebords du bas. Leur face interieure est NORMALE A LA PENTE et
    # non verticale : le chant de la plaquette l'est aussi, et deux faces qui
    # ne sont pas paralleles ne portent que sur une arete. Dessinees verticales,
    # elles mordaient la plaquette de 1,1 mm en bas. La normale a la pente,
    # vers le bas, est (sin a, -cos a) : les DEUX pieds s'en deduisent par
    # +h.sin a en y (le gauche etait en -h.sin a, face inclinee de 24 degres
    # sur la normale : la plaquette n'y portait que par l'arete du degagement).
    wb = p.PLAQ_REBORD_L_BAS                 # rebords du bas, plus larges
    y0, y1 = p.COIN_Y0 + wb, p.COIN_Y1 - wb
    h = p.PLAQ_REBORD_H

    c = G.Contour("coin")
    c.add(p.COIN_Y0, zr, 1.0)
    c.add(p.COIN_Y0 + w, zr, 1.0)
    c.add(p.COIN_Y0 + w, zt, p.PLAQ_REBORD_R)
    c.add(p.COIN_Y1 - w, zt, p.PLAQ_REBORD_R)
    c.add(p.COIN_Y1 - w, zr, 1.0)
    c.add(p.COIN_Y1, zr, 1.0)
    c.add(p.COIN_Y1, zb(p.COIN_Y1) - dr, 1.0)
    c.add(y1 + h * sa, zb(y1) - h * ca, 1.0)
    c.add(y1, zb(y1), p.PLAQ_REBORD_R)
    c.add(y0, zb(y0), p.PLAQ_REBORD_R)
    c.add(y0 + h * sa, zb(y0) - h * ca, 1.0)
    c.add(p.COIN_Y0, zb(p.COIN_Y0) - dr, 1.0)
    return c.build(), []


def f_coin(solid, Part, Vector):
    """
    Taraudage M16 sur COIN_TARAUD_L depuis le bout EPAIS, puis percage de
    passage au dela. Le taraud debouche ainsi dans un trou plus grand : les
    copeaux s'evacuent vers l'avant et il n'y a que 5 d a tarauder.

    Repere local du profil 'yz' : X = y global, Y = z global, Z = x global.
    """
    b2 = p.COIN_B / 2.0
    out = solid.cut(Part.makeCylinder(
        p.VIS_D / 2.0, p.COIN_L + 4.0,
        Vector(p.COIN_Y0 - 2.0, p.Z_VIS, b2), Vector(1, 0, 0)))
    return out.cut(Part.makeCylinder(
        p.VIS_PASSAGE_D / 2.0, p.COIN_L - p.COIN_TARAUD_L + 4.0,
        Vector(p.COIN_Y0 + p.COIN_TARAUD_L, p.Z_VIS, b2), Vector(1, 0, 0)))


def plaquette_haute_profile():
    """
    Plaquette de bronze du dessus, prise entre les deux rebords du coin.
    Profil dans le plan (x, y), extrude selon z.

    Piece usinee : rectangle plein PLAQ_B x PLAQ_L_HAUT x PLAQ_EP, sans trou.
    Pas une seule vis : le percage de la tige prend le milieu du coin. Ce sont
    les rebords qui prennent l'entrainement ; quelques points de silicone haute
    temperature la tiennent au montage. PAS d'epoxy : bronze et acier ne se
    dilatent pas pareil.
    """
    c = G.Contour("plaquette haute")
    b2 = p.PLAQ_B / 2.0
    c.add(-b2, p.PLAQ_HAUT_Y0)
    c.add(b2, p.PLAQ_HAUT_Y0)
    c.add(b2, p.PLAQ_HAUT_Y1)
    c.add(-b2, p.PLAQ_HAUT_Y1)
    return c.build(), []


def plaquette_basse_profile():
    """
    Plaquette de bronze du dessous, prise entre les deux rebords du coin.
    Profil dans le plan (x, y), extrude selon z, puis bascule de COIN_ANGLE
    pour se coucher sur la pente. Ses cotes en y sont donc prises SUR LA PENTE,
    d'ou sa longueur PLAQ_L_BAS, plus grande que celle de la haute.
    """
    c = G.Contour("plaquette basse")
    b2 = p.PLAQ_B / 2.0
    c.add(-b2, p.PLAQ_BAS_S0)
    c.add(b2, p.PLAQ_BAS_S0)
    c.add(b2, p.PLAQ_BAS_S1)
    c.add(-b2, p.PLAQ_BAS_S1)
    return c.build(), []


def pile_profile():
    """
    Encombrement de la pile. La geometrie reelle est faite par f_pile : une
    rondelle Belleville n'est pas une rondelle plate, et un tube plein ne
    montre ni la course ni le sens d'empilage.
    """
    return (G.circle(0.0, 0.0, p.RESSORT_DE / 2.0),
            [G.circle(0.0, 0.0, p.RESSORT_DI / 2.0)])


def f_pile(solid, Part, Vector):
    """
    Les RESSORT_N rondelles reelles, a la place du tube.

    Une Belleville est un TRONC DE CONE : sa section meridienne est un
    parallelogramme d'epaisseur RESSORT_T, incline de RESSORT_H0 sur la
    largeur (De - Di) / 2. En SERIE, les rondelles sont tete-beche : chacune
    ajoute l0 = h0 + t a la hauteur libre, et la pile porte alternativement
    par le GRAND puis par le PETIT diametre. C'est cet empilage, et lui seul,
    qui donne la course ; le meme paquet monte en parallele ferait douze fois
    l'effort pour un douzieme du debattement.

    La premiere rondelle est posee grand diametre EN BAS : elle s'appuie sur
    le plateau du poussoir par un cercle de RESSORT_DE, et non par le bord de
    l'alesage.
    """
    ri, re = p.RESSORT_DI / 2.0, p.RESSORT_DE / 2.0
    h0, t = p.RESSORT_H0, p.RESSORT_T
    rondelles = []
    for k in range(p.RESSORT_N):
        z0 = k * p.RESSORT_L0
        a, b = (re, ri) if k % 2 == 0 else (ri, re)   # bas, haut
        pts = [(a, z0), (b, z0 + h0), (b, z0 + h0 + t), (a, z0 + t)]
        vs = [Vector(x, 0.0, z) for x, z in pts]
        f = Part.Face(Part.makePolygon(vs + [vs[0]]))
        rondelles.append(f.revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360.0))
    return Part.makeCompound(rondelles)


def support_profile():
    """
    Platine de butee de la vis, profil dans le plan (x, z), extrude selon y.

    Une simple tole, deux fois. La platine porte sur deux entretoises
    tubulaires de part et d'autre de la vis, dans le plan de son axe, et le
    coin la POUSSE contre le flanc : tout est en compression, les tirants ne
    voient que la precharge. Le contour s'evase vers l'alesage, la ou le moment
    est maximal, et se resserre aux deux bouts, ou il est nul.
    """
    b2 = p.SUPPORT_B / 2.0
    e2 = p.SUPPORT_B_BOUT / 2.0
    x0, x1 = p.SUPPORT_X0, p.SUPPORT_X1
    zv = p.Z_VIS
    rc = p.SUPPORT_R_COIN
    c = G.Contour("platine de butee")
    c.add(x0, zv - e2, rc)
    c.add(0.0, zv - b2, p.SUPPORT_R_CONGE)
    c.add(x1, zv - e2, rc)
    c.add(x1, zv + e2, rc)
    c.add(0.0, zv + b2, p.SUPPORT_R_CONGE)
    c.add(x0, zv + e2, rc)
    holes = [G.circle(0.0, zv, p.VIS_PASSAGE_D / 2.0)]
    for (x, z) in p.TROU_SUPPORT:
        holes.append(G.circle(x, z, p.D_VIS / 2.0))
    return c.build(), holes


def vis_profile():
    """Vis de commande : profil dans le plan (x, z), extrude selon y."""
    return G.circle(0.0, 0.0, p.VIS_D / 2.0), []


def tourillon_profile():
    return G.circle(0.0, 0.0, p.TOURILLON_D / 2.0), []


# ============================================================ pieces collees

def patin_appui_profile():
    """Patin d'appui, vue de dessus. La rainure (RAINURE_B x RAINURE_P) est fraisee apres decoupe."""
    return G.rounded_rect(-p.PATIN_L / 2.0, -p.PATIN_B / 2.0,
                          p.PATIN_L / 2.0, p.PATIN_B / 2.0, p.PATIN_R), []


def patin_charge_profile():
    """
    Patin colle sur la poutre ; il fait FOND au poussoir. Aucun trou : sa
    longueur PATIN_CHARGE_L (selon x) laisse passer entre ses bouts les tetes
    des vis du poussoir.
    """
    return (G.rounded_rect(-p.PATIN_CHARGE_L / 2.0, -p.PATIN_CHARGE_B / 2.0,
                           p.PATIN_CHARGE_L / 2.0, p.PATIN_CHARGE_B / 2.0, p.PATIN_CHARGE_R),
            [])


def plat_profile():
    """Plat de renfort : piece du commerce, feuillard scie a longueur, angles vifs (PLAT_R)."""
    return G.rounded_rect(-p.PLAT_L / 2.0, -p.PLAT_B / 2.0,
                          p.PLAT_L / 2.0, p.PLAT_B / 2.0, p.PLAT_R), []


def entretoise_profile():
    return (G.circle(0.0, 0.0, p.ENTRETOISE_DE / 2.0),
            [G.circle(0.0, 0.0, p.ENTRETOISE_DI / 2.0)])


def pied_profile():
    """
    Pied vertical, plan (y, z), trace autour de son plan de pose z = 0 : deux
    encoches descendent du chant haut aux deux flancs, deux bossages aux DEUX
    BOUTS du chant bas posent sur les tablettes des crochets d etuve. Entre les
    deux, la plaque est AJOUREE : deux membrures et trois montants suffisent
    a porter 40 kg.
    """
    y2 = p.PIED_Y / 2.0
    w2 = p.ENCOCHE_PIED_B / 2.0        # encoche : tole REELLE du flanc (42CrMo4) + PIED_JEU
    h = p.PIED_H                       # le pied monte de PIED_CROIX au dessus du fond d encoche du flanc
    hb = p.PIED_BOSSAGE_H
    bb = p.PIED_BOSSAGE_B
    c = G.Contour("pied")
    # chant bas : bossage au bout, creux, bossage a l autre bout
    fb, fw, fh = p.PIED_FENTE_BORD, p.PIED_FENTE_B, p.PIED_FENTE_H
    c.add(-y2, 0.0, p.PIED_COIN_R)
    # fente de calage : la dent de l appui du crochet y entre
    c.add(-y2 + fb, 0.0, 0.5)
    c.add(-y2 + fb, fh, 0.5)
    c.add(-y2 + fb + fw, fh, 0.5)
    c.add(-y2 + fb + fw, 0.0, 0.5)
    c.add(-y2 + bb, 0.0, 2.0)
    c.add(-y2 + bb, hb, 2.0)
    c.add(y2 - bb, hb, 2.0)
    c.add(y2 - bb, 0.0, 2.0)
    c.add(y2 - fb - fw, 0.0, 0.5)
    c.add(y2 - fb - fw, fh, 0.5)
    c.add(y2 - fb, fh, 0.5)
    c.add(y2 - fb, 0.0, 0.5)
    c.add(y2, 0.0, p.PIED_COIN_R)
    # chant haut, de droite a gauche, avec les deux encoches des flancs
    c.add(y2, h, 6.0)
    # chaque encoche : joue a PIED_JEU, puis un NODE de PIED_NODE_L qui serre le
    # flanc de PIED_NODE_SERRE par cote, centre dans la profondeur, puis le fond
    # degage. Rampes a 45 degres de part et d autre du node. Le passage au node
    # vaut EP_TOLE_REELLE_42 - 2 x PIED_NODE_SERRE (7,8 sur une tole de 8) : il
    # recoit le flanc, en 42CrMo4.
    wn = p.EP_TOLE_REELLE_42 / 2.0 - p.PIED_NODE_SERRE
    zb = h - p.PIED_CROIX
    z1 = zb + (p.PIED_CROIX - p.PIED_NODE_L) / 2.0      # bas du node
    z2 = z1 + p.PIED_NODE_L                              # haut du node
    dr = w2 - wn                                         # rampe
    for yf in (p.Y_FLANC, -p.Y_FLANC):
        for sy in (1.0, -1.0):
            pts = [(yf + sy * w2, h), (yf + sy * w2, z2 + dr), (yf + sy * wn, z2),
                   (yf + sy * wn, z1), (yf + sy * w2, z1 - dr), (yf + sy * w2, zb)]
            if sy > 0:
                c.add(pts[0][0], pts[0][1], 1.0)
                for q in pts[1:5]:
                    c.add(q[0], q[1], 0.0)
                c.add(pts[5][0], pts[5][1], p.PIED_R, relief='diag')
            else:
                c.add(pts[5][0], pts[5][1], p.PIED_R, relief='diag')
                for q in reversed(pts[1:5]):
                    c.add(q[0], q[1], 0.0)
                c.add(pts[0][0], pts[0][1], 1.0)
    c.add(-y2, h, 6.0)
    holes = []
    if p.PIED_AJOUR:
        r = p.PIED_AJOUR_R
        z0 = hb + p.PIED_AJOUR_CHORD
        z1a = h - p.PIED_AJOUR_CHORD
        wc = p.Y_FLANC - w2 - p.PIED_AJOUR_POST             # ajour central, entre les deux encoches
        ye0 = p.Y_FLANC + w2 + p.PIED_AJOUR_POST            # ajours exterieurs, jusqu au bossage
        ye1 = y2 - bb - p.PIED_AJOUR_POST
        holes.append(G.rounded_rect(-wc, z0, wc, z1a, r))
        holes.append(G.rounded_rect(ye0, z0, ye1, z1a, r))
        holes.append(G.rounded_rect(-ye1, z0, -ye0, z1a, r))
    return c.build(), holes


def crochet_profile():
    """
    Crochet d etuve, plan (y, z) : y vers l INTERIEUR de l etuve depuis la face
    interieure de la paroi (y = 0), z = 0 au dessus de la langue haute. Le
    corps pend le long de la paroi par CROCHET_N_LANGUES langues a bec ; en bas,
    l appui part vers l interieur, une dent sur son dessus.
    """
    S, B, H = p.CROCHET_S, p.CROCHET_BANDE, p.CROCHET_H
    lh, ll, bec, becl = p.CROCHET_LANGUE_H, p.CROCHET_LANGUE_L, p.CROCHET_BEC, p.CROCHET_BEC_L
    za = p.CROCHET_Z_APPUI
    yd, db, dh = p.CROCHET_DENT_Y, p.CROCHET_DENT_B / 2.0, p.CROCHET_DENT_H
    c = G.Contour("crochet")
    c.add(0.0, -H, 3.0)
    c.add(S, -H, 3.0)
    c.add(S, za, 3.0)
    # la dent, angles vifs : elle entre dans la fente du pied, et son dessus est
    # incline comme le fond de cette fente (le pied en V penche vers l interieur)
    pente = math.tan(math.radians(p.PIED_DEBOUT_ANGLE))
    c.add(yd + db, za, 0.0)
    c.add(yd + db, za + dh - db * pente, 0.5)
    c.add(yd - db, za + dh + db * pente, 0.5)
    c.add(yd - db, za, 0.0)
    c.add(p.CROCHET_CORPS, za, 3.0)
    c.add(p.CROCHET_CORPS, 0.0, 3.0)
    # les langues, de haut en bas, le long de la face de paroi
    for i, zt in enumerate(p.CROCHET_LANGUE_Z):
        if i > 0:
            c.add(0.0, zt, 0.0)
        c.add(-ll, zt, 1.0)
        c.add(-ll, zt - lh - bec, 1.0)
        c.add(-ll + becl, zt - lh - bec, 1.0)
        c.add(-ll + becl, zt - lh, 0.5)
        c.add(0.0, zt - lh, 0.0)
    return c.build(), []


def poutre_profile():
    return G.rounded_rect(-p.POUTRE_L / 2.0, -p.POUTRE_B / 2.0,
                          p.POUTRE_L / 2.0, p.POUTRE_B / 2.0, 2.0), []


# ============================================================ nomenclature

class PartSpec(object):
    """
    Une piece du banc. Champs utiles aux sorties :

      profile()        geometrie FINIE (outer, holes) : 3D, plans, calculs.
      dxf_profile      None, ou une fonction sans argument qui renvoie le profil
                       DECOUPE au laser quand il differe du fini. export_dxf doit
                       prendre `spec.dxf_profile()` s'il existe, sinon
                       `spec.profile()`. Utilise par la traverse (chant du bas
                       + TRAVERSE_SUREP, a fraiser).
                       Le helper decoupe(spec) fait ce choix.
      dxf_avertissement  texte a porter en clair sur le DXF de la piece (et a
                       reprendre dans la nomenclature), "" sinon. Pied et
                       crochet : ALERTE_ETUVE tant que ETUVE_CONFIRMEE est faux.
      achete           piece du commerce : jamais de DXF, et rangee a part dans
                       la nomenclature (vis de guidage, pile,
                       tige filetee, plat de renfort).
      material, stock  matiere et brut, repris tels quels par build_freecad dans
                       out/masses.json, donc par la nomenclature.
      note             colonne "operations" de la nomenclature.
    """

    def __init__(self, name, designation, qty, material, stock, thickness,
                 profile, plane, origin, density=p.RHO_ACIER, flat=True,
                 features=None, instances=None, engrave=None, text_at=(0, 0),
                 note="", chanfrein=None, achete=False, dxf_profile=None,
                 dxf_avertissement=""):
        self.name = name
        self.achete = achete            # piece du commerce : pas de DXF
        self.dxf_profile = dxf_profile
        self.dxf_avertissement = dxf_avertissement
        self.designation = designation
        self.qty = qty
        self.material = material
        self.stock = stock
        self.thickness = thickness
        self.profile = profile
        self.plane = plane
        self.origin = origin
        self.density = density
        self.flat = flat
        self.features = features
        self.instances = instances or [dict(t=(0, 0, 0))]
        self._engrave = engrave
        self.text_at = text_at
        self.note = note
        # arete cassee sur les deux faces plates : jamais plus du quart de
        # l'epaisseur, pour que les toles minces ne soient pas mangees
        self.chanfrein = (min(p.CHANFREIN, thickness / 4.0)
                          if chanfrein is None and flat else chanfrein)
        self.rotate = None

    def engrave(self):
        return self._engrave() if self._engrave else []


def decoupe(spec):
    """Profil a DECOUPER (outer, holes) : dxf_profile s'il existe, sinon le profil fini."""
    return spec.dxf_profile() if spec.dxf_profile else spec.profile()


def brut_usinage(fini):
    """
    Brut d'une piece usinee dans la masse, a partir de ses cotes finies (trois
    valeurs, dans un ordre quelconque) : BRUT_SUREP par face sur les deux cotes
    de section, BRUT_SURLONG sur la plus grande, chaque cote arrondie au
    BRUT_PAS superieur. Meme ordre que `fini`.
    """
    lg = max(range(len(fini)), key=lambda i: fini[i])
    out = []
    for i, d in enumerate(fini):
        s = p.BRUT_SURLONG if i == lg else 2.0 * p.BRUT_SUREP
        out.append(math.ceil((d + s) / p.BRUT_PAS - 1e-9) * p.BRUT_PAS)
    return tuple(out)


def bruts_usinage():
    """
    (nom, cotes finies, brut) des pieces usinees dans la masse, cotes finies
    prises sur la BOITE ENGLOBANTE du profil (rebords du coin compris) et sur
    l'epaisseur d'extrusion. Ordre des cotes : x, y, z du banc.
    """
    y0, z0, y1, z1 = G.bbox(coin_profile()[0])
    coin = (p.COIN_B, y1 - y0, z1 - z0)
    x0, yy0, x1, yy1 = G.bbox(coulisseau_profile()[0])
    coul = (x1 - x0, yy1 - yy0, p.COULISSEAU_H)
    return [("coin", coin, brut_usinage(coin)), ("coulisseau", coul, brut_usinage(coul))]


def fr(v, n=1):
    """Nombre a la francaise pour les notes, sans zero inutile : 9,5 ; 64 ; 71,5."""
    s = ("%." + str(n) + "f") % v
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def _txt_brut(nom):
    """'plat 65 x 45, L 120 (fini 61 x 40 x 114,5)' pour la piece `nom`."""
    for n, fini, brut in bruts_usinage():
        if n == nom:
            lg = max(range(3), key=lambda i: fini[i])
            sec = sorted((brut[i] for i in range(3) if i != lg), reverse=True)
            sfin = [fini[i] for i in sorted((i for i in range(3) if i != lg),
                                            key=lambda i: -fini[i])] + [fini[lg]]
            return "plat %g x %g, L %g (fini %s)" % (
                sec[0], sec[1], brut[lg], " x ".join(fr(v) for v in sfin))
    raise KeyError(nom)


def n_entretoises():
    """Nombre d'entretoises de cadre de ECART_FLANCS (coins, bielles, chape, sommet)."""
    return len(_instances_entretoises())


# ---- rappels FreeCAD pour les usinages hors plan

def f_patin_rainure(solid, Part, Vector):
    """Rainure de guidage sous le patin, dans le sens de la poutre."""
    g = Part.makeBox(p.PATIN_L + 4, p.RAINURE_B, p.RAINURE_P + 1,
                     Vector(-(p.PATIN_L + 4) / 2.0, -p.RAINURE_B / 2.0, -1.0))
    return solid.cut(g)


def f_patin_bombe(solid, Part, Vector):
    """Dessus du patin de charge bombe : cylindre d axe y, rayon
    PATIN_CHARGE_BOMBE_R, sommet a l epaisseur pleine au milieu."""
    r, e, b = p.PATIN_CHARGE_BOMBE_R, p.PATIN_CHARGE_E, p.PATIN_CHARGE_B
    cyl = Part.makeCylinder(r, b + 10.0, Vector(0.0, -b / 2.0 - 5.0, e - r), Vector(0, 1, 0))
    return solid.common(cyl)


def f_coulisseau(solid, Part, Vector):
    """
    Alesage du tourillon vers le bas, dessus taille a l'angle du coin sur toute
    la section, et les quatre taraudages de guide dans les faces laterales.
    Repere local du profil 'xy' : X et Y globaux, Z = z - Z_COULISSEAU_BAS.
    """
    out = solid.cut(Part.makeCylinder(p.ALESAGE_D_COUL / 2.0, p.ALESAGE_P_COUL + 1.0,
                                      Vector(0, 0, -1.0)))
    # dessus a z = COULISSEAU_E + y.tan(a) : le coulisseau est epais du cote ou
    # le coin est mince, c'est-a-dire du cote de la butee. La reference est
    # COULISSEAU_E et surtout PAS POUSSOIR_H : ce sont deux pieces distinctes
    # depuis que le poussoir est un empilage, et les confondre ouvrait un jeu de
    # 6 mm entre le coin et le coulisseau.
    box = Part.makeBox(400, 400, 200, Vector(-200, -200, p.COULISSEAU_E))
    box.rotate(Vector(0, 0, p.COULISSEAU_E), Vector(1, 0, 0), p.COIN_ANGLE)
    out = out.cut(box)
    # taraudages M8 de guide : on figure l'avant-trou (GUIDE_TARAUD_D) a sa
    # profondeur de percage ; le filet n'en prend que GUIDE_TARAUD_P
    b2 = p.POUSSOIR_B / 2.0
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            out = out.cut(Part.makeCylinder(
                p.GUIDE_TARAUD_D / 2.0, p.GUIDE_PERCAGE_P + 1.0,
                Vector(sx * p.GUIDE_X, sy * (b2 + 1.0), p.GUIDE_Z),
                Vector(0.0, -sy, 0.0)))
    return out


def f_guide(solid, Part, Vector):
    """
    Le corps filete sous la tete : GUIDE_VIS_L, longueur SOUS TETE de la CHC
    ISO 4762, qui entre toute entiere dans le taraudage quand la tete porte
    sur la face du coulisseau. Repere local 'xz' : Z = y - POUSSOIR_B/2.
    """
    return solid.fuse(Part.makeCylinder(
        p.GUIDE_VIS_D / 2.0, p.GUIDE_VIS_L,
        Vector(p.GUIDE_X, p.Z_GUIDE, 0.0), Vector(0.0, 0.0, -1.0)))


def entretoise_vis_profile():
    """Entretoise de butee : meme tube que celles du cadre, coupe plus long."""
    return (G.circle(0.0, 0.0, p.ENTRETOISE_DE / 2.0),
            [G.circle(0.0, 0.0, p.ENTRETOISE_DI / 2.0)])


def f_vis(solid, Part, Vector):
    """
    Ce qui immobilise la tige dans la chape, DANS LES DEUX SENS :

      - cote exterieur, la butee a aiguilles puis les deux ecrous de
        manoeuvre. C'est cette face qui encaisse l'effort de commande
        (coin_effort, 5,5 kN) : en chargeant, le coin avance vers la chape, la
        face inclinee le repousse vers son bout epais, le filet tire donc la
        tige vers l'INTERIEUR du cadre et sa tete appuie, par la butee, sur la
        face exterieure des platines.
      - cote interieur, deux rondelles trempees AS 1730 (V5) et deux ecrous minces bloques l'un
        sur l'autre. Ils ne retiennent la tige qu'au desserrage
        (coin_desserrage, 329 N).

    Repere local du profil 'xz' : X = x global, Y = z global, Z = y global.
    """
    def zl(y):
        return y - p.VIS_Y0

    def hexa(z0, h):
        r = p.VIS_TETE_D / 2.0 / math.cos(math.radians(30.0))
        pts = [Vector(r * math.cos(math.radians(60.0 * k)),
                      r * math.sin(math.radians(60.0 * k)), z0) for k in range(7)]
        return Part.Face(Part.Wire(Part.makePolygon(pts))).extrude(Vector(0.0, 0.0, h))

    def rond(z0, h, d):
        return Part.makeCylinder(d / 2.0, h, Vector(0.0, 0.0, z0))

    out = solid
    y_int = p.COIN_Y_SUPPORT - p.SUPPORT_RONDELLE
    out = out.fuse(rond(zl(y_int), p.SUPPORT_RONDELLE, p.SUPPORT_BUTEE_D))
    out = out.fuse(hexa(zl(y_int - p.SUPPORT_ECROU_H), p.SUPPORT_ECROU_H))

    y_ext = p.SUPPORT_Y1
    out = out.fuse(rond(zl(y_ext), p.SUPPORT_BUTEE_H, p.SUPPORT_BUTEE_D))
    out = out.fuse(hexa(zl(y_ext + p.SUPPORT_BUTEE_H), p.VIS_TETE_H))
    return out


def all_parts():
    yf = p.ECART_FLANCS / 2.0

    def fl():
        return flanc_profile()

    parts = []

    parts.append(PartSpec(
        "flanc", "Flanc en treillis", 2, p.MATIERE_TOLE, p.BRUT_TOLE, p.EP_FLANC,
        fl, 'xz', (0.0, yf, 0.0), flat=True, engrave=flanc_gravure,
        text_at=(0.0, p.H_FLANC / 2.0 - 60.0),
        instances=[dict(t=(0, 0, 0)), dict(t=(0, 0, 0), mirror_y=True)],
        note="decoupe laser, aretes cassees %s x 45 deg, bossages non repris ; encoches a mi-bois"
             " et mortaise taillees sur la tole REELLE S355 des pieces qu elles recoivent : %s ;"
             " graduation de charge gravee"
             " (calque GRAVURE) d un seul cote de la lumiere, face gravee montee a l exterieur ;"
             " finition : %s ; %s"
             % (fr(p.CHANFREIN), p.NOTE_TOLE_REELLE, p.FINITION_FLANC, p.FINITION_GRAVURE)))

    hf = p.TRAVERSE_H
    hs = p.Z_TAB0 - p.Z_TRAVERSE_BAS
    parts.append(PartSpec(
        "traverse", "Plaque de traverse", p.TRAVERSE_N, p.MATIERE_TOLE_COURANTE,
        p.BRUT_TOLE_COURANTE, p.TRAVERSE_EP, traverse_profile, 'yz',
        (-p.TRAVERSE_LX / 2.0, 0.0, 0.0), flat=True,
        text_at=(0.0, p.Z_TRAVERSE_BAS + 18.0),
        instances=[dict(t=(i * p.TRAVERSE_EP, 0, 0)) for i in range(p.TRAVERSE_N)],
        dxf_profile=lambda: traverse_profile(brut=True),
        note="DXF = brut : chant du bas + %s (%s / %s) ; chants du bas FRAISES EN PAQUET serre,"
             " paquet aligne sur les faces HAUTES des tenons, a la cote finie %s / %s, Ra 1,6 :"
             " c est le plan de glissement"
             % (fr(p.TRAVERSE_SUREP), fr(hf + p.TRAVERSE_SUREP), fr(hs + p.TRAVERSE_SUREP),
                fr(hf), fr(hs))))

    parts.append(PartSpec(
        "poussoir", "Plateau de poussoir", p.POUSSOIR_N, p.MATIERE_TOLE_COURANTE,
        p.BRUT_TOLE_COURANTE, p.POUSSOIR_EP, poussoir_profile, 'xy',
        (0.0, 0.0, p.Z_POUSSOIR_BAS), flat=True,
        instances=[dict(t=(0, 0, i * p.POUSSOIR_EP)) for i in range(p.POUSSOIR_N)],
        note="%d plateaux perces : alesage %s traversant ; 2 trous de passage %s decoupes au laser"
             " a +/- %s ; assembles en bloc par 2 vis H M%g x %g, tete en dessous, ecrou au dessus,"
             " %s N.m ; le patin de charge fait fond"
             % (p.POUSSOIR_N, fr(p.ALESAGE_D), fr(p.POUSSOIR_VIS_PASSAGE),
                fr(p.POUSSOIR_VIS_X), p.POUSSOIR_VIS_D, p.POUSSOIR_VIS_L, fr(p.POUSSOIR_VIS_COUPLE))))

    parts.append(PartSpec(
        "coulisseau", "Coulisseau a tete inclinee", 1, "S355JR",
        _txt_brut("coulisseau"), p.COULISSEAU_H,
        coulisseau_profile, 'xy', (0.0, 0.0, p.Z_COULISSEAU_BAS),
        flat=False, features=f_coulisseau,
        note="dessus a %g degres sur toute la section ; alesage %s prof. %s par dessous ;"
             " 4 taraudages M%g prof. %s dans les faces laterales (avant-trou %s prof. %s),"
             " axe a %s du dessous, x = +/- %s"
             % (p.COIN_ANGLE, fr(p.ALESAGE_D_COUL) + " H8", fr(p.ALESAGE_P_COUL), p.GUIDE_VIS_D,
                fr(p.GUIDE_TARAUD_P), fr(p.GUIDE_TARAUD_D), fr(p.GUIDE_PERCAGE_P),
                fr(p.GUIDE_Z), fr(p.GUIDE_X))))

    parts.append(PartSpec(
        "guide", "Vis de guidage CHC M%g x %g" % (p.GUIDE_VIS_D, p.GUIDE_VIS_L), 4, "8.8",
        "CHC M%g x %g ISO 4762 8.8, tete lisse (non moletee)" % (p.GUIDE_VIS_D, p.GUIDE_VIS_L),
        p.GUIDE_TETE_H,
        guide_profile, 'xz', (0.0, p.POUSSOIR_B / 2.0, 0.0), flat=False,
        features=f_guide, achete=True,
        instances=[dict(t=(dx, 0, 0), mirror_y=m)
                   for dx in (0.0, -2.0 * p.GUIDE_X) for m in (False, True)],
        note="piece du commerce ; %g sous tete, toute la tige dans le taraudage de %g ;"
             " c est la TETE (%g x %g) qui guide : cylindre sur plan, contact lineique"
             % (p.GUIDE_VIS_L, p.GUIDE_TARAUD_P, p.GUIDE_TETE_D, p.GUIDE_TETE_H)))

    parts.append(PartSpec(
        "tourillon", "Tourillon de centrage", 1, p.TOURILLON_MATIERE,
        "rond etire %g h9 x %g" % (p.TOURILLON_D, p.TOURILLON_L), p.TOURILLON_L,
        tourillon_profile, 'xy',
        (0.0, 0.0, p.Z_TOURILLON_BAS), flat=False,
        note="rond etire h9 NON repris : tronconne, chanfrein %s x 45 deg aux deux bouts ;"
             " COLLE au fond de l alesage du coulisseau (%s) ; centre la pile et coulisse"
             " dans le poussoir : %s au repos, %s de garde au dessus du patin a la butee"
             % (fr(p.TOURILLON_CHANFREIN), p.TOURILLON_COLLE,
                fr(p.tourillon_course()[0]), fr(p.tourillon_course()[1]))))

    parts.append(PartSpec(
        "coin", "Coin de commande", 1, "C45",
        _txt_brut("coin"), p.COIN_B,
        coin_profile, 'yz', (-p.COIN_B / 2.0, 0.0, 0.0), flat=False,
        features=f_coin,
        note="acier taraude M%g sur %g depuis le bout EPAIS, passage %g au dela ; porte les deux"
             " plaques de frottement en bronze entre rebords de %s : dessus %s, dessous %s"
             " (faces normales a la pente)"
             % (p.VIS_D, p.COIN_TARAUD_L, p.VIS_PASSAGE_D, fr(p.PLAQ_REBORD_H),
                fr(p.PLAQ_REBORD_L, 2), fr(p.PLAQ_REBORD_L_BAS, 2))))

    parts.append(PartSpec(
        "plaquette_haute", "Plaque de frottement, dessus", 1, p.PLAQ_ALLIAGE,
        p.PLAQ_BRUT, p.PLAQ_EP, plaquette_haute_profile, 'xy',
        (0.0, 0.0, p.Z_COIN_HAUT), density=8800.0, flat=False,
        text_at=(0.0, (p.PLAQ_HAUT_Y0 + p.PLAQ_HAUT_Y1) / 2.0),
        note="fraisee %s x %s x %s, sans trou, faces planes et paralleles a 0,02, Ra 0,8 cote"
             " glissement, aretes cassees 0,3 ; entre ses deux rebords sur le dessus du coin, points"
             " de silicone HT au montage ; %s sur la face qui glisse sous la traverse"
             % (fr(p.PLAQ_B), fr(p.PLAQ_L_HAUT), fr(p.PLAQ_EP), p.PLAQ_LUBRIFIANT)))

    plaq = PartSpec(
        "plaquette_basse", "Plaque de frottement, dessous", 1, p.PLAQ_ALLIAGE,
        p.PLAQ_BRUT, p.PLAQ_EP, plaquette_basse_profile, 'xy',
        (0.0, 0.0, p.Z_COULISSEAU_HAUT), density=8800.0, flat=False,
        text_at=(0.0, (p.PLAQ_BAS_S0 + p.PLAQ_BAS_S1) / 2.0),
        note="comme la haute, mais %s x %s x %s ; entre ses deux rebords sous le coin, points de"
             " silicone HT au montage ; %s sur la face qui glisse sur la pente du coulisseau"
             % (fr(p.PLAQ_B), fr(p.PLAQ_L_BAS), fr(p.PLAQ_EP), p.PLAQ_LUBRIFIANT))
    plaq.rotate = ((1, 0, 0), p.COIN_ANGLE, (0, 0, p.Z_COULISSEAU_HAUT))
    parts.append(plaq)

    parts.append(PartSpec(
        "vis", "Tige filetee de commande M16", 1, "8.8",
        "tige filetee M16 classe 8.8, coupee a %g" % p.VIS_L, p.VIS_L,
        vis_profile, 'xz', (0.0, p.VIS_Y0, p.Z_VIS), flat=False,
        features=f_vis, achete=True,
        note="piece du commerce, coupee a longueur, montee a la pate cuivre ; ecrous et butee"
             " figures : ils montrent l arret axial dans les deux sens"))

    parts.append(PartSpec(
        "support", "Platine de butee de la vis", p.SUPPORT_N, p.MATIERE_TOLE,
        p.BRUT_TOLE, p.SUPPORT_EP, support_profile, 'xz',
        (0.0, p.COIN_Y_SUPPORT, 0.0), flat=True,
        text_at=(p.SUPPORT_X / 2.0, p.Z_VIS + p.SUPPORT_B / 4.0),
        instances=[dict(t=(0, i * p.SUPPORT_EP, 0)) for i in range(p.SUPPORT_N)],
        note="meme tole 42CrMo4 que les flancs (imbriquees dans leurs chutes), empilees et serrees par les deux vis H M10 x %g de la chape"
             % p.SUPPORT_TIRANT_L))

    parts.append(PartSpec(
        "entretoise_vis", "Entretoise de butee", len(p.TROU_SUPPORT), p.ENTRETOISE_MATIERE,
        p.ENTRETOISE_BRUT, p.SUPPORT_TUBE_L, entretoise_vis_profile, 'xz',
        (0.0, p.Y_FLANC_EXT, 0.0), flat=False,
        instances=[dict(t=(x, 0, z)) for (x, z) in p.TROU_SUPPORT],
        note="coupee a %s %s, faces dressees ; en compression pure : c est elle qui porte"
             " l effort de commande" % (fr(p.SUPPORT_TUBE_L), p.SUPPORT_TUBE_TOL)))

    parts.append(PartSpec(
        "patin_appui", "Patin d\'appui rainure", 4, "S355JR", "tole %g mm" % p.PATIN_E, p.PATIN_E,
        patin_appui_profile, 'xy', (0.0, 0.0, p.Z_PATIN_BAS), flat=True,
        features=f_patin_rainure, text_at=(0.0, 0.0),
        instances=[dict(t=(sx * p.X_APPUI, sy * p.Y_FLANC, 0))
                   for sx in (-1, 1) for sy in (-1, 1)],
        note="decoupe laser PUIS rainure %s x %s fraisee sur toute la longueur de la face"
             " d appui (%s de jeu par cote sur la tole reelle du flanc) ; colle en place, cadre"
             " monte, sous 0,5 kN de precharge ; un jeu par eprouvette"
             % (fr(p.RAINURE_B), fr(p.RAINURE_P), fr(p.RAINURE_JEU, 2))))

    parts.append(PartSpec(
        "patin_charge", "Patin de charge", 1, "S355JR", "tole %g mm" % p.PATIN_CHARGE_E, p.PATIN_CHARGE_E,
        patin_charge_profile, 'xy', (0.0, 0.0, p.Z_POUTRE_HAUT), flat=True,
        features=f_patin_bombe,
        note="sans trou, %s de long selon x pour laisser passer les tetes des vis du poussoir ;"
             " dessus BOMBE R%s fraise (cylindre d axe transversal, %s au milieu,"
             " %s aux bords) : le poussoir y porte sur une ligne ; dessous plat, colle centre au"
             " trace en meme temps que les patins d appui ; un par eprouvette"
             % (fr(p.PATIN_CHARGE_L), fr(p.PATIN_CHARGE_BOMBE_R),
                fr(p.PATIN_CHARGE_E), fr(p.PATIN_CHARGE_E - p.PATIN_CHARGE_BOMBE_F, 2))))

    parts.append(PartSpec(
        "plat_renfort", "Plat de renfort colle", 2, "S235",
        "feuillard %g x %g S235, coupe a %g" % (p.PLAT_B, p.PLAT_E, p.PLAT_L), p.PLAT_E,
        plat_profile, 'xy',
        (0.0, 0.0, p.Z_PLAT_BAS), flat=True, achete=True,
        instances=[dict(t=(0, sy * p.Y_FLANC, 0)) for sy in (-1, 1)],
        note="piece du commerce, coupee a longueur, bavures retirees ; collee sur toute la"
             " longueur a y = +/- %g, poncer et degraisser les deux faces ; un jeu par eprouvette"
             % p.Y_FLANC))

    n_e = n_entretoises()
    n_chape = len(p.TROU_SUPPORT)
    parts.append(PartSpec(
        "entretoise", "Entretoise tubulaire", n_e, p.ENTRETOISE_MATIERE, p.ENTRETOISE_BRUT,
        p.ENTRETOISE_L, entretoise_profile, 'xz',
        (0.0, -p.ECART_FLANCS / 2.0, 0.0), flat=False,
        instances=_instances_entretoises(),
        note="coupee a %s %s, faces dressees // 0,05 : c est elle qui fixe l ecart des flancs ;"
             " %d serrees par vis TH M10 x %g + ecrou %s, les %d de la chape par les vis H"
             " M10 x %g"
             % (fr(p.ENTRETOISE_L), p.ENTRETOISE_TOL, n_e - n_chape, p.ENTR_VIS_L,
                p.ECROU_FREIN_REF, n_chape, p.SUPPORT_TIRANT_L)))

    # Quatre pieds identiques. Les deux premiers dans le chant bas, debout sur le
    # sol z = -PIED_SOL. Les deux autres tournes d un quart de tour autour de y et
    # portes contre le chant d extremite x = -L/2, pour la position debout.
    # pieds debout : le plan de pose (z = PIED_CROIX_FLANC du repere de la piece)
    # tourne autour de y pour s aligner sur l encoche du coin (90 - angle en bas,
    # 90 + angle en haut) et vient a PIED_DEBOUT_PROF du coin vif
    ang = math.radians(p.PIED_DEBOUT_ANGLE)
    r = p.PIED_DEBOUT_PROF - p.PIED_CROIX_FLANC
    rx, rz = r * math.cos(ang), r * math.sin(ang)
    alerte = "" if p.ETUVE_CONFIRMEE else p.ALERTE_ETUVE
    parts.append(PartSpec(
        "pied", "Pied a mi-bois", 4, p.MATIERE_TOLE_COURANTE, p.BRUT_TOLE_COURANTE, p.PIED_E,
        pied_profile, 'yz', (-p.PIED_E / 2.0, 0.0, -p.PIED_SOL),
        dxf_avertissement=alerte,
        instances=[dict(t=(-p.PIED_X_POS, 0, 0)), dict(t=(p.PIED_X_POS, 0, 0)),
                   dict(rot=((0, 1, 0), 90.0 - p.PIED_DEBOUT_ANGLE, (0, 0, 0)),
                        t=(-p.L_FLANC / 2.0 + rx, 0, rz)),
                   dict(rot=((0, 1, 0), 90.0 + p.PIED_DEBOUT_ANGLE, (0, 0, 0)),
                        t=(-p.L_FLANC / 2.0 + rx, 0, p.H_FLANC - rz))],
        text_at=(0.0, p.PIED_H / 2.0),
        note=("ajoure, bossages aux deux bouts qui posent sur les crochets d etuve, fente de calage"
              " %s x %s a %s du bout ; encoches et nodes taillees sur la tole REELLE du flanc"
              " (42CrMo4), fente sur celle du crochet (S355) : %s ;"
              % (fr(p.PIED_FENTE_B), fr(p.PIED_FENTE_H), fr(p.PIED_FENTE_BORD), p.NOTE_TOLE_REELLE))
             + " meme plaque pour les deux positions : 2 dans le chant bas (couche), 2 aux coins"
               " de l about a %.0f degres (debout), aretes de pose a %.0f"
               % (p.PIED_DEBOUT_ANGLE, p.pied_debout_base())
             + ("" if p.ETUVE_CONFIRMEE else " ; largeur choisie pour l etuve : " + p.ALERTE_ETUVE)))

    # crochets d etuve : pour le cadre DEBOUT, dans le plan des flancs (z, x du
    # modele couche), a y = +/- PIED_FENTE_Y ou les pieds en V ont leur fente.
    # Le profil (u vers l interieur, v vers le haut) est pose en 'zx' : u -> z,
    # v -> x, le haut du cadre debout etant +x. Paroi z = CROCHET_Z_PAROI face
    # au coin bas ; l autre paroi par demi-tour autour de x. L appui (v = Z_APPUI)
    # vient sous l arete de pose du pied en V.
    xf, zf = p.pied_debout_fente()
    x0 = xf - p.CROCHET_Z_APPUI - p.CROCHET_DENT_H
    zw = p.CROCHET_Z_PAROI
    parts.append(PartSpec(
        "crochet", "Crochet d etuve", 4, p.MATIERE_TOLE_COURANTE, p.BRUT_TOLE_COURANTE, p.CROCHET_E,
        crochet_profile, 'zx', (0.0, -p.CROCHET_E / 2.0, 0.0),
        dxf_avertissement=alerte,
        instances=[dict(t=(x0, -p.PIED_FENTE_Y, zw)), dict(t=(x0, p.PIED_FENTE_Y, zw)),
                   dict(rot=((1, 0, 0), 180.0, (0, 0, 0)), t=(x0, -p.PIED_FENTE_Y, p.H_FLANC - zw)),
                   dict(rot=((1, 0, 0), 180.0, (0, 0, 0)), t=(x0, p.PIED_FENTE_Y, p.H_FLANC - zw))],
        text_at=(p.CROCHET_S / 2.0, p.CROCHET_Z_APPUI - p.CROCHET_BANDE / 2.0),
        note=("cadre DEBOUT : pend par %d langues a bec dans la colonne de trous carres de %g"
              " (paroi %g), dans le plan des flancs ; l arete du pied en V pose sur son appui,"
              " calee par la dent dans la fente du pied. Le fond de l etuve ne porte rien ; dent a"
              " %s de la paroi pour une etuve de %g"
              % (p.CROCHET_N_LANGUES, p.ETUVE_TROU, p.ETUVE_PAROI_E, fr(p.CROCHET_DENT_Y),
                 p.ETUVE_INTERIEUR))
             + ("" if p.ETUVE_CONFIRMEE else " : " + p.ALERTE_ETUVE)))

    parts.append(PartSpec(
        "pile_belleville", "Pile de %d rondelles Belleville" % p.RESSORT_N, 1, p.RESSORT_MATIERE,
        "%d rondelles %s" % (p.RESSORT_N, p.RESSORT_NORME), p.PILE_H_LIBRE, pile_profile, 'xy',
        (0.0, 0.0, p.Z_PILE_BAS), flat=False, features=f_pile, achete=True,
        note="piece du commerce : %d rondelles %s x %s x %s (ex-DIN 2093, PAS en C60S) montees TETE-BECHE, grand diametre aux"
             " deux bouts ; %s kN a plat, course %s mm ; cales de rattrapage %s mm (%s / %s) entre"
             " poussoir et pile si l empilement est court"
             % (p.RESSORT_N, fr(p.RESSORT_DE), fr(p.RESSORT_DI), fr(p.RESSORT_T),
                fr(p.RESSORT_F_PLAT / 1000.0), fr(p.PILE_COURSE),
                " et ".join(fr(e) for e in p.CALES_EP), fr(p.CALE_DE), fr(p.CALE_DI))))

    parts.append(PartSpec(
        "poutre", "Poutrelle beton", 1, "beton non arme", "-", p.POUTRE_H,
        poutre_profile, 'xy', (0.0, 0.0, p.Z_POUTRE_BAS),
        density=p.POUTRE_RHO, flat=False, note="eprouvette, pour reference"))

    return parts


def _instances_entretoises():
    xc = p.TROU_COIN[0]
    out = []
    for sx in (-1, 1):
        out.append(dict(t=(sx * xc, 0, p.TROU_COIN[1])))
        out.append(dict(t=(sx * xc, 0, p.TROU_COIN_HAUT_Z)))
        haut, noeud, bm, bn = ligne_bielle(sx)
        out.append(dict(t=((haut[0] + noeud[0]) / 2.0, 0,
                           (haut[1] + noeud[1] + bm[1] + bn[1]) / 4.0)))
    # deux de plus sur les tirants de la chape : les percages y sont de toute
    # facon, autant en faire des entretoises
    for (x, z) in p.TROU_SUPPORT:
        out.append(dict(t=(x, 0, z)))
    if p.ENTR_SOMMET:
        out.append(dict(t=(0.0, 0, p.Z_ENTR_SOMMET)))
    return out
