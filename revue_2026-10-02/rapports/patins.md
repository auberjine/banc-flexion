# Planche 04_patins : compte rendu de l'agent PATINS (02/10/2026)

## Fichiers touches

- `plans.py` : seulement le bloc de la planche 04. Il va du bandeau `# ==== pieces collees` jusqu'au bandeau `# ==== pied` (exclu), et contient `plan_patins()` et trois aides locales prefixees `p04_` : `p04_ligne`, `p04_poly` et `p04_titre`. Avant et apres le bloc, plans.py est identique a l'octet pres a la copie temoin (`correction/patins/temoin/plans.py`). Le fichier reste en LF et en ASCII.
- `draw.py` : **non modifie**. La planche utilise les ajouts ISO de l'agent ASSEMBLAGE (`cote_hx`, `cote_vx`, `renvoi`, `zone`, `trace_coupe`, `Sheet.motif`) et `View.rayon`. Elle n'appelle plus `cote_h`, `cote_v` ni `note`.
- SVG 00 a 03 et 05 a 07 : identiques a l'octet pres a ceux d'avant mon travail.
- Outils, dans `scratchpad/correction/patins/` :
  - `p04_new.py`, la source du bloc, et `splice.py` ;
  - `run.sh`, qui enchaine splice, plans, verif_plans, params, `../flanc/chk01.py 04_patins` (tous traits, fins compris), `../traverse/chk_croix.py 04_patins`, la comparaison des autres SVG et le rendu ;
  - `crop.py` (echelle reelle du rendu : 7,559 px/mm, et non 7,619) et les decoupes (`r*`, `z_*`, `f_*`, `g_*`, `final_full.png`) ;
  - `bac/`, une copie du projet avec EP_TOLE_REELLE = 8,25 pour l'essai de robustesse.

## Nouvelle mise en page

Le cartouche est construit a partir des PartSpec (`P.all_parts()`) et des reperes `nomenclature.REPERES` :
- matiere « S355JR / S235 » ;
- brut « tole 10 mm / feuillard 20 x 2 ». Si les deux patins n'ont plus la meme epaisseur, les deux bruts s'affichent ;
- quantite « 4 + 1 + 2 (04a, 04b, 04c) » ;
- echelle « 1:1 - coupe 5:1 - 04c 1:5 ».

Indice A et date du 02/10/2026 viennent de draw.py.

**04a PATIN D APPUI RAINURE, VUE DE DESSOUS (1:1)**. Sous-titre : « S355JR, 4 ex., brut tole 10 mm ».
- Contour lu dans `P.patin_appui_profile()`.
- Les deux aretes de la rainure sont en trait fort sur toute la longueur : elle est debouchante.
- Axe longitudinal, a 3 mm du contour.
- Cotes **90** et **20**, attachees aux angles vifs fictifs. Leurs lignes d'attache ne se croisent plus.
- **4 x R3** (`PATIN_R`).
- Trace de coupe A-A (ISO 128-44) a x = +25, hors du texte « 90 » : bouts epais, fleches et lettres.

**COUPE A-A (5:1)**, avec le sous-titre « face collee en haut, rainure cote bossage ». Il s'agit d'une coupe TRANSVERSALE : profil en U renverse, ouvert sur la face d'appui, hachure a 45 deg.
- **10** a droite.
- **9,5** sous la rainure. Le texte vient de `P.fr(RAINURE_B, 2)`, si bien qu'une tole de 8,25 affiche 9,75 et non 9,8.
- **1,5** dans le vide de la rainure, contre le flanc gauche. Fleches dehors, texte a gauche de la ligne, lisible. Les hachures sont interrompues autour de la queue haute de la cote, qui entre dans la matiere.
- Axe de symetrie : la rainure est centree.

