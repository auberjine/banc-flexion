# -*- coding: utf-8 -*-
"""
Ecrit NOMENCLATURE.md a partir du modele : parts.all_parts() pour les
designations, matieres, bruts, quantites et operations ; params pour la
visserie, les exigences de commande et les reglages ; out/masses.json (ecrit
par build_freecad) pour les masses seulement.

    python nomenclature.py
"""

import os
import json
import time
import params as p
import parts as P
import spec

try:                                    # largeur des etageres des DXF de groupe
    import export_dxf as X
    LARGEUR_GROUPE = X.LARGEUR_GROUPE
except Exception:
    LARGEUR_GROUPE = None

HERE = os.path.dirname(os.path.abspath(__file__))

# Repere = numero de planche, puis lettre de la vue. La pile est rangee avec la
# tete de charge (02e) ; les plaques de frottement sont dessinees sur la 06.
REPERES = {
    "flanc": "01", "coulisseau": "02a", "poussoir": "02b", "coin": "02c",
    "vis": "02d", "pile_belleville": "02e", "guide": "02f",
    "traverse": "03",
    "patin_appui": "04a", "patin_charge": "04b", "plat_renfort": "04c",
    "pied": "05", "crochet": "05c",
    "tourillon": "06a", "entretoise": "06b",
    "plaquette_haute": "06c", "plaquette_basse": "06d",
    "support": "07", "entretoise_vis": "07b",
    "poutre": "-",
}

GOUPILLE_L = 30.0            # goupilles du poussoir : POUSSOIR_H dans les plateaux, le reste dans le patin
CALE_SOUS_FLANC = 20.0       # montage a plat : de quoi loger tetes de vis M10 et rondelles sous le flanc


def fr(v, n=1):
    return P.fr(v, n)


