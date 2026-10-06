# -*- coding: utf-8 -*-
"""
Toutes les cotes du banc, en millimetres. Source unique : le 3D, les DXF et les
plans en decoulent. Changer une valeur ici et relancer make.py suffit.

Repere :  x le long de la poutre, 0 au milieu
          z vers le haut, 0 au bord inferieur du flanc
          y transversal, 0 au plan median du banc
"""

import math
import os

# ============================================================ eprouvette

POUTRE_L = 840.0          # longueur
POUTRE_B = 103.0          # largeur (y)
POUTRE_H = 107.0          # hauteur (z), sens de la flexion
POUTRE_RHO = 2400.0       # kg/m3
POUTRE_E = 30000.0        # MPa

PORTEE = 750.0            # entraxe des appuis
X_APPUI = PORTEE / 2.0

# plats de renfort colles sous la face inferieure. PIECE DU COMMERCE : feuillard
# 20 x 2 S235 coupe a longueur, angles vifs. Une bande de 840 x 20 decoupee au
# laser dans une tole de 2 se voilerait.
PLAT_B = 20.0
PLAT_E = 2.0
PLAT_L = POUTRE_L
PLAT_R = 0.0              # angles vifs : plat du commerce scie a longueur

# ============================================================ cadre

EP_FLANC = 8.0            # epaisseur NOMINALE des deux toles de 8 (42CrMo4 et S355JR, voir NUANCES) ; repli 10 en S355
# EPAISSEURS REELLES DES DEUX TOLES LIVREES. Les pieces de 8 sortent de DEUX
# toles (voir NUANCES DES TOLES) : 42CrMo4 pour les flancs et les platines de
# butee, S355JR pour les pieds, les crochets, les plaques de traverse et les
# plateaux du poussoir. Une tole de 8 du commerce sort avec une tolerance de
# l ordre de -0,5 / +1,2 (EN 10029 classe A, a confirmer avec le fournisseur) :
# des fentes calculees sur 8,00 juste n accepteraient plus une tole de 8,5. Les
# deux toles se MESURENT SEPAREMENT, et toute largeur DECOUPEE qui recoit une
# autre tole suit l epaisseur de la tole qu elle RECOIT :
#   EP_TOLE_REELLE_S355 : encoches a mi-bois du flanc (chant bas et coins :
#     elles recoivent un pied), mortaise de traverse (TRAVERSE_LX_REEL), fente
#     de calage du pied (elle recoit la dent du crochet) ;
#   EP_TOLE_REELLE_42 : encoches a mi-bois et nodes du pied (ils recoivent un
#     flanc), rainure des patins d appui (bossage du flanc), serrages de
#     boulonnerie a travers les flancs et les platines.
# Le modele 3D, les masses et le calcul EF restent a la cote NOMINALE. Avec les
# valeurs par defaut, la geometrie est identique au micron.
EP_TOLE_REELLE_42 = EP_FLANC      # tole 42CrMo4 MESUREE : flancs, platines de butee
EP_TOLE_REELLE_S355 = EP_FLANC    # tole S355JR MESUREE : pieds, crochets, traverse, poussoir
NOTE_TOLE_REELLE = ("mesurer les deux toles livrees, regler EP_TOLE_REELLE_42 (42CrMo4) et"
                    " EP_TOLE_REELLE_S355 (S355JR) et regenerer les DXF avant decoupe")
ECART_FLANCS = 60.0       # distance interieure entre les deux flancs
# ETUVE. Les 500 etaient une valeur avec marge ; des pieds de 518,4 (crochets
# a 500 d entraxe) imposent au moins 530. Largeur de 538 confirmee le 05/10/2026.
# verifie() passe pour ETUVE_INTERIEUR de 530 a 551 (balayage du 02/10/2026) :
# en dessous, la douille de manoeuvre n'a plus ses 90 mm ; au dessus, la dent
# du crochet n'a plus la place du conge R3 de l'angle de l'appui (le profil
# ne se construit plus) et le crochet est a redessiner. Le pied et le
# crochet en dependent : leurs DXF portent ALERTE_ETUVE tant que
# ETUVE_CONFIRMEE est faux.
# Chambre : LARGEUR 538 (parois laterales, ou pendent les crochets) et
# PROFONDEUR (porte - fond, sens des pieds) = pied + 5 de chaque cote (05/10/2026).
ETUVE_INTERIEUR = 538.0   # entre les DEUX PAROIS OU PENDENT LES CROCHETS (sens des 440 du cadre debout) : place la dent ; CONFIRMEE le 05/10/2026
ETUVE_HAUTEUR = 1400.0    # hauteur interieure : le cadre y est DEBOUT, sur son about  (A CONFIRMER)
ETUVE_CONFIRMEE = True    # 538 confirmee par l utilisateur le 05/10/2026
ALERTE_ETUVE = "NE PAS DECOUPER AVANT CONFIRMATION DE LA LARGEUR D'ETUVE"
ETUVE_PAROI_E = 1.0       # tole de paroi interieure
ETUVE_TROU = 10.0         # trous CARRES de paroi ou s accrochent les crochets
ETUVE_TROU_PAS = (40.0, 30.0)   # entraxes verticaux successifs des trous, de haut en bas : 40 et 30 en alternance (corrige le 05/10/2026, avant 40 / 50)
# Ce que le banc peut occuper selon y, de part et d autre de son plan median.
# La garde couvre un decentrage du cadre (pieds de 518,4 dans 538 : 9,8 mm) et
# 10 mm de marge. Remplace les 250 ecrits en dur de l ancienne etuve de 500.
ETUVE_JEU_PIED = 5.0      # jeu de chaque cote du pied dans l autre sens
# PROFONDEUR utile, sens porte - fond (y, celui des pieds) : le pied et 5 de chaque cote
ETUVE_Y = None           # fixee plus bas, une fois PIED_Y connu
ETUVE_GARDE = 2.0 * ETUVE_JEU_PIED   # decentrage du cadre (jeu du pied) + 5 de marge
Y_FLANC = (ECART_FLANCS + EP_FLANC) / 2.0     # 34, plan median d'un flanc

L_FLANC = 960.0
H_FLANC = 440.0           # la commande par coin libere le haut du cadre
R_COIN = 20.0

W_MONTANT = 45.0
X_FENETRE = L_FLANC / 2.0 - W_MONTANT         # 435.0

W_MEMBRURE = 20.0         # hauteur de la membrure haute
W_BIELLE = 35.0           # largeur des bielles, mesuree perpendiculairement
W_MEMB_BASSE = 40.0       # hauteur de la membrure basse

X_NOEUD = 65.0            # loge la fente du coin et les deux lumieres
Z_NOEUD_BAS = 216.0
Z_BIELLE_NOEUD = 300.0

# ============================================================ entretoises

# Tube de PRECISION : un tube de construction S235 commence a 21,3 de diametre.
# C est la longueur des entretoises qui fixe l ecart des flancs, donc le jeu des
# epaulements de traverse (TRAVERSE_JEU_Y) : coupe a +0,1/0, faces dressees.
# 20 x 2 depuis le 06/10/2026 (avant 20 x 4,5) : la precharge des M10, reduite
# a COUPLE_M10 = 25 N.m, y fait environ 110 MPa ; le voilement des flancs,
# tenu en partie par la flexion des tubes, a ete recalcule (fem_flamb3.py).
ENTRETOISE_DE = 20.0
ENTRETOISE_DI = 16.0
ENTRETOISE_RE = 235.0     # Re retenu pour le tube : celui du E235 normalise, sans compter le gain de l etat +C
ENTRETOISE_RE_CHAUD = 190.0   # a 150 C, meme abattement que le S235
# Serrage des vis M10 8.8 du cadre (V1) et de la chape (V9), et precharge
# F = C / (K d) avec K = 0,2 (acier zingue, sec).
COUPLE_M10 = 25.0
K_COUPLE = 0.2
PRECHARGE_M10 = COUPLE_M10 * 1000.0 / (K_COUPLE * 10.0)     # N, 12,5 kN a 25 N.m
ENTRETOISE_L = ECART_FLANCS
ENTRETOISE_MATIERE = "E235+C EN 10305-1"
ENTRETOISE_BRUT = "tube de precision %g x %s" % (ENTRETOISE_DE, ("%g" % ((ENTRETOISE_DE - ENTRETOISE_DI) / 2.0)).replace(".", ","))
ENTRETOISE_TOL = "+0,1/0"              # sur ENTRETOISE_L, faces dressees // 0,05
SUPPORT_TUBE_TOL = "+/-0,2"            # sur SUPPORT_TUBE_L, entretoises de butee

# ============================================================ boulonnerie M10
# Vis de CADRE : une par entretoise, sauf les deux de la chape qui ont leurs
# propres vis (SUPPORT_TIRANT_L). Vis TH M10 ISO 4014 8.8 zinguee, une rondelle
# sous la tete et une sous l ecrou, ecrou autofreine TOUT METAL ISO 7042
# classe 8. Pas d ecrou a bague polyamide (ISO 7040, DIN 985) : la bague flue
# vers 120 C et ne freine plus dans l etuve a 150 C. Les longueurs sont
# controlees par verifie() via boulonnerie().
RONDELLE_M10_E = 2.0      # rondelle ISO 7089 M10, 10,5 x 20 x 2
ECROU_FREIN_H = 10.0      # ecrou ISO 7042 M10, hauteur maxi
ECROU_FREIN_REF = "ISO 7042 classe 8, autofreine tout metal"
ENTR_VIS_L = 100.0        # vis TH M10 x 100 : serrage 80, ecrou sur le filet, 10 de depassement
ENTR_VIS_FILET = 26.0     # filetage partiel ISO 4014 : b = 2d + 6 pour L <= 125
TRAVERSE_TIRANT_L = 90.0  # tige filetee M10 x 90 du paquet de traverse + 2 rondelles + 2 ecrous ISO 7042
                          # (a 80, verifie() la refusait des 8,34 de tole mesuree ; a 90 elle couvre
                          # toute la tolerance de livraison, 7,5 a 9,2)
FILET_DEPASSE_MIN = 3.0   # 2 pas de M10 au dela de l ecrou : l element de freinage est en prise
FILET_MARGE_MIN = 2.5     # l ecrou reste sur la partie filetee malgre les tolerances d empilement

# ============================================================ appuis

# Le bossage est un BALANCIER, pas un galet : il donne une ligne de contact
# nette et laisse tourner la poutre, mais il n'absorbe pas le recul de 0,03 mm
# de la fibre basse, qui passe en frottement. Le rayon est donc choisi pour la
# pression de contact, pas pour une cinematique de roulement.
BOSSAGE_R = 150.0         # rayon du bombe
BOSSAGE_RELIEF = 3.5      # hauteur du bombe au dessus de la membrure basse
BOSSAGE_CONGE = 10.0      # conge de raccordement a l'arete

PATIN_B = 20.0            # largeur (y), egale a celle du plat
PATIN_L = 90.0            # longueur (x)
PATIN_E = 10.0
PATIN_R = 3.0             # angles du patin d appui, en plan
# Rainure de guidage, fraisee apres decoupe. Elle suit la tole REELLE du
# bossage qu elle recoit, celle du flanc (42CrMo4) : 9,5 avec la tole de 8,
# 11,5 en repli sur du 10.
RAINURE_JEU = 0.75        # jeu par cote du bossage dans la rainure
RAINURE_B = EP_TOLE_REELLE_42 + 2.0 * RAINURE_JEU     # 9,5
RAINURE_P = 1.5           # profondeur ; LE CONTACT A LIEU AU FOND DE LA RAINURE

PATIN_CHARGE_L = 100.0
PATIN_CHARGE_B = 100.0
PATIN_CHARGE_E = 10.0
PATIN_CHARGE_R = 6.0      # angles du patin de charge, en plan
# Dessus BOMBE (06/10/2026), comme les bossages des appuis : cylindre d axe y
# (en travers de la poutre), sommet au milieu. Le plateau bas du poussoir y
# porte sur une LIGNE a x = 0 : vraie flexion 3 points, et non une charge
# repartie sur 100 mm. Le dessous reste plat, colle sur la poutrelle.
PATIN_CHARGE_BOMBE_R = 1000.0
PATIN_CHARGE_BOMBE_F = (PATIN_CHARGE_L / 2.0) ** 2 / (2.0 * PATIN_CHARGE_BOMBE_R)   # 1,25 : chute aux bords
# Les deux goupilles 8 m6 du poussoir sont SERREES dans le patin de charge :
# trous 8 H7 perces puis aleses apres decoupe. Le laser ne fait qu un avant-trou ;
# un trou laser de 8 dans 10 mm (d < e) est conique et ne tient pas un H7.
PATIN_CHARGE_AVANT_TROU = 6.0

# ============================================================ empilement z

Z_MEMB_BASSE = W_MEMB_BASSE                         # 40
Z_BOSSAGE = Z_MEMB_BASSE + BOSSAGE_RELIEF           # 43,5 : point de contact
Z_PATIN_BAS = Z_BOSSAGE - RAINURE_P                 # 42,0 : dessous du patin
Z_PLAT_BAS = Z_PATIN_BAS + PATIN_E                  # 52,0
Z_POUTRE_BAS = Z_PLAT_BAS + PLAT_E                  # 54,0
Z_POUTRE_HAUT = Z_POUTRE_BAS + POUTRE_H             # 161,0
Z_PATIN_CHARGE_HAUT = Z_POUTRE_HAUT + PATIN_CHARGE_E

# ============================================================ rondelles Belleville

# DIN 2093 serie A 50 : De 50, Di 25,4, t 3,0, l0 4,3 donc h0 1,3.
RESSORT_DE = 50.0
RESSORT_DI = 25.4
RESSORT_T = 3.0
RESSORT_L0 = 4.3
RESSORT_H0 = RESSORT_L0 - RESSORT_T                 # 1,3, course d'une rondelle
RESSORT_N = 12                                      # en serie
RESSORT_E = 206000.0
RESSORT_NU = 0.30

CHARGE_DIM = 12000.0                                # N sur la vis


def _K1():
    d = RESSORT_DE / RESSORT_DI
    return (1.0 / math.pi) * ((d - 1.0) / d) ** 2 / ((d + 1.0) / (d - 1.0) - 2.0 / math.log(d))


def rondelle_force(s):
    """Almen-Laszlo : effort d'UNE rondelle pour un ecrasement s (mm)."""
    t, h0 = RESSORT_T, RESSORT_H0
    x = s / t
    return (4.0 * RESSORT_E / (1.0 - RESSORT_NU ** 2)) \
        * (t ** 4 / (_K1() * RESSORT_DE ** 2)) * x \
        * ((h0 / t - x) * (h0 / t - x / 2.0) + 1.0)


def pile_force(ecrasement):
    """Effort de la pile pour un ecrasement total (mm). En serie, meme effort."""
    return rondelle_force(ecrasement / RESSORT_N)


def pile_ecrasement(force):
    """Ecrasement total de la pile pour un effort donne, par dichotomie."""
    a, b = 0.0, RESSORT_H0 * RESSORT_N
    for _ in range(80):
        m = (a + b) / 2.0
        if pile_force(m) < force:
            a = m
        else:
            b = m
    return (a + b) / 2.0


PILE_H_LIBRE = RESSORT_N * RESSORT_L0               # 51,6
PILE_COURSE = RESSORT_N * RESSORT_H0                # 15,6
RESSORT_F_PLAT = rondelle_force(RESSORT_H0)
PILE_ECRAS_DIM = pile_ecrasement(CHARGE_DIM)
PILE_K_SECANT = CHARGE_DIM / PILE_ECRAS_DIM

# ============================================================ tete de charge

# Le poussoir n'est qu'un repartiteur : il etale l'effort de la pile, diametre
# 50, sur le patin de charge de 100. Aucune surface fonctionnelle, aucun
# usinage : c'est un EMPILAGE de la meme tole (EP_FLANC) que les flancs. Les
# trois plateaux sont perces au diametre du tourillon : c est le patin de
# charge, colle sur la poutre, qui fait fond.
POUSSOIR_EP = EP_FLANC
POUSSOIR_N = 3            # trois plateaux PERCES de 8 : c est le patin de charge qui fait fond
POUSSOIR_H = POUSSOIR_N * POUSSOIR_EP               # 24
POUSSOIR_L = 100.0        # poussoir : appuie sur le patin de charge
POUSSOIR_B = 58.0

# Debout, la gravite porte selon x : les plateaux du poussoir glisseraient les
# uns sur les autres avant la mise en charge. Deux goupilles 8 m6 x 30 les
# tiennent : LIBRES dans les plateaux (trous de passage decoupes au laser),
# SERREES dans le patin de charge (8 H7, voir PATIN_CHARGE_AVANT_TROU).
POUSSOIR_GOUPILLE_D = 8.0
POUSSOIR_GOUPILLE_X = 35.0
POUSSOIR_GOUPILLE_PASSAGE = 8.3   # trou de passage laser dans les plateaux

