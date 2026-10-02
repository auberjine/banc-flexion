# Planche 02_coulisseau : compte rendu de l'agent COULISSEAU (02/10/2026)

## Fichiers touches

- `plans.py` : seulement le bloc « tete de charge », du bandeau `# ==== tete de charge` jusqu'a `def plan_traverse():`. Il contient `plan_coulisseau()` et ses aides locales prefixees `c02_` : `c02_poly`, `c02_chemin`, `c02_decoupe`, `c02_axe`, `c02_cercle`, `c02_arc`, `c02_taraudage_bout`, `c02_cote_alignee`, `c02_cote_texte_h`, `c02_cote_angle`, `c02_rayon_creux`, `c02_appel` et `c02_titre`. Avant et apres le bloc, plans.py est identique a l'octet pres a la copie temoin (`correction/coulisseau/temoin/plans.py`). Le fichier reste en LF et en ASCII.
- `draw.py` : **non modifie**. La planche utilise les ajouts ISO de l'agent ASSEMBLAGE (`cote_hx`, `cote_vx`, `_cote_iso`, `renvoi`, `rupture`) et `View.rayon`. Elle n'appelle plus `cote_h`, `cote_v` ni `note`.
- Les SVG 00, 01 et 03 a 07 sont identiques a l'octet pres a ceux d'avant mon travail.
- Outils, dans `scratchpad/correction/coulisseau/` :
  - `pc_new.py`, la source du bloc ;
  - `splice.py` ;
  - `run.sh`, qui enchaine splice, plans, verif_plans, params, `../flanc/chk01.py 02_coulisseau` (tous traits, fins compris) et le rendu ;
  - `crop.py` et les decoupes de controle (`v1_*` a `h4`, `z_*`).

## Nouvelle mise en page

**02a Coulisseau (1:1)**. Trois vues alignees en projection europeenne : vue de face (depuis le bord mince), vue de droite a sa gauche, vue de dessus en dessous.
- Le titre porte le repere ; le sous-titre donne matiere, quantite et brut, lus dans `parts.all_parts()` : « S355JR, 1 ex., brut plat 65 x 40, L 120 (fini 58 x 36,2 x 114) ».
- **Vue de face** :
  - 4 taraudages M8 vus en bout, selon ISO 6410 : cercle du fond 6,8 en trait fort, cercle nominal 8 aux trois quarts en trait fin ;
  - cote **12** (axe depuis le dessous, `GUIDE_Z`) et cote **88** (`2 x GUIDE_X`), sur les axes prolonges ;
  - alesage en traits interrompus ;
  - arete du dessus incline, cote mince, avec les raccords R4.
- **Vue de droite** :
  - **36,2** au bord epais ;
  - **(23,8)** en cote auxiliaire, au bord mince, c'est-a-dire sur la bonne arete ;
  - vraie cote angulaire **12 deg**, hors de la piece ;
  - alesage en traits interrompus.
- **Vue de dessus** :
  - **114**, **58**, **4 x R4** (rayon lu sur le contour) ;
  - alesage cache ;
  - taraudages en traits interrompus depuis les faces laterales : filet 8 sur 16, avant-trou 6,8 sur 19 avec sa pointe a 118 deg ;
  - renvois a fleche « 4 x M8 prof. 16 / avant-trou 6,8 prof. 19 » et « alesage 25,4 prof. 20 / a fond plat, par dessous ».

**02c Coin (1:1, au lieu de 1:2)**. Le sous-titre donne « C45, 1 ex., brut plat 65 x 45, L 120 (fini 61 x 40 x 114,5) » ; l'epaisseur 40 est dans le titre.
- Cotes :
  - **114,5** ;
  - **100,4 +0,2/0** entre les rebords du dessus ;
  - **100,4 +0,2/0 alignee sur la pente** entre les faces interieures des rebords du dessous, attaches normales a la pente ;
  - **55,2** et **30,8** ;
  - **16** : axe du M16 depuis le plan du siege haut, en cote parallele avec le 30,8.