def visserie():
    """Visserie et petites pieces du commerce, longueurs et marges tirees de params."""
    v1, v2, v9 = p.boulonnerie()
    n_chape = len(p.TROU_SUPPORT)
    n_cadre = P.n_entretoises() - n_chape
    tole_max_v2 = ((p.TRAVERSE_TIRANT_L - 2.0 * p.RONDELLE_M10_E
                    - 2.0 * (p.ECROU_FREIN_H + p.FILET_DEPASSE_MIN)) / p.TRAVERSE_N)
    return [
        ("V1", "Vis TH M10 x %g ISO 4014 8.8 zinguee + ecrou %s + 2 rondelles ISO 7089 M10"
         % (p.ENTR_VIS_L, p.ECROU_FREIN_REF), n_cadre,
         "entretoises de cadre : %s. Serrage %s : l ecrou tombe"
         " sur le filet avec %s de marge, la vis en depasse de %s ; %g N.m. Pas d ecrou a bague"
         " polyamide (ISO 7040, DIN 985) : elle ne freine plus a 150 C. Acier, pas inox : meme"
         " dilatation que les flancs, la precharge tient a chaud"
         % (spec.entretoises_de_cadre(), fr(v1["serrage"]), fr(v1["marge_filet"]),
            fr(v1["depassement"]), spec.COUPLE_M10)),
        ("V2", "Tige filetee M10 x %g classe 8.8 + 2 rondelles ISO 7089 M10 + 2 ecrous %s"
         % (p.TRAVERSE_TIRANT_L, p.ECROU_FREIN_REF), 1,
         "tirant du paquet de plaques de traverse, ne reprend aucune charge. Serrage %s, depasse"
         " de %s a chaque bout. Tole mesuree au dela de %s : prendre une M10 x %g (verifie() le"
         " signale)"
         % (fr(v2["serrage"]), fr(v2["depassement"]), fr(tole_max_v2, 2), p.TRAVERSE_TIRANT_L + 10)),
        ("V3", "Goupille cylindrique ISO 2338 %g m6 x %g" % (p.POUSSOIR_GOUPILLE_D, GOUPILLE_L), 2,
         "reperage des plateaux du poussoir : serrees dans le patin de charge (%g H7, enfoncees"
         " de %s), libres dans les trous de %s des plateaux ; partent avec l eprouvette"
         % (p.POUSSOIR_GOUPILLE_D, fr(GOUPILLE_L - p.POUSSOIR_H), fr(p.POUSSOIR_GOUPILLE_PASSAGE))),
        ("V4", "Cale de rattrapage D%g / D%g, feuillard acier, ep. %s mm"
         % (p.CALE_DE, p.CALE_DI, " et ".join(fr(e) for e in p.CALES_EP)), len(p.CALES_EP),
         "une de chaque, entre le poussoir et la pile, si l empilement mesure au montage est"
         " court : le coin doit toucher a moins de 5 mm de son repos"),
        ("V5", "Rondelle trempee AS 1730 (17 x 30 x 1)", int(round(p.SUPPORT_RONDELLE)),
         "cote interieur des platines, sous les ecrous V8 : deux empilees font les %g mm de"
         " rondelle trempee (une rondelle trempee 30 x 2 n existe pas en M16)"
         % p.SUPPORT_RONDELLE),
        ("V6", "Butee a aiguilles AXK 1730 + 2 rondelles AS 1730", 1,
         "face EXTERIEURE des platines : c est elle qui encaisse les %.1f kN de commande"
         % (p.coin_effort() / 1000.0)),
        ("V7", "Ecrou M16 H ISO 4032 classe 8 + ecrou M16 HM ISO 4035, bloques", 1,
         "tete de manoeuvre, %s de haut, en appui sur la butee a aiguilles. Douille de 24 et"
         " cliquet : une cle plate bute sur les bouts des vis V9" % fr(p.VIS_TETE_H)),
        ("V8", "Ecrou M16 HM ISO 4035", 2,
         "bloques l un sur l autre cote interieur des platines, sur les rondelles V5, avec 0,1 a"
         " 0,3 de jeu axial : ils ne retiennent la tige qu au desserrage, %.0f N"
         % p.coin_desserrage()),
        ("V9", "Vis H M10 x %g ISO 4014 8.8 zinguee (filetee sur %g) + %d ecrous H M10 ISO 4032"
         " classe 8 + %d rondelles ISO 7089 M10"
         % (p.SUPPORT_TIRANT_L, p.SUPPORT_TIRANT_FILET, p.SUPPORT_ECROUS_M10_N,
            1 + p.SUPPORT_RONDELLES_ECROU), n_chape,
         "vis de chape : tete et 1 rondelle derriere le flanc oppose, flanc, entretoise de cadre,"
         " flanc, entretoise de butee, platines, %d rondelles, ecrou serre puis contre-ecrou bloque"
         " contre lui. Serrage %s, filet a partir de %g : le premier ecrou y tombe avec %s de"
         " marge, la vis depasse du contre-ecrou de %s ; %g N.m sur le premier"
         % (p.SUPPORT_RONDELLES_ECROU, fr(v9["serrage"]),
            p.SUPPORT_TIRANT_L - p.SUPPORT_TIRANT_FILET, fr(v9["marge_filet"]),
            fr(v9["depassement"]), spec.COUPLE_M10)),
    ]


# Etapes de l'ordre de montage, dans l'ordre : les renvois d'une etape a
# l'autre passent par ETAPE, jamais par un numero ecrit en dur.
CLES_MONTAGE = ["eprouvette", "coin_garni", "patin_charge", "sous_ensemble_chape", "empilement",
                "flanc1", "traverse", "poutrelle", "tete", "flanc2", "chape", "pieds",
                "patins", "guides", "coin", "precharge", "etalonnage"]
ETAPE = dict((k, i + 1) for i, k in enumerate(CLES_MONTAGE))