# Le coulisseau ne flechit pas : le coin appuie a la VERTICALE de la pile, sur
# la meme empreinte, et la piece ne fait que transmettre 12 kN en compression,
# soit 5,2 MPa. Son epaisseur n'est fixee que par deux details : il faut 5 mm
# de matiere au dessus des taraudages de guide du cote MINCE, et un chapeau au
# dessus de l'alesage du tourillon. Minimum justifie 28,7 ; on prend 30.
COIN_ANGLE = 12.0         # degres. Remonte ici : le coulisseau en depend.
COIN_TAN = math.tan(math.radians(COIN_ANGLE))

COULISSEAU_E = 30.0       # epaisseur de reference du coulisseau, au droit de y = 0
COULISSEAU_CHAPEAU = 6.0  # matiere minimale au dessus de l'alesage, bord mince
COULISSEAU_L = 114.0      # juste de quoi loger les taraudages de guide
# GUIDAGE DU COULISSEAU PAR TETES DE VIS.
#
# Quatre CHC M8 x 12 ISO 4762 vissees APRES COUP au travers des lumieres, dans
# quatre taraudages M8 des faces laterales du coulisseau. Leur tete, diametre 13
# et haute de 8, fait exactement l'epaisseur du flanc et devient le patin de
# guidage. Tete LISSE (non moletee) : la norme laisse le moletage au choix du
# fabricant, et c est la tete qui glisse dans la lumiere.
#
# Un cylindre sur un plan ne porte que sur une LIGNE. Il ne peut donc pas se
# coincer en biais comme le faisait la patte prismatique, dont les deux faces
# devaient rester paralleles aux joues de la lumiere ; et il est insensible aux
# rotations autour de son axe comme autour de la ligne de contact. Des quatre
# guidages hyperstatiques il ne reste que le strict necessaire.
#
# Le montage y gagne autant : on pose le coulisseau, on approche les deux
# flancs, PUIS on visse les quatre guides au travers des lumieres. Plus besoin
# d'engager des tenons a l'aveugle en presentant le second flanc.
GUIDE_VIS_D = 8.0         # CHC M8 ISO 4762 : sa tete fait 8, l'epaisseur du flanc
GUIDE_VIS_L = 12.0        # longueur SOUS TETE (ISO 4762) : CHC M8 x 12, 12 de filet = 1,5 d dans le S355
GUIDE_TETE_D = 13.0       # diametre de tete : c'est lui le patin
GUIDE_TETE_H = 8.0        # hauteur de tete = epaisseur du flanc
GUIDE_X = 44.0            # position selon x
GUIDE_Z = 12.0            # axe, au dessus du dessous du coulisseau
GUIDE_JEU = 0.5           # jeu par cote de la tete dans la lumiere
GUIDE_TARAUD_D = 6.8      # avant-trou du taraudage M8 x 1,25
GUIDE_TARAUD_P = 16.0     # profondeur TARAUDEE dans le coulisseau (la vis y entre de GUIDE_VIS_L)
GUIDE_PERCAGE_P = GUIDE_TARAUD_P + 3.0   # profondeur de l avant-trou, degagement du taraud

# Tourillon : rond etire h9, NON repris (jeu 0,40 a 0,66 dans le Di 25,4 des
# rondelles et du poussoir, ce que demande le guidage d une pile DIN 2093).
# Seulement tronconne et chanfreine aux deux bouts. Depuis le 06/10/2026 il
# est COLLE au fond de l alesage du coulisseau (25 H8, Loctite 648, 175 C) :
# flottant, il tombait sur le patin de charge, cadre couche, et n entrait plus
# que de 0,4 mm dans le coulisseau au repos. Il descend avec le coulisseau et
# ne coulisse que dans les plateaux du poussoir.
TOURILLON_D = 25.0
ALESAGE_D_COUL = 25.0         # alesage du coulisseau, H8, ou le tourillon est colle
TOURILLON_COLLE = "Loctite 648 (tient 175 C), alesage %g H8 degraisse" % ALESAGE_D_COUL
TOURILLON_ENGAGE = 8.0        # engagement dans le poussoir au repos, sans cale
TOURILLON_GARDE_MIN = 3.0     # au dessus du patin de charge, a la butee mecanique
TOURILLON_PRISE_MIN = 4.0     # dans le poussoir, au repos, avec toutes les cales
TOURILLON_CHANFREIN = 1.5  # x 45 deg aux deux bouts
TOURILLON_MATIERE = "C45+C"   # rond etire h9 courant en stock (EN 10277)
ALESAGE_D = 25.4
ALESAGE_P = POUSSOIR_N * POUSSOIR_EP                # 24 : l alesage du poussoir traverse, le patin fait fond
ALESAGE_P_COUL = 20.0     # profondeur du lamage dans le coulisseau : ne suit PAS la tole, le chapeau en depend

Z_POUSSOIR_BAS = Z_PATIN_CHARGE_HAUT
Z_POUSSOIR_HAUT = Z_POUSSOIR_BAS + POUSSOIR_H
Z_PILE_BAS = Z_POUSSOIR_HAUT
Z_COULISSEAU_BAS = Z_PILE_BAS + PILE_H_LIBRE        # a vide
Z_COULISSEAU_HAUT = Z_COULISSEAU_BAS + COULISSEAU_E
# longueur : colle sur ALESAGE_P_COUL, la pile libre, puis TOURILLON_ENGAGE dans le
# poussoir ; arrondie au demi-millimetre inferieur (coupe a la scie)
TOURILLON_L = math.floor(2.0 * (ALESAGE_P_COUL + PILE_H_LIBRE + TOURILLON_ENGAGE)) / 2.0
Z_TOURILLON_BAS = Z_COULISSEAU_BAS + ALESAGE_P_COUL - TOURILLON_L   # colle au fond du coulisseau


# ---------------------------------------------------------- commande par coin
# Une vis dans le plan des flancs regarderait une paroi d'etuve a
# (ETUVE_INTERIEUR - H_FLANC) / 2 : inaccessible. La commande est donc NORMALE
# AUX FLANCS. Un coin d'acier C45, qui porte le taraudage et deux plaques de
# frottement en bronze du commerce, glisse selon y entre le dessous plat de la
# traverse et le dessus du coulisseau taille au meme angle. Le coin ne se
# deplace que selon y : son dessus reste plaque sous la traverse, donc l'axe de
# la vis est fixe.
COIN_B = 40.0             # largeur selon x
COIN_T_MIN = 37.0         # epaisseur au droit de y = 0, coin recule
COIN_COURSE = 56.5        # course utile selon y
COIN_PORTEE = POUSSOIR_B  # le coin doit couvrir TOUTE la tete du coulisseau
COIN_L = COIN_COURSE + COIN_PORTEE                  # 114,5
COIN_MU = 0.12            # bronze graphite sur acier, a chaud : faces de glissement du coin
COIN_VIS_SOUS = 16.0      # axe du taraudage sous la face plate du coin
COIN_JEU_FENTE = 4.0      # jeu total du coin dans la fente du flanc
# RATTRAPAGE DE L EMPILEMENT VERTICAL. Poutrelle, patins, trois plateaux et
# douze rondelles : la chaine peut sortir courte de quelques mm. Au dela des
# 12 kN, le coin ne garde que COIN_COURSE.tan(a) - PILE_ECRAS_DIM de reserve en
# hauteur (2,4) ; verifie() en exige TOL_EMPILEMENT. Si l empilement mesure au
# montage est plus court, on intercale des cales de feuillard entre le
# poussoir et la pile : le coin doit toucher a moins de 5 mm de son repos.
TOL_EMPILEMENT = 2.0
CALES_EP = (1.0, 2.0)     # une cale de chaque, feuillard acier
CALE_DE = RESSORT_DE
CALE_DI = 26.0

# PLAQUETTES DE BRONZE (historique : la bague-ecrou citee ici a ete abandonnee,
# voir TARAUDAGE DIRECT plus bas). Le coin etait un bloc de bronze plein,
# 2,7 kg de barre 44 x 58 x 120 : une section qui ne se trouve pas en stock et
# qu'il faut faire debiter. Or le bronze n'est utile que sur TROIS surfaces,
# les deux faces de glissement et le filet. On le reduit donc a deux plaquettes
# de tole 8 et a une bague prise dans du rond 25, soit 0,6 kg de produits
# courants, et le coin devient un simple bloc d'acier.
#
# La plaquette du dessus est vissee SUR LE COIN et voyage avec lui : elle doit
# donc faire toute sa longueur. C'est plus de bronze que si elle etait fixee a
# la traverse (114 au lieu de 60), mais une tole ne coute rien au kilo et cela
# evite de tarauder le chant du paquet de toles de la traverse.
# PLAQUETTES DU COMMERCE : norelem 23765-01-038100, plaque de frottement en
# bronze CuZn25Al5Mn4Fe3-C a inserts graphite, autolubrifiante : 38 x 100 x 5,
# deux trous D9 a 70 d entraxe, 50 MPa statique, 35 dynamique, 230 C. Plus
# rien a decouper ni a usiner dans le bronze. Les trous ne servent pas a
# visser (le M16 passe au milieu du coin) : remplis de silicone HT, ils font
# cle. La largeur du coin (COIN_B) laisse 1 mm de chaque cote.
PLAQ_REF = "norelem 23765-01-038100"
PLAQ_ALLIAGE = "CuZn25Al5Mn4Fe3-C + graphite"
PLAQ_EP = 5.0
PLAQ_B = 38.0
PLAQ_L = 100.0
PLAQ_TROU_D = 9.0
PLAQ_TROU_L1 = 70.0
PLAQ_P_ADM = 35.0          # pression dynamique admissible du fabricant

# REBORDS DE LA PLAQUETTE DU COIN. Le collage tient largement l'entrainement,
# mais il le tient SEUL, et un joint colle qui lache ne previent pas. Deux
# rebords usines dans la masse du coin, un a chaque bout, encaissent les
# mu.N = 1,4 kN dans l'axe de la vis ; la colle ne fait plus que maintenir la
# plaquette en x et pendant le montage.
#
# Le rebord doit rester SOUS la surface du bronze : aux deux bouts de course
# il passe sous la traverse, et s'il affleurait ce serait de l'acier sur acier
# qu'on ferait glisser. Il en reste donc PLAQ_EP - PLAQ_REBORD_H de garde.
PLAQ_REBORD_H = 3.0        # hauteur du rebord au dessus de la portee : 2 de garde sous les 5 du bronze
PLAQ_JEU = 0.2             # jeu de la plaquette entre les deux rebords
# la plaquette est une piece du commerce de longueur fixe : c est la largeur
# des rebords qui s en deduit, et non l inverse
PLAQ_REBORD_L = (COIN_L - PLAQ_L - 2.0 * PLAQ_JEU) / 2.0    # rebords du dessus, selon y
PLAQ_REBORD_R = 1.5        # degagement de pied : l'angle vif de la plaquette doit porter

# FIXATION DES PLAQUETTES : pas d epoxy. Bronze et acier ne se dilatent pas
# pareil (18,5 contre 12 microdef/K) : a 150 C, une plaquette de 100 mm
# s allonge de 0,08 mm de plus que son siege. Colles sur toute la longueur par
# une epoxy rigide, ce sont 30 a 80 MPa de cisaillement en bout de joint pour
# 15 a 20 tenus : le joint fissure au premier cycle. Les rebords prennent deja
# tout l entrainement ; il ne reste a la fixation qu a tenir la plaquette le
# temps du montage. Un silicone haute temperature, mille fois plus souple,
# le fait sans rien transmettre.
COLLE_G = 1.0              # MPa, module de cisaillement d un silicone HT
COLLE_EP = 0.3             # mm, epaisseur du joint
COLLE_TAU_ADM = 1.5        # MPa, tenue au cisaillement d un silicone HT
ALPHA_BRONZE = 18.5e-6
ALPHA_ACIER = 12.0e-6
DELTA_T = 130.0            # de l atelier a l etuve

# LES DEUX PLAQUETTES SONT SUR LE COIN. La basse pourrait etre posee sur la
# pente du coulisseau, ou elle ne ferait que POUSSOIR_B de long ; elle est mise
# sur le coin comme la haute, et doit alors faire toute sa longueur. Ce sont
# 0,12 kg de bronze de plus, et en echange le coulisseau redevient un bloc nu
# -- un percage et un plan a 12 degres, ni poche ni taraudage -- les deux faces
# d'usure sortent ensemble avec le coin, et c'est deux fois le meme rebord a
# usiner au lieu de deux logements differents.
#
# Ce que cela coute : la plaquette basse traverse la fente du flanc avec le
# coin. La fente s'approfondit donc de PLAQ_DROP.
PLAQ_REBORD_DROP = PLAQ_REBORD_H / math.cos(math.radians(COIN_ANGLE))
PLAQ_DROP = PLAQ_EP / math.cos(math.radians(COIN_ANGLE))  # sa hauteur VERTICALE sur la pente

# TARAUDAGE DIRECT DANS L'ACIER. Une bague-ecrou en bronze a ete dessinee puis
# abandonnee : a la vitesse de manoeuvre d'un banc a la main, ce n'est pas la
# vitesse qui use un filet, et le couple acier dur sur acier plus tendre tient
# sans probleme s'il est monte a la pate cuivre. La tige 8.8 est plus dure que
# le C45 brut du coin : c'est le coin qui s'use, et son taraudage se refait.
#
# Le filet ne fait que COIN_TARAUD_L et non toute la longueur du coin : au dela
# le percage est repris a VIS_PASSAGE_D. Le taraud debouche donc dans un trou
# plus grand, les copeaux s'evacuent vers l'avant, et il n'y a que 5 d a
# tarauder au lieu de 7. Si le filet devait un jour lacher, le lamage d'une
# bague de bronze reste possible : rien ici n'est irreversible.
COIN_TARAUD_L = 80.0       # longueur filetee, depuis le bout EPAIS

# SENS DE MONTAGE DU COIN. Le bout EPAIS est du cote oppose a la chape, si bien
# que le coin AVANCE VERS ELLE pour charger. C'est ce sens, et lui seul, qui
# rend l'arret axial de la tige possible : la face inclinee repousse le coin
# vers son bout EPAIS, le filet tire donc la tige vers l'INTERIEUR du cadre, et
# sa tete vient appuyer sur la FACE EXTERIEURE des platines, a travers la
# butee a aiguilles. Monte a l'envers, l'effort pousserait la tige hors du
# cadre : la tete quitterait la butee et ce seraient les ecrous interieurs,
# entre les platines et le bout du coin, qui porteraient. Voir DEBOUT.md.
#
# Position de repos : le bout mince affleure le bord du coulisseau. C'est la
# SEULE position qui garde le contact sur toute la largeur du coulisseau d'un
# bout a l'autre de la course. Centrer le coin au repos reviendrait a le voir
# glisser hors du coulisseau en fin de course, avec un appui deux fois plus
# court et decentre, donc un basculement de la tete sur la pile.
COIN_Y0 = -(POUSSOIR_B / 2.0 + COIN_COURSE)         # bout EPAIS, coin recule
COIN_Y1 = COIN_Y0 + COIN_L                          # bout mince, coin recule
COIN_Y_MAX = COIN_Y1 + COIN_COURSE                  # plus grand y atteint, en fin de course
COIN_T_BOUT_EPAIS = COIN_T_MIN - COIN_Y0 * COIN_TAN
COIN_T_BOUT_MINCE = COIN_T_MIN - COIN_Y1 * COIN_TAN
COIN_T_MAX = COIN_T_MIN + COIN_COURSE * COIN_TAN    # au droit de y = 0, coin avance
PLAQ_HAUT_Y0 = COIN_Y0 + PLAQ_REBORD_L + PLAQ_JEU   # plaquette haute entre ses rebords
PLAQ_HAUT_Y1 = COIN_Y1 - PLAQ_REBORD_L - PLAQ_JEU
PLAQ_HAUT_L = PLAQ_HAUT_Y1 - PLAQ_HAUT_Y0
# plaquette basse : meme portee, mais posee sur la pente. Ses cotes sont prises
# SUR LA PENTE, et son chant penche : c'est son angle HAUT, contre le siege du
# coin, qui doit venir au pied du rebord. L'angle bas est en retrait de
# PLAQ_EP.sin(a) = 1,0 mm selon y, ce qui decale sa portee sur le coulisseau
# d'autant. Les faces interieures des rebords du dessous sont NORMALES A LA
# PENTE, comme le chant de la plaquette (parts.coin_profile).
_C = math.cos(math.radians(COIN_ANGLE))
_S = math.sin(math.radians(COIN_ANGLE))
# rebords du dessous : plus larges, pour que la meme plaque de PLAQ_L tienne
# entre eux une fois couchee sur la pente
PLAQ_REBORD_L_BAS = (COIN_L - _C * (PLAQ_L + 2.0 * PLAQ_JEU)) / 2.0
PLAQ_BAS_S0 = (COIN_Y0 + PLAQ_REBORD_L_BAS + PLAQ_EP * _S) / _C + PLAQ_JEU
PLAQ_BAS_S1 = (COIN_Y1 - PLAQ_REBORD_L_BAS + PLAQ_EP * _S) / _C - PLAQ_JEU
PLAQ_BAS_L = PLAQ_BAS_S1 - PLAQ_BAS_S0
PLAQ_BAS_Y0 = PLAQ_BAS_S0 * _C          # portee sur le coulisseau, face du BAS
PLAQ_BAS_Y1 = PLAQ_BAS_S1 * _C
COULISSEAU_H = COULISSEAU_E + (POUSSOIR_B / 2.0) * COIN_TAN  # le plan incline prend toute la section

