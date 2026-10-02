# -*- coding: utf-8 -*-
"""
Ecrit SPEC.md a partir du modele vivant : params.py, le calcul EF et les masses.
La specification ne peut donc plus deriver du modele.

    python spec.py

L'accumulateur du document s'appelle L : ne jamais creer de variable locale L
dans main(), SPEC.md sortirait vide sans la moindre erreur.
"""

import os
import json
import math
import time
import params as p
import parts as P

HERE = os.path.dirname(os.path.abspath(__file__))

# Couple de serrage des vis M10 8.8 du cadre (V1) et de la chape (V9). Precharge
# d'environ 17 kN : 80 MPa dans un tube d'entretoise, sans l'ecraser.
COUPLE_M10 = 35.0


def charge_fissuration(f_ct=4.0):
    """Effort sur la vis a la fissuration, section homogeneisee."""
    n = p.E_ACIER / p.POUTRE_E
    a_b = p.POUTRE_B * p.POUTRE_H
    a_p = 2.0 * p.PLAT_B * p.PLAT_E * n
    v = p.axe_neutre()
    i_b = p.POUTRE_B * p.POUTRE_H ** 3 / 12.0 + a_b * (p.POUTRE_H / 2.0 - v) ** 2
    i_p = a_p * (v + p.PLAT_E / 2.0) ** 2
    i = i_b + i_p
    # contrainte de traction dans le beton a la fibre inferieure (z = 0)
    moment = f_ct * i / v
    return 4.0 * moment / p.PORTEE, i, v


def lire_json(nom):
    """(contenu, date du calcul jj/mm/aaaa) d'un resultat de out/, ou ({}, "").
    La date est celle que le calcul a ecrite dans le fichier (date_calcul) ;
    a defaut seulement, celle du fichier, que git ne conserve pas."""
    f = os.path.join(HERE, "out", nom)
    if not os.path.isfile(f):
        return {}, ""
    with open(f) as fh:
        d = json.load(fh)
    if isinstance(d, dict) and d.get("date_calcul"):
        return d, d["date_calcul"]
    return d, time.strftime("%d/%m/%Y", time.localtime(os.path.getmtime(f)))


def entretoises_de_cadre():
    """'4 de coin, 2 de bielle, 1 de sommet' : les entretoises serrees par les vis de cadre."""
    parts_ = [(4, "de coin"), (2, "de bielle"), (1 if p.ENTR_SOMMET else 0, "de sommet")]
    if sum(n for n, _ in parts_) != P.n_entretoises() - len(p.TROU_SUPPORT):
        return "%d" % (P.n_entretoises() - len(p.TROU_SUPPORT))       # le modele a change
    return ", ".join("%d %s" % (n, t) for n, t in parts_ if n)


def encombrement_y():
    """Etendue du banc selon y : (coin recule, bout des vis de chape ou de la tige)."""
    tete_v9 = -(p.Y_FLANC_EXT + p.RONDELLE_M10_E + 6.4)      # tete H M10 : 6,4
    return min(p.COIN_Y0, tete_v9), max(p.Y_BOUT_VIS, p.Y_BOUT_TIRANT)


