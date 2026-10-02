# Planche 01_flanc : compte rendu de l'agent FLANC (02/10/2026)

## Fichiers touches

- `plans.py` : seulement le bloc « flanc », c'est-a-dire `plan_flanc()` et cinq aides locales prefixees `f01_` (`f01_pm`, `f01_chemin`, `f01_decoupe`, `f01_cote_alignee`, `f01_cote_angle`, `f01_rayon_creux`, `f01_appel`). Le reste de plans.py est identique a l'octet pres a la copie temoin (`correction/flanc/temoin/plans.py`), ce que j'ai verifie avant et apres le bloc. Le fichier reste en LF et en ASCII.
- `draw.py` : **non modifie**. J'utilise les ajouts ISO de l'agent ASSEMBLAGE (`cote_hx`, `cote_vx`, `_cote_iso`, `bulle`, `rupture`). Les fonctions anciennes `cote_h` / `cote_v` / `note` ne servent plus sur la planche 01, sauf `View.rayon` pour le R150.
- Les SVG 00 et 02 a 07 sont identiques a l'octet pres a ceux d'avant mon travail.
- Mes outils sont dans `scratchpad/correction/flanc/` :
  - `pf_new.py`, la source du bloc ;
  - `splice.py`, qui remet le bloc dans plans.py entre les bandeaux « flanc » et « tete de charge » ;
  - `run.sh`, qui enchaine splice, plans, verif_plans, params, chk00 et le rendu de la 01 ;
  - `chk01.py`, un controle plus severe que verif_plans et que chk00. Il prend TOUS les traits : fins, arcs echantillonnes et cercles d'appel compris. Il utilise la boite ORIENTEE des textes tournes et teste aussi le recouvrement des textes et la distance au cadre ;
  - `crop.py`, pour les decoupes.

## Nouvelle mise en page

- **Vue de face 1:4** (titre « VUE DE LA FACE GRAVEE (1:4) ») :
  - contours, axe de symetrie, graduation tracee en trait fin a sa place ;
  - bulles A a E des percages, terminees par un point ;
  - quatre appels de detail ISO (cercle fin et lettre) : X (bossage), Y (graduation), Z (encoche de coin), W (encoche du chant bas) ;
  - cotes : 440, 960, 750 +/-0,3 entre les sommets des bossages et 500 entre les encoches du chant bas. Les lignes paralleles sont espacees de 7 mm, toutes les cotes sont hors de la piece et passent par cote_hx / cote_vx (texte a gauche des cotes verticales, attaches ISO).