- Taraudage M16 en traits interrompus : nominal 16 et fond de filet 13,8 (`VIS_D - 1,0825·VIS_PAS`) sur 80, epaulement, puis passage 18. L'axe est un vrai trait mixte : l'ancien `contour()` fermait le chemin.
- Renvoi a fleche : « M16 x 2 prof. 80 depuis le bout EPAIS, centre sur l epaisseur ; passage 18 debouchant ».
- Appels B et C, cercles fins, sur les rebords du bout mince.
- **DETAIL B (4:1)**, rebords du dessus : hauteur **3**, degagement **R1,5** centre sur l'angle (renvoi par le centre), **R1** ; largeur (7,05) en auxiliaire.
- **DETAIL C (4:1)**, rebords du dessous :
  - hauteur **3** le long de la face interieure, donc normale a la pente, avec le texte horizontal (ISO 129-1 : une ligne presque verticale inclinee ne se lit ni du bas ni de la droite) ;
  - largeur (8,15) en projection en auxiliaire ;
  - faces NORMALES a la pente, dites en note.

**02b Plateau de poussoir (1:1)**. Le sous-titre donne « 42CrMo4 +A, 3 ex., brut tole 8 mm, cert. 3.1, Re >= 430 » (`BRUT_TOLE`, D4).
- Cotes : **100**, **58**, **70** (entraxe des goupilles, prise sur les axes), **4 x R4**.
- Renvois « 2 x diam. 8,3 (passage) » (D7, `POUSSOIR_GOUPILLE_PASSAGE`) et « alesage 25,4 traversant ».

**Cartouche** :
- matiere « S355JR / 42CrMo4 +A / C45 » ;
- brut « voir sous les titres » ;
- quantite « 1 + 3 + 1 (02a, 02b, 02c) » ;
- echelle « 1:1 - details 4:1 ».

Le bronze n'est plus dans la matiere : les plaques sont achetees et citees en note.

**Notes** (12 lignes), toutes calculees :
- aretes cassees `CHANFREIN` ;
- 02a : pente Ra 1,6, planeite 0,05 (meme exigence que le dessous de traverse) ; bord epais cote chape ;
- 02c :
  - logements centres, sieges plans a 0,05 ; 55,2, 30,8 et 16 depuis les plans des sieges prolonges ;
  - pente du dessous (12 deg, celle du coulisseau) ; faces des rebords du dessous normales ; angles R1 (rayon lu sur le contour) ;
  - plaques norelem 06c / 06d ;
  - effort, couple et effet d'un tour de vis ;
  - autoblocage (`coin_mu_autoblocage` 0,106) et irreversibilite du filet a `VIS_MU_MIN` (marge x2,13 ; un Tr16x4 tomberait a x0,91) ;
  - pression sur les flancs du filet ; pate cuivre ;
- 02b : plateaux empiles, `poussoir.dxf`, patin 04b ; goupilles V3 (lu dans `nomenclature.visserie()`) libres, serrees en 8 H7 dans 04b ;
- SENS DE MONTAGE.

## Constats appliques

