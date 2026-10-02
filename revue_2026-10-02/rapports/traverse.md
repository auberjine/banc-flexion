# Planche 03_traverse : compte rendu de l'agent TRAVERSE (02/10/2026)

## Fichiers touches

- `plans.py` : seulement le bloc de la planche 03. Il va de `# Aides de la planche 03 (02/10/2026)` jusqu'au bandeau `# ==== pieces collees`, et contient `plan_traverse()` et ses aides locales prefixees `t03_` :
  - `t03_ligne`, `t03_axe`, `t03_chemin`, `t03_decoupe` ;
  - `t03_appel`, `t03_rayon_trou`, `t03_titre` ;
  - les constantes `T03_MIXTE2` (trait mixte a deux tirets, piece voisine, meme motif que A00_MIXTE2) et `T03_TOL_TENON` (0,1).
  Avant et apres le bloc, plans.py est identique a l'octet pres a la copie temoin (`correction/traverse/temoin/plans.py`). Il reste en LF et en ASCII.
- `draw.py` : **non modifie**. La planche utilise les ajouts ISO de l'agent ASSEMBLAGE (`cote_hx`, `cote_vx`, `renvoi`, `rupture`). Elle n'appelle plus `cote_h`, `cote_v` ni `note`.
- SVG 00, 01, 02 et 04 a 07 : identiques a l'octet pres a ceux d'avant mon travail.
- Outils, dans `scratchpad/correction/traverse/` :
  - `t03_new.py`, la source du bloc, et `splice.py` ;
  - `run.sh`, qui enchaine splice, plans, verif_plans, params, `../flanc/chk01.py 03_traverse` (tous traits, fins compris) et le rendu ;
  - `chk_croix.py`, qui liste les croisements entre traits fins : attaches, lignes de cote, renvois, axes ;
  - `crop.py` et les decoupes (`v1_*`, `v2_*`, `f_*`), avec `avant_full.png` et `apres_full.png`.

## Nouvelle mise en page

