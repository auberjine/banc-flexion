# Planche 07_chape : compte rendu de l'agent CHAPE (02/10/2026)

## Fichiers touchés

- `plans.py` : seulement le bloc de la planche 07, qui va du bandeau `# ==== chape` jusqu'au bandeau `# ==== assemblage` (exclu).
  - Avant mon travail, ce bloc allait de `def support_moment():` à `support_fleche()` inclus.
  - Le diff contre la copie témoin (`correction/chape/temoin/plans.py`) se limite aux lignes 1732 à 1863 d'origine.
  - Le fichier reste en LF et en ASCII.
- Contenu du bloc : la nouvelle `plan_chape()` et des aides locales préfixées `c07_` (`c07_titre`, `c07_ligne`, `c07_rect`, `c07_d3`, `c07_filet`, `c07_arc_pres`, `c07_sommet_fictif`, `c07_court`, `c07_min`, `c07_dec`).
- S'y ajoutent les constantes de norme `C07_M10_K`, `C07_M10_S`, `C07_M10_RONDELLE_D`, `C07_M10_PAS` et `C07_K_COUPLE`, toutes commentées avec leur norme.
- `support_moment`, `support_sigma`, `support_sigma_tube` et `support_fleche` sont supprimées. Elles ne servaient qu'à cette planche (grep sur tout le projet) et sont remplacées par `p.platine_contrainte()`.
- `draw.py` : **non modifié**. La planche utilise les ajouts ISO déjà présents (`cote_hx`, `cote_vx`, `bulle`, `zone`, `rupture`, `renvoi`, `Sheet.motif`) ainsi que `rayon`, `axe` et `D.table`. Elle n'appelle plus `cote_h`, `cote_v` ni `note`.
- SVG 00 à 06 : identiques à l'octet près à ceux d'avant mon travail.
- Outils, dans `scratchpad/correction/chape/` :
  - `c07_new.py`, la source du bloc ;
  - `splice.py` et `run.sh` (splice, plans, verif_plans, params, chk01, chk_croix, comparaison des autres SVG et de draw.py, rendu) ;
  - `robust.py`, avec `chk07.py` et `croix07.py` (chk01 et chk_croix acceptant un chemin) ;
  - `crop.py`, `temoin/` et les découpes (`avant_full.png`, `r3_full.png`, `k*.png`).

## Nouvelle planche (tout au 1:1)