| constat | ce qui est fait |
|---|---|
| **02-01, 02-04, conc-01, conc-03, docu-01, D1** | M8 partout : `GUIDE_VIS_D`, `GUIDE_TARAUD_D` (6,8), `GUIDE_TARAUD_P`, `GUIDE_PERCAGE_P`. Plus aucun M10 ni 8,5 sur la planche ; `p.D_TARAUD` n'est plus lu. |
| **02-02, 02-15, conc-22, D1** | Taraudages dessines sur les faces laterales (vue de dessus) et en bout (vue de face), axe a 12 du dessous et x = +/-44 cotes. |
| **02-03, 02-19, conc-21, conc-38, docu-08** | 100,4 +0,2/0 dessus et le long de la pente ; plus de « 4 rebords 7.05 » ; details B et C a 4:1 ; coin a 1:1. |
| **02-05, 02-13** | 36,2 cote ; vraie cote angulaire 12 deg ; « 30 au milieu » supprime ; pente Ra 1,6 et planeite 0,05 ; sieges du coin planeite 0,05. |
| **02-06, 02-29** | Le 16 part du plan du siege. La note explique que 55,2, 30,8 et 16 partent des plans des sieges prolonges. L'« axe a 16 sous le dessus », ambigu, est supprime. |
| **02-07, 02-20, 02-21, conc-16 (plans), D7** | Poussoir avec axes, entraxe 70, 2 x 8,3 de passage, R4. La cote 58 est passee a gauche, plus aucun croisement. Les goupilles et l'ajustement 8 H7 dans 04b sont en note. |
| **02-08, 02-23, 02-32, conc-19, docu-13, D12** | Cartouche corrige. Reperes 02a / 02b / 02c dans les titres. Bruts et quantites lus dans `all_parts()`, donc les nouveaux bruts D12 du coin et du coulisseau. |
| **02-10, 02-11, 02-16, 02-24** | Toutes les cotes passent par `cote_hx` / `cote_vx` : texte a gauche des cotes verticales, attaches qui depassent la ligne de 2 mm. Les axes sont raccourcis : aucun ne traverse un texte. |
| **02-12, 02-14, 02-25** | Note « 23.8 au bord mince » remplacee par la cote (23,8) sur la bonne arete. La cote flottante « 20 alesage » est remplacee par l'alesage dessine en cache dans les vues de face et de droite, la profondeur et le « fond plat » etant en note. |
| **02-17, 02-28, 02-31** | Plus de cercle sur le texte d'alesage. La cote 88 est dans la vue de face, 114 dans la vue de dessus : plus d'imbrication. Tous les textes sont a plus de 11 mm du cadre. |
| **02-18** | Axe du M16 en trait mixte ; taraudage et passage dessines ; position cotee depuis le siege. |
| **02-26** | R4 cotes (coulisseau, poussoir), R1 et R1,5 cotes, note d'aretes cassees. |
| **02-27, 02-30** | Toutes les valeurs passent par `D.fmt`, sans point decimal. Seul « cert. 3.1 » reste ecrit ainsi : c'est la designation EN 10204, pas un nombre. |
| **02-33** | Renvois termines par une fleche (`renvoi(fin="fleche")`) et fleches de rayon. |
| **conc-37** | La phrase fausse « Le coin n est pas irreversible » est remplacee par « autobloquant seulement si mu > 0,106 : on n y compte pas », avec la marge a `VIS_MU_MIN`. La planche est coherente avec les 329 N de la planche 07. |

## Ecartes, avec la raison