def main():
    fem, _ = lire_json("fem_flanc.json")
    masses, date_masses = lire_json("masses.json")
    flamb3, date_f3 = lire_json("flambement3.json")
    flamb1, date_f1 = lire_json("flambement.json")
    balayage_r, date_br = lire_json("balayage_R_FEN_BAS.json")
    specs = dict((s.name, s) for s in P.all_parts())
    masse = dict((it["nom"], it) for it in masses.get("pieces", []))

    fcr, inertie, v = charge_fissuration()
    fleche_cr = fcr * p.PORTEE ** 3 / (48.0 * p.POUTRE_E * inertie)
    sig_memb = p.effort_membrure() / (p.W_MEMBRURE * p.EP_FLANC)
    fem_vm = max(fem.get("von_mises_max", 0.0), 1.0)    # pas de division par zero sans EF
    y_min, y_max = encombrement_y()
    p_haut, p_bas = p.pressions_plaquettes()
    ph = p.portee_plaquette(p.PLAQ_HAUT_Y0, p.PLAQ_HAUT_Y1, p.TRAVERSE_B)
    pbb = p.portee_plaquette(p.PLAQ_BAS_Y0, p.PLAQ_BAS_Y1, p.POUSSOIR_B)
    boulons = p.boulonnerie()
    v9 = boulons[2]                     # vis de chape
    n_entr = P.n_entretoises()
    n_chape = len(p.TROU_SUPPORT)

    L = []
    a = L.append
    a("# Banc de flexion 3 points - specification")
    a("")
    a("Indice %s du %s. Fichier engendre par `spec.py` a partir de `params.py`,"
      % (p.INDICE_REVISION, p.DATE_EDITION))
    a("du calcul elements finis et du modele 3D. Ne pas le modifier a la main.")
    a("")

    a("## 1. Objet")
    a("")
    a("Fissuration controlee d'une poutrelle beton non arme instrumentee fibre")
    a("optique, en etuve jusqu'a 150 degres C, avec correlation d'images sur une")
    a("face laterale. Le cadre est auto-reactif : aucune reaction exterieure. Il")
    a("travaille COUCHE sur la paillasse et DEBOUT, sur son about, dans l'etuve")
    a("(voir `DEBOUT.md`).")
    a("")

    a("## 2. Eprouvette et renfort")
    a("")
    a("| grandeur | valeur |")
    a("|---|---|")
    a("| Poutrelle | %.0f x %.0f x %.0f mm, beton non arme |" % (p.POUTRE_B, p.POUTRE_H, p.POUTRE_L))
    a("| Plats de renfort colles | 2 x %.0f x %.0f x %.0f, feuillard S235 du commerce, a y = +/- %g (axe des flancs) |"
      % (p.PLAT_B, p.PLAT_E, p.PLAT_L, p.Y_FLANC))
    a("| Colle | epoxy haute temperature (Duralco 4420) |")
    a("| Axe neutre de la section homogeneisee | %.2f mm au dessus de la face inferieure |" % v)
    a("| Inertie homogeneisee | %.3g mm4 |" % inertie)
    a("| Effort a la fissuration (beton a 4 MPa) | %.2f kN |" % (fcr / 1000.0))
    a("| Fleche a la fissuration | %.3f mm |" % fleche_cr)
    a("")
    a("Le renfort rend la fissuration progressive et pilote l'ouverture. Il")
    a("descend l'axe neutre de %.1f mm par rapport au beton nu." % (p.POUTRE_H / 2.0 - v))
    a("")
    a("Les deux plats, les quatre patins d'appui et le patin de charge sont colles")
    a("sur la poutrelle et partent avec elle : il en faut un jeu par eprouvette.")
    a("")

    a("## 3. Chargement")
    a("")
    a("| grandeur | valeur |")
    a("|---|---|")
    a("| Schema | 3 points, portee %.0f mm |" % p.PORTEE)
    a("| Charge de dimensionnement du cadre | %.0f kN |" % (p.CHARGE_DIM / 1000.0))
    a("| Commande | coin d'acier C45 a %.0f deg garni de deux plaques de bronze du commerce,"
      " tige filetee M%.0f pas %.1f normale aux flancs |"
      % (p.COIN_ANGLE, p.VIS_D, p.VIS_PAS))
    a("| Pile de rondelles | %d x DIN 2093 A50 (%.0f x %.1f x %.1f), montees tete-beche |"
      % (p.RESSORT_N, p.RESSORT_DE, p.RESSORT_DI, p.RESSORT_T))
    a("| Hauteur libre de la pile | %.1f mm |" % p.PILE_H_LIBRE)
    a("| Effort de la pile a plat | %.1f kN |" % (p.RESSORT_F_PLAT / 1000.0))
    a("| Course totale | %.1f mm |" % p.PILE_COURSE)
    a("| Ecrasement a %.0f kN | %.2f mm (raideur secante %.0f N/mm) |"
      % (p.CHARGE_DIM / 1000.0, p.PILE_ECRAS_DIM, p.PILE_K_SECANT))
    a("| Butee de course en bas de lumiere | %.1f mm, plafonne l'effort a %.1f kN |"
      % (p.ecrasement_butee(), p.pile_force(p.ecrasement_butee()) / 1000.0))
    reserve = (p.COIN_T_MAX - p.COIN_T_MIN) - p.PILE_ECRAS_DIM
    a("| Rattrapage d'empilement | %.1f mm de course en reserve au dela des %.0f kN (%.0f exiges) ;"
      " cales de %s mm, D%g / D%g, entre poussoir et pile |"
      % (reserve, p.CHARGE_DIM / 1000.0, p.TOL_EMPILEMENT,
         " et ".join(P.fr(e) for e in p.CALES_EP), p.CALE_DE, p.CALE_DI))
    e05, c05, t05 = p.coin_tours(500.0)
    a("| Precharge de collage, 0,5 kN | %.2f mm de pile, %.2f mm de coin, %.2f tour de tige apres le contact |"
      % (e05, c05, t05))
    a("")
    a("La loi des rondelles Belleville n'est pas lineaire. Graduation gravee :")
    a("")
    a("| charge | descente du coulisseau |")
    a("|---|---|")
    for kn in (2, 4, 6, 8, 10, 12):
        a("| %d kN | %.2f mm |" % (kn, p.pile_ecrasement(kn * 1000.0)))
    a("")
    a("Cette lecture est un indicateur a quelques pour cent pres : elle englobe la")
    a("souplesse propre du cadre (%.3f mm a %.0f kN) et la fleche de la poutre."
      % (fem.get("fleche_max", 0.0), p.CHARGE_DIM / 1000.0))
    a("La mesure de reference est la fibre collee sur la membrure haute.")
    a("")

    a("## 4. Appuis")
    a("")
    a("Les flancs sont RENTRES sous les plats de renfort : ils portent dessous, et")
    a("la face laterale de la poutrelle reste entierement degagee pour la camera.")
    a("")
    a("| poste | cote |")
    a("|---|---|")
    a("| Largeur de la poutrelle | %.0f |" % p.POUTRE_B)
    a("| Debord de la poutrelle de chaque cote | %.1f |" % (p.POUTRE_B / 2.0 - p.Y_FLANC - p.EP_FLANC / 2.0))
    a("| Epaisseur d'un flanc | %.0f |" % p.EP_FLANC)
    a("| Ecart interieur entre flancs | %.0f (impose par les rondelles %.0f) |"
      % (p.ECART_FLANCS, p.RESSORT_DE))
    a("| Largeur hors tout des flancs | %.0f |" % (p.ECART_FLANCS + 2 * p.EP_FLANC))
    a("| Face inferieure libre au centre | %.0f (passage du cable) |"
      % (2 * (p.Y_FLANC - p.PLAT_B / 2.0)))
    a("")
    a("Le contact se fait au FOND de la rainure du patin, %.1f mm au dessus de sa" % p.RAINURE_P)
    a("face inferieure.")
    a("")
    a("| grandeur | valeur |")
    a("|---|---|")
    a("| Patins d'appui | %.0f x %.0f x %.0f, S355JR, colles en place |" % (p.PATIN_L, p.PATIN_B, p.PATIN_E))
    a("| Rainure de guidage | %.1f x %.1f, fraisee apres decoupe, jeu %.2f par cote sur la tole reelle |"
      % (p.RAINURE_B, p.RAINURE_P, p.RAINURE_JEU))
    a("| Bossage | R%.0f, relief %.1f, largeur totale %.1f |"
      % (p.BOSSAGE_R, p.BOSSAGE_RELIEF, p.largeur_bossage()))
    a("| Pression de Hertz a %.0f kN | %.0f MPa sur %.1f mm portants (flanc de %g moins ses deux aretes cassees de %g) |"
      % (p.CHARGE_DIM / 1000.0, p.hertz_appui(), p.hertz_largeur(), p.EP_FLANC, p.CHANFREIN))
    a("| Limite au contact a 150 degres C | %.0f MPa, 1,6 Re a chaud du corps le plus mou (le patin S355JR) ; coefficient %.2f |"
      % (p.HERTZ_LIM, p.hertz_coef()))
    a("| Pression sur le beton sous un patin | %.2f MPa |"
      % (p.CHARGE_DIM / 4.0 / (p.PATIN_L * p.PATIN_B)))
    a("| Bras contact - axe neutre | %.2f mm |" % p.bras_contact_axe_neutre())
    a("")
    a("Le bossage est un BALANCIER, pas un galet. Il donne une ligne de contact")
    a("nette et laisse tourner la poutrelle, mais il n'absorbe pas le recul de")
    a("%.3f mm de la fibre basse a la fissuration, qui passe en frottement et"
      % (p.bras_contact_axe_neutre() * fleche_cr * 6.0 / p.PORTEE))
    a("coute quelques pour cent sur le moment. Pour le supprimer il faudrait un")
    a("vrai galet libre sur une des deux lignes d'appui.")
    a("")
    a("Les patins sont colles sur le plat par leur face SUPERIEURE seulement : la")
    a("rainure reste seche sur le bossage, qui doit pouvoir basculer.")
    a("")

    a("## 5. Empilement vertical")
    a("")
    a("z = 0 au bord inferieur du flanc.")
    a("")
    a("| z | element |")
    a("|---|---|")
    for nom, z in [("dessus de la membrure basse", p.Z_MEMB_BASSE),
                   ("dessous du patin d'appui", p.Z_PATIN_BAS),
                   ("sommet du bossage, fond de rainure, point de contact", p.Z_BOSSAGE),
                   ("dessous du plat de renfort", p.Z_PLAT_BAS),
                   ("face inferieure de la poutrelle", p.Z_POUTRE_BAS),
                   ("face superieure de la poutrelle", p.Z_POUTRE_HAUT),
                   ("dessus du patin de charge", p.Z_PATIN_CHARGE_HAUT),
                   ("dessus du poussoir", p.Z_POUSSOIR_HAUT),
                   ("dessous du coulisseau, pile libre", p.Z_COULISSEAU_BAS),
                   ("dessous du coulisseau a 12 kN", p.Z_COULISSEAU_BAS - p.PILE_ECRAS_DIM),
                   ("dessus du coulisseau, pile libre", p.Z_COULISSEAU_HAUT),
                   ("dessous de la traverse a tenons, plan de glissement du coin", p.Z_TRAVERSE_BAS),
                   ("dessous de la membrure haute", p.Z_MEMB_HAUTE),
                   ("hors tout", p.H_FLANC)]:
        a("| %.1f | %s |" % (z, nom))
    a("")
    a("Encombrement des flancs %.0f x %.0f x %.0f mm. Selon y, le banc va de %.1f"
      % (p.L_FLANC, p.H_FLANC, p.ECART_FLANCS + 2 * p.EP_FLANC, y_min))
    a("(coin recule) a +%.0f (bout des vis de chape), soit %.1f mm ; les pieds font %.0f."
      % (y_max, y_max - y_min, p.PIED_Y))
    a("Etuve %g x %g x %g mm (A CONFIRMER) : le cadre y travaille DEBOUT sur son"
      % (p.ETUVE_INTERIEUR, p.ETUVE_INTERIEUR, p.ETUVE_HAUTEUR))
    a("about, pose par deux pieds en V sur quatre crochets pendus aux parois ; sur")
    a("la paillasse il travaille couche sur deux pieds. Voir `DEBOUT.md`.")
    a("")

    a("## 6. Flanc en treillis")
    a("")
    a("Le moment est triangulaire et la profondeur du treillis suit, donc l'effort")
    a("dans la membrure haute est constant sur toute sa longueur.")
    a("")
    a("| membre | section | valeur |")
    a("|---|---|---|")
    a("| Membrure haute | %.0f x %.0f | %.2f kN de traction, %.1f MPa |"
      % (p.W_MEMBRURE, p.EP_FLANC, p.effort_membrure() / 1000.0, sig_memb))
    a("| Bielles | %.0f x %.0f, pente %.2f degres | compression |"
      % (p.W_BIELLE, p.EP_FLANC, math.degrees(P.bielle_angle())))
    a("| Montants | %.0f x %.0f | traction |" % (p.W_MONTANT, p.EP_FLANC))
    a("| Membrure basse | %.0f x %.0f | moment constant de %.0f N.m entre appuis |"
      % (p.W_MEMB_BASSE, p.EP_FLANC,
         p.CHARGE_DIM / 4.0 * (p.X_FENETRE - p.X_APPUI) / 1000.0))
    a("| Profondeur du treillis | %.1f mm | |" % P.profondeur_treillis())
    a("")
    if fem:
        a("Calcul elements finis CalculiX, %d noeuds, elements du second ordre," % fem.get("noeuds", 0))
        a("charge de %.0f N au noeud, appuis glissants sur les deux bossages :" % fem.get("charge_N", 0))
        a("")
        a("| grandeur | valeur |")
        a("|---|---|")
        a("| von Mises maxi | %.0f MPa |" % fem.get("von_mises_max", 0))
        a("| Coefficient a froid, %s (Re %.0f) | %.2f |"
          % (p.MATIERE_TOLE, p.RE_TOLE, p.RE_TOLE / fem_vm))
        a("| Coefficient a 150 degres C (Re %.0f) | %.2f |" % (p.RE_TOLE_CHAUD, p.RE_TOLE_CHAUD / fem_vm))
        a("| Fleche du flanc | %.3f mm |" % fem.get("fleche_max", 0.0))
        if flamb3:
            sym = dict((q["cas"], q["facteurs"][0]) for q in flamb3["cas"])
            a("| Flambement hors plan, mode symetrique (fem_flamb3, %s) | facteur %.1f couche, %.1f debout, avec les %d entretoises |"
              % (date_f3, sym.get("tubes_couche", 0), sym.get("tubes_debout", 0), n_entr))
        if flamb1:
            anti = dict((q["cas"], q["facteurs"][0]) for q in flamb1["cas"])
            a("| Flambement, flancs en sens contraire (fem_flambement, %s) | facteur %.1f au moins : calcul fait avant les entretoises de chape et de sommet, qui ne peuvent que le relever |"
              % (date_f1, anti.get("entretoises_couche", 0)))
        a("")
        a("Points les plus charges :")
        a("")
        a("| x | z | von Mises | zone |")
        a("|---|---|---|---|")
        etiquettes = {}
        for sx in (-1, 1):
            etiquettes[(sx * 420, 30)] = "membrure basse sous le montant, cote appui ; encoche de pied du coin voisine"
            etiquettes[(sx * 390, 30)] = "console d'appui sous le bossage"
            etiquettes[(sx * 30, 390)] = "angle de la mortaise de traverse, arete ou portent les tenons"
            etiquettes[(sx * 30, 330)] = "angle haut de la fente du coin"
            etiquettes[(sx * 30, 270)] = "ligament entre la fente du coin et la lumiere"
            etiquettes[(sx * 60, 270)] = "ligament exterieur de la lumiere"
            etiquettes[(sx * 60, 240)] = "angle bas du noeud"
            etiquettes[(sx * 240, 360)] = "trou d'entretoise de bielle"
        etiquettes[(0, 420)] = "membrure haute dans l'axe"
        etiquettes[(420, 420)] = "angle montant / membrure haute"
        etiquettes[(480, 450)] = "blocage numerique du calcul, sans objet"
        for pt in fem.get("points_chauds", [])[:8]:
            a("| %d | %d | %.0f MPa | %s |"
              % (pt["x"], pt["z"], pt["mpa"],
                 etiquettes.get((pt["x"], pt["z"]), "")))
        a("")
        pts = dict(((pt["x"], pt["z"]), pt["mpa"]) for pt in fem.get("points_chauds", []))
        if (-420, 30) in pts and (420, 30) in pts:
            a("La piece est symetrique, le calcul donne pourtant %.0f MPa d'un cote et %.0f"
              % (max(pts[(-420, 30)], pts[(420, 30)]), min(pts[(-420, 30)], pts[(420, 30)])))
            a("de l'autre : c'est l'ordre de grandeur du bruit de maillage a l'appui, et")
            a("l'on retient la plus forte valeur.")
            a("")
        a("Le point chaud est dans la membrure basse sous le montant, pas sur l'arc")
        a("du conge R%.0f du raccordement membrure basse / montant." % p.R_FEN_BAS)
        if balayage_r:
            vals = [q[1]["vm"] for q in balayage_r]
            a("Un balayage du rayon de R%.0f a R%.0f (fem_balayage.py, %s, sur le flanc de"
              % (balayage_r[0][0], balayage_r[-1][0], date_br))
            a("l'epoque) donne %.0f a %.0f MPa sans tendance : c'est du bruit de maillage,"
              % (min(vals), max(vals)))
            a("le rayon n'est pas le levier.")
        else:
            # out/balayage_*.json n'est pas suivi par git (.gitignore) : un depot
            # tout juste extrait ne l'a pas. Resultat historique, flanc de 10.
            a("Un balayage du rayon de R10 a R26 (fem_balayage.py, 16/09/2026, sur le flanc de")
            a("l'epoque) donne 151 a 160 MPa sans tendance : c'est du bruit de maillage,")
            a("le rayon n'est pas le levier.")
        a("")
        a("NUANCE ET EPAISSEUR. Le cadre est en tole de %g mm %s, etat recuit +A" % (p.EP_FLANC, p.NUANCE_TOLE))
        a("(Re %.0f, %.0f a 150 C). L'EN 10083-3 ne garantit a l'etat +A qu'une durete"
          % (p.RE_TOLE, p.RE_TOLE_CHAUD))
        a("maximale, pas de limite elastique : toute la marge du flanc repose sur Re,")
        a("qui est donc EXIGE a la commande -- %s." % p.EXIGENCE_TOLE)
        a("Le flanc travaille a %.0f MPa a l'appui : %.2f de coefficient a froid, %.2f a"
          % (fem_vm, p.RE_TOLE / fem_vm, p.RE_TOLE_CHAUD / fem_vm))
        a("150 C, contre 1,91 a chaud pour le cadre precedent en 10 mm S355 (157 MPa)")
        if masses:
            a("et %.1f kg de cadre au lieu de 44,5." % masses.get("cadre_kg", 0))
        else:
            a("et environ 9 kg de moins.")
        a("Si la tole de 8 en 42CrMo4 manque, le repli est le 10 mm S355 ou S460 :")
        a("EP_FLANC = 10 et tout suit.")
        a("")

    a("## 7. Tete de charge")
    a("")
    a("Chaine d'effort, de haut en bas : traverse a tenons portee par la mortaise")
    a("des flancs, coin de commande qui glisse sous elle sur ses plaques de bronze,")
    a("coulisseau guide par les tetes de quatre CHC M%g dans les lumieres, pile de"
      % p.GUIDE_VIS_D)
    a("rondelles sur tourillon flottant, poussoir, patin de charge colle. La")
    a("reaction remonte par les montants et les bielles dans la membrure haute,")
    a("qui travaille en traction.")
    a("")
    a("| piece | remarque |")
    a("|---|---|")
    a("| Traverse | %d plaques de tole %g, tenons dans la mortaise des flancs, chant du bas fraise en paquet |"
      % (p.TRAVERSE_N, p.TRAVERSE_EP))
    a("| Coulisseau | S355JR, dessus incline sur TOUTE sa section ; un bloc, sans tenon |")
    a("| Guidage | 4 tetes de CHC M%g x %g ISO 4762, tete lisse, diametre %g, dans des lumieres de %g ; taraudages M%g prof. %g |"
      % (p.GUIDE_VIS_D, p.GUIDE_VIS_L, p.GUIDE_TETE_D, p.LUMIERE_B, p.GUIDE_VIS_D, p.GUIDE_TARAUD_P))
    a("| Poussoir | %d plateaux de tole %g perces, reperes par 2 goupilles %g m6 serrees dans le patin de charge, qui fait fond |"
      % (p.POUSSOIR_N, p.POUSSOIR_EP, p.POUSSOIR_GOUPILLE_D))
    a("| Tourillon | %s, rond etire %g h9 non repris, flottant, engage de %.1f mm dans chaque alesage au repos |"
      % (p.TOURILLON_MATIERE, p.TOURILLON_D, (p.TOURILLON_L - p.PILE_H_LIBRE) / 2.0))
    a("| Tige filetee | immobile axialement dans la chape, le coin est son ecrou |")
    a("| Butee de course | bas de la lumiere, interdit l'aplatissement de la pile |")
    a("")

    a("## 7 bis. Commande par coin")
    a("")
    a("L'etuve fait %g x %g x %g (A CONFIRMER) et n'offre aucun passage de paroi"
      % (p.ETUVE_INTERIEUR, p.ETUVE_INTERIEUR, p.ETUVE_HAUTEUR))
    a("utilisable. Le cadre y est debout : un axe de vis dans le plan des flancs")
    a("regarderait une paroi a %.0f mm, inaccessible. La commande est donc NORMALE"
      % ((p.ETUVE_INTERIEUR - p.H_FLANC) / 2.0))
    a("AUX FLANCS. Un coin en ACIER, qui porte le taraudage, coulisse selon y entre")
    a("le dessous plat de la traverse et le dessus du coulisseau taille au meme")
    a("angle. Le coin ne se deplace que selon y : son dessus reste plaque sous la")
    a("traverse, donc l'axe de la vis est fixe.")
    a("")
    m_plaq = sum(masse[n]["masse_kg"] for n in ("plaquette_haute", "plaquette_basse") if n in masse)
    a("| grandeur | valeur |")
    a("|---|---|")
    a("| Angle | %.0f degres |" % p.COIN_ANGLE)
    a("| Coin | acier C45, %.0f de large, %.1f a %.1f d'epaisseur, %.1f de long |"
      % (p.COIN_B, p.COIN_T_BOUT_MINCE, p.COIN_T_BOUT_EPAIS, p.COIN_L))
    a("| Plaques de frottement | 2 plaques du commerce %s, %g x %g x %g, %s%s |"
      % (p.PLAQ_REF, p.PLAQ_B, p.PLAQ_L, p.PLAQ_EP, p.PLAQ_ALLIAGE,
         (", %.2f kg en tout" % m_plaq) if m_plaq else ""))
    a("| Course utile | %.1f mm selon y |" % p.COIN_COURSE)
    a("| Position de repos | bout epais a y %.1f, bout mince a y %.0f |"
      % (p.COIN_Y0, p.COIN_Y1))
    a("| Sens de marche | vers la chape ; en fin de course le bout mince est a y %.1f |"
      % p.COIN_Y_MAX)
    a("| Depassement hors cadre | %.1f mm, d'un cote au repos, de l'autre en fin de course |"
      % (p.COIN_Y_MAX - p.Y_FLANC_EXT))
    a("| Vis | M%.0f pas %.1f, taraudee dans le coin, immobile axialement |"
      % (p.VIS_D, p.VIS_PAS))
    a("| Effort moteur a %.0f kN | %.1f kN |" % (p.CHARGE_DIM / 1000.0, p.coin_effort() / 1000.0))
    a("| Couple sur la vis | %.1f N.m |" % p.coin_couple())
    dz, df = p.coin_par_tour()
    a("| Course par tour | %.3f mm de coulisseau, environ %.0f N |" % (dz, df))
    a("| Pression de contact, fin de course | %.1f MPa en haut sur %.1f x %.1f (joints de traverse deduits), %.1f MPa en bas sur %.0f x %.1f ; %g admis |"
      % (p_haut, p.portee_coin(), ph, p_bas, p.PLAQ_B, pbb, p.PLAQ_P_ADM))
    a("| Rendement | %.0f pour cent |"
      % (100 * p.CHARGE_DIM * math.tan(math.radians(p.COIN_ANGLE)) / p.coin_effort()))
    a("")
    a("Le coin n'est autobloquant que si le frottement de ses deux faces depasse")
    a("%.3f (tan a / 2) : avec le bronze graphite a chaud (%.2f) on y est a peine,"
      % (p.coin_mu_autoblocage(), p.COIN_MU))
    a("on ne compte donc pas dessus. C'est la vis M%.0f qui tient la charge, son" % p.VIS_D)
    a("angle d'helice etant tres inferieur a l'angle de frottement. Le filet est")
    a("de l'acier sur acier monte a la pate cuivre, et le cas dangereux est le")
    psi, rho, marge = p.filet_marge()
    a("frottement BAS : a %.2f, helice %.2f degres contre %.2f degres de frottement"
      % (p.VIS_MU_MIN, psi, rho))
    a("apparent, marge x%.2f." % marge)
    a("")
    psi_tr = math.degrees(math.atan(4.0 / (math.pi * 14.0)))           # Tr16x4, d2 = 14
    rho_tr = math.degrees(math.atan(p.VIS_MU_MIN / math.cos(math.radians(15.0))))
    a("C'est pourquoi le filet reste METRIQUE a pas de %.0f et non trapezoidal."
      % p.VIS_PAS)
    a("Au meme frottement de %.2f, un Tr16x4 tomberait a une marge de %.2f :"
      % (p.VIS_MU_MIN, rho_tr / psi_tr))
    a("%s, et il doublerait le pas de charge a %.0f N par tour."
      % ("il serait REVERSIBLE" if rho_tr < psi_tr else "a peine irreversible",
         2 * p.coin_par_tour()[1]))
    a("A pas egal, le profil trapezoidal ne gagne rien non plus : sa hauteur de")
    a("recouvrement vaut 0,5 P contre 0,541 P pour le metrique, soit MOINS de")
    a("flanc portant. Les flancs travaillent a %.1f MPa, engagement plafonne a"
      % p.pression_filet())
    a("1,5 d, pour %g admis sur un taraudage C45 et une tige 8.8 en manoeuvre lente."
      % p.FILET_P_ADM)
    a("")
    a("Le filet est TARAUDE DIRECTEMENT DANS L'ACIER du coin. Une bague-ecrou en")
    a("bronze a ete dessinee puis abandonnee : a la vitesse de manoeuvre d'un")
    a("banc a la main, ce n'est pas la vitesse qui use un filet, et le couple")
    a("tige 8.8 sur C45 brut tient sans probleme monte a la pate cuivre. La tige")
    a("est la plus dure : c'est le taraudage du coin qui s'use, et il se refait.")
    a("Il ne court que sur %.0f mm et non sur toute la longueur du coin ; au dela"
      % p.COIN_TARAUD_L)
    a("le percage est repris a %.0f, si bien que le taraud debouche dans un trou"
      % p.VIS_PASSAGE_D)
    a("plus grand : les copeaux s'evacuent vers l'avant et il n'y a que %.0f d a"
      % (p.COIN_TARAUD_L / p.VIS_D))
    a("tarauder au lieu de %.0f. Si le filet devait un jour lacher, le lamage"
      % (p.COIN_L / p.VIS_D))
    a("d'une bague de bronze reste possible : rien ici n'est irreversible.")
    a("")
    a("LE BRONZE N'EST PLUS QUE DEUX PLAQUES DU COMMERCE, TOUTES DEUX SUR LE COIN.")
    a("Un coin de bronze plein aurait demande 2,7 kg de barre, une section qu'il")
    a("faut faire debiter. Or le bronze n'est utile que sur les deux faces de")
    a("glissement : il est reporte sur deux plaques de frottement autolubrifiantes")
    a("%s (%g x %g x %g), et le coin devient un bloc d'acier C45"
      % (p.PLAQ_REF, p.PLAQ_B, p.PLAQ_L, p.PLAQ_EP))
    brut_coin = specs["coin"].stock if "coin" in specs else ""
    if "coin" in masse:
        a("de %.2f kg, usine dans un %s." % (masse["coin"]["masse_kg"], brut_coin))
    else:
        a("usine dans un %s." % brut_coin)
    a("")
    a("La basse pourrait etre posee sur la pente du coulisseau, ou elle ne ferait")
    a("que %.0f de long au lieu de %.0f. Elle est mise sur le coin comme la"
      % (p.POUSSOIR_B, p.PLAQ_BAS_L))
    a("haute : le coulisseau redevient un bloc nu -- un percage et un plan a %.0f"
      % p.COIN_ANGLE)
    a("degres, ni poche ni taraudage -- les deux faces d'usure sortent ensemble")
    a("avec le coin, et c'est deux fois le meme rebord a usiner. Ce que cela")
    a("coute : la plaquette basse traverse la fente du flanc avec le coin, qui")
    a("s'approfondit donc de %.1f mm." % p.PLAQ_DROP)
    a("")
    cis, flex, pres = p.rebord_contrainte()
    a("Aucune vis : le coin ne fait que %.0f de large et le percage de la tige en"
      % p.COIN_B)
    a("prend le milieu, il ne reste pas de quoi noyer une tete fraisee a un")
    a("ligament d'epaisseur. Chaque plaquette est prise entre DEUX REBORDS usines")
    a("dans la masse, %.2f (dessus) et %.2f (dessous) x %g, qui encaissent les %.2f kN"
      % (p.PLAQ_REBORD_L, p.PLAQ_REBORD_L_BAS, p.PLAQ_REBORD_H, p.CHARGE_DIM * p.COIN_MU / 1000.0))
    a("d'entrainement dans l'axe de la vis : flexion %.1f MPa au pied, matage du chant %.0f MPa."
      % (flex, pres))
    d_th = (p.ALPHA_BRONZE - p.ALPHA_ACIER) * p.DELTA_T * p.PLAQ_BAS_L
    a("Elles ne sont PAS collees a l epoxy. Bronze et acier ne se dilatent pas")
    a("pareil : a %.0f C la plaquette s allonge de %.2f mm de plus que son siege,"
      % (20 + p.DELTA_T, d_th))
    a("et un joint rigide sur toute la longueur encaisserait 30 a 80 MPa de")
    a("cisaillement en bout pour 15 a 20 tenus : il fissurerait au premier")
    a("chauffage. Les rebords prenant tout l entrainement, la fixation n a plus")
    a("qu a tenir la plaquette le temps du montage : quelques points de silicone")
    a("haute temperature, %.0f fois plus souple, y suffisent -- %.3f MPa de"
      % (1000.0 / p.COLLE_G, p.COLLE_G * d_th / 2.0 / p.COLLE_EP))
    a("cisaillement thermique dans le joint. Aucune pate sur les plaques ni sur")
    a("leurs sieges : elles sont autolubrifiantes, et le silicone ne prend pas sur")
    a("une pate.")
    a("")
    a("Pied de rebord DEGAGE et non conge : l'angle vif de la plaquette doit")
    a("porter sur toute la hauteur. Et sur la face inclinee, la face interieure")
    a("du rebord est NORMALE A LA PENTE et non verticale, comme le chant de la")
    a("plaquette : dessinees verticales, elles la mordaient de %.1f mm en bas."
      % (p.PLAQ_EP * p.COIN_TAN))
    a("")
    a("Les rebords s'arretent %g mm SOUS la surface du bronze. Aux deux bouts de"
      % (p.PLAQ_EP - p.PLAQ_REBORD_H))
    a("course ils passent sous la conjuguee, et s'ils affleuraient ce serait de")
    a("l'acier sur acier qu'on ferait glisser. Il en coute de la portee : la")
    a("plaquette haute porte sur %.1f mm au lieu de %.0f, la basse sur %.1f au"
      % (ph, p.TRAVERSE_B, pbb))
    a("lieu de %.0f, soit %.1f et %.1f MPa." % (p.POUSSOIR_B, p_haut, p_bas))
    a("")
    a("Le filet reste engage sur %.1f mm coin recule, soit %.1f d, ce qui est"
      % ((p.COIN_Y0 + p.COIN_TARAUD_L) - p.VIS_Y0,
         ((p.COIN_Y0 + p.COIN_TARAUD_L) - p.VIS_Y0) / p.VIS_D))
    a("tout ce qui porte : au dela de 1,5 d, l'ecart de pas entre la tige et le")
    a("taraudage fait que les derniers filets ne prennent plus rien.")
    a("")
    a("Le coin traverse les deux flancs par une fente de %.0f x %.0f, entre les"
      % (p.FENTE_COIN_B, p.FENTE_COIN_Z1 - p.FENTE_COIN_Z0))
    a("deux lumieres de guidage reportees a x = +/- %.0f. Il reste alors %.0f mm"
      % (p.GUIDE_X, 2 * p.X_NOEUD - p.FENTE_COIN_B - 2 * p.LUMIERE_B))
    a("de section nette dans le noeud, soit %.1f MPa nominal pour les %.0f N par flanc."
      % (p.CHARGE_DIM / 2 / ((2 * p.X_NOEUD - p.FENTE_COIN_B - 2 * p.LUMIERE_B) * p.EP_FLANC),
         p.CHARGE_DIM / 2))
    a("")
    a("La suppression de la vis verticale a ramene la hauteur du cadre de 480 a")
    a("%.0f mm : debout dans l'etuve de %g, il reste %.0f mm de chaque cote, ou se"
      % (p.H_FLANC, p.ETUVE_INTERIEUR, (p.ETUVE_INTERIEUR - p.H_FLANC) / 2.0))
    a("logent les pieds en V et les crochets. Elle a aussi permis de descendre le")
    a("noeud : la profondeur du treillis passe de 139,5 a %.1f mm." % P.profondeur_treillis())
    a("")

    a("### Sens de montage du coin, et arret axial de la tige")
    a("")
    a("Le bout EPAIS du coin est du cote OPPOSE a la chape : le coin avance donc")
    a("VERS elle en chargeant. C'est ce sens, et lui seul, qui rend l'arret axial")
    a("de la tige possible. L'equilibre du coin le montre : la composante selon y")
    a("de la reaction du coulisseau, plus les deux frottements, valent %.1f kN, et"
      % (p.coin_effort() / 1000.0))
    a("la tige doit les fournir. La face inclinee repousse le coin vers son bout")
    a("EPAIS : le filet tire donc la tige vers l'INTERIEUR du cadre, et sa tete")
    a("vient appuyer sur la FACE EXTERIEURE des platines, a travers la butee a")
    a("aiguilles. Cote interieur, deux rondelles trempees et deux ecrous minces ne")
    a("reprennent que l'effort de desserrage : %.0f N a un frottement de %.2f, quand"
      % (p.coin_desserrage(), p.COIN_MU))
    a("le coin est autobloquant ; en dessous de %.3f la charge le chasse d'elle-meme"
      % p.coin_mu_autoblocage())
    a("et ils ne voient rien.")
    a("")
    a("Monte a l'envers, le coin s'eloignerait de la chape en chargeant : la tige")
    a("serait tiree hors de son alesage et ne pousserait rien. Il faudrait alors")
    a("loger la butee a aiguilles entre les platines et le bout du coin, ou elle")
    a("ne tient pas. Le controle des cotes refuse ce sens.")
    a("")

    a("### Position de repos du coin")
    a("")
    a("Le coin est dessine au repos bout mince AFFLEURANT le bord du coulisseau,")
    a("et non centre sur lui. C'est la seule position qui garde le contact sur")
    a("toute la largeur du coulisseau d'un bout a l'autre de la course. Centre au")
    a("repos, le coin aurait glisse a moitie hors du coulisseau en fin de course :")
    a("appui reduit a %.0f mm au lieu de %.0f, pression doublee, et surtout"
      % (p.POUSSOIR_B / 2.0, p.POUSSOIR_B))
    a("resultante decalee de %.1f mm, donc basculement de la tete sur la pile."
      % (p.POUSSOIR_B / 4.0))
    a("Le prix a payer est que le bout mince atteint y %.1f en fin de course, ce"
      % p.COIN_Y_MAX)
    a("qui fixe la position de la chape de butee.")
    a("")

    a("## 7 ter. Butee axiale de la tige")
    a("")
    a("Le coin avance VERS la butee en chargeant et tire la tige vers l'interieur")
    a("du cadre ; la tete de la tige pousse donc la butee, et les platines, contre")
    a("le flanc : platines en flexion, entretoises en compression, aucune piece de")
    a("la butee ne travaille en traction. Il n'y a aucune raison d'usiner une chape")
    a("dans la masse. Deux platines de la MEME tole que les flancs, portees par deux")
    a("entretoises du MEME tube que le cadre, de part et d'autre de la vis, dans le")
    a("plan de son axe. Deux vis H M10 x %.0f traversent platines, entretoises de"
      % p.SUPPORT_TIRANT_L)
    a("butee, LES DEUX flancs et une entretoise de cadre entre eux, tete derriere")
    a("le flanc oppose, ecrou cote platines : plus aucun taraudage dans le flanc,")
    a("et deux entretoises de plus entre les flancs. Elles ne voient que la")
    a("precharge et les %.0f N de desserrage." % p.coin_desserrage())
    a("")
    sig_pl, fle_pl, sig_tube = p.platine_contrainte()
    a("| grandeur | valeur |")
    a("|---|---|")
    a("| Platines | %d x tole %g, %.0f de haut au droit de l'alesage, %.0f de long |"
      % (p.SUPPORT_N, p.SUPPORT_EP, p.SUPPORT_B, p.SUPPORT_X1 - p.SUPPORT_X0))
    a("| Flexion d'une platine | %.0f MPa, coefficient %.1f a froid, %.1f a 150 C, fleche %.3f mm |"
      % (sig_pl, p.RE_TOLE / sig_pl, p.RE_TOLE_CHAUD / sig_pl, fle_pl))
    a("| Entretoises de butee | %s, L = %.1f %s, %.1f MPa de COMPRESSION chacune |"
      % (p.ENTRETOISE_BRUT, p.SUPPORT_TUBE_L, p.SUPPORT_TUBE_TOL, sig_tube))
    a("| Fixation | 2 vis H M10 x %.0f ISO 4014 (filetees sur %.0f) a x = +/- %.0f, z %.1f, tete et 1 rondelle derriere le flanc oppose, %d rondelles + ecrou H cote platines |"
      % (p.SUPPORT_TIRANT_L, p.SUPPORT_TIRANT_FILET, p.SUPPORT_X, p.Z_VIS, p.SUPPORT_RONDELLES_ECROU))
    a("| Serrage sous tete | %.1f mm, filet a partir de %.0f : ecrou sur le filet avec %.1f de marge, %.1f de depassement |"
      % (v9["serrage"], p.SUPPORT_TIRANT_L - p.SUPPORT_TIRANT_FILET, v9["marge_filet"], v9["depassement"]))
    a("| Serrage | %g N.m, aucun taraudage : les vis traversent les deux flancs |" % COUPLE_M10)
    a("| Butee a aiguilles | AXK 1730 + 2 rondelles AS 1730, a plat sur la face EXTERIEURE, centree par la tige |")
    a("| Retenue interieure | 2 rondelles trempees AS 1730 + 2 ecrous HM M16, %.0f mm, desserrage seulement |"
      % (p.SUPPORT_RONDELLE + p.SUPPORT_ECROU_H))
    a("| Bout de tige | y %.0f, soit %.0f mm de degagement pour la douille, cadre decentre au pire dans l'etuve de %g (%.0f centre) |"
      % (p.Y_BOUT_VIS, p.DEGAGEMENT_DOUILLE, p.ETUVE_INTERIEUR, p.ETUVE_INTERIEUR / 2.0 - p.Y_BOUT_VIS))
    a("| Manoeuvre | douille de 24 et cliquet SEULEMENT : les bouts des vis de chape (y %.0f) depassent la tete de manoeuvre dans son plan, une cle plate bute dessus |"
      % p.Y_BOUT_TIRANT)
    a("")
    a("Tout sort du debit deja commande : les platines nichent dans la tole de %g"
      % p.EP_FLANC)
    a("des flancs, les entretoises sont coupees dans le meme tube que celles du")
    a("cadre. Rien a usiner. Les vis traversent LES DEUX flancs, avec une")
    a("entretoise de cadre entre eux : la commande se monte du cote que l'on veut,")
    a("en retournant le coin, et les deux percages servent dans les deux cas.")
    if p.ENTR_SOMMET:
        a("")
        a("Une entretoise de sommet, dans l'axe a z %.0f, au dessus de la mortaise de" % p.Z_ENTR_SOMMET)
        a("traverse : la membrure haute n'avait aucune liaison sur 500 mm et c'est la")
        a("que partait le mode de voilement symetrique. Meme tube de %.0f, meme vis TH"
          % p.ENTRETOISE_L)
        a("M10 x %.0f que les autres entretoises de cadre. Ce n'est PAS un serrage des"
          % p.ENTR_VIS_L)
        a("flancs sur le paquet de traverse : le tube de %.0f fixe l'ecart des flancs,"
          % p.ENTRETOISE_L)
        a("et les epaulements de la traverse gardent %g de jeu selon y (%g de chaque"
          % (p.TRAVERSE_JEU_Y, p.TRAVERSE_JEU_Y / 2.0))
        a("cote) : la traverse n'est jamais pincee.")
    a("")
    a("Boulonnerie M10 du cadre, toutes longueurs controlees par `verifie()` sur la")
    a("tole reelle (EP_TOLE_REELLE) : l'ecrou doit tomber sur le filet avec %g de"
      % p.FILET_MARGE_MIN)
    a("marge et le bout depasser de %g pour que le freinage soit en prise." % p.FILET_DEPASSE_MIN)
    a("")
    a("| boulonnerie | serrage | ecrou | depassement | marge de filet |")
    a("|---|---|---|---|---|")
    for b in boulons:
        a("| %s | %.1f | %g | %.1f | %s |"
          % (b["nom"], b["serrage"], b["ecrou"], b["depassement"],
             "-" if b["marge_filet"] is None else "%.1f" % b["marge_filet"]))
    a("")
    a("Ecrous de cadre et de traverse : %s. Pas d'ecrou a bague polyamide" % p.ECROU_FREIN_REF)
    a("(ISO 7040, DIN 985) : la bague flue vers 120 C et ne freine plus a 150 C.")
    a("%d vis de cadre (%s) et %d vis de chape"
      % (n_entr - n_chape, entretoises_de_cadre(), n_chape))
    a("serrent les %d entretoises." % n_entr)
    a("")

    a("## 8. Instrumentation")
    a("")
    a("| poste | valeur |")
    a("|---|---|")
    a("| Fibre sur le chant de la membrure haute | %.1f microdeformations par kN |"
      % (sig_memb / p.E_ACIER * 1e6 / (p.CHARGE_DIM / 1000.0)))
    a("| Resolution a 1 microdeformation | %.0f N |"
      % (1000.0 / (sig_memb / p.E_ACIER * 1e6 / (p.CHARGE_DIM / 1000.0))))
    a("| Lecture mecanique | position du coulisseau dans la lumiere |")
    a("| Correlation d'images | face laterale degagee sur %.0f x %.0f mm |"
      % (p.POUTRE_L, p.POUTRE_H))
    a("")
    a("Il n'y a pas de col de mesure : la membrure pleine donne deja une")
    a("resolution suffisante, et un col serait une entaille de plus.")
    a("")

    if masses:
        a("## 9. Masses")
        a("")
        a("Masses du modele 3D (out/masses.json, construit le %s)." % date_masses)
        a("")
        a("| piece | qte | masse unitaire | total |")
        a("|---|---|---|---|")
        for it in masses.get("pieces", []):
            s = specs.get(it["nom"])
            a("| %s | %d | %.2f kg | %.2f kg |"
              % (s.designation if s else it["designation"], it["qte"], it["masse_kg"],
                 it["masse_totale_kg"]))
        a("")
        a("**Cadre complet %.1f kg**, poutrelle %.1f kg."
          % (masses.get("cadre_kg", 0),
             masses.get("total_kg", 0) - masses.get("cadre_kg", 0)))
        a("")

    a("## 10. Conduite d'essai")
    a("")
    a("- rampes thermiques sous 0,2 degres C par minute : avec %.0f mm d'epaisseur," % p.POUTRE_H)
    a("  une rampe de 1 degre par minute creee deja 5 MPa d'ecart entre coeur et peau")
    a("- palier de stabilisation d'au moins 2 heures avant toute lecture")
    a("- acier nu ou phosphate, pas de zingue au dela de 200 degres C")
    a("- pate graphite ou cuivre sur le filetage de la tige, rien sur les plaques de bronze")
    a("- relaxation des rondelles de quelques pour cent au dela de 100 degres C :")
    a("  reprendre la charge a chaque palier")
    a("- revetement de la fibre a verifier : l'acrylate standard ne tient pas 150 degres C")
    a("- manoeuvre a la douille de 24 et au cliquet")
    a("")

    a("## 11. Points ouverts")
    a("")
    a("- **Largeur d'etuve %g, A CONFIRMER.** Elle place la dent du crochet (a %.1f"
      % (p.ETUVE_INTERIEUR, p.CROCHET_DENT_Y))
    a("  de la paroi) et a fixe la largeur des pieds (%g). Tant qu'elle n'est pas" % p.PIED_Y)
    a("  confirmee, les DXF du pied et du crochet portent : %s." % p.ALERTE_ETUVE)
    a("  La hauteur (%g) est aussi a confirmer." % p.ETUVE_HAUTEUR)
    a("- **Epaisseur reelle de la tole** : %s (EP_TOLE_REELLE = %g pour une" % (p.NOTE_TOLE_REELLE, p.EP_TOLE_REELLE))
    a("  tole nominale de %g). Encoches, nodes, fentes, mortaise et rainures des" % p.EP_FLANC)
    a("  patins en derivent ; le 3D et le calcul restent a la cote nominale.")
    a("- **Calage de la poutrelle debout** : rien ne la retient selon x, devenu")
    a("  vertical, que le frottement aux appuis. Point ouvert, assume : voir")
    a("  `DEBOUT.md`, paragraphe 6.")
    a("")

    path = os.path.join(HERE, "SPEC.md")
    with open(path, "w") as f:
        f.write("\n".join(L))
    print(path, "%d lignes" % len(L))


if __name__ == "__main__":
    main()