**Cartouche**, entièrement calculé :
- titre « PLATINE ET ENTRETOISE DE BUTEE » (30 caractères, il tient dans sa case) ;
- rep. 07 ;
- matière « 42CrMo4 +A, Re >= 430 / E235+C » ;
- brut « tole 8 cert.3.1 / tube 20 x 4,5 » ;
- quantité « 2 + 2 (07, 07b) » ;
- échelle « 1:1 » (vraie et normalisée ; l'ancien « montage 0,8:1 » est supprimé) ;
- indice A et date du 02/10/2026, qui viennent de draw.py.

La case brut ne peut pas contenir tout BRUT_TOLE suivi du tube : verif_plans compte 0,55 h par caractère, ce qui limite la case à 31 caractères. L'exigence D4 est donc répartie :
- « Re >= 430 » dans la case matière ;
- « cert.3.1 » dans la case brut ;
- BRUT_TOLE en entier sous le titre de la vue 07 ;
- EXIGENCE_TOLE en entier dans la note 1.

**07 PLATINE DE BUTEE (1:1)**. Sous-titre : « 42CrMo4 +A, 2 ex. identiques, empilees » et « brut tole 8 mm, cert. 3.1, Re >= 430 ». La vue porte :
- le contour et les trous ;
- les axes, qui ne dépassent que de 3 mm ;
- les arêtes fictives marquées selon ISO 129-1 aux quatre points d'où partent des cotes : les deux coins de droite, le coin bas gauche et les deux sommets ;
- **140** : attaches issues des coins fictifs, à l'extérieur ;
- **104** : sous le 140, plus près de la pièce, les axes des trous servant d'attaches ;
- **40** : à droite, à 10 mm ;
- **70** entre les sommets fictifs (voir « écartés ») ;
- **4 x R8** et **2 x R12** ;
- **diam. 18** et **2 x diam. 11**, par des lignes de repère radiales fléchées dont les textes sont alignés en haut à gauche.

**MONTAGE DE LA CHAPE, COUPE PAR LES AXES (1:1)**. C'est une coupe par le plan horizontal qui contient la tige et les deux V9, vue de dessus, butée en haut. Sous-titres :
- « coin et tete de charge non representes » ;
- « jeu des V9 dans leurs trous non represente (trous de 11, vis de 10) ».

Ce que montre la coupe :
- Hachurés, avec trois motifs différents : les flancs (rompus à 6 mm au-delà des platines, fente du coin et trous ouverts), les entretoises 06b et 07b coupées en long, et les deux platines séparées.
- Non coupées (ISO 128-50), et seulement leurs parties vues :
  - la tige M16, de VIS_Y0 à Y_BOUT_VIS, avec le fond de filet en trait fin ;
  - les 2 écrous HM V8, séparés ;
  - les 2 rondelles AS V5 ;
  - la butée V6 (AS + cage + AS) ;
  - la tête V7, écrou H puis écrou HM ;
  - les V9 : tête, rondelle, **3 rondelles** sous l'écrou (D6), écrou, et bout fileté vu de 20,5.

Le dessin est entièrement paramétré.

Cotes du montage :
- **71,5 +/-0,2**, la longueur de 07b (D11). C'est la seule cote de cette pièce, d'où l'absence de vue propre pour 07b ;
- **4,5**, le calage de la tête V7 sur le bout de tige (ordre de montage).

Les dix bulles (01, 06b, 07b, 07, 02d, V5 à V9) renvoient au tableau « Pieces du montage » (rep., désignation, qté). Les repères et quantités viennent de `nomenclature.REPERES`, de `visserie()` et des PartSpec. Les désignations de V5, V6 et V8 sont celles de la nomenclature.

**Notes** (8 lignes, toutes calculées, virgule décimale partout) :
1. EXIGENCE_TOLE.
2. Découpe laser, arêtes cassées 0,8 ; 40 et 70 entre arêtes fictives : au sommet R12, la tôle mesure 69,46.
3. 07b : tube EN 10305-1, coupé à la longueur cotée, les 2 à la même butée, faces dressées.
4. Trajet d'effort : le coin tire la tige, la tête V7 pousse la butée ; les V9 voient 329 N au desserrage.
5. Platine : 130 MPa, coefficient 3,3 à 20 C et 3,0 à 150 C, flèche 0,14 mm.
6. 07b : 12,6 MPa chacune sous la commande, environ 92 avec la précharge des V9 (35 N.m, K = 0,2).
7. V9 : empilement, écrou sur le filet (marge 3,5), 35 N.m.
8. V8 : jeu 0,1 à 0,3 puis contre-blocage. V7 : douille de 24 et cliquet.

## Constats appliqués

Tous les constats de la 07 étaient « non vérifiés ». Je les ai contrôlés sur le SVG et le code d'origine : tous étaient exacts sur le défaut décrit.

| constat | ce qui est fait |
|---|---|
| 07-01, 07-02, 07-13 | Arêtes fictives marquées. La hauteur réelle de 69,46 au sommet est en note, calculée sur le profil. 4 x R8 et 2 x R12 sont cotés (SUPPORT_R_COIN et SUPPORT_R_CONGE, lus sur les arcs du profil). Les attaches du 140 partent des coins et celles du 70 des sommets. |
| 07-03, 07-05 | Cotes passées à cote_vx : le texte d'une cote verticale est à gauche de sa ligne et n'est plus barré. draw.py est inchangé. |
| 07-06 | La cote 40 n'est plus collée au cadre : elle est à 10 mm du bout droit et loin du cadre. L'axe s'arrête 3 mm après la pièce. |
| 07-07 | Les attaches du 70 partent des sommets fictifs. |
| 07-08, 07-09 | 104 est près de la pièce, 140 à l'extérieur, à 8 mm l'une de l'autre. L'axe vertical s'arrête 3 mm sous le sommet, à plus de 2 mm du texte 104. |
| 07-04, 07-22, conc-19, conc-06 (part 07) | Cartouche « 2 + 2 (07, 07b) », matière et brut des deux pièces, repère 07b dans les bulles et le tableau. Échelle 1:1 partout. |
| 07-10, 07-11, 07-14, 07-19 | Les repères en texte, qui croisaient cotes et traits, sont remplacés par des bulles et un tableau. chk01 et chk_croix le confirment. |
| 07-12, 07-15, 07-18 | La montage est redessiné en coupe : parties vues seulement, deux écrous HM séparés, tige jusqu'à 155 (4,5 au-delà de V7), bout fileté des V9 vu en trait fort, axes de bonne longueur, tête V7 repérée. |
| 07-16, 07-21, conc-36 | La planche utilise `p.platine_contrainte()` : coefficient à 20 C et à 150 C, 12,6 MPa PAR tube, ordre de grandeur avec précharge. Virgule décimale partout. |
| 07-17, conc-29, D6 | 3 rondelles sous l'écrou des V9, dessinées et comptées (« + 4 rondelles »), marge de filet 3,5 en note. |
| 07-20 | Les attaches du 71,5 partent de la face du flanc et du bout des platines. |
| D11, conc-47 | « 71,5 +/-0,2 » (SUPPORT_TUBE_TOL), E235+C EN 10305-1, faces dressées. |
| conc-52 | Note « douille de 24 et cliquet, une cle plate bute sur les V9 ». |
| docu-13, conc-54 | Sous-repères dans le titre de vue (07), les bulles et le tableau. 02e n'apparaît pas ici. |

## Écartés, avec la raison

- **Correction de `draw._ligne_cote` (07-03, 07-05)** : non faite. C'est une fonction partagée. Aucune planche ne l'appelle plus (vérifié par grep sur plans.py).
- **Cote 70 à l'extérieur (07-01, 07-07)** : écartée.
  - À droite ou à gauche, ses attaches horizontales (aux sommets, de x = 0 au-delà du bout) couperaient forcément l'attache du 140 (x = ±70) et l'axe du trou qui sert d'attache au 104. Ce n'est évitable dans aucun placement.
  - La ligne de cote est donc entre l'alésage et le trou de droite (x = 27,75, calculé). Ses attaches sont courtes et l'axe de symétrie s'interrompt pour la laisser passer.
  - Le texte est dans la pièce, dans une zone vide.
- **« 70 (sommets fictifs) », « 40 (fictif) » dans le texte de cote (07-01)** : remplacés par le marquage ISO des arêtes fictives et par la note 2.
- **Vue propre pour 07b** : non dessinée.
  - À 1:1, « diam. 11 » (11,5 mm) ne tient pas entre ses attaches de 11.
  - À 2:1, la vue ne laisse plus de place au tableau.
  - La seule cote de fabrication, 71,5 +/-0,2, est portée sur la coupe du montage. Les diamètres sont ceux du brut « tube de precision 20 x 4,5 » (sous-titre, tableau, note 3).
- **« les deux égales à 0,1 près » (07-04)** : pas de nouvelle tolérance chiffrée, puisque D11 fixe ±0,2. La note demande « les 2 a la meme butee », ce qui donne deux longueurs égales sans coût.
- **Cotes 60 et 71,5 dans le montage en plus des vues de pièce** : le 60 appartient à 06b (planche 06) et n'est pas répété. Le 71,5 n'est porté qu'une fois.
- **Libellés en texte du montage (07-10, 07-11, 07-14, 07-19)** : les déplacements proposés sont remplacés par des bulles. Celles des pièces de bord sont en colonne à gauche, celles de l'axe dans les vides du montage.
- **Trait de début de filet des V9 (07-18)** : supprimé. Il tombe sous les rondelles, donc il est caché.

## Ce qui reste

1. **Croisements résiduels signalés par chk_croix (5)**, tous voulus :
   - trois croix d'axes aux centres de l'alésage et des trous ;
   - la ligne d'attache et la ligne de cote du 4,5. C'est une cote courte à flèches extérieures, dont les attaches dépassent la ligne prolongée, ce qui est normal en ISO 129.
2. **Jeu des V9 non représenté dans le montage** : trous et alésages de tube y sont dessinés à 10 au lieu de 11, ce que le sous-titre annonce. Le jeu réel de 0,5 donnait deux traits forts confondus. Le jeu de la tige dans l'alésage de 18 est conservé.
3. **« 0,1 a 0,3 » de jeu axial des V8, « AS 1730 » et « AXK 1730 »** n'ont pas de paramètre. Ils sont écrits comme dans nomenclature.py (les désignations V5, V6 et V8 du tableau y sont même lues).
4. **K = 0,2** (couple → précharge) est une constante locale `C07_K_COUPLE`. Si la précharge doit servir ailleurs, il faudra en faire un paramètre de params.py.
5. **draw.py** : `cote_h`, `cote_v`, `note` et `_ligne_cote` ne sont plus appelées par aucune planche. On peut les corriger ou les retirer.
6. **params.py** : `D_TARAUD` n'est plus lu par plans.py (grep) ; l'alias transitoire peut être supprimé (hors de mon périmètre).
7. out/plans/plans.pdf n'est pas régénéré par plans.py.

## Contrôles (état final)

| contrôle | résultat |
|---|---|
| `python plans.py` | sans erreur |
| `python verif_plans.py` | 0 faute sur les 8 planches (777 textes, 84 sur la 07), complétude bonne |
| `python params.py` | 0 problème |
| `python verif_percages.py` | 0 faute |
| `chk01.py 07_chape 0.25` (tous les traits, fins compris, contre tous les textes) | 0 remarque (84 textes, 1105 traits) |
| `chk_croix.py 07_chape` | 5 croisements, tous voulus (voir « reste » 1) |
| SVG 00 à 06 et draw.py | identiques à la copie témoin |
| plans.py hors du bloc | identique au témoin, LF, ASCII |
| motifs de hachures | noms uniques dans plans.html (c07_hf, c07_ht, c07_hp) |
| robustesse (`robust.py`, en mémoire) | 0 faute verif_plans, 0 remarque chk01, mêmes 5 croisements dans chaque cas : nominal, 4 rondelles sous l'écrou, tôle réelle 8,2, B 76 / bout 44, entraxe 96, R12 → 15 et R8 → 6 |
| rendu | `scratchpad/planches/07_chape.png` |

Relecture finale du rendu, découpe par découpe :
- planche entière ;
- titre et haut du montage ;
- butée, écrous et bulles du centre ;
- bas du montage avec les flancs et les têtes des V9 ;
- côté droit et cote 71,5 ;
- platine entière, puis zooms ×2 sur les quatre coins et sur les repères du haut ;
- tableau, notes, cartouche.

Résultat :
- aucun texte n'est traversé ;
- aucune attache ne croise une autre cote ou un texte ;
- les lignes de cote parallèles sont à 8 mm ;
- les cotes sont hors de la pièce, sauf le 70, pour la raison donnée plus haut.