- **Tolerance d'angle « 12 deg +/-0,15 » et controle au bleu** (02-05, second amendement). La tolerance generale ISO 2768-m suffit, et la tete bascule sur la pile Belleville (premier amendement). L'exigence utile, l'etat de la face de glissement, est portee : Ra 1,6, planeite 0,05.
- **Cote angulaire sur le coin** (conc-21, 02-05). Au coin bas du bout epais, l'arc couperait le renvoi M16 et l'attache de la cote alignee ; au bout mince, la reference tomberait dans la matiere. La pente est deja definie par 114,5, 55,2 et 30,8, et rappelee en note : « pente du dessous (12 deg, celle du coulisseau) ».
- **Hauteurs hors tout (61,2) / (36,9) en cotes auxiliaires** (02-06, 02-09, 02-29). La hauteur hors tout 61 figure dans le sous-titre (« fini 61 x 40 x 114,5 »). Elle se deduit aussi de 55,2 et des rebords de 3 (details). Une troisieme cote a gauche aurait encombre la zone de la cote 55,2 et du renvoi M16.
- **7,05 et 8,15 en cotes normales**. Avec 114,5 et 100,4, elles fermeraient la chaine. Elles sont donc donnees en auxiliaires, et la note dit que les logements sont centres.
- **Vue de bout du coin**. L'epaisseur 40 est dans le titre et le taraudage est « centre sur l epaisseur » dans le renvoi. Une vue de plus ne tenait pas sans serrer les details.
- **Cote 90 deg dans le detail C**. Un angle droit dessine est implicite (ISO), et « NORMALES a la pente » est ecrit. L'arc tombait sur la cote 3.
- **Taraudages de guide dans la vue de droite** (02-02 a 02-04, 02-12). En projection selon x, leurs traits caches (y +/-10 a +/-13) se superposent a l'alesage (+/-12,7). Ils sont definis par la vue de face (cercles, 12, 88) et par la vue de dessus (profondeurs).
- **Notes de conception retirees du plan** : « 7,8 mm au dessus des taraudages », « ne flechit pas, 5,2 MPa », « son epaisseur ne tient qu'aux guides… ». verifie() les controle, et leur place est dans SPEC. La note « dessous de la traverse fraise en paquet » appartient a la planche 03.
- **Correction de `draw._ligne_cote` / `cote_h` / `cote_v`, et `re.sub` dans `Sheet.text`** (02-10, 02-11, 02-24, 02-27, 02-30). Ces fonctions sont partagees : la planche 02 ne les appelle plus.
- **02-07 B (`POUSSOIR_GOUPILLE_TROU = 8.2`)** : remplace par D7 (8,3).
- **02-21** (remonter la vue, verser les textes en notes) et **02-31** (positions 278 / 283) : sans objet, la mise en page est refaite.
- **02-22, 02-01 et 02-09 pour leurs parties params / parts / nomenclature** : deja faites par MODELE et DOCUMENTS. NOMENCLATURE 02a dit M8, 02f dit « CHC M8 x 12 », le brut du coin est « plat 65 x 45, L 120 ».
- **02-26, aretes cassees 0,5 pour les pieces usinees** : aucun parametre n'existe. J'ai garde `CHANFREIN` (0,8) pour les trois pieces, plutot qu'une valeur en dur.

## Ce qui reste

1. **params.py** : l'alias transitoire `D_TARAUD` (l.588-591) n'a plus aucun lecteur. MODELE peut le supprimer.
2. **Appels B et C** : leurs cercles fins coupent les attaches fines voisines (100,4, 114,5, 16/30,8, cote alignee). C'est inevitable, toutes les faces des rebords portant une attache. Aucun texte ni aucune ligne de cote n'est touche.
3. **Litteraux de plan sans parametre** :
   - « +0,2/0 » (jeu des logements) ;
   - « planeite 0,05 », « Ra 1,6 » ;
   - les constantes ISO 2904 du Tr16x4 (pas 4, d2 14, flanc 15) ;
   - la pointe de foret a 118 deg ;
   - le coefficient ISO 724 du fond de filet.
4. **Planche 04** : le patin de charge doit montrer ses trous 8 H7 a l'entraxe 70, que la note 02b cite. C'est a l'agent de la planche 04.
5. **A trancher par l'utilisateur, si souhaite** : une tolerance d'angle propre (12 deg) sur coin et coulisseau, et la valeur d'arete cassee des pieces usinees (0,5 ou 0,8).

## Controles (etat final)

| controle | resultat |
|---|---|
| `python plans.py` | sans erreur |
| `python verif_plans.py` | 0 faute sur les 8 planches (650 textes) |
| `python params.py` | 0 probleme |
| `python verif_percages.py` | 0 faute |
| `chk01.py 02_coulisseau`, tous traits fins compris | 0 remarque (75 textes, 1321 traits) |
| SVG 00, 01, 03 a 07 et draw.py | identiques a la copie temoin |
| plans.py hors du bloc | identique |

Relecture finale du rendu, decoupe par decoupe :
- planche entiere ;
- titres ;
- vue de droite et vue de face ;
- cercle de taraudage (x2,5) ;
- vue de dessus, avec ses renvois et le coin droit ;
- coin (bout epais, bout mince et appels) ;
- details B et C ;
- poussoir ;
- notes et cartouche.

Resultat :
- aucun texte n'est traverse ;
- les lignes de cote paralleles sont a 7 mm ;
- les cotes sont hors des pieces ;
- les echelles sont vraies et annoncees (1:1 dans chaque titre, 4:1 aux details).