VIS_D = 16.0              # tige filetee M16
VIS_PAS = 2.0
VIS_D2 = 14.7             # diametre sur flancs du filet
VIS_FLANC = 30.0          # demi angle de flanc : 30 metrique ISO, 15 trapezoidal
VIS_H1 = 0.541266 * VIS_PAS   # hauteur de recouvrement des flancs
VIS_L = 185.0
VIS_TETE_D = 24.0         # un ecrou H et un ecrou HM bloques font la tete
VIS_TETE_H = 22.8         # ecrou H ISO 4032 M16 (14,8) + ecrou HM ISO 4035 M16 (8)
VIS_PASSAGE_D = 18.0
# Frottement du FILET de commande : tige 8.8 dans le taraudage du coin en C45,
# acier sur acier, monte a la pate cuivre. Pour l'irreversibilite, le cas
# dangereux est le frottement BAS : on la juge a VIS_MU_MIN, pas a COIN_MU.
VIS_MU_MIN = 0.08
FILET_P_ADM = 12.0        # MPa sur les flancs : taraudage C45 / tige 8.8, manoeuvre lente

# Butee de la vis. Le coin avancant VERS elle, la butee est POUSSEE contre le
# flanc : tout le trajet d'effort est en compression. Il n'y a donc aucune
# raison d'usiner un C dans la masse. Deux platines de la MEME tole que les
# flancs, deux entretoises du MEME tube que le cadre, et deux vis H M10 x 200
# qui traversent tout : platines, entretoises, LES DEUX flancs et une entretoise
# du cadre entre eux, tete derriere le flanc oppose, ecrou cote platines. Plus
# aucun taraudage dans le flanc, et deux entretoises de cadre en plus au
# passage. Les vis ne voient que la precharge et les 329 N de desserrage.
# Les deux entretoises sont DE PART ET D'AUTRE de la vis, dans le plan de son
# axe : la platine est une poutre horizontale sur deux appuis, et les ecrous
# exterieurs tombent dans le noeud, entre la fente du coin et les bielles.
SUPPORT_EP = EP_FLANC     # meme tole que les flancs, meme debit
SUPPORT_N = 2             # platines empilees
SUPPORT_B = 70.0          # largeur au droit de l'alesage
SUPPORT_B_BOUT = 40.0     # largeur aux deux bouts, la ou le moment est nul
SUPPORT_R_BOUT = 18.0     # matiere autour des trous de vis
SUPPORT_R_CONGE = 12.0    # conges des deux flancs de la platine
SUPPORT_R_COIN = 8.0      # rayons des quatre angles d about de la platine
SUPPORT_BUTEE_D = 30.0    # butee a aiguilles AXK 1730, la seule qui passe un M16
SUPPORT_BUTEE_H = 4.0     # hauteur de l'empilage cage + deux rondelles
# cote interieur : ce qui retient la tige au DESSERRAGE seulement, 329 N
SUPPORT_RONDELLE = 2.0    # 2 rondelles trempees AS 1730 de 1 (V5) contre la face interieure
SUPPORT_ECROU_H = 16.0    # deux ecrous HM bloques l'un sur l'autre
SUPPORT_X = 52.0          # entraxe / 2 des tirants, de part et d'autre de la vis
SUPPORT_GARDE_FENTE = 6.0 # garde entre l'entretoise et le bord de la fente du coin
SUPPORT_TIRANT_D = 10.0   # vis H M10 x 200 ISO 4014, filetees sur 32, tete derriere le flanc oppose

# La traverse est le plan de glissement du coin et rien d'autre : elle recoit
# 12 kN vers le haut et les rend aux deux flancs. Elle est faite de plaques
# VERTICALES cote a cote, dont le chant du bas forme la portee, et dont deux
# tenons par plaque s'engagent dans une mortaise du flanc. Chaque plaque est une
# poutre de 64 de haut pour 60 de portee : la matiere est la ou il faut, et il
# n'y a plus ni barreau a acheter, ni taraudage, ni vis.
TRAVERSE_EP = EP_FLANC
TRAVERSE_N = 6            # 6 x 8 = 48, plus large que le coin et son jeu de fente
TRAVERSE_LX = TRAVERSE_N * TRAVERSE_EP              # 48 selon x, plus large que le coin
TRAVERSE_LX_REEL = TRAVERSE_N * EP_TOLE_REELLE_S355     # le paquet tel qu il sera livre (tole S355) : la mortaise du flanc en derive
TRAVERSE_B = ECART_FLANCS
TRAVERSE_JEU = 0.4        # jeu du tenon dans la mortaise, en HAUTEUR
# Selon y, les epaulements de la plaque laissent TRAVERSE_JEU_Y / 2 de chaque
# cote contre les faces interieures des flancs : 59,6 entre epaulements pour
# des entretoises de 60. Le tube fixe l ecart, la traverse n est jamais pincee.
TRAVERSE_JEU_Y = 0.4
# En largeur, le tenon est un EMPILAGE de TRAVERSE_N toles : la tolerance
# d'epaisseur de tole (EN 10029) s'y ajoute six fois. C'est pourquoi la
# mortaise est taillee sur TRAVERSE_LX_REEL, donc sur la tole MESUREE
# des plaques (EP_TOLE_REELLE_S355), et non sur la cote nominale.
# Le jeu en largeur vaut exactement DEUX FOIS le rayon de conge : l'arete
# superieure droite fait alors tout juste la largeur du paquet de tenons, qui
# porte sur toute sa largeur sans deborder sur un conge.
TRAVERSE_R_MORT = 2.0     # conges de la mortaise
TRAVERSE_JEU_X = 2.0 * TRAVERSE_R_MORT
TRAVERSE_R_PIED = 1.5     # degagement de pied de tenon (3 traits, poche de r.sqrt2 = 2.1 mm)
TRAVERSE_TAB_H = 20.0     # hauteur du tenon
TRAVERSE_TAB_DEP = 2.0    # depassement du tenon hors du flanc
TRAVERSE_COIFFE = 6.0     # matiere au dessus du tenon
TRAVERSE_TIRANT_D = 11.0  # passage de la tige M10 x TRAVERSE_TIRANT_L qui serre les plaques entre elles
# CHANT DU BAS FRAISE EN PAQUET : le DXF le decoupe avec TRAVERSE_SUREP de
# surepaisseur (brut laser 65 / 39), le fraisage le ramene a la cote finie
# (64 / 38) en referencant le paquet sur les faces HAUTES des tenons. Le modele
# 3D, les plans et les calculs restent a la cote finie.
TRAVERSE_SUREP = 1.0

FENTE_COIN_B = COIN_B + COIN_JEU_FENTE              # passage du coin dans le flanc
FENTE_COIN_R = 4.0                                  # conges de la fente du coin

# cotes derivees de la commande par coin, une fois l'empilement connu
Y_FLANC_EXT = Y_FLANC + EP_FLANC / 2.0              # 38, face exterieure du flanc
# Le jeu entre le dessous de traverse et le dessus du coulisseau ne vaut plus
# l'epaisseur du coin seule : il faut y loger les deux plaquettes de bronze.
Z_PLAQ_COUL = Z_COULISSEAU_HAUT + PLAQ_DROP         # dessus de la plaquette basse
Z_COIN_HAUT = Z_PLAQ_COUL + COIN_T_MIN              # face plate du coin
Z_TRAVERSE_BAS = Z_COIN_HAUT + PLAQ_EP              # dessous de traverse
Z_VIS = Z_COIN_HAUT - COIN_VIS_SOUS                 # axe du taraudage M16 du coin
FENTE_COIN_Z0 = Z_COIN_HAUT - COIN_T_BOUT_EPAIS - PLAQ_DROP - 2.0
FENTE_COIN_Z1 = Z_TRAVERSE_BAS + 2.0

# les deux tirants de la chape : dans le plan de l'axe de vis, a x = +/- SUPPORT_X
TROU_SUPPORT = ((-SUPPORT_X, Z_VIS), (SUPPORT_X, Z_VIS))

# Tenons de traverse : TRAVERSE_GARDE_FENTE de matiere entre le haut de la
# fente du coin et le bas de la mortaise. Les 36 sont une valeur historique,
# fixee quand l'entretoise haute de la chape enjambait encore la fente ; le
# minimum controle par verifie() est 10. La reduire raccourcirait la traverse
# (qui ne travaille qu a quelques MPa) mais deplacerait la mortaise, donc le
# flanc et son calcul EF : on la garde.
TRAVERSE_GARDE_FENTE = 36.0
Z_TAB0 = FENTE_COIN_Z1 + TRAVERSE_GARDE_FENTE
Z_TAB1 = Z_TAB0 + TRAVERSE_TAB_H
Z_TRAVERSE_HAUT = Z_TAB1 + TRAVERSE_COIFFE
TRAVERSE_H = Z_TRAVERSE_HAUT - Z_TRAVERSE_BAS
TRAVERSE_TIRANT_Z = (Z_TRAVERSE_BAS + Z_TAB0) / 2.0

COIN_Y_SUPPORT = COIN_Y_MAX + SUPPORT_ECROU_H + SUPPORT_RONDELLE + 6.0
SUPPORT_Y1 = COIN_Y_SUPPORT + SUPPORT_N * SUPPORT_EP    # face exterieure
SUPPORT_TUBE_L = COIN_Y_SUPPORT - Y_FLANC_EXT           # entretoises de butee
SUPPORT_Z0 = Z_VIS - SUPPORT_B / 2.0                    # platine : hauteur B
SUPPORT_Z1 = Z_VIS + SUPPORT_B / 2.0
SUPPORT_X0 = -SUPPORT_X - SUPPORT_R_BOUT                # platine : longueur
# Entretoise de SOMMET : une neuvieme, dans l'axe, au dessus de la mortaise de
# traverse. La membrure haute n'avait aucune liaison sur 500 mm, et c'est la que
# part le mode de voilement symetrique (fem_flamb3 : vers (0, 440)). Ce n'est
# PAS un serrage des flancs sur le paquet de traverse : le tube fixe l'ecart a
# ENTRETOISE_L et les epaulements de traverse gardent TRAVERSE_JEU_Y. Meme tube
# de 60, meme vis TH M10 (ENTR_VIS_L) que les autres entretoises de cadre.
ENTR_SOMMET = os.environ.get("BANC_ENTR_SOMMET", "1") == "1"
Z_ENTR_SOMMET = (Z_TAB1 + TRAVERSE_JEU / 2.0 + H_FLANC) / 2.0    # a mi-hauteur du ligament
SUPPORT_X1 = SUPPORT_X + SUPPORT_R_BOUT
# vis de chape : tete + rondelle derriere le flanc oppose, flanc, entretoise de
# cadre, flanc, entretoise de butee, platines, rondelles, ecrou. Vis du commerce
# a filetage PARTIEL : l'ecrou doit tomber entierement sur le filet, et avec
# FILET_MARGE_MIN de marge, car l'empilement additionne 4 toles et 2 tubes
# coupes. D'ou QUATRE rondelles sous l'ecrou : l'empilement fait 173,5 pour un
# filet qui commence a 168 (5,5 de marge ; 9,7 de depassement au dela des deux
# ecrous ISO 4032 de 8,4 contre-bloques), et verifie() l'accepte sur toute la tolerance de livraison de
# la tole (7,5 a 9,2). Avec trois, une tole mesuree sous 7,75 faisait tomber
# la marge sous FILET_MARGE_MIN.
SUPPORT_TIRANT_L = 200.0          # vis H M10 x 200 ISO 4014
SUPPORT_TIRANT_FILET = 32.0       # longueur filetee (b = 2d + 12 pour L > 125)
SUPPORT_RONDELLE_E = RONDELLE_M10_E
SUPPORT_RONDELLES_ECROU = 4       # sous l'ecrou
SUPPORT_ECROU_M10_H = 8.4         # ecrou H ISO 4032 M10
# Deux ecrous H contre-bloques : le premier serre (COUPLE_M10), le second est
# bloque contre lui en tenant le premier. Freinage tout metal, qui tient a
# 150 C comme les ISO 7042 des autres vis M10. Deux H plutot que H + HM : c'est
# le premier qui porte la precharge, et un HM ISO 4035 est un ecrou faible.
SUPPORT_ECROUS_M10_N = 2
SUPPORT_EMPILEMENT = (2 * EP_TOLE_REELLE_42 + ECART_FLANCS + SUPPORT_TUBE_L + SUPPORT_N * EP_TOLE_REELLE_42
                      + SUPPORT_RONDELLE_E * (1 + SUPPORT_RONDELLES_ECROU))   # sous tete, ecrou exclu
VIS_Y0 = COIN_Y0 + COIN_COURSE - 1.0                # bout de la tige filetee :
# il s'arrete a 1 mm du bout epais du coin quand celui-ci est en fin de course.
# Plus loin serait inutile, le filetage n'est jamais engage au dela.
# Ce qui depasse du cote de la chape, et ce qu il reste devant pour la douille
# de manoeuvre (cadre decentre au pire dans l etuve, voir Y_ETUVE_LIBRE).
Y_BOUT_VIS = VIS_Y0 + VIS_L
Y_BOUT_TIRANT = -Y_FLANC_EXT - SUPPORT_RONDELLE_E + SUPPORT_TIRANT_L
DEGAGEMENT_DOUILLE = None   # calcule apres ETUVE_Y (voir plus bas)

Z_MEMB_HAUTE = H_FLANC - W_MEMBRURE                 # 420

# ============================================================ percages

D_VIS = 11.0              # passage M10

TROU_COIN = ((X_FENETRE + L_FLANC / 2.0) / 2.0, 50.0)   # 40 -> 50 le 22/09/2026 : +3 MPa a l appui, mais 11 mm entre l ecrou et le pied debout au lieu de 3
TROU_COIN_HAUT_Z = H_FLANC - TROU_COIN[1]           # symetrique du bas, JAMAIS en dur
# Plus de trous de levage ni de butee d'about (supprimes le 22/09/2026).
# CALAGE DE LA POUTRELLE DEBOUT : POINT OUVERT, ASSUME. Debout, rien ne retient
# la poutrelle selon x (devenu vertical) que le frottement aux appuis, environ
# 0,15 F : il ne depasse son poids qu au dela de 1,5 kN environ. En dessous,
# le poids passe par la tete de charge. A traiter au montage (DEBOUT.md).

# ============================================================ lumiere

# Le bas de la lumiere sert de BUTEE DE COURSE : la tete de guide y arrive
# avant que la pile ne soit a plat, ce qui plafonne l'effort.
LUMIERE_B = GUIDE_TETE_D + 2.0 * GUIDE_JEU          # 14
LUMIERE_BUTEE = 11.8      # ecrasement de pile atteint quand la tete talonne
LUMIERE_GARDE = 3.0       # jeu en haut de lumiere, tete au repos
Z_GUIDE = Z_COULISSEAU_BAS + GUIDE_Z                # axe des guides, au repos
LUMIERE_Z0 = Z_GUIDE - LUMIERE_BUTEE - LUMIERE_B / 2.0
LUMIERE_Z1 = Z_GUIDE + LUMIERE_B / 2.0 + LUMIERE_GARDE

# ============================================================ ajourage

AJOUR_LIGAMENT = 10.0
AJOUR_RMIN = 8.0

AJOUR_BASSE = True
AJOUR_BASSE_N = 7
AJOUR_BASSE_R = 10.0      # 10 mm de matiere de part et d'autre, soit l'epaisseur
AJOUR_BASSE_Z = 20.0
AJOUR_BASSE_MARGE = 90.0  # recul devant les appuis : degage les trous de pied

# ============================================================ conges de fenetre