**03 Plaque de traverse, vue selon x (2:1)** (l'ancienne vue etait a 1:1). Titre et echelle dans le titre. Sous-titre : « ep. 8, 6 plaques identiques serrees en paquet ». Contour fini lu dans `P.traverse_profile()`.

Cotes, toutes par `cote_hx` / `cote_vx`, attachees aux angles vifs fictifs des aretes. Aucune ne croise une autre :
- en haut :
  - **59,6** entre epaulements (`TRAVERSE_JEU_Y`), attaches sur les flancs de la coiffe ;
  - **80** entre bouts de tenon, a 8 mm au-dessus ;
- **6** : coiffe, dans le creux au-dessus du tenon droit ;
- a droite, chaine alignee sur une seule ligne : **(38)** auxiliaire, puis **20 +/-0,1** pour le tenon ; a 8 mm au-dela, **58**, la cote fonctionnelle, du chant fraise aux faces HAUTES (portantes) des tenons ;
- a gauche : **19**, hauteur du trou du tirant. La ligne de rappel haute est l'axe du trou prolonge ;
- renvois a fleche :
  - « diam. 11 : passage du tirant V2 », radial, qui sort par le chant ;
  - « chant FRAISE EN PAQUET : plan de glissement », pose sur le chant ;
- appel A, cercle fin, sur le pied de tenon bas droit ;
- axe de symetrie et axe du trou, raccourcis : 3 mm au-dela du contour.

**Mortaise du flanc (rep. 01) et paquet de tenons, vue selon y (2:1)** :
- sous-titre « vue de reference : la mortaise est definie planche 01 (tableau DECOUPES INTERIEURES) » ;
- mortaise lue dans `P.flanc_mortaise()`, donc sur la tole REELLE ;
- 7 limites de tenons en trait mixte fin a deux tirets (piece voisine), tirees de `TRAVERSE_LX_REEL` et `EP_TOLE_REELLE` ;
- axe reduit a deux amorces hors de la mortaise ;
- cotes auxiliaires **(52)** et **(20,4)** et rayon **(4 x R2)**, fleche posee de l'exterieur ;
- renvoi a point « 6 tenons jointifs : 6 x tole reelle » ;
- note « Largeur = 6 x tole REELLE + 2 x R2 (EP_TOLE_REELLE) : l arete droite porte sur toute la largeur du paquet ».

Essai sur une copie (`correction/traverse/bac`) avec EP_TOLE_REELLE = 8,25 : la cote passe a (53,5), sans retouche et avec 0 faute.

**DETAIL A (10:1), pied de tenon, 4 par plaque** :
- contour reel decoupe dans le profil fini (`t03_decoupe`), bords de vue en traits de rupture fins ;
- angle vif fictif en traits fins ;
- cote **1,5** (`TRAVERSE_R_PIED`) ;
- note : « poche carree tournee a 45 deg, centree sur l angle vif fictif : 3 traits droits, jamais un conge (il deborderait de l epaulement) ».

**Cartouche** :
- matiere `spec.material` (42CrMo4 +A) ;
- brut `spec.stock` (tole 8 mm, cert. 3.1, Re >= 430) ;
- quantite « 6 plaques identiques » ;
- echelle « 2:1 - detail 10:1 ».

Indice A et date du 02/10/2026 viennent de draw.py.

**Notes au-dessus du cartouche** (9 lignes, toutes calculees) :
1. `EXIGENCE_TOLE` (D4).
2. Decoupe d'apres traverse.dxf, calque DECOUPE : le DXF est le BRUT, chant du bas descendu de 1 (65 de haut au lieu de 64) (D8).
3. Fraisage en paquet serre sur le tirant V2 : paquet retourne sur les faces HAUTES des 12 tenons, 2 cales de plus de 6 (la coiffe passe entre), fraise a 58 de ces faces.
4. Chant fraise : planeite 0,05 sur le paquet, Ra 1,6 ; plan de glissement de la plaque de bronze 06c.
5. Aretes cassees 0,8 x 45 sur les deux faces APRES le fraisage (rainure en V de 1,6, reserve de graisse), puis paquet resserre sur V2, chants fraises sur un marbre.
6. Angles non cotes R2. La valeur est lue sur le contour ; les pieds de tenon renvoient au detail A.
7. Les tenons portent par leur face HAUTE sur l'arete superieure de la mortaise : pas de vis.

**Bloc de calcul et montage**, en bas a gauche. Toutes les valeurs viennent de params :
- matage 26,5 MPa sur 38,4 x 5,9 par flanc (`appui_tenon`, `matage_tenon`) ;
- racine de tenon 11,5 MPa sur 17 nets (`flexion_tenon`) ;
- plaque 7,6 MPa, majorant (`flexion_traverse`, 64 percee de 11, appuis a 68,5) ;
- bronze 06c 7,7 MPa sur 30 nets, 5 joints dans ses 38 (`pressions_plaquettes`, `portee_coin`) ;
- Re a 150 C : 390 MPa ;
- MONTAGE, coherent avec l'etape 7 de NOMENCLATURE.md.

## Constats appliques

| constat | ce qui est fait |
|---|---|
| **03-01, 03-03, 03-16** (texte barre par sa ligne de cote, attaches arretees avant la ligne) | La planche passe par `cote_hx` / `cote_vx` : texte a gauche des cotes verticales, attaches qui depassent de 2 mm. chk01 (marge 0, tous traits) : 0 remarque. |
| **03-02, 03-28** (axe de mortaise a travers « 52 ») | Axe reduit a deux amorces hors de la mortaise ; dans la mortaise, la limite de tenon passe avant l'axe. Le texte (52) est decale le long de sa ligne. |
| **03-04, 03-27** (attaches detachees) | Toutes les attaches partent des angles vifs fictifs des aretes cotees : 80 aux bouts de tenon, 59,6 aux epaulements, 58 / (38) au chant et aux faces de tenon. |
| **03-05** (repere du trou par le degagement) | Renvoi radial a fleche, qui sort par le chant ; « diam. 11 », comme les autres planches. |
| **03-06** (59.6 sur les flancs, trace du flanc) | 59,6 tire entre les epaulements, avec `TRAVERSE_JEU_Y` (conc-34) et D.fmt. La trace du flanc est retiree de la vue de la plaque. |
| **03-07, 03-09, 03-13, conc-45** (degagement « 2 », non cote) | Detail A a 10:1, cote 1,5, forme dite en note. La valeur fausse a disparu. |
| **03-08, 03-14** (hauteur du trou) | Cote 19, depuis le chant fraise. |
| **03-10** (position de la mortaise) | La mortaise est cotee en position au tableau DECOUPES INTERIEURES de la planche 01 (fait par FLANC). La vue de la 03 y renvoie. |
| **03-11** (jeu de 4 et tolerance de tole) | Traite par D5 : la mortaise est taillee sur `TRAVERSE_LX_REEL`, donc l'arete droite fait la largeur du paquet REEL. La note le dit. |
| **03-12, conc-17, D8** (cote fonctionnelle, brut) | Cote 58 du chant aux faces portantes, (38) en auxiliaire. Mode de fraisage reference sur les faces HAUTES, brut du DXF en note. |
| **03-15** (ajustements non toleres) | Tenon 20 +/-0,1. Avec la mortaise en ISO 2768-m (20,4 +/-0,2), le jeu reste de 0,1 au moins. |
| **03-17** (renvoi « chant fraise » qui coupe 3 traits) | Les cotes selon y sont passees au-dessus. Le renvoi ne coupe plus rien. |
| **03-18** (renvois sans terminaison) | Renvois `renvoi()` : fleche sur un trait, point dans une surface. |
| **03-19, 03-26, docu-25** (« cinq toles ») | Texte supprime ; tout ce qui depend du nombre lit `TRAVERSE_N`. |
| **03-20** (axes trop longs) | Axes a 3 mm du contour, sauf l'axe du trou, qui sert de rappel au 19. chk_croix : seul croisement restant, les deux axes au centre du trou. |
| **03-21** (chaine en escalier) | (38) et 20 sur une meme ligne, 58 a l'exterieur a 8 mm. |
| **03-22** (point decimal) | Tout passe par D.fmt. Le seul point restant est « cert. 3.1 », une designation EN 10204. |
| **03-23** (pieces voisines en trait cache) | Limites de tenons en trait mixte fin a deux tirets, traces ouverts. Trace du flanc retiree de la vue de la plaque. |
| **03-24** (portee nette 32 sur 40) | 30 nets sur les 38 du bronze, par les fonctions de params corrigees par MODELE. |
| **03-25** (valeur et ordre du chanfrein) | 0,8 x 45 sur les deux faces, APRES le fraisage, avec la reprise du paquet. |
| **03-29** (calculs faux) | Remplaces par `appui_tenon`, `matage_tenon`, `flexion_tenon`, `flexion_traverse` : le plan et verifie() disent la meme chose. |
| **D4, D5, D8** | Voir les notes. Cartouche : `MATIERE_TOLE` et `BRUT_TOLE`. |

## Ecartes, avec la raison

- **Correction de `draw._ligne_cote`, `cote_h` et `cote_v`** (03-01, 03-03, 03-16) : non faite, comme pour les agents precedents. Ces fonctions sont partagees, elles deplaceraient les textes des planches 04 a 07, et mon mandat sur draw.py se limite a des ajouts. La 03 ne les appelle plus.
- **« Ø » et passage des SVG en UTF-8** (03-05) : j'ecris « diam. », comme les planches 01 et 02. Cela evite de toucher Sheet.save et index_html.
- **Detail par clipPath** (03-07) : verif_plans lirait les traits caches. J'ai fait une decoupe geometrique des segments.
- **03-11, options A (mortaise a 54), chanfrein 2,5 des tenons extremes, `TRAVERSE_PAQUET_MAX`** : D17 fige la geometrie du flanc, et D5 regle l'epaisseur reelle. Seul reste le flottement lateral du paquet, voir « reste ».
- **« 58 identique a 0,02 » et « 58 0/+0,2 »** (03-12) :
  - l'identite des 6 plaques vient du fraisage en paquet et de la planeite 0,05, qui sont ecrits ;
  - l'ecart de cote absolu est rattrape par la course du coin (reserve `TOL_EMPILEMENT`) ;
  - 0,02 est plus serre que la planeite.
- **« 59,6 +/-0,1 »** (03-15) : inutile depuis D11 (entretoises 60 +0,1/0). Au pire on a 59,9 contre 60, soit 0,1 de jeu.
- **« 20,4 +/-0,1 » sur la mortaise** (03-15) : la mortaise est une forme du flanc, definie planche 01. La tolerance du tenon suffit a garder un jeu positif.
- **Fleche dans `draw.note`** (03-18) : fonction partagee. J'utilise `renvoi()`.
- **Cote 64 hors tout** :
  - placee a l'exterieur des tenons, ses attaches a z haut croiseraient forcement les attaches du 80 (bouts de tenon a +/-40). J'ai essaye toutes les dispositions ;
  - la hauteur est definie par la chaine 58 + 6 ;
  - le hors tout (64 fini, 65 brut) est ecrit dans la note de decoupe.
- **Trace du flanc dans la vue de la plaque** (03-06, 03-23) : retiree au lieu d'etre raccourcie. A 2:1, la face du flanc (y 30) passerait a 0,4 mm de l'epaulement (29,8) et doublerait le trait fort. L'ajustement est montre par la vue de la mortaise.
- **Second renvoi « tenon en appui »** (03-18 a 03-20) : remplace par la note generale « les tenons portent par leur face HAUTE », sans doublon.
- **Corrections de params, parts, README, DEBOUT et commentaires** proposees dans 03-11, 03-19, 03-24, 03-25, 03-26, 03-29 et docu-20 : deja faites par MODELE et DOCUMENTS, ou hors de mon perimetre.

## Ce qui reste

1. **Flottement lateral du paquet dans la mortaise** (03-11, avis des verificateurs). Avec D5, l'arete droite fait exactement la largeur du paquet reel. Mais rien ne centre le paquet selon x : decale de plus de 0,8 environ, la plaque extreme commence a monter sur un conge R2. Aucune decision D ne le traite, c'est a trancher. Pistes : centrage au montage, ou chanfrein de 2,5 sur l'arete exterieure des tenons extremes.
2. **Planche 01** (facultatif) : porter +/-0,1 sur la hauteur de la mortaise dans le tableau DECOUPES INTERIEURES. Le jeu minimal passerait de 0,1 a 0,2.
3. **draw.py** : `_ligne_cote`, `cote_h` et `cote_v` restent defectueux pour les planches qui les appellent encore (04 a 07).
4. **Litteraux de plan sans parametre** :
   - planeite 0,05, Ra 1,6, « 150 C » ;
   - tolerance du tenon (`T03_TOL_TENON`, constante locale commentee) ;
   - rayon R2 des angles, ecrit en dur dans `parts.traverse_profile`. Le plan le lit sur le contour.
5. **export_dxf** (LIVRABLES) : le DXF de la traverse porte la mention « fentes et encoches taillees pour une tole reelle de ... ». Elle vient de `de_la_tole()`, alors que le profil de la plaque ne depend pas de EP_TOLE_REELLE. C'est sans consequence, mais inexact.

## Controles (etat final)

| controle | resultat |
|---|---|
| `python plans.py` | sans erreur |
| `python verif_plans.py` | 0 faute sur les 8 planches (660 textes, 57 sur la 03) |
| `python params.py` | 0 probleme |
| `python verif_percages.py` | 0 faute |
| `chk01.py 03_traverse`, marge 0, tous traits | 0 remarque (57 textes, 490 traits) |
| `chk_croix.py 03_traverse` | 1 croisement, les deux axes au centre du trou (voulu) |
| SVG 00, 01, 02, 04 a 07 et draw.py | identiques a la copie temoin |
| plans.py hors du bloc 03 | identique |
| essai EP_TOLE_REELLE = 8,25 (copie) | mortaise (53,5), 0 faute |

Relecture finale du rendu, decoupe par decoupe :
- planche entiere ;
- titres et cotes du haut ;
- tenon droit et chaine de droite ;
- cote gauche et renvois du bas ;
- mortaise ;
- detail A ;
- notes et cartouche ;
- bloc de calcul.

Resultat :
- aucun texte n'est traverse ;
- les lignes de cote paralleles sont espacees de 8 mm ;
- toutes les cotes sont hors de la piece ;
- aucune attache ne croise une autre cote ;
- les echelles sont vraies et annoncees (2:1 dans les titres, 10:1 au detail) ;
- le cartouche est juste.