**04b PATIN DE CHARGE, epaisseur 10 (1:1)**. Sous-titre : « S355JR, 1 ex., brut tole 10 mm ».
- Profil FINI (`P.patin_charge_profile()`), avec ses deux trous de 8.
- Axes a 3 mm du contour (+/-50 + 3, au lieu de +/-58). Petits axes verticaux sur les trous.
- Entraxe **70** au-dessus de la piece. Ses lignes d'attache prolongent les axes des trous.
- **100** dessous et **100** a gauche, attaches aux angles vifs fictifs.
- **4 x R6** (`PATIN_CHARGE_R`).
- Renvoi a fleche sur un trou : « 2 x diam. 8 H7 / perces-aleses ».

**04c PLAT DE RENFORT (1:5)**. Sous-titre : « S235, 2 ex., piece du commerce : feuillard 20 x 2 coupe a longueur, angles vifs ; pas de DXF ».
- Contour lu dans `P.plat_profile()` (`PLAT_R = 0`).
- Cote **840**.
- Sous la vue : « colles sous la poutrelle, un dans l axe de chaque flanc : entraxe 68, centres sur la poutrelle, bord exterieur a 7,5 du bord de la poutrelle (planche 00, coupe A-A) ». Les valeurs 68 et 7,5 sont calculees depuis Y_FLANC et POUTRE_B. Le « +/- 35 » faux a disparu.

**Notes au-dessus du cartouche** (9 lignes, toutes calculees) :
1. Aretes vives des patins cassees 0,8 x 45 deg (`spec.chanfrein`) ; plat ebavure.
2. 04a : decoupe laser d'apres patin_appui.dxf (calque DECOUPE), PUIS rainure fraisee sur toute la longueur de la face d'appui.
3. 04a : rainure 9,5 = tole REELLE du flanc (EP_TOLE_REELLE = 8) + 2 x 0,75 de jeu. Mesurer la tole livree et regenerer ce plan (D2, D5).
4. 04a : le fond de rainure porte le bossage, 3 kN par appui. Hertz 339 MPa, limite 480 MPa a 150 C, coefficient 1,42 : S355JR au minimum (D3, `hertz_appui`, `HERTZ_LIM`, `hertz_coef`).
5. 04b : decoupe d'apres patin_charge.dxf, avant-trous 6. PERCER puis ALESER les 2 trous 8 H7, ou les goupilles V3 (8 m6) sont serrees (D7 ; V3 est lu dans `nomenclature.visserie()`).
6. Collage, renvoi a l'ordre de montage par `nomenclature.ETAPE` : 04c etape 1, 04b etape 9, 04a etape 13 ; polymerisation sous la precharge (etape 16).
7. 04a : colle par sa face superieure seulement, rainure SECHE sur le bossage (balancier).
8. Surfaces a coller : P80, acetone ; colle Duralco 4420, post-cuisson.
9. Un jeu neuf par eprouvette : 4 x 04a, 1 x 04b et ses 2 goupilles V3, 2 x 04c (conc-56).

## Constats appliques