R_FEN_BAS = 22.0   # le plus grand rayon qui garde une tangente droite avant le pied du
                   # bossage (x = 413 a 435). Rejoue par EF avec le blocage propre
                   # (fem_balayage.py, R10 a R26) : 151 a 160 MPa sans tendance, c est
                   # du bruit de maillage. Le point chaud (420, 30) est dans la membrure
                   # sous le montant, pas sur l arc : le rayon n est pas le levier.
R_FEN_MONTANT = 20.0
R_FEN_NOEUD = 25.0
R_FEN_NOEUD_BAS = 15.0

# ============================================================ pied plie

# PIED A MI-BOIS CROISE. Le pied est une plaque VERTICALE de la meme tole
# (EP_FLANC) que les flancs, perpendiculaire a eux. Une encoche descend de son chant
# haut la ou passe chaque flanc ; une encoche de meme profondeur monte du chant
# du flanc la ou passe le pied. Les deux plaques s emboitent a angle droit.
# Ni vis, ni goupille, ni taraudage, ni pliage : deux decoupes laser.
#
# Ce qui PORTE, c est le fond d encoche du flanc pose sur le fond d encoche du
# pied. Pour cela le pied doit depasser le fond d encoche du flanc d une
# encoche (la sienne, pas celle du flanc, qui peut etre bien moindre) : des
# chants affleurants ne se toucheraient que par les
# joues, et le cadre ne tiendrait que par frottement. Le controle de contact
# l a signale a 0,93 mm de vide avant que quiconque ne le voie.
#
# LE MEME PIED SERT AUX DEUX POSITIONS. Couche, deux pieds dans le chant bas
# des flancs. Debout dans l etuve -- le cadre sur son about, 960 de haut --
# deux pieds dans le chant d extremite, a deux hauteurs symetriques du centre
# de gravite. Les pieds en V se montent UN PAR UN, chacun coulisse le long de
# sa propre encoche. Au passage a l etuve on laisse les pieds couches sur la
# paillasse : autour du cadre debout, la place est prise par les pieds en V et
# les crochets.
#
# Le chant au sol de chaque pied porte deux BOSSAGES : quatre points au sol. Le
# cadre est auto-reactif, le sol ne recoit que son poids.
FLANC_ENCOCHES = True     # False : flanc sans encoches de pied, pour la reference EF seulement
PIED_E = EP_FLANC
# Largeur du pied DERIVEE de l entraxe des colonnes de trous de l etuve, ou
# pendent les crochets (05/10/2026 : 500), avec PIED_FENTE_BORD_INIT de matiere
# au dela de chaque fente (fente = tole S355 du crochet + 2 x 0,2) : 518,4
# pour une tole de 8.
PIED_FENTE_ENTRAXE = 500.0     # entraxe des fentes = entraxe des crochets = colonnes de trous
PIED_FENTE_BORD_INIT = 5.0     # matiere entre la fente et le bout du pied : peu, mais impose
PIED_Y = PIED_FENTE_ENTRAXE + (EP_TOLE_REELLE_S355 + 2 * 0.2) + 2 * PIED_FENTE_BORD_INIT   # largeur : les deux bouts posent sur les crochets d etuve
PIED_CROIX = 20.0         # encoche du PIED : ce qu il embrasse du flanc
PIED_CROIX_FLANC = 8.0    # encoche du FLANC : juste de quoi le situer en x ; la membrure garde 32 de ses 40
PIED_SOL = 30.0           # du fond d encoche du pied au sol
PIED_H = PIED_SOL + PIED_CROIX + PIED_CROIX_FLANC   # 58 : le pied depasse le fond d encoche du flanc de PIED_CROIX
PIED_JEU = 0.4            # jeu total dans chaque encoche
# Largeurs decoupees des encoches a mi-bois : chacune suit la tole qu elle RECOIT.
ENCOCHE_FLANC_B = EP_TOLE_REELLE_S355 + PIED_JEU    # 8,4 : encoches du FLANC (chant bas, coins), recoivent un pied S355
ENCOCHE_PIED_B = EP_TOLE_REELLE_42 + PIED_JEU       # 8,4 : encoches du PIED, recoivent un flanc 42CrMo4
PIED_X_POS = 250.0        # plan des pieds couches, entre deux ajours, hors du champ de contrainte des appuis
# PIEDS DEBOUT : les memes plaques, emboitees aux QUATRE COINS du flanc, dans
# une encoche inclinee de PIED_DEBOUT_ANGLE sur le grand cote. Le conge R_COIN
# disparait la : c est l encoche qui tient le coin. Les deux pieds d un about
# font un V et posent le cadre sur une base de pied_debout_base(), au plus pres
# de la largeur d etuve ; ils portent sur l arete exterieure de leurs bossages.
# 38 degres et non 45 : a 45 le pied passe a 1 mm du tube d entretoise du coin.
# L encoche du coin bas entame le bout de la membrure basse : avec elle, l EF
# donne 213 MPa a l appui (out/fem_flanc.json), coefficient 2,02 a froid et
# 1,83 a 150 C sur RE_TOLE.
PIED_DEBOUT_ANGLE = 38.0
PIED_DEBOUT_PROF = 28.0   # du coin vif au fond d encoche, le long de l encoche
PIED_BOSSAGE_B = 40.0     # les deux appuis, AUX DEUX BOUTS de la plaque : ils posent sur les crochets
PIED_BOSSAGE_H = 8.0
PIED_BOSSAGE_Y = PIED_Y / 2.0 - PIED_BOSSAGE_B / 2.0    # bossage affleurant le bout
# AJOURS du pied : la plaque n est qu une poutre de 40 kg sur 470 de portee,
# on la vide entre deux membrures de PIED_AJOUR_CHORD et des montants de
# PIED_AJOUR_POST, en gardant pleins les deux bouts sous les bossages
PIED_AJOUR = True
PIED_AJOUR_CHORD = 8.0
PIED_AJOUR_POST = 10.0    # 8 laissait 5,9 au droit des degagements de fond d encoche
PIED_AJOUR_R = 6.0

# CROCHETS D ETUVE. Le fond de l etuve ne porte pas le cadre : quatre plaques
# de la meme tole PENDENT dans la colonne de trous carres des parois (tole de
# 1, trous de 10) par CROCHET_N_LANGUES langues a bec, comme un crochet de
# rayonnage ; leur bas porte un APPUI horizontal vers l interieur sur lequel
# pose le bout du pied, de chant. Une DENT sur l appui entre dans une petite
# fente du chant bas du pied, a PIED_FENTE_BORD de son bout : le cadre est
# cale en y. Plaque dans le plan du pied (y, z) ; z = 0 est le dessus de la
# langue haute, y = 0 la face interieure de la paroi.
# Le poids et le couple de l appui tirent le haut vers l interieur : les becs
# des langues le retiennent ; le bas du corps s appuie sur la paroi. Pose :
# la tete (langue + bec) passe le trou DE FACE, crochet a l horizontale, puis
# on le laisse descendre : le bec retombe derriere la paroi. Un crochet rigide a
# plusieurs langues ne peut pas s incliner pour engager une tete plus haute que le
# trou (12,7 deg au plus entre deux langues), d ou langue 6 + bec 3 < 10.
CROCHET_E = EP_FLANC      # 8 dans un carre de 10 : 1 de jeu par cote
CROCHET_N_LANGUES = 4     # 4 trous au lieu de 3 : l effort se repartit sur une paroi de 1 sans allonger le crochet
CROCHET_LANGUE_H = ETUVE_TROU - 4.0        # 6 : descend de 4 apres le passage de la tete
CROCHET_BEC = 3.0         # retombee derriere la paroi : tete de 9 dans le carre de 10
CROCHET_BEC_L = 5.0       # sa longueur, au dela de la paroi
# la langue traverse la paroi, laisse 3 de jeu, puis retombe en bec : l encoche
# entre le bec et le corps fait 4 = la moitie de la tole, ce que le laser coupe
# proprement (verif_percages, encoches du contour)
CROCHET_LANGUE_L = ETUVE_PAROI_E + 3.0 + CROCHET_BEC_L
CROCHET_BANDE = 20.0      # hauteur de l appui
CROCHET_CORPS = 12.0      # largeur du corps le long de la paroi : la dent doit passer a cote
CROCHET_S = 60.0          # appui, de la paroi vers l interieur
CROCHET_LANGUE_Z = tuple(-sum(ETUVE_TROU_PAS[j % 2] for j in range(i)) for i in range(CROCHET_N_LANGUES))  # dessus des langues
# La langue basse descend au niveau de l appui (elle est cote paroi, l appui
# de l autre cote du corps) : 10 au plus entre le dessous de la langue basse
# et le bas du crochet.
CROCHET_GARDE_BAS = 10.0
CROCHET_H = -CROCHET_LANGUE_Z[-1] + CROCHET_LANGUE_H + CROCHET_GARDE_BAS   # hauteur totale
CROCHET_Z_APPUI = -CROCHET_H + CROCHET_BANDE                                # dessus de l appui
# fente de calage du pied et dent de l appui
PIED_FENTE_BORD = PIED_FENTE_BORD_INIT     # du bout du pied a la fente
ETUVE_Y = PIED_Y + 2.0 * ETUVE_JEU_PIED     # 528,4 : profondeur utile de la chambre (porte - fond)
Y_ETUVE_LIBRE = ETUVE_Y / 2.0 - ETUVE_GARDE    # ce que le banc peut occuper selon y
DEGAGEMENT_DOUILLE = Y_ETUVE_LIBRE - Y_BOUT_VIS
PIED_COIN_R = 2.0         # rayon des angles du bout du pied
PIED_FENTE_JEU = 0.2      # jeu par cote de la dent du crochet dans la fente
PIED_FENTE_B = EP_TOLE_REELLE_S355 + 2.0 * PIED_FENTE_JEU    # 8,4 : la dent du crochet (tole S355) y passe
PIED_FENTE_H = 7.0        # assez pour la dent meme sur le pied debout, incline de PIED_DEBOUT_ANGLE
# La dent PORTE le pied : le fond de la fente pose dessus. Comme le pied en V
# est incline, le fond de sa fente l est aussi : le dessus de la dent est coupe
# a PIED_DEBOUT_ANGLE pour porter sur toute sa largeur, et la dent est un peu
# plus etroite que l epaisseur du pied vue en biais (8 / cos 38 = 10,2).
CROCHET_DENT_B = 6.0      # largeur de la dent le long de l appui
CROCHET_DENT_H = 4.5      # hauteur au milieu de la dent
# Les crochets servent le cadre DEBOUT : ils sont dans le plan des flancs (x, z),
# a y = +/- PIED_FENTE_Y, la ou les pieds en V ont leur fente ; ils pendent aux
# parois qui font face aux abouts du cadre couche (z = H/2 +/- ETUVE/2) et
# leur appui recoit l arete basse de chaque pied en V. La dent est a l aplomb
# de cette arete : sa distance a la paroi depend de la largeur d etuve, A CONFIRMER.
PIED_FENTE_Y = PIED_Y / 2.0 - PIED_FENTE_BORD - PIED_FENTE_B / 2.0    # 245,8 : axe des fentes, et des crochets
MASSE_TOTALE_ESTIMEE = 70.0   # kg, cadre et poutrelle, pour les crochets
CROCHET_Z_PAROI = H_FLANC / 2.0 - ETUVE_INTERIEUR / 2.0   # paroi face au coin bas, cadre couche ; l autre par symetrie
PIED_R = 1.5              # degagements de fond d encoche (3 traits, poche de 2.1 mm)
# NODES : sur chaque joue d encoche du pied, une bosse de PIED_NODE_L de long qui
# ramene le passage de ENCOCHE_PIED_B (8,4) a EP_TOLE_REELLE_42 - 2 x
# PIED_NODE_SERRE (7,8) : le flanc (42CrMo4) y entre avec PIED_NODE_SERRE de SERRAGE par
# cote et l assemblage ne prend plus de jeu ; le reste de la joue garde
# PIED_JEU. C est la pratique courante des assemblages laser a tenons.
PIED_NODE_L = 8.0
PIED_NODE_SERRE = 0.1
TROU_PIED_DX = 25.0

# Arete cassee des pieces de tole. Ce n'est pas une coquetterie : c'est la cote
# qui rend l'empilage LISIBLE. Les six plaques de traverse jointives, sans
# arete cassee, forment un bloc de 48 a l'ecran comme a la main ; avec un
# chanfrein a 45 il y a une rainure en V a chaque joint. Elle sert aussi de
# reserve de graisse sous le coin, et elle evite l'arete vive qui marquerait
# le bronze. Elle se paie sur les surfaces portantes : le bossage d'appui ne
# porte que sur EP_FLANC - 2 x CHANFREIN (hertz_appui), le bronze et les
# tenons de traverse perdent 2 x CHANFREIN par joint (portee_coin, appui_tenon).
CHANFREIN = 0.8

# ============================================================ matiere

RHO_ACIER = 7850.0
# NUANCES DES TOLES DE 8 (decision du 05/10/2026) : DEUX toles.
# - 42CrMo4 +A (MATIERE_TOLE, BRUT_TOLE) : FLANCS et PLATINES DE BUTEE ; les
#   platines s imbriquent dans les chutes de la tole des flancs.
# - S355JR (MATIERE_TOLE_COURANTE, BRUT_TOLE_COURANTE), tole de 8 du commerce,
#   certificat 2.2 : PIEDS, CROCHETS, PLAQUES DE TRAVERSE, PLATEAUX DU POUSSOIR.
# Seul le flanc (213 MPa a l EF) a besoin du 42CrMo4. La platine (130 MPa)
# garderait en S355 un coefficient de 2,3 a 150 C, sous le seuil de 2,5 de
# verifie() : elle reste en 42CrMo4. La traverse travaille a 8 MPa en flexion
# et 26 en matage, les crochets a environ 15 MPa, les pieds et le poussoir a
# quelques MPa : le S355 suffit largement. Les plaques de traverse en S355
# frottent sur la plaque bronze-graphite par leur chant fraise : acceptable a
# environ 8 MPa et a cette vitesse.
# TOLE 42CrMo4. Le cadre est passe de 10 mm S355 a 8 mm 42CrMo4 (environ
# 9 kg de moins). Limite elastique retenue : etat RECUIT (+A), le plus mou que
# puisse livrer un fournisseur ; a l'etat +QT elle depasse 650. Or l'EN 10083-3
# ne garantit a l'etat +A qu'une durete maximale, pas de Re : toute la marge du
# flanc (EF 213 MPa, 2,02 a froid, 1,83 a 150 C) repose sur RE_TOLE. Il faut
# donc l'EXIGER a la commande, certificat 3.1 avec essai de traction : c'est
# EXIGENCE_TOLE, reprise en abrege (BRUT_TOLE) dans les cartouches et la
# nomenclature. Abattement a 150 C : 10 pour cent, comme les aciers doux.
NUANCE_TOLE = "42CrMo4"
RE_TOLE = 430.0
RE_TOLE_CHAUD = 390.0
MATIERE_TOLE = "%s +A" % NUANCE_TOLE
BRUT_TOLE = "tole %g mm, cert. 3.1, Re >= %.0f" % (EP_FLANC, RE_TOLE)     # tient dans une case de cartouche
EXIGENCE_TOLE = ("%s recuit +A, tole %g mm : certificat 3.1 EN 10204 avec essai de"
                 " traction, Re >= %.0f MPa a 20 C" % (NUANCE_TOLE, EP_FLANC, RE_TOLE))
RE_S355 = 355.0           # coulisseau, patins, tole courante
RE_S355_CHAUD = 300.0     # limite elastique a 150 degres C
# TOLE COURANTE S355JR : pieds, crochets, plaques de traverse, plateaux du poussoir.
NUANCE_TOLE_COURANTE = "S355JR"
MATIERE_TOLE_COURANTE = NUANCE_TOLE_COURANTE
RE_TOLE_COURANTE = RE_S355
RE_TOLE_COURANTE_CHAUD = RE_S355_CHAUD
BRUT_TOLE_COURANTE = "tole %g mm, cert. 2.2" % EP_FLANC      # tient dans une case de cartouche
EXIGENCE_TOLE_COURANTE = ("%s, tole %g mm du commerce : certificat 2.2 EN 10204"
                          % (NUANCE_TOLE_COURANTE, EP_FLANC))
# Contact bossage / fond de rainure : la limite est celle du plus mou des deux
# corps, le patin en S355 (1,6 Re a chaud = 480 MPa), et non celle de la tole.
HERTZ_LIM = 1.6 * min(RE_S355_CHAUD, RE_TOLE_CHAUD)
HERTZ_COEF_MIN = 1.3
# REPLI si la tole de 8 en 42CrMo4 manque : EP_FLANC = 10 en S355 (157 MPa,
# 1,91 a 150 C) ou en S460 (2,48). Le rayon de fenetre n est pas un levier
# (balayage EF R10-R26 : bruit de maillage).
RE_S460 = 460.0
RE_S460_CHAUD = 390.0     # meme abattement que le S355 a 150 degres C
E_ACIER = 210000.0