def ordre_de_montage():
    n_chape = len(p.TROU_SUPPORT)
    n_entr = P.n_entretoises()
    e05, c05, t05 = p.coin_tours(500.0)
    cale_poutre = CALE_SOUS_FLANC - (p.POUTRE_B / 2.0 - p.Y_FLANC_EXT)
    nominal = p.Z_COULISSEAU_BAS - p.Z_BOSSAGE
    reserve = (p.COIN_T_MAX - p.COIN_T_MIN) - p.PILE_ECRAS_DIM
    bout_tete = p.Y_BOUT_VIS - (p.SUPPORT_Y1 + p.SUPPORT_BUTEE_H + p.VIS_TETE_H)
    return [
        # preparation
        "**Eprouvette, a l avance.** Coller les deux plats %g x %g sous la poutrelle, a y = +/- %g"
        " (axe des flancs), sur toute la longueur ; poncer P80 et degraisser les deux faces ;"
        " polymeriser." % (p.PLAT_B, p.PLAT_E, p.Y_FLANC),
        "**Coin, a l avance.** Degraisser les deux sieges ; poser chaque plaque de frottement ENTRE"
        " SES DEUX REBORDS, trous remplis et quelques points de silicone haute temperature --"
        " PAS d epoxy, bronze et acier ne se dilatent pas pareil ; laisser prendre. Aucune pate"
        " sur les plaques ni sur les sieges : elles sont autolubrifiantes, et le silicone ne"
        " prend pas sur une pate.",
        "**Patin de charge.** Chasser les deux goupilles V3 dans ses trous %g H7, enfoncees de"
        " %s : elles depassent de %g, la hauteur du poussoir."
        % (p.POUSSOIR_GOUPILLE_D, fr(GOUPILLE_L - p.POUSSOIR_H), p.POUSSOIR_H),
        "**Sous-ensemble de chape, sur l etabli.** Sur la tige M16, visser par son bout"
        " exterieur l ecrou H et l ecrou HM de manoeuvre (V7), bloques a %s du bout ; enfiler"
        " par l autre bout une rondelle AS, la butee AXK 1730 et la seconde AS (V6), les deux"
        " platines, les deux rondelles trempees (V5), puis visser les deux ecrous HM (V8) :"
        " 0,1 a 0,3 mm de jeu axial, contre-bloquer. Pate cuivre sur le filet de la tige."
        % fr(bout_tete),
        "**Empilement.** Mesurer la poutrelle avec ses plats, les patins d appui sous la rainure,"
        " le patin de charge, le poussoir et la pile libre. Du sommet des bossages au dessous"
        " du coulisseau, le nominal fait %s (%s + %g + %g + %g + %g + %s). S il manque plus de"
        " 1 mm, prevoir entre poussoir et pile la cale de 1, de 2 ou les deux (V4) : au dela"
        " des 12 kN le coin ne garde que %s mm de reserve en hauteur."
        % (fr(nominal), fr(p.PATIN_E - p.RAINURE_P), p.PLAT_E, p.POUTRE_H, p.PATIN_CHARGE_E,
           p.POUSSOIR_H, fr(p.PILE_H_LIBRE), fr(reserve)),
        # cadre, monte a plat
        "**Premier flanc.** Poser a plat, sur cales de %g, le flanc OPPOSE a la chape, face"
        " gravee DESSOUS : la graduation doit finir a l exterieur. Passer par dessous, rondelle"
        " sous tete, les %d vis V1 (%s) et les %d vis V9"
        " (chape, x = +/- %g). Enfiler une entretoise de %g sur chacune des %d vis."
        % (CALE_SOUS_FLANC, n_entr - n_chape, spec.entretoises_de_cadre(), n_chape, p.SUPPORT_X,
           p.ENTRETOISE_L, n_entr),
        "**Traverse.** Engager dans la mortaise le paquet des %d plaques, serre par la tige V2"
        " (rondelles et ecrous ISO 7042) ; chants fraises du cote du coin."
        % p.TRAVERSE_N,
        "**Poutrelle.** La coucher dans la fenetre du flanc, plats vers les bossages, SANS ses"
        " patins d appui, sur cales de %s sous sa face laterale (elle descend de %s sous le flanc)."
        % (fr(cale_poutre), fr(p.POUTRE_B / 2.0 - p.Y_FLANC_EXT)),
        "**Tete de charge.** Encoller le patin de charge sur sa face inferieure et le poser au"
        " milieu de la poutrelle, goupilles vers la tete ; enfiler sur les goupilles les %d"
        " plateaux du poussoir, poser la cale eventuelle (V4), le tourillon, la pile TETE-BECHE"
        " (grand diametre aux deux bouts) et le coulisseau, cote epais de sa pente vers la chape."
        " De cet encollage a la precharge, tout doit tenir dans la vie en pot de la colle :"
        " faire d abord les etapes %d a %d et preparer la visserie. Si elle est trop courte,"
        " coller le patin de charge la veille sur la poutrelle, centre au trace, sous une masse."
        % (p.POUSSOIR_N, ETAPE["coin_garni"], ETAPE["empilement"]),
        "**Second flanc.** Le presenter face gravee DESSUS : il enfile les %d vis, les tenons de"
        " la traverse et la poutrelle dans sa fenetre. Poser les %d ecrous V1 sur rondelle,"
        " serres sans bloquer." % (n_entr, n_entr - n_chape),
        "**Chape.** Enfiler sur les deux vis V9 les entretoises de butee de %s, puis le"
        " sous-ensemble de chape, la tige passant par la fente du coin ; %d rondelles et un"
        " ecrou H par vis, %g N.m, puis le contre-ecrou H bloque contre lui en tenant le premier."
        % (fr(p.SUPPORT_TUBE_L), p.SUPPORT_RONDELLES_ECROU, spec.COUPLE_M10),
        "**Pieds.** Dresser le cadre et le poser dans ses deux pieds couches, encoche dans"
        " encoche : les nodes serrent de %s par cote, chasser au maillet. Bloquer les V1 a"
        " %g N.m. La poutrelle, sans patins, repose sur les bossages."
        % (fr(p.PIED_NODE_SERRE), spec.COUPLE_M10),
        "**Patins d appui, coin non engage.** Soulever la poutrelle d environ %s mm, glisser les"
        " 4 patins par la fenetre, rainure SECHE sur le bossage (c est un balancier, il doit"
        " basculer) et colle sur la face superieure seulement, contre le plat ; reposer."
        % fr(p.PATIN_E - p.RAINURE_P + 1.0),
        "**Guides.** Visser les 4 CHC M%g x %g au travers des lumieres dans les taraudages du"
        " coulisseau. C est la TETE qui guide : jamais de vis a tete fraisee."
        % (p.GUIDE_VIS_D, p.GUIDE_VIS_L),
        "**Coin.** Pate cuivre dans son taraudage ; l engager du cote des tetes de V9, bout MINCE"
        " en premier, par la fente du flanc, entre la traverse et le coulisseau ; visser la tige"
        " jusqu au contact. Le bout epais doit alors etre a moins de 5 mm de sa position de"
        " repos, %s mm hors de la face exterieure du flanc ; sinon revoir les cales (etape %d)."
        % (fr(-p.COIN_Y0 - p.Y_FLANC_EXT), ETAPE["empilement"]),
        "**Precharge.** %s tour de tige au dela du contact (%s mm de pile, %s mm de coin) donne"
        " 0,5 kN. Laisser polymeriser sous cette precharge : l epoxy rattrape l hyperstaticite"
        " des quatre appuis. Post-cuire selon la notice Duralco avant toute mise en charge."
        % (fr(t05, 2), fr(e05, 2), fr(c05)),
        "**Etalonnage.** Etalonner la graduation de charge sur presse, ou par la fibre de la"
        " membrure.",
    ]