| constat | ce qui est fait |
|---|---|
| **04-01, 04-12, conc-16, docu-04** (trous de goupille absents) | Trous dessines d'apres le profil fini ; entraxe 70 cote ; « 2 x diam. 8 H7 perces-aleses » ; note avant-trous 6 / percer-aleser (D7). La « cire » n'est pas reprise (amendement). |
| **04-02, 04-04, 04-11, conc-04, conc-20, docu-03** (« 10,6 » en dur) | Plus aucune valeur en dur : la cote et la note lisent RAINURE_B (9,5, D2). La largeur suit EP_TOLE_REELLE (essai a 8,25 : 9,75 partout). |
| **04-03, 04-05, 04-16** (coupe fausse, sans trace ni hachure) | Coupe transversale en U ouvert, hachuree, a 5:1 (echelle normalisee) ; trace A-A sur la vue de dessous, fleches dans le bon sens (`trace_coupe`). |
| **04-06, 04-15** (« 1,5 » illisible et accroche dans le vide) | Cote prise sur le flanc de la rainure, dans le vide, a 5:1 : 7,5 mm de feuille, texte libre, hachures interrompues. |
| **04-07, 04-13, conc-05, conc-19, docu-05** (cartouche « tole 8 mm ») | Brut lu dans les PartSpec : « tole 10 mm / feuillard 20 x 2 ». « epaisseur 10 » et la section du plat viennent de params. |
| **04-08, 04-22** (« y = +/- 35 », doublon « longueur 840 ») | Position du plat : entraxe 68 et bord a 7,5, calcules. La longueur n'est plus ecrite en texte, la cote 840 suffit. |
| **04-09, 04-14** (texte des cotes verticales barre) | `cote_vx` : texte a gauche de la ligne (ISO 129-1). chk01 en marge 0 : aucune remarque. |
| **04-17, 04-19** (axes trop longs) | Axes a 3 mm au-dela du contour sur les deux patins. Ils ne touchent plus aucun texte. |
| **04-18, 04-21** (rayons non cotes) | 4 x R3 et 4 x R6, lus dans `PATIN_R` et `PATIN_CHARGE_R`. Plat a angles vifs (`PLAT_R = 0`, D10), ecrit dans le sous-titre. |
| **04-20** (titre de coupe colle a la vue du dessus) | 15 mm entre la cote 90 et le titre de la coupe ; sous-titre d'orientation. |
| **04-23, docu-13** (reperes absents des titres) | Titres « 04a / 04b / 04c », avec quantite, lus dans `nomenclature.REPERES`. |
| **conc-51, D10** (plat a la fois achete et decoupe) | Le plan dit « piece du commerce ... ; pas de DXF ». Le modele (achete=True) a ete corrige par MODELE. |
| **conc-56** (un jeu par eprouvette) | Note 9. |
| **D3** | Note 4 : Hertz, limite et coefficient publies sur la planche du patin, qui est le corps limitant. |

Les constats « non_verifie » de conception.json et documents.json (conc-04, 05, 16, 19, 20, 51, 56, docu-03, 04, 05, 13) ont ete controles sur le code et le rendu d'avant correction, et tous etaient exacts :
- texte « 10,6 » en dur, alors que la rainure etait tracee a 11,5 ;
- cartouche « tole 8 mm » (EP_FLANC), pour des patins de 10 ;
- plat place a « +/- 35 », alors que Y_FLANC = 34 ;
- trous jetes (`outer2, _`) ;
- aucun repere dans les titres.

## Ecartes, avec la raison

- **04-10** (tolerances +0,2/0 et +/-0,1, Ra 3,2, planeite 0,05 au fond de rainure) : rejete par les verificateurs, et je suis d'accord.
  - Avec 0,75 de jeu par cote, l'ISO 2768-m du cartouche suffit.
  - Le patin est colle en place sous precharge, et la colle rattrape la hauteur.
  - Le scenario de bavure sur le conge R10 est physiquement impossible.
  - Seule l'arete cassee generale est reprise (note 1).
- **Correction de `draw._ligne_cote`, `cote_h`, `cote_v`** (04-06, 04-09, 04-14, 04-15) : non faite. Ce sont des fonctions partagees, et mon mandat sur draw.py se limite a des ajouts. La planche 04 ne les appelle plus.
- **Coupe a 2:1 ou 4:1** (04-03, 04-05, 04-20) :
  - 4:1 n'est pas une echelle normalisee ;
  - a 2:1, la profondeur ne ferait que 3 mm de feuille ;
  - 5:1 tient sans rien deplacer.