# ============================================================ bruts d usinage

# Bruts des pieces USINEES (coin, coulisseau), calcules par parts.brut_usinage
# sur la boite englobante de la piece finie : BRUT_SUREP par face, BRUT_SURLONG
# sur la longueur (trait de scie et dressage), arrondi au BRUT_PAS superieur.
BRUT_SUREP = 1.5
BRUT_SURLONG = 5.0
BRUT_PAS = 5.0

# ============================================================ edition

# Indice et date portes par les cartouches et les DXF : plusieurs generations
# de fichiers ont cohabite dans out/, l'atelier doit savoir laquelle il tient.
INDICE_REVISION = "B"
DATE_EDITION = "05/10/2026"

# ============================================================ grandeurs derivees


def axe_neutre():
    """
    Position de l'axe neutre de la section homogeneisee, au dessus de la face
    INFERIEURE de la poutre. Les deux plats colles le descendent de 2,6 mm.
    """
    n = E_ACIER / POUTRE_E
    a_beton = POUTRE_B * POUTRE_H
    a_plats = 2.0 * PLAT_B * PLAT_E * n
    return (a_beton * POUTRE_H / 2.0 + a_plats * (-PLAT_E / 2.0)) / (a_beton + a_plats)


def bras_contact_axe_neutre():
    """Distance du point de contact d'appui a l'axe neutre de la poutre."""
    return (Z_POUTRE_BAS + axe_neutre()) - Z_BOSSAGE




def pied_debout_arete():
    """
    Pied en V du coin (-L/2, 0) : point (x, z) de l arete par laquelle il pose,
    la plus basse (x mini) de sa face de bout. Le plan de pose du pied (z = 0 de
    son profil) est a PIED_SOL sous le fond d encoche, lui-meme a
    PIED_DEBOUT_PROF du coin vif le long de l encoche ; le bout de la plaque
    est a PIED_E / 2 de part et d autre de sa ligne moyenne.
    """
    a = math.radians(PIED_DEBOUT_ANGLE)
    d = (math.cos(a), math.sin(a))                   # le long de l encoche, vers la matiere
    n = (-math.sin(a), math.cos(a))                  # normale a la plaque, vers x negatif
    t = PIED_DEBOUT_PROF - PIED_CROIX_FLANC - PIED_SOL
    px, pz = -L_FLANC / 2.0 + d[0] * t + n[0] * PIED_E / 2.0, d[1] * t + n[1] * PIED_E / 2.0
    # l angle est arrondi a PIED_COIN_R : le point le plus bas est celui de l arc,
    # a r de son centre, et le centre est a r des deux faces (directions d et -n)
    r = PIED_COIN_R
    return (px + r * (d[0] - n[0]) - r, pz + r * (d[1] - n[1]))


def pied_debout_base():
    """Ecartement des deux aretes de pose des pieds en V, de part et d autre du cadre."""
    return H_FLANC - 2.0 * pied_debout_arete()[1]


def pied_debout_encombrement():
    """Ce que les pieds en V ajoutent de chaque cote du cadre debout, et sous son about."""
    a = math.radians(PIED_DEBOUT_ANGLE)
    d = (math.cos(a), math.sin(a))
    t = PIED_DEBOUT_PROF - PIED_CROIX_FLANC - PIED_SOL
    z_ext = d[1] * t - math.cos(a) * PIED_E / 2.0     # angle exterieur du bout
    return -z_ext, -pied_debout_arete()[0] - L_FLANC / 2.0


def pied_debout_fente():
    """
    Pied en V du coin (-L/2, 0) : point (x, z) du fond de sa fente de calage,
    au milieu de l epaisseur, la ou pose le dessus de la dent du crochet. Le
    fond de la fente est parallele a la face de bout, PIED_FENTE_H plus haut le
    long de la plaque ; on le prend a mi-hauteur de dent au dessus du bord.
    """
    a = math.radians(PIED_DEBOUT_ANGLE)
    d = (math.cos(a), math.sin(a))
    t = PIED_DEBOUT_PROF - PIED_CROIX_FLANC - PIED_SOL + PIED_FENTE_H
    return (-L_FLANC / 2.0 + d[0] * t, d[1] * t)


CROCHET_DENT_Y = pied_debout_fente()[1] - CROCHET_Z_PAROI   # la dent sous le fond de la fente du pied en V


def pied_debout_coins():
    """
    Pour le coin (-L/2, H), les autres par symetrie : angles du fond d encoche
    (cote chant haut, cote chant d about), bout du pied, et garde du pied au
    tube d entretoise du coin (distance du bord du pied au tube).
    """
    a = math.radians(PIED_DEBOUT_ANGLE)
    d = (math.cos(a), -math.sin(a))          # direction de l encoche, vers la matiere
    n = (math.sin(a), math.cos(a))           # normale, cote chant haut
    w2 = ENCOCHE_FLANC_B / 2.0               # encoche du flanc : recoit le pied
    t = PIED_DEBOUT_PROF
    x0, z0 = -L_FLANC / 2.0, H_FLANC
    ca = (x0 + d[0] * t + n[0] * w2, z0 + d[1] * t + n[1] * w2)
    cb = (x0 + d[0] * t - n[0] * w2, z0 + d[1] * t - n[1] * w2)
    tb = t + PIED_CROIX
    bout = (x0 + d[0] * tb, z0 + d[1] * tb)
    # tube du coin : projection sur l axe du pied, bornee au segment fond -> bout
    hx, hz = -TROU_COIN[0] - x0, TROU_COIN_HAUT_Z - z0
    s = min(max(hx * d[0] + hz * d[1], 0.0), tb)
    px, pz = x0 + d[0] * s, z0 + d[1] * s
    garde = math.hypot(px + TROU_COIN[0], pz - TROU_COIN_HAUT_Z) - ENTRETOISE_DE / 2.0 - PIED_E / 2.0
    return ca, cb, bout, garde


def hertz_largeur():
    """
    Longueur portante du bossage dans le fond de rainure : l'epaisseur du flanc
    moins ses deux aretes cassees, qui ne touchent pas.
    """
    return EP_FLANC - 2.0 * CHANFREIN


def hertz_appui(charge_par_contact=None):
    """Pression de Hertz au contact bossage / fond de rainure, en MPa."""
    f = charge_par_contact if charge_par_contact else CHARGE_DIM / 4.0
    pp = f / hertz_largeur()
    e_etoile = E_ACIER / (2.0 * (1.0 - 0.3 ** 2))
    a = math.sqrt(4.0 * pp * BOSSAGE_R / (math.pi * e_etoile))
    return 2.0 * pp / (math.pi * a)


def hertz_charge():
    """Pression de Hertz au contact plateau bas du poussoir / dessus bombe du
    patin de charge, a CHARGE_DIM, en MPa : ligne de POUSSOIR_B, aretes cassees."""
    pp = CHARGE_DIM / (POUSSOIR_B - 2.0 * CHANFREIN)
    e_etoile = E_ACIER / (2.0 * (1.0 - 0.3 ** 2))
    a = math.sqrt(4.0 * pp * PATIN_CHARGE_BOMBE_R / (math.pi * e_etoile))
    return 2.0 * pp / (math.pi * a)


def hertz_coef():
    """Coefficient au contact d'appui : HERTZ_LIM (patin S355 a chaud) sur la pression."""
    return HERTZ_LIM / hertz_appui()


def largeur_bossage():
    """Largeur totale du bossage, conges compris."""
    dz = Z_MEMB_BASSE - (Z_BOSSAGE - BOSSAGE_R)
    return 2.0 * math.sqrt((BOSSAGE_R + BOSSAGE_CONGE) ** 2 - (dz + BOSSAGE_CONGE) ** 2)


def effort_membrure(charge=None):
    """Traction dans la membrure haute, par flanc, en N."""
    import parts
    f = (charge if charge else CHARGE_DIM) / 2.0
    return (f / 2.0 * X_APPUI) / parts.profondeur_treillis()


def portee_coin():
    """
    Largeur REELLE de contact sur la traverse, selon x. Ce n'est pas le coin
    qui frotte sous la traverse mais la plaquette de bronze du dessus, large de
    PLAQ_B : c'est elle qu'on compte.

    Les aretes cassees des plaques creusent une rainure en V a chaque joint :
    le bronze n'appuie plus sur toute sa largeur. C'est une perte assumee, les
    rainures servant de reserve de graisse, mais elle doit etre comptee.
    """
    joints = [-TRAVERSE_LX / 2.0 + k * TRAVERSE_EP for k in range(1, TRAVERSE_N)]
    dedans = sum(1 for x in joints if abs(x) < PLAQ_B / 2.0)
    return PLAQ_B - 2.0 * CHANFREIN * dedans


def pressions_plaquettes():
    """
    Pressions de contact (haute, basse) des deux plaques de bronze, en MPa, au
    plus defavorable des deux bouts de course : largeur nette selon x fois
    longueur portante selon y. La haute porte sur la traverse rainuree
    (portee_coin), la basse sur le coulisseau, un bloc plein (PLAQ_B entier).
    """
    ph = portee_plaquette(PLAQ_HAUT_Y0, PLAQ_HAUT_Y1, TRAVERSE_B)
    pb = portee_plaquette(PLAQ_BAS_Y0, PLAQ_BAS_Y1, POUSSOIR_B)
    return CHARGE_DIM / (portee_coin() * ph), CHARGE_DIM / (PLAQ_B * pb)


def pression_coin():
    """Pression de contact du bronze sur la traverse, rainures deduites, fin de course."""
    return pressions_plaquettes()[0]


def coin_effort():
    """Effort moteur sur le coin, a la charge de dimensionnement."""
    # Forme exacte : la reaction de la face inclinee est a (a + phi) de la
    # verticale, celle de la face plate ajoute mu. L approximation tan a + 2 mu
    # donnait 1,9 pour cent de moins.
    a = math.radians(COIN_ANGLE)
    return CHARGE_DIM * (math.tan(a + math.atan(COIN_MU)) + COIN_MU)


def coin_couple():
    """Couple sur la vis de commande, butee a aiguilles comprise."""
    return coin_effort() * (0.16 * VIS_PAS + 0.58 * 0.15 * VIS_D2) / 1000.0 + 0.5


def portee_plaquette(lo, hi, largeur):
    """
    Longueur portante d'une plaquette contre sa piece conjuguee, au plus
    defavorable des deux bouts de course. C'est la que le rebord entre sous la
    conjuguee : il ne porte pas, et la plaquette a recule d'autant.
    (lo, hi) est la trace de la face portante selon y, `largeur` celle de la
    conjuguee : TRAVERSE_B pour la plaquette haute, POUSSOIR_B pour la basse.
    """
    b2 = largeur / 2.0
    return min(min(hi + dy, b2) - max(lo + dy, -b2) for dy in (0.0, COIN_COURSE))


def rebord_contrainte():
    """
    Cisaillement et flexion au pied d'un rebord, qui encaisse seul le mu.N de
    la traverse sur la plaquette. (cisaillement, flexion, pression sur le chant)
    """
    f = CHARGE_DIM * COIN_MU
    aire = COIN_B * PLAQ_REBORD_L
    w = COIN_B * PLAQ_REBORD_L ** 2 / 6.0
    return (f / aire,
            f * (PLAQ_REBORD_H / 2.0) / w,
            f / (COIN_B * PLAQ_REBORD_H))


def filet_marge():
    """
    Irreversibilite du filetage de commande : (angle d'helice, angle de
    frottement apparent, rapport).

    C'est LA propriete qui tient la charge. La butee a aiguilles ne freine
    rien, et le coin a 12 degres n'est autobloquant que si le frottement de
    ses deux faces depasse coin_mu_autoblocage() (0,106) : avec le bronze
    graphite a chaud on y est a peine, on ne compte donc pas dessus. Si le
    filet cesse d'etre irreversible, les 12 kN emmagasines dans la pile
    devissent la tige tout seuls.

    Le filet est de l'acier sur acier (tige 8.8 dans le C45 du coin) monte a la
    pate cuivre : le cas dangereux est le frottement BAS, d'ou VIS_MU_MIN.
    Le demi-angle de flanc entre par 1/cos : 30 degres pour un filet metrique,
    15 pour un trapezoidal, qui est donc MOINS sur a pas egal.
    """
    psi = math.degrees(math.atan(VIS_PAS / (math.pi * VIS_D2)))
    rho = math.degrees(math.atan(VIS_MU_MIN / math.cos(math.radians(VIS_FLANC))))
    return psi, rho, rho / psi


def coin_mu_autoblocage():
    """
    Frottement des deux faces du coin au dela duquel il est autobloquant :
    l'effort de desserrage CHARGE_DIM.(2 mu - tan a) change de signe.
    """
    return math.tan(math.radians(COIN_ANGLE)) / 2.0


def coin_desserrage(mu=None):
    """
    Effort sur la tige au DESSERRAGE, a la charge de dimensionnement (N). C'est
    lui que retiennent les ecrous interieurs de la chape : 329 N avec COIN_MU.
    """
    m = COIN_MU if mu is None else mu
    return abs(CHARGE_DIM * (2.0 * m - math.tan(math.radians(COIN_ANGLE))))


def pression_filet():
    """
    Pression sur les flancs du filet, taraudage C45 / tige 8.8. L'engagement
    reel va de 59 a 114 mm, mais au dela de 1,5 d l'ecart de pas entre la tige
    et le taraudage fait que les derniers filets ne portent plus : on plafonne,
    c'est la regle des ecrous longs.
    """
    n = min(1.5 * VIS_D, COIN_TARAUD_L) / VIS_PAS
    return coin_effort() / (math.pi * VIS_D2 * VIS_H1 * n)


def coin_tours(force):
    """
    Pour amener la pile a `force` (N) depuis le contact du coin : (ecrasement de
    la pile, course du coin selon y, tours de tige). Sert aux consignes de
    montage : 0,5 kN de precharge = 0,36 mm de pile, 1,7 de coin, 0,84 tour.
    """
    e = pile_ecrasement(force)
    course = e / COIN_TAN
    return e, course, course / VIS_PAS


def coin_par_tour():
    """Descente du coulisseau par tour de vis, et effort correspondant."""
    dz = VIS_PAS * math.tan(math.radians(COIN_ANGLE))
    e0 = pile_ecrasement(4000.0)
    k = (pile_force(e0 + 0.2) - pile_force(e0 - 0.2)) / 0.4
    return dz, dz * k


def ecrasement_butee():
    """
    Ecrasement de la pile quand la tete de guide talonne en bas de lumiere.
    La tete et le bout de lumiere sont deux cercles de rayons voisins, 6,5 et
    7 : le contact y est CONFORME, rayon equivalent R1.R2 / (R2 - R1) = 91 mm,
    et non ponctuel comme l'etait le chant d'une patte prismatique sur un
    demi-cercle.
    """
    return Z_GUIDE - (LUMIERE_Z0 + LUMIERE_B / 2.0)


def boulonnerie():
    """
    Les trois boulonneries M10 du cadre, chacune controlee comme les vis de
    chape : l'ecrou doit tomber entierement sur le filet (marge >= FILET_MARGE_MIN
    pour les vis a filetage partiel) et le bout depasser de l'ecrou d'au moins
    FILET_DEPASSE_MIN, pour que l'element de freinage soit en prise.

    Renvoie une liste de dict : nom, longueur L, serrage (rondelles comprises,
    sous tete ou entre ecrous), hauteur d'ecrou, depassement au dela de
    l'ecrou, marge de filet (None pour une tige entierement filetee).
    Les epaisseurs de tole sont prises a la tole REELLE de chaque piece :
    EP_TOLE_REELLE_42 pour les flancs et les platines, TRAVERSE_LX_REEL (tole
    S355) pour le paquet de traverse.
    """
    out = []
    # vis de cadre : rondelle, flanc, tube, flanc, rondelle
    s = 2.0 * EP_TOLE_REELLE_42 + ENTRETOISE_L + 2.0 * RONDELLE_M10_E
    out.append(dict(nom="vis de cadre TH M10 x %.0f" % ENTR_VIS_L, L=ENTR_VIS_L,
                    serrage=s, ecrou=ECROU_FREIN_H,
                    depassement=ENTR_VIS_L - s - ECROU_FREIN_H,
                    marge_filet=s - (ENTR_VIS_L - ENTR_VIS_FILET)))
    # tige du paquet de traverse : rondelle, six toles, rondelle, un ecrou a chaque bout
    s = TRAVERSE_LX_REEL + 2.0 * RONDELLE_M10_E
    out.append(dict(nom="tige filetee M10 x %.0f de traverse" % TRAVERSE_TIRANT_L,
                    L=TRAVERSE_TIRANT_L, serrage=s, ecrou=ECROU_FREIN_H,
                    depassement=(TRAVERSE_TIRANT_L - s) / 2.0 - ECROU_FREIN_H,
                    marge_filet=None))
    # vis de chape
    s = SUPPORT_EMPILEMENT
    out.append(dict(nom="vis de chape H M10 x %.0f" % SUPPORT_TIRANT_L, L=SUPPORT_TIRANT_L,
                    serrage=s, ecrou=SUPPORT_ECROUS_M10_N * SUPPORT_ECROU_M10_H,
                    depassement=SUPPORT_TIRANT_L - s - SUPPORT_ECROUS_M10_N * SUPPORT_ECROU_M10_H,
                    marge_filet=s - (SUPPORT_TIRANT_L - SUPPORT_TIRANT_FILET)))
    return out