def position_debout():
    return [
        "Accrocher d abord les 4 crochets aux parois de l etuve : crochet a l horizontale, engager"
        " les trois tetes de langue DE FACE dans leurs trous carres, puis laisser descendre : les"
        " becs retombent derriere la paroi.",
        "Le cadre couche sur ses pieds, engager les deux pieds en V UN PAR UN sur les deux coins"
        " d un meme about, chacun chasse le long de sa propre encoche a %g degres (maillet,"
        " nodes). Ils ne se montent pas ensemble : leurs encoches font %g degres entre elles."
        % (p.PIED_DEBOUT_ANGLE, 2 * p.PIED_DEBOUT_ANGLE),
        "Soulever le cadre hors des pieds couches, qui restent sur la paillasse, et le dresser"
        " sur ses pieds en V.",
        "L entrer dans l etuve tige vers la porte, pieds tenus 5 mm au dessus des appuis jusqu au"
        " fond, puis descendre les quatre fentes des pieds sur les dents des crochets.",
        "Calage de la poutrelle debout : point ouvert, assume (voir `DEBOUT.md`, paragraphe 6).",
    ]


def changement_eprouvette():
    coul_haut = p.Z_COULISSEAU_HAUT + p.POUSSOIR_B / 2.0 * p.COIN_TAN
    garde = p.Z_VIS - p.ENTRETOISE_DE / 2.0 - coul_haut
    intro = ("Les plats, les patins d appui et le patin de charge sont colles sur la poutrelle et"
             " partent avec elle : il faut un jeu neuf par eprouvette (4 patins d appui, 1 patin"
             " de charge et ses 2 goupilles, 2 plats ; colle). Les goupilles, serrees dans le patin"
             " de charge, montent de %g dans le poussoir, et la tete ne peut remonter que de %s"
             " avant que le coulisseau touche les entretoises de chape : l eprouvette ne sort pas"
             " cadre ferme, on rouvre le flanc cote chape."
             % (p.POUSSOIR_H, fr(garde)))
    etapes = [
        "Decharger : devisser la tige jusqu a liberer la pile, puis jusqu a degager le filet ;"
        " sortir le coin du cote des tetes de V9.",
        "Deposer les 4 guides. Sortir le cadre de l etuve ou de ses pieds et le coucher a plat,"
        " chape en haut, sur cales de %g." % CALE_SOUS_FLANC,
        "Deposer les ecrous et rondelles des deux V9, le sous-ensemble de chape d un bloc (platines"
        " et tige), puis les deux entretoises de butee.",
        "Deposer les %d ecrous V1 et soulever le flanc cote chape." % (P.n_entretoises() - len(p.TROU_SUPPORT)),
        "Sortir l eprouvette avec sa tete de charge ; sur l etabli, degager le poussoir des"
        " goupilles, qui restent dans le patin de charge.",
        "Remonter la nouvelle eprouvette, preparee aux etapes %d, %d et %d de l ordre de montage,"
        " en reprenant a l etape %d : le premier flanc a garde ses vis, ses entretoises et la"
        " traverse."
        % (ETAPE["eprouvette"], ETAPE["patin_charge"], ETAPE["empilement"], ETAPE["poutrelle"]),
    ]
    return intro, etapes