- **Cote 20 repetee dans la coupe** (04-03) : elle est sur la vue de dessous, avec tout le contour decoupe. La repeter ferait une cote en double.
- **Cote 20 de la section du plat, et mention « longueur 840 »** (04-22) : la section est donnee par la designation du feuillard du commerce, et la longueur par la cote. Pas de doublon.
- **Cote 70 centree sous les trous, et note de trou placee sur la cote verticale** (04-12, propositions) : remplacees par l'entraxe 70 AU-DESSUS de la piece, avec pour attaches les axes des trous. Le renvoi va vers la droite et la cote 100 verticale passe a gauche : aucun croisement.
- **Croquis de pose du plat sous la poutrelle** : non ajoute. La planche 00 (coupe A-A, 1:2) le montre deja, avec l'entraxe 68, et la note y renvoie.
- **Retrait des trous du DXF du patin de charge, pointage grave** (04-12, amendement) : remplace par D7. Le DXF garde des avant-trous de 6, ce qui est fait par MODELE.
- **Corrections de params.py, parts.py, nomenclature.py, SPEC, SUITE et des commentaires** (04-02, 04-08, 04-11, 04-18, 04-21, 04-22) : deja faites par MODELE et DOCUMENTS, ou hors de mon perimetre.
- **Planche 02** (trous de passage 8,3 du poussoir, cote 70) : hors perimetre. COULISSEAU l'a fait.

## Ce qui reste

1. **Litteraux de plan sans parametre** :
   - « Duralco 4420 », « P80 », « acetone » (meme texte que spec.py et nomenclature.py) ;
   - « 150 C » ;
   - « planche 00, coupe A-A » (renvoi a la planche d'ensemble).
2. **Precharge de collage** : la valeur 0,5 kN n'a pas de parametre (elle est en dur dans parts.py et nomenclature.py). La planche renvoie donc a l'etape « precharge » de l'ordre de montage sans ecrire la valeur.
3. **Hertz** : `hertz_largeur()` utilise EP_FLANC nominal, pas EP_TOLE_REELLE. C'est sans consequence aujourd'hui, mais a savoir si l'on regle une tole reelle.
4. **draw.py** : `_ligne_cote`, `cote_h` et `cote_v` restent defectueux pour les planches qui les appellent encore (05 a 07). Ces planches sont confiees a d'autres agents.

## Controles (etat final)

| controle | resultat |
|---|---|
| `python plans.py` | sans erreur |
| `python verif_plans.py` | 0 faute sur les 8 planches (676 textes, 50 sur la 04) |
| `python params.py` | 0 probleme |
| `python verif_percages.py` | 0 faute |
| `chk01.py 04_patins`, marge 0, tous traits | 0 remarque (50 textes, 363 traits) |
| `chk_croix.py 04_patins` | 5 croisements, tous voulus : centres des deux patins, deux centres de trous, trace A-A sur l'axe, et une attache de la cote 1,5 qui depasse de 2 mm sa propre ligne prolongee (ISO 129) |
| SVG 00 a 03, 05 a 07, et draw.py | identiques a la copie temoin |
| plans.py hors du bloc | identique |
| essai EP_TOLE_REELLE = 8,25 (copie `bac/`) | rainure 9,75 sur la cote et dans la note, 0 faute |
| `rend.sh` | planche rendue dans `scratchpad/planches/04_patins.png` |

Relecture finale du rendu, decoupe par decoupe :
- planche entiere ;
- 04a, haut (titre, trace A, R3) puis bas (trace A, cote 90) ;
- coupe A-A, puis zoom x2 sur la cote 1,5 et la rainure ;
- 04b, haut (titre, 70, R6), renvoi des trous, gauche et bas (cotes 100) ;
- 04c ;
- notes ;
- cartouche.

Resultat :
- aucun texte n'est traverse ;
- aucune ligne d'attache ne croise un texte ou une autre cote ;
- les cotes sont hors des pieces (la 1,5 est dans le vide de la rainure) ;
- les echelles sont vraies et annoncees : 1:1, 5:1 et 1:5 dans les titres et au cartouche ;
- le cartouche est juste (matiere, brut, quantites, echelle).