def platine_contrainte():
    """
    Butee de la vis : (contrainte de flexion d'une platine, fleche, compression
    dans CHAQUE entretoise de butee). La platine est une poutre sur deux appuis,
    les entretoises, chargee au milieu par la butee ; les SUPPORT_N platines se
    partagent l'effort. Les deux tubes se partagent l'effort de commande.
    """
    L = 2.0 * SUPPORT_X
    a_ = b_ = SUPPORT_X
    f = coin_effort() / SUPPORT_N
    w = (SUPPORT_B - VIS_PASSAGE_D) * SUPPORT_EP ** 2 / 6.0
    i = (SUPPORT_B - VIS_PASSAGE_D) * SUPPORT_EP ** 3 / 12.0
    sig = f * a_ * b_ / L / w
    fleche = f * a_ ** 2 * b_ ** 2 / (3.0 * E_ACIER * i * L)
    aire_tube = math.pi / 4.0 * (ENTRETOISE_DE ** 2 - ENTRETOISE_DI ** 2)
    sig_tube = coin_effort() / len(TROU_SUPPORT) / aire_tube
    return sig, fleche, sig_tube


def appui_tenon():
    """
    Portee REELLE d'un paquet de tenons sur l'arete haute de la mortaise, par
    flanc : (largeur selon x, profondeur selon y, entraxe des deux appuis).
    Les aretes cassees des plaques (6 x 2 x CHANFREIN), celles de la mortaise
    et le degagement de pied de tenon (TRAVERSE_R_PIED) ne portent pas.
    """
    yb = ECART_FLANCS / 2.0 - TRAVERSE_JEU_Y / 2.0          # epaulement
    yt = Y_FLANC_EXT + TRAVERSE_TAB_DEP                      # bout du tenon
    y0 = max(ECART_FLANCS / 2.0 + CHANFREIN, yb + TRAVERSE_R_PIED)
    y1 = min(Y_FLANC_EXT - CHANFREIN, yt - 2.0)
    lx = TRAVERSE_N * (TRAVERSE_EP - 2.0 * CHANFREIN)
    return lx, y1 - y0, y0 + y1


def matage_tenon():
    """Pression de matage du tenon sur l'arete de mortaise, par flanc (MPa)."""
    lx, ly, _ = appui_tenon()
    return CHARGE_DIM / 2.0 / (lx * ly)


def flexion_tenon():
    """
    Racine du tenon en console : (contrainte, hauteur nette). La hauteur nette
    est celle du tenon moins les deux degagements de pied ; le bras va de
    l'epaulement au milieu de l'appui.
    """
    _, _, entraxe = appui_tenon()
    bras = entraxe / 2.0 - (ECART_FLANCS / 2.0 - TRAVERSE_JEU_Y / 2.0)
    hn = (Z_TAB1 - Z_TAB0) - 2.0 * TRAVERSE_R_PIED
    f = CHARGE_DIM / TRAVERSE_N / 2.0
    return f * bras / (TRAVERSE_EP * hn ** 2 / 6.0), hn


def flexion_traverse():
    """
    Corps d'une plaque de traverse : (contrainte, entraxe des appuis). Section
    pleine de TRAVERSE_H percee du trou de tirant, appuis au milieu des portees
    de tenon, charge de la plaque CONCENTREE au milieu (majorant : le bronze
    l'etale en realite sur une cinquantaine de mm).
    """
    b, h, d = TRAVERSE_EP, TRAVERSE_H, TRAVERSE_TIRANT_D
    zh = TRAVERSE_TIRANT_Z - Z_TRAVERSE_BAS
    aire = b * h - b * d
    zc = (b * h * h / 2.0 - b * d * zh) / aire
    inertie = (b * h ** 3 / 12.0 + b * h * (h / 2.0 - zc) ** 2
               - (b * d ** 3 / 12.0 + b * d * (zh - zc) ** 2))
    w = inertie / max(zc, h - zc)
    _, _, entraxe = appui_tenon()
    m = CHARGE_DIM / TRAVERSE_N * entraxe / 4.0
    return m / w, entraxe


# ============================================================ verifications

def controle_bombe(pb):
    """Bombe du patin de charge : pression de Hertz, et le patin garde de la
    matiere aux bords."""
    if HERTZ_LIM / hertz_charge() < HERTZ_COEF_MIN:
        pb.append("patin de charge : Hertz %.0f MPa, coefficient %.2f"
                  % (hertz_charge(), HERTZ_LIM / hertz_charge()))
    if PATIN_CHARGE_E - PATIN_CHARGE_BOMBE_F < 0.75 * PATIN_CHARGE_E:
        pb.append("bombe du patin de charge trop creuse : %.2f aux bords" % PATIN_CHARGE_BOMBE_F)


def tourillon_course():
    """Tourillon colle dans le coulisseau : (engagement dans le poussoir au
    repos, garde au dessus du patin de charge a la butee mecanique, engagement
    au repos avec toutes les cales entre poussoir et pile)."""
    rep = TOURILLON_L - ALESAGE_P_COUL - PILE_H_LIBRE
    return rep, ALESAGE_P - rep - ecrasement_butee(), rep - sum(CALES_EP)