- **DETAIL X (1,5:1)**, bossage d'appui, 2 ex. :
  - profil ouvert, bords de vue en traits de rupture fins ;
  - R150 ; R10 par une ligne qui passe par le centre du conge ;
  - 3,5 avec son attache haute partant du sommet ;
  - (66,6) en cote auxiliaire ;
  - texte de Hertz D3 : « Hertz 339 MPa sur 6,4 portants (8 - 2 x 0,8 d'aretes cassees), limite 480 MPa (patin S355 a 150 C), coefficient 1,42 », entierement calcule (`hertz_appui`, `hertz_largeur`, `HERTZ_LIM`, `hertz_coef`).
- **DETAIL Y (2:1)**, graduation :
  - lumiere +X en vue partielle, son axe, la tete de guide au repos en trait mixte, les 13 traits ;
  - cotes en chaine 9,5 (depuis l'axe de la lumiere) et 8 ;
  - reperes 0 / 6 / 12 kN ;
  - note : traits sans chiffres, 4,5 aux kN impairs, zero = tangente haute de la tete de guide au repos (Z 265,10), Z au tableau.
  - La geometrie est lue dans `P.flanc_gravure()`, source unique.
- **DETAIL Z (2:1)**, encoche de coin (coin haut droit, 4 ex. symetriques) :
  - chants prolonges en trait fin jusqu'au coin vif fictif ;
  - axe de l'encoche ;
  - cote angulaire 38 deg prise sur le chant de 960 ;
  - profondeur 28 parallele a l'axe, depuis le coin vif, avec l'attache du fond tiree du sommet de la poche ;
  - largeur 8,4.
- **DETAIL W (2:1)**, encoche du chant bas, 2 ex. : 8,4 et 8.
- **Note commune Z / W** : poche carree de 2,1 a 45 deg centree sur l'angle vif (3 traits), bouches R1. Le R1 est lu dans le contour.
- **Tableaux**, tous avec une colonne nb et l'origine « X depuis l'axe, Z depuis le chant bas » :
  - PERCAGES (A a E) ;
  - AJOURS ;
  - FENETRE : sommets en coins vifs fictifs avec leur conge. Une note donne la pente de bielle calculee (17,97 deg) et renvoie les bossages a la cote 750 et au detail X ;
  - DECOUPES INTERIEURES : fente du coin, lumieres, mortaise. Les valeurs sont lues sur les contours eux-memes (bbox), donc elles suivent EP_TOLE_REELLE ;
  - GRADUATION : Z des 13 traits.
- **Notes au-dessus du cartouche** :
  - decoupe et gravure laser d'apres flanc.dxf, calques DECOUPE et GRAVURE ;
  - `EXIGENCE_TOLE` (D4) ;
  - encoches et mortaise sur la tole reelle, puis `NOTE_TOLE_REELLE` (D5) ;
  - aretes cassees 0,8, bossages compris (D3) ;
  - symetrie et graduation d'un seul cote : le second flanc, tourne de 180 deg autour de Z, a sa graduation le long de la lumiere -X (conc-50) ;
  - planeite et coplanarite ;
  - masse.
- **Cartouche** : matiere `spec.material` (42CrMo4 +A), brut `spec.stock` (tole 8 mm, cert. 3.1, Re >= 430), quantite `spec.qty` (2), echelle « 1:4 - details 1,5:1 et 2:1 ». L'indice A et la date viennent de draw.py.

## Constats appliques (01_flanc.json)

- **01-01, docu-24, conc-39 (partie planche 01)** : la pente n'est plus ecrite en dur. Elle est calculee par `bielle_angle()` (17,97). Plus aucun litteral 750 / 216 / 20 / R22... : tout passe par params, parts et D.fmt.
- **01-02, 01-03, 01-04, 01-05, 01-20** : les sommets de la fenetre et de l'arete de bielle (435 ; 383,2) et (65 ; 263,2), le noeud (+/-65, 216), la fente, la mortaise et les lumieres sont maintenant definis en taille et en position (tableaux FENETRE et DECOUPES).
- **01-06, conc-50** : la graduation est dessinee, cotee (detail Y) et tabulee. Le zero est defini, la face et le cote sont dits, et la note de symetrie est corrigee.
- **01-07, 01-19, 01-28** : les encoches sont definies par les details Z et W. L'ancienne note a long renvoi, qui coupait les cotes 750 et 960, est supprimee.
- **01-08, 01-15** : la cote « 20 » et la note « membrure 20 » sont supprimees, parce qu'elles visaient une ligne de construction absente de la piece.
- **01-09, 01-10** (verifies sur le code : texte des cotes verticales du cote du pied des lettres, attaches arretees 2 mm avant la ligne) : la planche 01 n'utilise plus `cote_h` / `cote_v`, elle passe par `cote_hx` / `cote_vx` (ISO). draw.py n'est pas modifie (voir ce qui reste).
- **01-11, 01-26, 01-27** : la cote 28,8 et le renvoi de la fente sont supprimes, les deux etant repris au tableau. Le noeud de traits a disparu.
- **01-12** : la note « bielle 35, pente 18,57 » et son renvoi, qui barrait « 14.0 », sont supprimes.
- **01-13** : les bulles sont placees une a une. A et B sont hors du chant, a 3,3 mm. C est dans la fenetre, D au-dessus du trou, E a droite. Aucune ne mange un contour.
- **01-14** : la cote 440 est a 8 mm du cadre (texte a x 14 et plus), et le detail X est separe de la vue.
- **01-16, 01-22** : la cote 870 est retiree, puisque X +/-435 est au tableau FENETRE. Le 750 part des sommets des bossages et porte sa tolerance +/-0,3.
- **01-17, 01-24, 01-25** : le detail du bossage s'appelle X, hors de la plage A a E. Il a un appel ISO (cercle fin) et le renvoi « detail A » est supprime.
- **01-18, 01-23** : l'axe ne traverse plus aucun texte ; R10 n'est plus barre ; l'attache haute du 3,5 part du sommet ; les bords de la vue partielle sont en traits de rupture fins, et non plus une fausse plaque en trait fort.
- **01-21, 01-30** : origine dans le titre, colonne nb, plus de numerotation B4 a B7 ni de mention « symetriques » fausse pour E et pour l'ajour en X 0.
- **01-29, 01-33** : virgule decimale partout (D.fmt). Plus de 11.0, 14.0, 8.4, 9.65 ni 10.2.
- **01-31** : MATIERE_TOLE et BRUT_TOLE dans le cartouche, EXIGENCE_TOLE en note.
- **01-32** : bulles terminees par un point, fleches de rayon. Il n'y a plus de note a renvoi nu sur la vue.
- **01-34** : les doublons sont supprimes : Z 40 et saillie 3,5 en texte, la tolerance du 750 en note, les conges en texte ambigu.
- **D3, conc-09, docu-30** : le chiffre de Hertz est publie sur la planche (339 / 480 / 1,42).
- **D4, D5** : en notes et dans le cartouche. Essai sur une copie (`correction/flanc/bac/`, EP_TOLE_REELLE = 8,5) : les encoches passent a 8,9 et la mortaise a 55 sans retouche de la planche.

## Ecartes, avec la raison

- **conc-23** (ne plus chanfreiner le bossage) : contraire a D3, qui garde le chanfrein et compte EP_FLANC - 2·CHANFREIN.
- **01-07 : cotes de bouche 5,3 et 6,8 ; detail du coin bas gauche ; quatre reperes de coin** :
  - les bouches derivent de la largeur, de l'angle et de l'axe par le coin vif : les coter ferait double emploi. Le R1 est en note ;
  - le coin bas gauche est encombre par les attaches des cotes 440 et 960 : le detail et son appel portent donc sur le coin haut droit, avec la mention « 4 ex. symetriques ».
- **01-19 : clipPath SVG pour les details** : verif_plans lirait les traits caches hors du masque et y verrait de fausses fautes. Les segments sont donc decoupes geometriquement (`f01_decoupe`).
- **01-21 / 01-29 : reperes T1 a T4 / M1 a M4 dans les ajours** : je n'ai mis aucun repere. Un ajour se designe sans ambiguite par X, Z et diam, et un texte dans des trous de 5 mm a 1:4 surchargeait la vue, en plus d'etre coupe par l'axe pour l'ajour en X 0. La colonne rep des ajours est donc supprimee.
- **01-08 (option)** : cote « 30 » de ligament non ajoutee, puisqu'elle double le tableau des ajours.
- **01-15 (option)** : pas de lignes de construction de la membrure ni de la bielle en trait mixte. Elles n'existent pas sur la piece.
- **01-20** : le haut de montant Z 355,7 n'est pas donne. C'est la tangence du R20, qui se deduit du sommet (435 ; 383,2) et du rayon.
- **01-24 : 66,6 en cote normale** : elle est donnee en cote auxiliaire (66,6), parce qu'elle derive de R150, 3,5 et R10.
- **01-26 : rayons poses sur la vue** : les conges sont nommes sans ambiguite dans le tableau FENETRE, et des reperes de rayon a 1:4 auraient traverse la matiere vers des zones chargees.
- **01-09 / 01-10 / 01-14 (partie draw.py et verif_plans.py)** : hors de mon mandat. Ce sont des fonctions partagees et un autre fichier.

## Ce qui reste

1. **verif_plans.py** (01-35, et 01-14 pour la MARGE) : il ignore toujours les traits fins et garde une marge de 8 mm, plus petite que le cadre a 10. `correction/flanc/chk01.py` montre ce qu'il faudrait :
   - prendre tous les traits, arcs echantillonnes et cercles compris ;
   - utiliser la boite orientee des textes tournes, faute de quoi chk00 signale encore deux faux positifs sur les textes tournes « 28 » et « 8,4 » de la planche 01. Je les ai controles a l'oeil et avec chk01 : aucun trait ne les traverse.
   C'est a integrer par qui en a la charge.
2. **draw.py `_ligne_cote`, `cote_h`, `cote_v`** (01-09, 01-10) : defauts toujours presents pour les planches qui les appellent encore. On pourra les corriger une fois toutes les planches passees a `cote_hx` / `cote_vx`.
3. **Valeurs encore en dur dans parts.py**, lues sur la geometrie par la planche mais sans parametre :
   - le rayon des bouches R1 (`coin_encoche`, `flanc_contour`) ;
   - le depart 2,5 et les longueurs 8 et 4,5 des traits de graduation (`flanc_gravure`).
   Ces valeurs relevent de l'agent MODELE. Les tolerances 0,5 (planeite) et 0,3 (750, coplanarite) restent des litteraux de plan, faute de parametre.
4. **Planche 05** : son detail « encoche du flanc, vue selon y (1:1) » redessine l'encoche du chant bas du flanc, desormais definie au detail W de la planche 01. L'agent de la planche 05 peut y renvoyer.
5. **Masse** : 10,2 kg, lue dans out/masses.json. Elle suivra une reconstruction FreeCAD.

## Controles (etat final)

| controle | resultat |
|---|---|
| `python plans.py` | sans erreur |
| `python verif_plans.py` | 0 faute sur les 8 planches (632 textes) |
| `python params.py` | 0 probleme |
| `python verif_percages.py` | 0 faute |
| `chk01.py 01_flanc`, marge 0, tous traits | 0 remarque (232 textes, 3065 segments) |
| SVG 00 et 02 a 07 | identiques a l'octet pres a la copie temoin |
| plans.py hors du bloc flanc | identique |

Relecture finale du rendu, decoupe par decoupe : planche entiere ; vue de face en quatre quarts plus le noeud ; details X, Y, Z et W ; tableaux ; notes et cartouche. Resultat :
- aucun texte n'est traverse ;
- les cotes paralleles sont a 7 mm et hors de la piece ;
- les echelles sont vraies et annoncees ;
- le cartouche est juste.