def main():
    data, date_masses = spec.lire_json("masses.json")
    masse = dict((it["nom"], it) for it in data["pieces"])
    specs = [s for s in P.all_parts() if s.name != "poutre"]

    out = []
    out.append("# Banc de flexion 3 points - nomenclature\n")
    out.append("Indice %s du %s. Fichier engendre par `nomenclature.py` ; ne pas le modifier a la main.\n"
               % (p.INDICE_REVISION, p.DATE_EDITION))
    out.append("Poutrelle beton non arme %g x %g x %g, portee %g, capacite %g kN.\n"
               % (p.POUTRE_B, p.POUTRE_H, p.POUTRE_L, p.PORTEE, p.CHARGE_DIM / 1000.0))
    y_min, y_max = spec.encombrement_y()
    out.append("Encombrement des flancs %g x %g x %g mm ; selon y, de %s (coin recule) a +%g (bout"
               " des vis de chape), soit %s ; pieds de %g.\n"
               % (p.L_FLANC, p.H_FLANC, p.ECART_FLANCS + 2 * p.EP_FLANC, fr(y_min), y_max,
                  fr(y_max - y_min), p.PIED_Y))
    out.append("")

    out.append("## Exigences de commande\n")
    out.append("- **Tole de %g en %s** (flancs, traverse, poussoir, platines, pieds, crochets) :"
               " %s. C est elle qui porte toute la marge du flanc. Les cartouches et la colonne"
               " brut l abregent en \"%s\"."
               % (p.EP_FLANC, p.NUANCE_TOLE, p.EXIGENCE_TOLE, p.BRUT_TOLE))
    out.append("- **Epaisseur reelle** : %s. Encoches a mi-bois, nodes, fentes de calage, mortaise"
               " de traverse et rainures des patins en derivent (EP_TOLE_REELLE = %g aujourd hui)."
               % (p.NOTE_TOLE_REELLE, p.EP_TOLE_REELLE))
    out.append("- **Entretoises** : %s, %s ; %d coupees a %g %s et %d a %s %s, faces dressees //"
               " 0,05 : ce sont elles qui fixent l ecart des flancs."
               % (p.ENTRETOISE_MATIERE, p.ENTRETOISE_BRUT, P.n_entretoises(), p.ENTRETOISE_L,
                  p.ENTRETOISE_TOL, len(p.TROU_SUPPORT), fr(p.SUPPORT_TUBE_L), p.SUPPORT_TUBE_TOL))
    if not p.ETUVE_CONFIRMEE:
        attente = [s.name for s in specs if s.dxf_avertissement]
        out.append("- **Etuve %g x %g x %g A CONFIRMER** : %s (%s)."
                   % (p.ETUVE_INTERIEUR, p.ETUVE_Y, p.ETUVE_HAUTEUR, p.ALERTE_ETUVE,
                      ", ".join(attente)))
    out.append("")

    out.append("## Pieces fabriquees\n")
    out.append("| rep | designation | qte | matiere | brut | masse u. | masse tot. | operations |")
    out.append("|---|---|---|---|---|---|---|---|")
    total = 0.0
    for s in specs:
        m = masse.get(s.name)
        if m:
            total += m["masse_totale_kg"]
        if s.achete:
            continue
        out.append("| %s | %s | %d | %s | %s | %s | %s | %s |"
                   % (REPERES.get(s.name, "?"), s.designation, s.qty, s.material, s.stock,
                      "%.2f kg" % m["masse_kg"] if m else "-",
                      "%.2f kg" % m["masse_totale_kg"] if m else "-", s.note))
    out.append("")

    out.append("## Pieces du commerce\n")
    out.append("| rep | designation | qte | reference | matiere | masse u. | remarque |")
    out.append("|---|---|---|---|---|---|---|")
    for s in specs:
        if not s.achete:
            continue
        m = masse.get(s.name)
        out.append("| %s | %s | %d | %s | %s | %s | %s |"
                   % (REPERES.get(s.name, "?"), s.designation, s.qty, s.stock, s.material,
                      "%.2f kg" % m["masse_kg"] if m else "-", s.note))
    out.append("")
    out.append("**Masse du cadre complet : %.1f kg.** Poutrelle beton : %.1f kg. Masses du modele 3D"
               " (out/masses.json du %s)."
               % (total, masse["poutre"]["masse_kg"] if "poutre" in masse else 0.0, date_masses))
    out.append("")

    out.append("## Visserie et petites pieces du commerce\n")
    out.append("| rep | designation | qte | remarque |")
    out.append("|---|---|---|---|")
    for r, d, q, rem in visserie():
        out.append("| %s | %s | %d | %s |" % (r, d, q, rem))
    out.append("")

    out.append("## Pieces planes a decouper\n")
    out.append("Fichiers DXF dans `out/dxf/`, cotes en millimetres, contours fermes, indice %s du %s ;"
               " la liste tenue a jour par `export_dxf.py` est `out/dxf/LISTE.txt`."
               % (p.INDICE_REVISION, p.DATE_EDITION))
    out.append("")
    out.append("- **Calques** : DECOUPE = contour a couper ; GRAVURE = marquage laser, sans traverser,"
               " sur la face superieure de decoupe (graduation de charge du flanc, d un seul cote"
               " de la lumiere : face gravee montee a l exterieur) ; TEXTE = identification, ni"
               " coupe ni marquage.")
    out.append("- **Tole reelle** : %s." % p.NOTE_TOLE_REELLE)
    out.append("- **Brut de decoupe** : le DXF de la traverse porte %s mm de surepaisseur sur le chant"
               " du bas (fraise ensuite en paquet), celui du patin de charge des avant-trous de %s"
               " (perces et aleses %g H7 ensuite)."
               % (fr(p.TRAVERSE_SUREP), fr(p.PATIN_CHARGE_AVANT_TROU), p.POUSSOIR_GOUPILLE_D))
    out.append("- **Groupes** : `tole_<ep>mm_<nuance>.dxf` reprend tous les exemplaires d une"
               " epaisseur et d une nuance, ranges en etageres de %s mm de large au plus. C est un"
               " controle de quantites, pas une imbrication : le decoupeur imbrique sur son format."
               " Les pieces en attente sont dans un groupe a part, suffixe `_EN_ATTENTE`."
               % ("%.0f" % LARGEUR_GROUPE if LARGEUR_GROUPE else "3000"))
    out.append("- Les pieces du commerce n ont pas de DXF.")
    out.append("")
    out.append("| fichier | epaisseur | matiere | nombre | statut |")
    out.append("|---|---|---|---|---|")
    for s in specs:
        if s.flat and not s.achete:
            statut = s.dxf_avertissement or "a decouper"
            if s.dxf_profile:
                statut += " ; DXF = brut, reprise apres decoupe"
            out.append("| %s.dxf | %g mm | %s | %d | %s |"
                       % (s.name, s.thickness, s.material, s.qty, statut))
    out.append("")

    out.append("## Reglages et constantes d'essai\n")
    out.append("| grandeur | valeur |")
    out.append("|---|---|")
    out.append("| Portee entre bossages | %.0f mm |" % p.PORTEE)
    out.append("| Bossages | R%.0f, balancier, %.0f MPa de Hertz sur %s mm portants |"
               % (p.BOSSAGE_R, p.hertz_appui(), fr(p.hertz_largeur())))
    out.append("| Pression de Hertz aux appuis | %.0f MPa ; limite %.0f MPa, 1,6 Re a chaud du patin"
               " S355JR, le plus mou des deux corps ; coefficient %.2f |"
               % (p.hertz_appui(), p.HERTZ_LIM, p.hertz_coef()))
    out.append("| Pile Belleville | %d x DIN 2093 A50, hauteur libre %.1f mm |"
               % (p.RESSORT_N, p.PILE_H_LIBRE))
    out.append("| Effort de la pile a plat | %.1f kN |" % (p.RESSORT_F_PLAT / 1000.0))
    out.append("| Course totale de la pile | %.1f mm |" % p.PILE_COURSE)
    out.append("| Ecrasement a %g kN | %.2f mm, soit %.0f N/mm en secant |"
               % (p.CHARGE_DIM / 1000.0, p.PILE_ECRAS_DIM, p.PILE_K_SECANT))
    out.append("| Butee de course (bas de lumiere) | %.1f mm, plafonne l'effort a %.1f kN |"
               % (p.ecrasement_butee(), p.pile_force(p.ecrasement_butee()) / 1000.0))
    reserve = (p.COIN_T_MAX - p.COIN_T_MIN) - p.PILE_ECRAS_DIM
    out.append("| Rattrapage d empilement | %.1f mm en reserve au dela des %g kN ; cales V4 de %s mm |"
               % (reserve, p.CHARGE_DIM / 1000.0, " et ".join(fr(e) for e in p.CALES_EP)))
    dz, df = p.coin_par_tour()
    out.append("| Commande | coin acier a %.0f degres, vis M%.0f normale aux flancs |"
               % (p.COIN_ANGLE, p.VIS_D))
    out.append("| Course par tour | %.3f mm de coulisseau, environ %.0f N |" % (dz, df))
    e05, c05, t05 = p.coin_tours(500.0)
    out.append("| Precharge de collage, 0,5 kN | %.2f tour de tige apres le contact (%.2f mm de pile, %.1f mm de coin) |"
               % (t05, e05, c05))
    out.append("| Couple sur la vis a %g kN | %.1f N.m |" % (p.CHARGE_DIM / 1000.0, p.coin_couple()))
    out.append("| Couple de serrage des vis M10 (V1, V9) | %g N.m |" % spec.COUPLE_M10)
    psi, rho, marge = p.filet_marge()
    out.append("| Irreversibilite du filet | helice %.2f deg / frottement %.2f deg a mu %.2f (acier sur acier, pate cuivre), marge x%.2f |"
               % (psi, rho, p.VIS_MU_MIN, marge))
    out.append("| Coin | autobloquant seulement si mu > %.3f ; desserrage %.0f N a mu %.2f |"
               % (p.coin_mu_autoblocage(), p.coin_desserrage(), p.COIN_MU))
    out.append("| Flancs du filet, taraude dans l acier | %.1f MPa pour %g admis, %.0f mm filetes, engagement utile %.0f mm |"
               % (p.pression_filet(), p.FILET_P_ADM, p.COIN_TARAUD_L, 1.5 * p.VIS_D))
    cis, flex, pres = p.rebord_contrainte()
    p_haut, p_bas = p.pressions_plaquettes()
    out.append("| Plaques de frottement | %s, %g x %g x %g, %s ; %.1f MPa au plus pour %g admis |"
               % (p.PLAQ_REF, p.PLAQ_B, p.PLAQ_L, p.PLAQ_EP, p.PLAQ_ALLIAGE,
                  max(p_haut, p_bas), p.PLAQ_P_ADM))
    out.append("| Rebords des plaquettes | %.2f (dessus) et %.2f (dessous) x %g, %.1f MPa de flexion, garde %g sous le bronze |"
               % (p.PLAQ_REBORD_L, p.PLAQ_REBORD_L_BAS, p.PLAQ_REBORD_H, flex, p.PLAQ_EP - p.PLAQ_REBORD_H))
    for nom, lo, hi, larg, largx, pr in (
            ("haute", p.PLAQ_HAUT_Y0, p.PLAQ_HAUT_Y1, p.TRAVERSE_B, p.portee_coin(), p_haut),
            ("basse", p.PLAQ_BAS_Y0, p.PLAQ_BAS_Y1, p.POUSSOIR_B, p.PLAQ_B, p_bas)):
        pp = p.portee_plaquette(lo, hi, larg)
        out.append("| Portee de la plaquette %s | %.1f x %.1f mm (sur %.0f) en fin de course, %.1f MPa |"
                   % (nom, largx, pp, larg, pr))
    out.append("| Arete cassee des pieces de tole | %g x 45 degres sur les deux faces |"
               % p.CHANFREIN)
    fcr, inertie, v = spec.charge_fissuration()
    out.append("| Effort estime a la fissuration (beton a 4 MPa) | %.1f kN |" % (fcr / 1000.0))
    out.append("| Fleche a la fissuration | %.2f mm |"
               % (fcr * p.PORTEE ** 3 / (48.0 * p.POUTRE_E * inertie)))
    sig = p.effort_membrure() / (p.W_MEMBRURE * p.EP_FLANC)
    out.append("| Jauge fibre sur la membrure haute | %.1f microdef/kN |"
               % (sig / p.E_ACIER * 1e6 / (p.CHARGE_DIM / 1000.0)))
    fem, _ = spec.lire_json("fem_flanc.json")
    if fem:
        out.append("| Calcul EF du flanc a %g kN | von Mises %.0f MPa, coefficient %.2f a froid, fleche %.3f mm |"
                   % (p.CHARGE_DIM / 1000.0, fem["von_mises_max"], p.RE_TOLE / fem["von_mises_max"],
                      fem["fleche_max"]))
        out.append("| Coefficient a 150 C | %.2f en %s de %g mm (Re %.0f a chaud, pour %.0f a 20 C EXIGES au certificat) |"
                   % (p.RE_TOLE_CHAUD / fem["von_mises_max"], p.MATIERE_TOLE, p.EP_FLANC, p.RE_TOLE_CHAUD,
                      p.RE_TOLE))
    f3, d3 = spec.lire_json("flambement3.json")
    f1, d1 = spec.lire_json("flambement.json")
    if f3:
        sym = dict((q["cas"], q["facteurs"][0]) for q in f3["cas"])
        out.append("| Flambement hors plan des flancs | facteur critique %.1f couche, %.1f debout (les deux"
                   " flancs penchent ensemble, tenus par la flexion des %d entretoises tubulaires, bouts serres) |"
                   % (sym.get("tubes_couche", 0), sym.get("tubes_debout", 0), P.n_entretoises()))
    if f1:
        anti = dict((q["cas"], q["facteurs"][0]) for q in f1["cas"])
        out.append("| Flambement, flancs en sens contraire | au moins %.1f (calcul du %s, avant les entretoises de chape et de sommet) |"
                   % (anti.get("entretoises_couche", 0), d1))
    out.append("")
    out.append("Graduation de charge gravee sur le flanc, loi non lineaire :\n")
    out.append("| charge | descente du coulisseau |")
    out.append("|---|---|")
    for kn in (2, 4, 6, 8, 10, 12):
        out.append("| %d kN | %.2f mm |" % (kn, p.pile_ecrasement(kn * 1000.0)))
    out.append("")

    out.append("## Ordre de montage\n")
    out.append("Le cadre se monte A PLAT : les entretoises, la traverse et la tete de charge doivent"
               " etre en place avant de presenter le second flanc. Les numeros V renvoient a la"
               " visserie.\n")
    ordre = ordre_de_montage()
    if len(ordre) != len(CLES_MONTAGE):
        raise SystemExit("ordre de montage : %d etapes pour %d cles (CLES_MONTAGE)"
                         % (len(ordre), len(CLES_MONTAGE)))
    for i, t in enumerate(ordre):
        out.append("%d. %s" % (i + 1, t))
    out.append("")

    out.append("## Position debout, dans l'etuve\n")
    for i, t in enumerate(position_debout()):
        out.append("%d. %s" % (i + 1, t))
    out.append("")

    out.append("## Changement d'eprouvette\n")
    intro, etapes = changement_eprouvette()
    out.append(intro)
    out.append("")
    for i, t in enumerate(etapes):
        out.append("%d. %s" % (i + 1, t))
    out.append("")

    path = os.path.join(HERE, "NOMENCLATURE.md")
    with open(path, "w") as f:
        f.write("\n".join(out))
    print(path)
    print("masse du cadre : %.1f kg" % total)


if __name__ == "__main__":
    main()