def verifie():
    pb = []
    # entretoises 20 x 2 : la precharge des M10 ne doit pas les ecraser, a chaud
    s_pre = PRECHARGE_M10 / (math.pi / 4.0 * (ENTRETOISE_DE ** 2 - ENTRETOISE_DI ** 2))
    if s_pre > ENTRETOISE_RE_CHAUD / 1.5:
        pb.append("entretoises a %.0f MPa sous la precharge de %.1f kN : serrer moins"
                  % (s_pre, PRECHARGE_M10 / 1000.0))

    if abs(Z_POUTRE_BAS - (Z_BOSSAGE - RAINURE_P + PATIN_E + PLAT_E)) > 1e-9:
        pb.append("empilement bas incoherent")
    if ECART_FLANCS < RESSORT_DE + 6:
        pb.append("ECART_FLANCS trop faible pour les rondelles")
    # etuve : le cadre y est DEBOUT, sur son about et ses pieds en V ; selon y,
    # ce qui depasse de part et d'autre doit rester dans Y_ETUVE_LIBRE
    if L_FLANC + pied_debout_encombrement()[1] > ETUVE_HAUTEUR - 50.0:
        pb.append("le cadre debout (%.0f avec ses pieds) ne tient pas dans les %.0f de l etuve"
                  % (L_FLANC + pied_debout_encombrement()[1], ETUVE_HAUTEUR))
    if DEGAGEMENT_DOUILLE < 90.0:
        pb.append("moins de 90 mm pour la douille : bout de tige a y %.0f, paroi libre a %.0f"
                  % (Y_BOUT_VIS, Y_ETUVE_LIBRE))
    if Y_BOUT_TIRANT > Y_ETUVE_LIBRE:
        pb.append("les vis de chape sortent de l etuve (y %.0f)" % Y_BOUT_TIRANT)
    if -COIN_Y0 > Y_ETUVE_LIBRE:
        pb.append("le coin recule sort de l etuve (y %.0f)" % COIN_Y0)

    y_int = ECART_FLANCS / 2.0
    if not (Y_FLANC - PLAT_B / 2.0 <= y_int and y_int + EP_FLANC <= Y_FLANC + PLAT_B / 2.0):
        pb.append("le flanc ne porte pas sous le plat")
    if Y_FLANC + PLAT_B / 2.0 > POUTRE_B / 2.0:
        pb.append("le plat deborde de la poutre")

    if PILE_ECRAS_DIM > 0.75 * PILE_COURSE:
        pb.append("pile ecrasee a %.0f %% de sa course a la charge de dimensionnement"
                  % (100 * PILE_ECRAS_DIM / PILE_COURSE))
    # Pile tete-beche : avec un nombre PAIR, les deux bouts presentent le grand
    # diametre aux plateaux plats. En nombre impair, un bout porterait par le
    # bord de l'alesage, sur une arete, et matterait le plateau.
    if RESSORT_N % 2:
        pb.append("pile de %d rondelles : en nombre impair, un bout porte par"
                  " le bord de l'alesage au lieu du grand diametre" % RESSORT_N)
    if RESSORT_F_PLAT < CHARGE_DIM * 1.2:
        pb.append("rondelles trop faibles : %.0f N a plat" % RESSORT_F_PLAT)

    guide_bas = Z_GUIDE - PILE_ECRAS_DIM
    if guide_bas < LUMIERE_Z0 + LUMIERE_B / 2.0:
        pb.append("lumiere trop courte en bas (guide a z %.1f)" % guide_bas)
    if Z_GUIDE > LUMIERE_Z1 - LUMIERE_B / 2.0:
        pb.append("lumiere trop courte en haut (guide a z %.1f)" % Z_GUIDE)
    if LUMIERE_Z0 - Z_NOEUD_BAS < 12:
        pb.append("moins de 12 mm de matiere sous la lumiere")

    controle_bombe(pb)
    # tourillon colle dans le coulisseau : il descend avec lui dans le poussoir
    t_rep, t_but, t_cal = tourillon_course()
    if t_but < TOURILLON_GARDE_MIN:
        pb.append("le tourillon arrive a %.1f mm du patin de charge a la butee (mini %g)"
                  % (t_but, TOURILLON_GARDE_MIN))
    if t_cal < TOURILLON_PRISE_MIN:
        pb.append("le tourillon n entre que de %.1f mm dans le poussoir avec les cales (mini %g)"
                  % (t_cal, TOURILLON_PRISE_MIN))

    eb = ecrasement_butee()
    if eb >= PILE_COURSE:
        pb.append("la butee de lumiere n'empeche pas l'aplatissement de la pile")
    elif pile_force(eb) < CHARGE_DIM * 1.15:
        pb.append("la butee bride l'effort a %.0f N, trop pres de la charge" % pile_force(eb))

    # commande par coin : course, effort, geometrie
    z_haut = LUMIERE_Z1 - LUMIERE_B / 2.0
    # position du dessus de la PLAQUETTE du coulisseau selon l'epaisseur du coin
    top_mince = Z_COIN_HAUT - COIN_T_MIN
    top_epais = Z_COIN_HAUT - COIN_T_MAX
    if abs(top_mince - Z_PLAQ_COUL) > 2.5:
        pb.append("coin trop mince ou trop epais : dessus de plaquette a %.1f au lieu de %.1f"
                  % (top_mince, Z_PLAQ_COUL))
    # au dela des 12 kN, il faut encore TOL_EMPILEMENT de course en hauteur pour
    # rattraper un empilement vertical court (sinon : cales CALES_EP)
    if Z_PLAQ_COUL - top_epais < PILE_ECRAS_DIM + TOL_EMPILEMENT:
        pb.append("course du coin insuffisante : %.1f mm pour %.1f mm d'ecrasement"
                  " et %.1f de rattrapage d'empilement"
                  % (Z_PLAQ_COUL - top_epais, PILE_ECRAS_DIM, TOL_EMPILEMENT))
    # Le taraudage M16 est dans le coin : il ne doit crever ni la face de
    # glissement du dessus, ni le dessous au bout mince.
    if COIN_VIS_SOUS - VIS_D / 2.0 < 5.0:
        pb.append("moins de 5 mm d'acier au dessus du taraudage (%.1f)"
                  % (COIN_VIS_SOUS - VIS_D / 2.0))
    if COIN_T_BOUT_MINCE - COIN_VIS_SOUS - VIS_PASSAGE_D / 2.0 < 3.0:
        pb.append("moins de 3 mm de matiere sous le percage de passage au bout mince (%.1f)"
                  % (COIN_T_BOUT_MINCE - COIN_VIS_SOUS - VIS_PASSAGE_D / 2.0))
    if VIS_PASSAGE_D / 2.0 + 6.0 > COIN_B / 2.0:
        pb.append("le percage de la tige ne laisse pas 6 mm de flanc au coin")
    # Le filet doit rester engage AUX DEUX BOUTS de la course. Le coin recule
    # emmene sa partie filetee loin de la tige, c'est la position critique.
    eng = (COIN_Y0 + COIN_TARAUD_L) - VIS_Y0
    if eng < 1.5 * VIS_D:
        pb.append("filet engage sur %.1f mm seulement, coin recule : il en faut %.1f"
                  % (eng, 1.5 * VIS_D))
    if COIN_TARAUD_L > 6.0 * VIS_D:
        pb.append("taraudage de %.0f d : trop profond pour un taraud machine"
                  % (COIN_TARAUD_L / VIS_D))
    # LONGUEUR DU COIN. Elle vaut portee + course, et les deux moities sont
    # tenues. La course doit mener le coulisseau jusqu'a sa butee de lumiere,
    # pas seulement jusqu'aux 12 kN : sinon la butee mecanique devient
    # inatteignable et ne protege plus rien. Tout ce qui depasse allonge pour
    # rien le coin, la tige et la chape (les plaques de bronze, elles, sont
    # du commerce et de longueur fixe).
    course_butee = ecrasement_butee() / COIN_TAN
    if COIN_COURSE < course_butee:
        pb.append("course du coin %.1f mm : la butee de lumiere en demande %.1f,"
                  " elle est donc inatteignable" % (COIN_COURSE, course_butee))
    if COIN_COURSE > course_butee + 3.0:
        pb.append("course du coin %.1f mm pour %.1f utiles : %.0f mm de coin et de"
                  " chape sans emploi" % (COIN_COURSE, course_butee, COIN_COURSE - course_butee))
    # rebords et plaquettes, memes cotes sur les deux faces du coin
    if abs(PLAQ_HAUT_L - PLAQ_L) > 0.01 or abs(PLAQ_BAS_L - PLAQ_L) > 0.01:
        pb.append("les plaquettes du commerce font %g : il en reste %.1f et %.1f entre les rebords"
                  % (PLAQ_L, PLAQ_HAUT_L, PLAQ_BAS_L))
    if min(PLAQ_REBORD_L, PLAQ_REBORD_L_BAS) < 4.0:
        pb.append("rebord de %.1f mm : trop etroit a fraiser" % min(PLAQ_REBORD_L, PLAQ_REBORD_L_BAS))
    if PLAQ_B > COIN_B - 1.0:
        pb.append("plaquette plus large que le coin")
    # pression des plaques : largeur nette selon x FOIS longueur portante selon
    # y (et non deux largeurs selon x multipliees entre elles)
    p_plaq = max(pressions_plaquettes())
    if p_plaq > PLAQ_P_ADM:
        pb.append("plaquette a %.1f MPa, au dessus des %g admis par le fabricant"
                  % (p_plaq, PLAQ_P_ADM))
    if PLAQ_EP - PLAQ_REBORD_H < 1.5:
        pb.append("rebord a %.1f mm sous la surface du bronze : aux bouts de course"
                  " il frotterait la piece conjuguee, acier sur acier"
                  % (PLAQ_EP - PLAQ_REBORD_H))
    cis, flex, pres = rebord_contrainte()
    if flex > RE_S355_CHAUD / 2.0 or cis > RE_S355_CHAUD / 3.0:
        pb.append("rebord trop faible : %.0f MPa de flexion, %.0f de cisaillement"
                  % (flex, cis))
    if pres > 40.0:
        pb.append("chant de la plaquette matte a %.0f MPa contre le rebord" % pres)
    if PLAQ_REBORD_R > PLAQ_REBORD_H / 2.0:
        pb.append("degagement de pied plus haut que la moitie du rebord")
    if PLAQ_EP < 4.0:
        pb.append("plaquette de bronze trop mince pour etre rectifiee et usee")
    # fixation des plaquettes : la dilatation differentielle bronze/acier doit
    # passer dans le joint sans le cisailler, et le joint ne doit pas etre
    # une epoxy rigide -- voir COLLE_G
    d_th = (ALPHA_BRONZE - ALPHA_ACIER) * DELTA_T * PLAQ_BAS_L / 2.0
    tau_th = COLLE_G * d_th / COLLE_EP
    if tau_th > COLLE_TAU_ADM / 2.0:
        pb.append("joint des plaquettes cisaille a %.2f MPa par la dilatation seule"
                  " : trop rigide, ou trop mince" % tau_th)
    if COLLE_G > 50.0:
        pb.append("COLLE_G = %.0f MPa : c est une epoxy, elle fissurera en bout"
                  " de plaquette au premier chauffage" % COLLE_G)
    for nom, lo, hi, larg, pression in (
            ("haute", PLAQ_HAUT_Y0, PLAQ_HAUT_Y1, TRAVERSE_B, pressions_plaquettes()[0]),
            ("basse", PLAQ_BAS_Y0, PLAQ_BAS_Y1, POUSSOIR_B, pressions_plaquettes()[1])):
        pp = portee_plaquette(lo, hi, larg)
        if pression > 12.0:
            pb.append("plaquette %s a %.1f MPa sur %.1f mm portants" % (nom, pression, pp))
        if pp < larg - 2.0 * (PLAQ_REBORD_L + PLAQ_JEU) - 0.1:
            pb.append("la plaquette %s sort de sa conjuguee avant la fin de course" % nom)
    # la plaquette basse descend sous le coin : la fente du flanc doit la passer
    bas = Z_COIN_HAUT - COIN_T_BOUT_EPAIS - PLAQ_DROP
    if FENTE_COIN_Z0 > bas - 1.0:
        pb.append("la fente du flanc ne passe pas la plaquette basse (%.1f contre %.1f)"
                  % (FENTE_COIN_Z0, bas))
    # pied a mi-bois
    if PIED_CROIX_FLANC > W_MEMB_BASSE - 2.0 * EP_FLANC:
        pb.append("encoche de pied trop profonde : il reste moins de deux epaisseurs de membrure basse")
    if PIED_SOL - PIED_BOSSAGE_H < 15.0:
        pb.append("pied trop bas sous l encoche")
    if abs(PIED_H - PIED_SOL - PIED_CROIX - PIED_CROIX_FLANC) > 1e-6:
        pb.append("le pied doit depasser le fond d encoche du flanc d une profondeur d encoche, sinon rien ne porte")
    if AJOUR_BASSE and PIED_X_POS - ENCOCHE_FLANC_B / 2.0 - 10.0 < AJOUR_BASSE_MARGE + AJOUR_BASSE_R + 10.0:
        pb.append("encoche de pied couche trop pres d un ajour de membrure basse")
    if PIED_X_POS + ENCOCHE_FLANC_B / 2.0 + 10.0 > X_APPUI - 20.0:
        pb.append("encoche de pied couche trop pres de l appui")
    if PIED_BOSSAGE_Y + PIED_BOSSAGE_B / 2.0 > PIED_Y / 2.0 + 1e-6:
        pb.append("bossage de pied hors de la plaque")
    # epaisseur reelle de tole : les nodes doivent encore serrer, les fentes
    # rester des fentes
    if not 0.0 < PIED_NODE_SERRE < PIED_JEU:
        pb.append("nodes de pied : serrage %.2f hors de ]0, PIED_JEU[" % PIED_NODE_SERRE)
    for nom_ep, ep_r in (("EP_TOLE_REELLE_42", EP_TOLE_REELLE_42),
                         ("EP_TOLE_REELLE_S355", EP_TOLE_REELLE_S355)):
        if abs(ep_r - EP_FLANC) > 1.5:
            pb.append("%s = %.2f pour une tole nominale de %g : ce n est pas la"
                      " meme tole, revoir EP_FLANC" % (nom_ep, ep_r, EP_FLANC))
    if PIED_AJOUR:
        wc = Y_FLANC - ENCOCHE_PIED_B / 2.0 - PIED_AJOUR_POST
        y_ext0 = Y_FLANC + ENCOCHE_PIED_B / 2.0 + PIED_AJOUR_POST
        y_ext1 = PIED_Y / 2.0 - PIED_BOSSAGE_B - PIED_AJOUR_POST
        if wc < PIED_AJOUR_R + 2.0 or y_ext1 - y_ext0 < 2.0 * PIED_AJOUR_R + 4.0:
            pb.append("ajours de pied trop etroits")
        if PIED_H - PIED_AJOUR_CHORD - (PIED_BOSSAGE_H + PIED_AJOUR_CHORD) < 2.0 * PIED_AJOUR_R + 4.0:
            pb.append("ajours de pied trop bas")
    # crochets d etuve
    if CROCHET_LANGUE_H > ETUVE_TROU - 2.0 or CROCHET_E > ETUVE_TROU - 1.5:
        pb.append("la langue du crochet (%g x %g) ne passe pas un carre de %g" % (CROCHET_E, CROCHET_LANGUE_H, ETUVE_TROU))
    if CROCHET_LANGUE_H + CROCHET_BEC > ETUVE_TROU - 1.0:
        pb.append("tete de langue du crochet (%g + %g de bec) plus haute que le carre de %g :"
                  " elle ne passe pas de face" % (CROCHET_LANGUE_H, CROCHET_BEC, ETUVE_TROU))
    if min(ETUVE_TROU_PAS) - CROCHET_LANGUE_H < ETUVE_TROU + 4.0:
        pb.append("deux langues du crochet tombent dans le meme trou")
    if CROCHET_LANGUE_L - CROCHET_BEC_L - ETUVE_PAROI_E < 1.5:
        pb.append("le bec du crochet est dans la paroi")
    if CROCHET_LANGUE_L - CROCHET_BEC_L < 0.5 * CROCHET_E:
        pb.append("encoche de bec du crochet de %.1f : moins de la demi-epaisseur,"
                  " le laser ne la degage pas" % (CROCHET_LANGUE_L - CROCHET_BEC_L))
    if PIED_Y / 2.0 + 2.0 > ETUVE_Y / 2.0:
        pb.append("pied de %g plus large que la chambre de %g" % (PIED_Y, ETUVE_Y))
    # de part et d autre de la dent, il faut la place des conges R3 des angles
    # de l appui (parts.crochet_profile) : sinon le profil ne se construit plus
    if not CROCHET_CORPS + CROCHET_DENT_B / 2.0 + 3.0 <= CROCHET_DENT_Y <= CROCHET_S - CROCHET_DENT_B / 2.0 - 3.0:
        pb.append("la dent du crochet (a %.1f de la paroi) sort de l appui" % CROCHET_DENT_Y)
    enc_z, enc_x = pied_debout_encombrement()
    if H_FLANC / 2.0 + enc_z > ETUVE_INTERIEUR / 2.0 - CROCHET_CORPS - 2.0:
        pb.append("le pied en V touche le corps du crochet ou la paroi")
    if abs(2.0 * PIED_FENTE_Y - PIED_FENTE_ENTRAXE) > 1e-6:
        pb.append("fentes du pied a %.1f d entraxe au lieu de %g" % (2.0 * PIED_FENTE_Y, PIED_FENTE_ENTRAXE))
    if PIED_FENTE_Y + PIED_E / 2.0 + 2.0 > ETUVE_Y / 2.0:
        pb.append("les crochets, a y = +/- %.1f, sortent de l etuve" % PIED_FENTE_Y)
    if CROCHET_DENT_B / math.cos(math.radians(PIED_DEBOUT_ANGLE)) > PIED_E + 2.0 * PIED_FENTE_H * math.tan(math.radians(PIED_DEBOUT_ANGLE)) - 1.0:
        pb.append("la dent est trop large pour la fente du pied incline")
    if PIED_FENTE_BORD + PIED_FENTE_B + 5.0 > PIED_BOSSAGE_B:
        pb.append("la fente de calage sort du bossage du pied")
    # la paroi de 1 : bord du trou de la langue haute, poids et couple de l appui
    f_pied = MASSE_TOTALE_ESTIMEE / 4.0 * 9.81
    bras = CROCHET_DENT_Y
    f_bec = f_pied * bras / (CROCHET_H - CROCHET_LANGUE_H / 2.0)   # langue haute tiree, bas du corps contre la paroi
    if (f_pied / CROCHET_N_LANGUES + f_bec) / (CROCHET_E * ETUVE_PAROI_E) > 120.0:
        pb.append("bord du trou de paroi a %.0f MPa sous la langue haute" % ((f_pied / CROCHET_N_LANGUES + f_bec) / (CROCHET_E * ETUVE_PAROI_E)))
    if f_pied * bras / (CROCHET_E * CROCHET_BANDE ** 2 / 6.0) > 0.3 * RE_TOLE_COURANTE:   # crochet en S355
        pb.append("appui de crochet trop charge")
    # pieds debout : aux quatre coins, inclines
    ang = math.radians(PIED_DEBOUT_ANGLE)
    w2 = ENCOCHE_FLANC_B / 2.0               # encoche de coin du flanc
    bouche = w2 * max(math.tan(ang), 1.0 / math.tan(ang))     # ou la joue la plus longue sort du chant
    if PIED_DEBOUT_PROF - bouche < (PIED_CROIX + PIED_NODE_L) / 2.0 + 2.0:
        pb.append("encoche de coin trop courte : les nodes du pied ne portent pas sur le flanc")
    if not 25.0 <= PIED_DEBOUT_ANGLE <= 65.0:
        pb.append("pied debout a %.0f degres : trop couche ou trop droit" % PIED_DEBOUT_ANGLE)
    ca, cb, bout, garde = pied_debout_coins()
    if ca[0] > -X_FENETRE - 10.0 or bout[0] > -X_FENETRE - 6.0:
        pb.append("l encoche de coin ou le pied debout sort du montant d extremite")
    trou = (-TROU_COIN[0], TROU_COIN_HAUT_Z)
    for nom, pt in (("angle haut", ca), ("angle d about", cb)):
        lig = math.hypot(pt[0] - trou[0], pt[1] - trou[1]) - D_VIS / 2.0
        if lig < 10.0:
            pb.append("encoche de coin : %.1f de ligament entre l %s et le trou d entretoise" % (lig, nom))
    garde_ecrou = garde + ENTRETOISE_DE / 2.0 - 10.5      # rondelle M10 : rayon 10,5
    if garde_ecrou < 8.0:
        pb.append("le pied debout passe a %.1f mm de l ecrou du coin (rondelle rayon 10,5)" % garde_ecrou)
    base = pied_debout_base()
    if base > ETUVE_INTERIEUR - 8.0:
        pb.append("base des pieds debout de %.0f : ne passe pas dans l etuve de %.0f" % (base, ETUVE_INTERIEUR))
    if base < H_FLANC + 4.0:
        pb.append("les aretes de pose des pieds debout ne depassent pas le cadre (%.0f)" % base)
    psi, rho, marge = filet_marge()
    if marge < 1.8:
        pb.append("filetage de commande reversible ou limite : helice %.2f deg"
                  " contre %.2f deg de frottement, marge x%.2f. Rien d'autre ne"
                  " tient les 12 kN de la pile." % (psi, rho, marge))
    if pression_filet() > FILET_P_ADM:
        pb.append("flancs du filet a %.1f MPa, au dela des %g MPa admis pour un"
                  " taraudage C45 / tige 8.8 en manoeuvre lente" % (pression_filet(), FILET_P_ADM))
    if abs(VIS_H1 - (0.541266 if VIS_FLANC > 22.0 else 0.5) * VIS_PAS) > 1e-6:
        pb.append("VIS_H1 ne correspond pas au profil declare")
    if FENTE_COIN_B / 2.0 + 8 > GUIDE_X - LUMIERE_B / 2.0:
        pb.append("la fente du coin et les lumieres se touchent")
    if GUIDE_X + LUMIERE_B / 2.0 + 8 > X_NOEUD:
        pb.append("les lumieres sortent du noeud")
    if Z_VIS - VIS_PASSAGE_D / 2.0 < FENTE_COIN_Z0 or Z_VIS + VIS_PASSAGE_D / 2.0 > FENTE_COIN_Z1:
        pb.append("l'axe de vis ne passe pas dans la fente du coin")
    if Z_TRAVERSE_BAS < Z_COULISSEAU_BAS + COULISSEAU_H:
        pb.append("le coulisseau touche la traverse en position haute")

    # SENS DE MONTAGE : le bout epais doit etre du cote oppose a la chape. La
    # face inclinee repousse alors le coin vers son bout epais, le filet tire la
    # tige vers l'interieur du cadre, et sa tete appuie sur la face exterieure
    # des platines, la ou se trouve la butee a aiguilles. Monte a l'envers, la
    # tige sortirait du cadre et ce sont les ecrous interieurs qui porteraient.
    if COIN_T_BOUT_EPAIS <= COIN_T_BOUT_MINCE:
        pb.append("le coin est a l'envers : bout epais du cote de la chape")
    if COIN_Y_MAX <= COIN_Y1:
        pb.append("le coin s'eloigne de la chape en chargeant : arret axial impossible")

    # le coin doit couvrir TOUTE la tete du coulisseau, du debut a la fin
    if COIN_Y0 > -POUSSOIR_B / 2.0 - COIN_COURSE + 1e-6:
        pb.append("le coin ne couvre pas le coulisseau au repos")
    manque = POUSSOIR_B / 2.0 - COIN_Y1
    if manque > 1e-6:
        pb.append("le coin quitte le coulisseau de %.1f mm au repos" % manque)
    if abs(COULISSEAU_H - (COULISSEAU_E + POUSSOIR_B / 2.0 * COIN_TAN)) > 1e-6:
        pb.append("le plan incline du coulisseau n'occupe pas toute sa section")
    # hauteur du coulisseau : ce sont les taraudages de guide et l'alesage qui
    # la fixent, pas la contrainte. Les deux cotes se mesurent du cote MINCE de
    # la pente.
    mince = COULISSEAU_E - POUSSOIR_B / 2.0 * COIN_TAN
    if mince < GUIDE_Z + GUIDE_VIS_D / 2.0 + 5.0:
        pb.append("pas 5 mm de matiere au dessus du taraudage de guide, bord mince"
                  " (%.1f)" % (mince - GUIDE_Z - GUIDE_VIS_D / 2.0))
    if GUIDE_Z - GUIDE_VIS_D / 2.0 < 5.0:
        pb.append("pas 5 mm de matiere sous le taraudage de guide")
    if GUIDE_PERCAGE_P + 4.0 > POUSSOIR_B / 2.0:
        pb.append("les deux avant-trous de guide se rejoignent dans le coulisseau")
    if not GUIDE_VIS_D - 1.5 <= GUIDE_TARAUD_D < GUIDE_VIS_D - 1.0:
        pb.append("avant-trou de %.1f : ce n'est pas celui d'un M%g" % (GUIDE_TARAUD_D, GUIDE_VIS_D))
    if abs(GUIDE_TETE_H - EP_FLANC) > 0.5:
        pb.append("la tete de guide ne fait pas l'epaisseur du flanc")
    if COULISSEAU_L / 2.0 - GUIDE_X - GUIDE_VIS_D / 2.0 < 6.0:
        pb.append("pas 6 mm de matiere au bout du coulisseau apres le taraudage")
    chapeau = COULISSEAU_E - ALESAGE_D / 2.0 * COIN_TAN - ALESAGE_P_COUL
    if chapeau < COULISSEAU_CHAPEAU:
        pb.append("chapeau de %.1f mm seulement au dessus de l'alesage du tourillon"
                  % chapeau)
    # et rester sous la traverse, qui est son plan de glissement
    rec = min(COIN_Y1, TRAVERSE_B / 2.0) - max(COIN_Y0 + COIN_COURSE, -TRAVERSE_B / 2.0)
    if rec < 0.9 * TRAVERSE_B:
        pb.append("appui du coin sous la traverse reduit a %.0f mm" % rec)

    # butee de la vis : platines de tole sur deux entretoises
    garde = COIN_Y_SUPPORT - COIN_Y_MAX - SUPPORT_ECROU_H - SUPPORT_RONDELLE
    if garde < 4.0:
        pb.append("les ecrous de retenue touchent le bout du coin en fin de course"
                  " (%.1f mm)" % garde)
    # les deux entretoises posent a plat sur le flanc, de part et d'autre de la
    # fente, dans le plan de l'axe de vis ; leurs jumelles entre les flancs
    # passent au dessus du coulisseau et sous la traverse
    re = ENTRETOISE_DE / 2.0
    if SUPPORT_X - re < FENTE_COIN_B / 2.0 + SUPPORT_GARDE_FENTE:
        pb.append("les entretoises de chape mordent la fente du coin")
    coul_haut = Z_COULISSEAU_HAUT + POUSSOIR_B / 2.0 * COIN_TAN
    if Z_VIS - re < coul_haut + 4.0:
        pb.append("les entretoises de chape touchent le coulisseau (%.1f mm)"
                  % (Z_VIS - re - coul_haut))
    if Z_VIS + re > Z_TRAVERSE_BAS - 4.0:
        pb.append("les entretoises de chape touchent la traverse")
    # boulonnerie M10 (cadre, traverse, chape) : l'ecrou entierement sur le
    # filet avec FILET_MARGE_MIN de marge pour les tolerances d'empilement, et
    # au moins deux filets qui depassent de l'ecrou (freinage en prise)
    for b in boulonnerie():
        if b["marge_filet"] is not None and b["marge_filet"] < FILET_MARGE_MIN:
            pb.append("%s : l'ecrou n'a que %.1f mm de marge sur le filet (il en faut %g ;"
                      " ajouter une rondelle ou changer de longueur)"
                      % (b["nom"], b["marge_filet"], FILET_MARGE_MIN))
        if b["depassement"] < FILET_DEPASSE_MIN:
            pb.append("%s trop courte : %.1f mm au dela de l'ecrou, il en faut %g"
                      % (b["nom"], b["depassement"], FILET_DEPASSE_MIN))
    if ENTR_SOMMET:
        if Z_ENTR_SOMMET - re < Z_TRAVERSE_HAUT + 4.0:
            pb.append("l'entretoise de sommet touche la coiffe de traverse")
        if Z_ENTR_SOMMET - D_VIS / 2.0 < Z_TAB1 + TRAVERSE_JEU / 2.0 + 2.0 * EP_FLANC:
            pb.append("pas 2 epaisseurs entre le trou de sommet et la mortaise")
        if H_FLANC - Z_ENTR_SOMMET - D_VIS / 2.0 < 2.0 * EP_FLANC:
            pb.append("pas 2 epaisseurs entre le trou de sommet et le chant haut")
    if Z_VIS - re < LUMIERE_Z1 + 4.0 and SUPPORT_X - re < GUIDE_X + LUMIERE_B / 2.0 + 4.0:
        pb.append("les entretoises de chape mordent les lumieres")
    # guidage du coulisseau : pas d'arc-boutement, pas d'hyperstatisme aveugle
    if (LUMIERE_B - GUIDE_TETE_D) / 2.0 < 0.3:
        pb.append("jeu de tete de guide trop faible dans la lumiere")
    # la tete depasse du coulisseau de sa propre hauteur : elle doit traverser
    # le flanc sans toucher la face exterieure
    if GUIDE_TETE_H > EP_FLANC + 1.0:
        pb.append("la tete de guide deborde de la face exterieure du flanc")
    # GUIDE_VIS_L est la longueur SOUS TETE (ISO 4762) : c'est elle qui entre
    # dans le taraudage quand la tete porte sur la face du coulisseau
    if GUIDE_VIS_L > GUIDE_TARAUD_P - 1.0:
        pb.append("la vis de guide (%g sous tete) talonne au fond de son taraudage de %g :"
                  " la tete resterait decollee" % (GUIDE_VIS_L, GUIDE_TARAUD_P))
    if GUIDE_VIS_L < 1.25 * GUIDE_VIS_D:
        pb.append("vis de guide trop courte : %g de filet en prise" % GUIDE_VIS_L)

    # traverse a tenons
    if abs(TRAVERSE_JEU_X - 2.0 * TRAVERSE_R_MORT) > 1e-6:
        pb.append("l'arete portante de la mortaise n'a pas la largeur des tenons")
    if Z_TAB0 - FENTE_COIN_Z1 < 10.0:
        pb.append("mortaise de traverse a %.1f mm de la fente du coin"
                  % (Z_TAB0 - FENTE_COIN_Z1))
    if Z_MEMB_HAUTE - Z_TAB1 < 20.0:
        pb.append("moins de 20 mm entre la mortaise et la membrure haute")
    if (TRAVERSE_LX_REEL + TRAVERSE_JEU_X) / 2.0 + 10.0 > X_NOEUD:
        pb.append("la mortaise de traverse sort du noeud")
    # Le bronze du dessus doit rester ENTIER sur la traverse, chanfrein de la
    # tole exterieure deduit, quand la traverse (jeu de mortaise) et le coin (jeu
    # de fente) sont decales a l'oppose l'un de l'autre. On compare des
    # DEMI-largeurs : comparer la largeur totale au decalage d'un seul cote
    # affichait 4 mm de marge la ou il y en a 0,2.
    jx = TRAVERSE_JEU_X / 2.0 + COIN_JEU_FENTE / 2.0
    marge_x = TRAVERSE_LX / 2.0 - CHANFREIN - jx - PLAQ_B / 2.0
    if marge_x < 0.0:
        pb.append("la plaque de bronze peut deborder de la traverse de %.1f mm" % -marge_x)
    if portee_coin() < 0.75 * PLAQ_B:
        pb.append("les aretes cassees mangent %.0f pour cent de la portee du bronze"
                  % (100.0 * (1.0 - portee_coin() / PLAQ_B)))
    if pression_coin() > 15.0:
        pb.append("pression du bronze sur la traverse : %.1f MPa" % pression_coin())
    # selon y : le tube fixe l'ecart, les epaulements ne doivent jamais pincer
    if TRAVERSE_JEU_Y < 0.2:
        pb.append("epaulements de traverse a %.2f des flancs : le paquet serait pince"
                  % (TRAVERSE_JEU_Y / 2.0))
    if abs(ENTRETOISE_L - ECART_FLANCS) > 1e-9:
        pb.append("les entretoises de %.1f ne font pas l'ecart des flancs" % ENTRETOISE_L)
    # tenons et plaques : portee reelle, aretes cassees et degagements deduits.
    # Plaques en S355 (tole courante), le plus mou des deux au matage.
    if matage_tenon() > 0.5 * RE_TOLE_COURANTE:
        pb.append("matage du tenon sur l'arete de mortaise : %.0f MPa" % matage_tenon())
    if flexion_tenon()[0] > 0.4 * RE_TOLE_COURANTE:
        pb.append("racine de tenon a %.0f MPa en flexion" % flexion_tenon()[0])
    if flexion_traverse()[0] > 0.4 * RE_TOLE_COURANTE:
        pb.append("plaques de traverse a %.0f MPa en flexion" % flexion_traverse()[0])
    if TRAVERSE_SUREP < 0.3 or TRAVERSE_SUREP > 2.0:
        pb.append("surepaisseur de fraisage de la traverse de %.1f : hors 0,3 - 2" % TRAVERSE_SUREP)

    # poussoir : l alesage TRAVERSE les plateaux, c est le patin de charge colle
    # sur la poutre qui fait fond. Un plateau plein de plus n apportait rien.
    if abs(ALESAGE_P - POUSSOIR_H) > 1e-6:
        pb.append("l'alesage du poussoir (%.0f) doit traverser ses %d plateaux (%.0f)"
                  % (ALESAGE_P, POUSSOIR_N, POUSSOIR_H))
    if POUSSOIR_GOUPILLE_X + POUSSOIR_GOUPILLE_D / 2.0 + 8.0 > PATIN_CHARGE_L / 2.0:
        pb.append("les goupilles du poussoir sortent du patin de charge")
    # goupilles 8 m6 (8,006 a 8,015) : libres dans les trous laser des plateaux,
    # serrees dans le 8 H7 perce-alese du patin, pris dans un avant-trou laser
    if POUSSOIR_GOUPILLE_PASSAGE < POUSSOIR_GOUPILLE_D + 0.2:
        pb.append("trous de goupille des plateaux de %.1f : trop justes pour un trou laser"
                  % POUSSOIR_GOUPILLE_PASSAGE)
    if PATIN_CHARGE_AVANT_TROU > POUSSOIR_GOUPILLE_D - 1.5:
        pb.append("avant-trou de %.1f : pas assez de matiere pour percer et aleser a %g H7"
                  % (PATIN_CHARGE_AVANT_TROU, POUSSOIR_GOUPILLE_D))
    if PATIN_CHARGE_AVANT_TROU < 0.5 * PATIN_CHARGE_E:
        pb.append("avant-trou de %.1f dans %g : trop petit pour le laser"
                  % (PATIN_CHARGE_AVANT_TROU, PATIN_CHARGE_E))

    # appui : rainure du patin et contact de Hertz
    j_rain = (RAINURE_B - EP_TOLE_REELLE_42) / 2.0
    if not 0.5 <= j_rain <= 1.0:
        pb.append("jeu de rainure du patin de %.2f par cote, hors 0,5 - 1,0" % j_rain)
    if (PATIN_B - RAINURE_B) / 2.0 < 4.0:
        pb.append("moins de 4 mm de joue de part et d'autre de la rainure du patin")
    if hertz_coef() < HERTZ_COEF_MIN:
        pb.append("contact d'appui a %.0f MPa de Hertz pour %.0f admis (patin S355 a chaud) :"
                  " coefficient %.2f" % (hertz_appui(), HERTZ_LIM, hertz_coef()))

    # flexion de l'empilage de platines (42CrMo4), appui simple sur les deux
    # entretoises, et compression de CHAQUE entretoise de butee
    sig_pl, _fl, sig_tube = platine_contrainte()
    if sig_pl > RE_TOLE_CHAUD / 2.5:
        pb.append("platines de butee a %.0f MPa en flexion, coefficient %.1f a chaud"
                  % (sig_pl, RE_TOLE_CHAUD / sig_pl))
    if sig_tube > 0.3 * 235.0:
        pb.append("entretoises de butee a %.0f MPa en compression" % sig_tube)
    if SUPPORT_B < SUPPORT_BUTEE_D + 12.0:
        pb.append("platine trop etroite pour le siege de la butee a aiguilles")
    if SUPPORT_BUTEE_D < VIS_D + 8.0:
        pb.append("butee a aiguilles trop petite pour un M%.0f" % VIS_D)
    if SUPPORT_B_BOUT / 2.0 < D_VIS / 2.0 + 8.0:
        pb.append("pas assez de matiere autour des trous de vis de la platine")

    # tige filetee : longueur, prise dans le coin, degagement de la douille
    besoin = (SUPPORT_Y1 + SUPPORT_BUTEE_H + VIS_TETE_H) - VIS_Y0
    if VIS_L < besoin:
        pb.append("tige filetee trop courte : %.0f mm pour %.0f" % (VIS_L, besoin))
    # prise du filetage : la plus faible des deux positions extremes
    prise = min(min(VIS_Y0 + VIS_L, COIN_Y1) - max(VIS_Y0, COIN_Y0),
                min(VIS_Y0 + VIS_L, COIN_Y_MAX) - max(VIS_Y0, COIN_Y0 + COIN_COURSE))
    if prise < 3.0 * VIS_D:
        pb.append("prise du filetage dans le coin reduite a %.0f mm" % prise)
    # (le degagement de la douille, Y_ETUVE_LIBRE, est controle en tete)

    # couple de commande, butee a aiguilles comprise
    if coin_couple() > 25.0:
        pb.append("couple de commande %.1f N.m, trop pour une cle a main" % coin_couple())

    # bruts des pieces usinees : jamais plus petits que la piece finie
    import parts
    for nom, fini, brut in parts.bruts_usinage():
        for f_, b_ in zip(sorted(fini), sorted(brut)):
            if b_ < f_ + 2.0 * BRUT_SUREP - 1e-6:
                pb.append("brut du %s (%s) trop petit pour la piece finie (%s)"
                          % (nom, " x ".join("%g" % v for v in brut),
                             " x ".join("%.1f" % v for v in fini)))
                break

    return pb


if __name__ == "__main__":
    import parts
    print("Empilement :")
    for nom, v in [("membrure basse", Z_MEMB_BASSE), ("contact d'appui", Z_BOSSAGE),
                   ("dessous du patin", Z_PATIN_BAS), ("plat", Z_PLAT_BAS),
                   ("poutre bas", Z_POUTRE_BAS), ("poutre haut", Z_POUTRE_HAUT),
                   ("patin de charge", Z_PATIN_CHARGE_HAUT),
                   ("poussoir haut", Z_POUSSOIR_HAUT),
                   ("coulisseau bas a vide", Z_COULISSEAU_BAS),
                   ("coulisseau bas a 12 kN", Z_COULISSEAU_BAS - PILE_ECRAS_DIM),
                   ("coulisseau haut a vide", Z_COULISSEAU_HAUT),
                   ("traverse", Z_TRAVERSE_BAS), ("membrure haute", Z_MEMB_HAUTE),
                   ("hors tout", H_FLANC)]:
        print("   %-26s z = %7.1f" % (nom, v))

    print("\nRessorts :")
    print("   %d rondelles A50 en serie, hauteur libre %.1f mm" % (RESSORT_N, PILE_H_LIBRE))
    print("   effort a plat             %8.0f N" % RESSORT_F_PLAT)
    print("   course totale             %8.1f mm" % PILE_COURSE)
    print("   ecrasement a %.0f N       %8.2f mm" % (CHARGE_DIM, PILE_ECRAS_DIM))
    print("   raideur secante           %8.0f N/mm" % PILE_K_SECANT)
    print("   butee de lumiere a        %8.2f mm, soit %.0f N"
          % (ecrasement_butee(), pile_force(ecrasement_butee())))
    print("   graduation : " + "  ".join(
        "%dkN:%.1f" % (kn, pile_ecrasement(kn * 1000.0)) for kn in (2, 4, 6, 8, 10, 12)))

    print("\nAppuis :")
    print("   axe neutre a %.2f mm au dessus de la face inferieure" % axe_neutre())
    print("   bras contact - axe neutre %.2f mm" % bras_contact_axe_neutre())
    print("   pression de Hertz         %.0f MPa sur %.1f portants (limite %.0f MPa, patin S355"
          " a chaud : coefficient %.2f)"
          % (hertz_appui(), hertz_largeur(), HERTZ_LIM, hertz_coef()))
    print("   largeur du bossage        %.1f mm sous un patin de %.0f"
          % (largeur_bossage(), PATIN_L))
    print("   rainure du patin          %.1f x %.1f, jeu %.2f par cote"
          % (RAINURE_B, RAINURE_P, (RAINURE_B - EP_TOLE_REELLE_42) / 2.0))

    print("\nCommande :")
    print("   bronze sur traverse       %.1f mm nets, %.1f MPa ; sur coulisseau %.1f MPa"
          % ((portee_coin(),) + pressions_plaquettes()))
    psi, rho, marge = filet_marge()
    print("   filet M16 irreversible    helice %.2f deg, frottement %.2f deg a mu %.2f :"
          " marge x%.2f" % (psi, rho, VIS_MU_MIN, marge))
    print("   coin autobloquant si mu > %.3f ; desserrage %.0f N a mu %.2f"
          % (coin_mu_autoblocage(), coin_desserrage(), COIN_MU))
    sig_pl, fl_pl, sig_tube = platine_contrainte()
    print("   platine de butee          %.0f MPa, coefficient %.1f a froid, %.1f a 150 C,"
          " fleche %.3f ; entretoises %.1f MPa chacune"
          % (sig_pl, RE_TOLE / sig_pl, RE_TOLE_CHAUD / sig_pl, fl_pl, sig_tube))

    print("\nTraverse :")
    lx, ly, ea = appui_tenon()
    print("   matage du tenon           %.1f MPa sur %.1f x %.1f par flanc" % (matage_tenon(), lx, ly))
    print("   racine de tenon           %.1f MPa (%.0f nets)" % flexion_tenon())
    print("   corps de plaque           %.1f MPa, appuis a %.1f" % flexion_traverse())

    print("\nBoulonnerie M10 :")
    for b in boulonnerie():
        print("   %-34s serrage %6.1f, depasse %5.1f%s"
              % (b["nom"], b["serrage"], b["depassement"],
                 "" if b["marge_filet"] is None else ", marge de filet %.1f" % b["marge_filet"]))

    print("\nEtuve %g x %g x %g%s :" % (ETUVE_INTERIEUR, ETUVE_Y, ETUVE_HAUTEUR,
                                          "" if ETUVE_CONFIRMEE else " (A CONFIRMER)"))
    print("   degagement de la douille  %.0f mm devant le bout de tige (y %.0f)"
          % (DEGAGEMENT_DOUILLE, Y_BOUT_VIS))
    print("   dent du crochet           a %.1f de la paroi" % CROCHET_DENT_Y)

    print("\nBruts usines :")
    for nom, fini, brut in parts.bruts_usinage():
        print("   %-10s fini %s, brut %s" % (nom, " x ".join("%.1f" % v for v in fini),
                                            " x ".join("%g" % v for v in brut)))

    print("\nTreillis :")
    print("   profondeur                %.1f mm" % parts.profondeur_treillis())
    print("   traction de membrure      %.0f N" % effort_membrure())
    sig = effort_membrure() / (W_MEMBRURE * EP_FLANC)
    print("   contrainte de membrure    %.1f MPa, soit %.1f microdef/kN"
          % (sig, sig / E_ACIER * 1e6 / (CHARGE_DIM / 1000.0)))

    pb = verifie()
    print("\n%d probleme(s)" % len(pb))
    for x in pb:
        print("   ! " + x)
