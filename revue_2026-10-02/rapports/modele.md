# Agent MODELE : compte rendu du 02/10/2026

Fichiers modifiés : `params.py`, `parts.py` et `verif_percages.py` (dossier banc-flexion). Aucun autre fichier du projet n'a été touché. `out/` n'a pas été régénéré : les essais FreeCAD, plans, spec et nomenclature ont tourné dans une copie, `scratchpad/correction/modele/bac/` et `plans_test/`.

## Contrôles finaux

| contrôle | résultat |
|---|---|
| `python params.py` | **0 problème(s)** |
| `python verif_percages.py` | **0 faute**. Chaque pièce est contrôlée finie et, si elle a un `dxf_profile`, aussi sur son profil de découpe. Le nouveau contrôle d'encoches du contour est actif. |
| construction de tous les profils de `all_parts()` et des 2 `dxf_profile` | 20 pièces, sans erreur |
| profil du flanc, comparé à la sauvegarde du 01/10 à 1e-9 près | **IDENTIQUE** (même liste de segments). Z_TAB0, mortaise, encoches, nodes et fente inchangés avec EP_TOLE_REELLE = EP_FLANC |
| `plans.py` | tourne sans erreur. Les SVG ont été écrits dans `correction/modele/plans_test/`, et non dans out/plans. `verif_plans` sur ces SVG : 0 faute |
| `build_freecad.py` + `verif_interference.py` (FreeCAD 1.0, copie bac/) | cadre 35,23 kg ; **0 interférence réelle, 16 contacts vérifiés, 0 rompu**. Les engrènements attendus restent : flanc/pied 12 mm³, coulisseau/guide 167 mm³ (tige de 8 dans l'avant-trou de 6,8 figuré) |
| `spec.py`, `nomenclature.py`, `export_dxf.py` (copie bac/) | tournent. export_dxf : le plat de renfort n'est plus exporté ; le groupe 8 mm s'appelle toujours `tole_8mm_42crmo4.dxf` (split()[0] de "42CrMo4 +A") |
| balayage ETUVE_INTERIEUR | verifie() passe de **530 à 553** (avant 514-552). En dessous de 530, la douille n'a plus 90 mm ; au-dessus de 553, la dent sort de l'appui. Le commentaire est corrigé. |
| balayage EP_TOLE_REELLE | verifie() passe de 7,75 à 8,25. Au-delà de 8,3, la tige V2 M10 x 80 n'a plus 3 mm de dépassement (il faudrait une x 90) ; en dessous de 7,75, l'écrou V9 n'a plus 2,5 mm sur le filet. C'est voulu : ces contrôles calculent les serrages avec la tôle mesurée. |
| contrôles volontairement cassés (GUIDE_VIS_L 20, 2 rondelles V9, V1 x 90, V2 x 70, jeu de rainure 1,75, µ 0,05, ancien crochet…) | chacun est bien refusé par verifie(). L'ancien crochet est aussi refusé par verif_percages (encoche de 3,0). |

Chiffres publiés par `python params.py` : Hertz 339 MPa sur 6,4 mm portants, limite 480, coefficient 1,42 ; bronze 30 mm nets, 7,7 MPa sur la traverse et 6,5 MPa sur le coulisseau ; filet M16 marge x2,13 à µ 0,08 ; platine 130 MPa (coefficients 3,3 à froid et 3,0 à 150 °C), entretoises 12,6 MPa chacune ; matage du tenon 26,5 MPa sur 38,4 x 5,9, racine de tenon 11,5 MPa, corps de plaque 7,6 MPa ; V1 dépasse de 10 (marge de filet 6), V2 de 4, V9 de 20,5 (marge 3,5) ; douille 95 mm ; bruts du coin 45 x 120 x 65 et du coulisseau 120 x 65 x 40.

## Fait, décision par décision

- **D1, guides** : `GUIDE_VIS_L = 12` (longueur sous tête, CHC M8 x 12 ISO 4762, tête lisse). Nouveaux paramètres `GUIDE_TARAUD_D = 6.8` et `GUIDE_PERCAGE_P = GUIDE_TARAUD_P + 3 = 19` ; `GUIDE_TARAUD_P = 16` est inchangé. Côté 3D, f_coulisseau perce à 6,8 sur 19 et f_guide dessine une tige de GUIDE_VIS_L. verifie() vérifie la longueur sous tête contre le taraudage, `GUIDE_VIS_L > GUIDE_TARAUD_P - 1`, la cohérence de l'avant-trou avec un M8, la longueur minimale de filet, et que les avant-trous opposés ne se rejoignent pas. Les commentaires M10 / 16 x 10 / 17,0 / 136 sont corrigés. La pièce guide est passée `achete=True`, désignation « CHC M8 x 12 ISO 4762 8.8, tête lisse (non moletée) ». **`D_TARAUD` est gardé comme alias transitoire égal à GUIDE_TARAUD_D (6,8)**, parce que plans.py l.200 le lit encore : plus aucune valeur 8,5.
- **D2, rainure** : `RAINURE_JEU = 0.75`, `RAINURE_B = EP_TOLE_REELLE + 2*RAINURE_JEU` (9,5). verifie() contrôle un jeu compris entre 0,5 et 1,0 par côté, et au moins 4 mm de joue.
- **D3, Hertz** : nouvelle fonction `hertz_largeur()` = EP_FLANC - 2·CHANFREIN, utilisée par `hertz_appui()`. Nouveaux `HERTZ_LIM = 1.6*min(RE_S355_CHAUD, RE_TOLE_CHAUD)` (480) et `HERTZ_COEF_MIN = 1.3`, nouvelle fonction `hertz_coef()` (1,42). verifie() contrôle le coefficient, et le __main__ l'affiche.
- **D4, matière** : `MATIERE_TOLE = "42CrMo4 +A"`, `BRUT_TOLE = "tole 8 mm, cert. 3.1, Re >= 430"` (31 caractères, tient dans la case brut du cartouche), `EXIGENCE_TOLE` (texte complet : certificat 3.1 EN 10204 avec essai de traction, Re >= 430 MPa à 20 °C). Les pièces en tôle (flanc, traverse, poussoir, support, pied, crochet) ont `material = MATIERE_TOLE` et `stock = BRUT_TOLE`.
- **D5, tôle réelle** : `EP_TOLE_REELLE = EP_FLANC` et `NOTE_TOLE_REELLE` (« mesurer la tole livree, regler EP_TOLE_REELLE et regenerer les DXF avant decoupe »). En dérivent : `ENCOCHE_PIED_B = EP_TOLE_REELLE + PIED_JEU` (encoches à mi-bois du flanc, du pied et des coins, et contrôles de verifie), les nodes (`EP_TOLE_REELLE/2 - PIED_NODE_SERRE`), `PIED_FENTE_JEU = 0.2` avec `PIED_FENTE_B = EP_TOLE_REELLE + 2*PIED_FENTE_JEU`, la mortaise (`TRAVERSE_LX_REEL = TRAVERSE_N*EP_TOLE_REELLE`), RAINURE_B, et les serrages de boulonnerie et `SUPPORT_EMPILEMENT`. Le 3D reste nominal. Avec la valeur par défaut, aucune géométrie ne bouge (vérifié). La note est reprise dans les notes du flanc et du pied. Essai à 8,5 : tout se construit, mortaise 55, encoches 8,9, 0 faute de ligament.
- **D6, visserie** : nouveaux `RONDELLE_M10_E = 2`, `ECROU_FREIN_H = 10`, `ECROU_FREIN_REF = "ISO 7042 classe 8, autofreine tout metal"`, `ENTR_VIS_L = 100`, `ENTR_VIS_FILET = 26`, `TRAVERSE_TIRANT_L = 80`, `FILET_DEPASSE_MIN = 3`, `FILET_MARGE_MIN = 2.5` ; `SUPPORT_RONDELLES_ECROU = 3` et `SUPPORT_RONDELLE_E = RONDELLE_M10_E`. Nouvelle fonction `boulonnerie()`, qui donne pour V1, V2 et V9 la longueur, le serrage, la hauteur d'écrou, le dépassement et la marge de filet. verifie() contrôle les trois boulonneries, ce qui remplace l'ancien contrôle V9 seul. Le commentaire « empilement 163,5 » est corrigé : 171,5, filet à 168, marge 3,5.
- **D7, goupilles** : `POUSSOIR_GOUPILLE_PASSAGE = 8.3` (trous laser des plateaux) et `PATIN_CHARGE_AVANT_TROU = 6.0`. `poussoir_goupilles(d=None)` prend désormais un diamètre. `patin_charge_profile(brut=False)` donne les trous finis 8 H7 ; avec `brut=True`, les avant-trous de 6. verifie() contrôle le passage (au moins d + 0,2) et l'avant-trou (au plus 8 - 1,5, au moins 0,5·e).
- **D8, traverse** : `TRAVERSE_SUREP = 1.0` ; `traverse_profile(brut=False)` ; avec `brut=True`, seul le chant du bas descend de 1,0 (brut 65 / 39, fini 64 / 38). Le PartSpec traverse porte `dxf_profile=lambda: traverse_profile(brut=True)`. La note précise que le DXF est le brut et qu'on fraise en paquet, aligné sur les faces HAUTES des tenons. verifie() borne la surépaisseur entre 0,3 et 2.
- **D9, crochet** : `CROCHET_LANGUE_L = ETUVE_PAROI_E + 3.0 + CROCHET_BEC_L` (9). L'encoche de bec passe à 4,0, soit 0,5·e. verifie() refuse une encoche inférieure à 0,5·e. L'interférence reste bonne.
- **D10, plat** : `PLAT_R = 0`, `plat_renfort` passé `achete=True`, matière S235, brut « feuillard 20 x 2 S235, coupe a 840 ». Il ne produit plus de DXF.
- **D11, entretoises** : `ENTRETOISE_MATIERE = "E235+C EN 10305-1"`, `ENTRETOISE_BRUT = "tube de precision 20 x 4,5"`, `ENTRETOISE_TOL = "+0,1/0"`, `SUPPORT_TUBE_TOL = "+/-0,2"`, repris dans les notes : « coupée à 60 +0,1/0, faces dressées // 0,05 » et « 71,5 +/-0,2 ». La quantité vient de la nouvelle fonction `n_entretoises()` (9). La note de cadre dit « 7 serrées par vis TH M10 x 100 + écrou ISO 7042…, les 2 de la chape par les vis H M10 x 200 ».
- **D12, bruts** : nouveaux `BRUT_SUREP = 1.5` (par face), `BRUT_SURLONG = 5`, `BRUT_PAS = 5`. Nouvelles fonctions `parts.brut_usinage(fini)` et `parts.bruts_usinage()`, calculées sur la boîte englobante (G.bbox). Coin : « plat 65 x 45, L 120 (fini 61 x 40 x 114,5) » au lieu de 44 x 58. Coulisseau : « plat 65 x 40, L 120 (fini 58 x 36,2 x 114) ». verifie() contrôle brut ≥ fini + 2·BRUT_SUREP.
- **D13, polissage** :
  - `TRAVERSE_GARDE_FENTE = 36` donne Z_TAB0 à la même valeur au 1e-9 près ;
  - `TRAVERSE_JEU_Y = 0.4` (épaulement yb = 29,8 inchangé) ; verifie() contrôle que la traverse n'est pas pincée et que ENTRETOISE_L = ECART ;
  - étuve : `ETUVE_HAUTEUR = 1400` (À CONFIRMER), `ETUVE_GARDE = 20`, `Y_ETUVE_LIBRE = ETUVE_INTERIEUR/2 - ETUVE_GARDE` (250), `Y_BOUT_VIS`, `Y_BOUT_TIRANT`, `DEGAGEMENT_DOUILLE` (95) ; les critères morts H_FLANC > 480, L_FLANC > 1400 et 2*190 sont remplacés par la hauteur de l'étuve debout, la douille, le bout des vis de chape et le coin reculé, comparés à Y_ETUVE_LIBRE ;
  - filet : `VIS_MU_MIN = 0.08` dans `filet_marge()` (marge x2,13) et `FILET_P_ADM = 12`, avec le message « taraudage C45 / tige 8.8 ». verifie() utilise `coin_couple()`. Nouvelles fonctions `coin_mu_autoblocage()` (0,106) et `coin_desserrage()` (329 N) ;
  - platine : `platine_contrainte()` donne σ, la flèche et la compression PAR tube ; le seuil devient RE_TOLE_CHAUD/2,5 (au lieu de 0,4·RE_S355) ;
  - marges nulles : le débord du bronze sur la traverse se juge en demi-largeurs, chanfrein déduit (marge réelle 0,2). `portee_coin()` compte maintenant la plaque de bronze PLAQ_B (30 nets au lieu de 32 sur 40) ; seuil 0,75·PLAQ_B. Nouvelle fonction `pressions_plaquettes()` (largeur nette x longueur portante : 7,7 / 6,5) ; `pression_coin()` en renvoie la haute ;
  - commentaires et docstrings périmés réécrits : tôle de 10, M10 des guides, voile, logette, bague-écrou, « cinq tôles », # 35 / # 40 / # 50 / # 30 / 17,0, rayon équivalent 136 (devenu 91), EF 190-206 / 1,89 (devenu 213 MPa, 2,02 / 1,83), sens de l'effort sur la tige (conc-40, il est maintenant décrit vers l'intérieur), nodes (passage 7,8, serrage 0,1), pieds couchés « 30 mm », plaquette 104, retrait 1,7.

## Constats des JSON appliqués côté modèle (hors D1-D13)

- conc-33 : `TOL_EMPILEMENT = 2.0` (verifie exige une réserve de course de 2 ; il y en a 2,36), `CALES_EP = (1.0, 2.0)`, `CALE_DE = 50`, `CALE_DI = 26`. Le message « bronze sans emploi » est reformulé.
- conc-34, 35, 36, 37, 40, 41, 42, 43, 44, docu-29, conc-53 (parties params/parts), docu-30 : traités dans D2-D13 ci-dessus.
- conc-43 / verif_percages : nouvelle fonction `encoches(pa, prof_mini)` qui mesure le vide entre deux bords du contour extérieur qui se font face (directions opposées à 30° près, chacun d'au moins `PROF_ENCOCHE = 3` mm de long, vide jugé au milieu de la partie en regard). Elle s'applique à toutes les pièces planes. Résultats : flanc 8,4, pied 7,8 (nodes), crochet 4,0. Les dégagements de 2,1 et les congés sont ignorés.
- conc-24 / D15 (partie modèle) : `ETUVE_CONFIRMEE = False`, `ALERTE_ETUVE = "NE PAS DECOUPER AVANT CONFIRMATION DE LA LARGEUR D'ETUVE"`. Le PartSpec du pied et celui du crochet portent `dxf_avertissement = ALERTE_ETUVE`, et leurs notes le répètent. La note du crochet donne aussi la distance de la dent à la paroi (48,2 pour 540).
- conc-46 : `achete=True` pour guide, pile_belleville (brut « 12 rondelles DIN 2093 A50 »), vis (tige filetée M16 coupée à 185) et plat_renfort, en plus des plaquettes qui l'étaient déjà.
- conc-48 : `INDICE_REVISION = "A"`, `DATE_EDITION = "02/10/2026"` (pour draw.py et les DXF).
- conc-56, partie notes : « un jeu par éprouvette » dans les notes des patins et du plat.
- conc-26 : nouvelle fonction `coin_tours(force)`, qui renvoie (écrasement, course du coin, tours) ; 0,5 kN donne 0,36 / 1,68 / 0,84 tour, pour l'ordre de montage.
- 01-03 : `FENTE_COIN_R = 4.0` (géométrie identique). 07-02 : `SUPPORT_R_COIN = 8.0` (identique). 04-21 : `PATIN_R = 3.0`, `PATIN_CHARGE_R = 6.0` (identiques). 06-18 : `TOURILLON_CHANFREIN = 1.5`.
- 06-01 : tourillon en `TOURILLON_MATIERE = "C45+C"`, brut « rond etire 25 h9 x 76 », note « non repris, chanfreins 1,5 x 45 aux deux bouts ». C'est un choix à valider (voir « reste »).
- 03-24 : portee_coin sur PLAQ_B (voir D13). 03-29 : nouvelles fonctions `appui_tenon()` (38,4 x 5,9, entraxe 68,5), `matage_tenon()` (26,5), `flexion_tenon()` (11,5 MPa, 17 nets) et `flexion_traverse()` (7,6 MPa en majorant charge concentrée). Elles remplacent les formules en ligne de verifie() et sont prêtes pour plans/spec.
- **02-06 (c), défaut de géométrie du coin, vérifié par le calcul puis sur le dessin `correction/modele/coin_rebord.png`** : la face intérieure du rebord bas gauche partait en `y0 - h·sin a`. Elle était inclinée de 24° sur la normale à la pente, et la plaquette basse ne portait que par l'arête du dégagement. Elle part maintenant en `y0 + h·sin a`, normale à la pente comme le rebord droit et comme le chant de la plaquette (jeu 0,2 parallèle). C'est le seul changement de profil fini avec le crochet (D9), le poussoir (D7) et le plat (D10). L'interférence reste bonne.
- 05-02 : commentaire des nodes corrigé.
- Notes de pièces réécrites à partir des paramètres : flanc (gravure d'un seul côté, face gravée à l'extérieur), poussoir, coulisseau (M8, avant-trou, axe à 12, x = ±44), coin (rebords dessus 7,05 / dessous 8,15, faces normales à la pente), patin d'appui (rainure fraisée après découpe, 9,5 x 1,5), patin de charge (avant-trous 6, percés-alésés 8 H7), support et entretoises.

## Écartés, avec la raison

- **03-11** (mortaise à 54 pour absorber la tolérance de tôle) : écarté. D17 fige la géométrie du flanc et D5 traite la tolérance par EP_TOLE_REELLE, d'où découle la mortaise.
- **conc-23** (ne plus chanfreiner le bossage, EBAVURAGE / CHANFREIN_TRAVERSE séparés) : écarté. D3 retient le chanfrein sur le bossage et compte la largeur portante EP_FLANC - 2·CHANFREIN.
- **conc-13** (CHC M8 x 16, taraudage 20) et **conc-25 / docu-02 option b** (garder M8 x 20, taraudage 22) : remplacés par D1 (M8 x 12, taraudage 16).
- **conc-17 / 03-12**, surépaisseur 0,5 : remplacée par D8 (1,0).
- **02-07 / conc-16 / 04-12**, passage 8,2 et trous de patin « pointés au laser » : remplacés par D7 (passage 8,3, avant-trou laser de 6).
- **conc-18, rondelle trempée V8 « 30 x 2 » à passer à 3 mm (ISO 7089 M16 300 HV)** : non appliqué au modèle. SUPPORT_RONDELLE = 3 décalerait la chape de 1 mm et porterait les entretoises de butée à 72,5, contre les 71,5 ±0,2 fixés par D11. Voir « reste ».
- **conc-31**, DEGAGEMENT_DOUILLE = PIED_Y/2 - bout de tige (100), et **00-09**, cadre centré (115) : on garde la définition de conc-11 (`Y_ETUVE_LIBRE = E/2 - 20`, soit 95), plus prudente, que D13 demande explicitement.
- Contrôle « ETUVE_GARDE couvre le décentrage sur les pieds » : essayé puis retiré. Debout, le cadre est calé par les crochets, pas par ses pieds ; ce contrôle aurait réduit sans raison la plage d'étuve admissible.
- **conc-02/07/12/22/49, conc-19/21/22/38/39, conc-26/27/28/52/54/55/56, docu-04 à 28** : relèvent de plans.py, export_dxf.py, build_freecad.py, nomenclature.py, spec.py ou des .md, hors de mon périmètre.

## Interface pour les autres agents (à brancher)

**export_dxf.py (LIVRABLES)**

- Remplacer `o, h = spec.profile()` par `o, h = P.decoupe(spec)`. Ce helper renvoie `spec.dxf_profile()` s'il existe, sinon `spec.profile()`.
  - Traverse : chant du bas à Z_TRAVERSE_BAS - 1,0.
  - Patin de charge : trous de 6.
- Écrire `spec.dxf_avertissement`, quand il n'est pas vide, en texte (calque TEXTE) sur le DXF de la pièce et sur le DXF de groupe. Cela concerne le pied et le crochet : ALERTE_ETUVE.
- Ajouter `p.INDICE_REVISION` et `p.DATE_EDITION` aux textes DXF.
- Les pièces `achete=True` sont déjà exclues ; le plat de renfort disparaît des DXF.
- **build_freecad.py, l.221-230, écrit AUSSI un DXF par pièce plate dans out/dxf**, à partir du profil fini et sans exclure les pièces achetées. Il en sortirait un plat_renfort.dxf et une traverse sans surépaisseur. Il faut soit utiliser `P.decoupe(spec)` et sauter `spec.achete`, soit supprimer ce bloc, puisque export_dxf fait le travail.

**plans.py (PLANCHES)**

- Remplacer `p.D_TARAUD` par `p.GUIDE_TARAUD_D` (l.200), puis supprimer l'alias D_TARAUD de params.py.
- Paramètres disponibles :
  - RAINURE_B / RAINURE_P ; hertz_appui(), HERTZ_LIM, hertz_coef(), hertz_largeur() ;
  - platine_contrainte(), qui remplace support_sigma / support_sigma_tube / support_fleche ; appui_tenon(), matage_tenon(), flexion_tenon(), flexion_traverse() ;
  - portee_coin() (désormais sur PLAQ_B, 30) et pressions_plaquettes() ; coin_mu_autoblocage(), coin_desserrage() ;
  - BRUT_TOLE, MATIERE_TOLE, EXIGENCE_TOLE ; DEGAGEMENT_DOUILLE, Y_ETUVE_LIBRE, Y_BOUT_TIRANT ; CROCHET_DENT_Y ; ALERTE_ETUVE ;
  - TRAVERSE_SUREP, TRAVERSE_JEU_Y ; FENTE_COIN_R, SUPPORT_R_COIN, PATIN_R, PATIN_CHARGE_R ;
  - POUSSOIR_GOUPILLE_PASSAGE, PATIN_CHARGE_AVANT_TROU, GUIDE_PERCAGE_P ;
  - TOURILLON_CHANFREIN, TOURILLON_MATIERE ; ENTRETOISE_TOL, SUPPORT_TUBE_TOL, ENTRETOISE_MATIERE ;
  - n_entretoises(), bruts_usinage() ; quantités et matières par `{s.name: s for s in P.all_parts()}`.
- Les profils finis servent aux vues : patin_charge_profile() avec trous de 8, traverse_profile() fini.

**spec.py, nomenclature.py (DOCS)**

- La limite de Hertz est désormais HERTZ_LIM / hertz_coef(), et non 1,6·RE_TOLE_CHAUD.
- Les pressions de plaquettes se calculent par pressions_plaquettes(), et non portee_coin()*PLAQ_B ni portee_coin()*pp.
- Le jeu en largeur de la mortaise est TRAVERSE_JEU_X, et non TRAVERSE_JEU*10.
- Remplacer le 250 en dur par Y_ETUVE_LIBRE / DEGAGEMENT_DOUILLE, et utiliser ETUVE_HAUTEUR.
- Visserie :
  - longueurs par ENTR_VIS_L, TRAVERSE_TIRANT_L, SUPPORT_TIRANT_L et SUPPORT_RONDELLES_ECROU (3, donc 4 rondelles en V9) ;
  - marges par boulonnerie() ; écrou ECROU_FREIN_REF ;
  - quantité V1 = n_entretoises() - len(TROU_SUPPORT) (7).
- Précharge : coin_tours(500).
- Cales : CALES_EP, CALE_DE, CALE_DI.
- Exigence matière : EXIGENCE_TOLE. Note de tôle : NOTE_TOLE_REELLE.
- `spec.achete` sert à la section « pièces du commerce » ; `spec.dxf_avertissement` à la table des DXF.
- out/masses.json (brut, matière) ne reflétera les nouveaux bruts et matières qu'après une reconstruction FreeCAD.

## Reste à faire ou à décider

1. **Rondelle trempée V8 « 30 x 2 »** (conc-18), introuvable en standard pour M16. Je propose de la désigner « 2 rondelles AS 1730 (17 x 30 x 1) », ce qui garde SUPPORT_RONDELLE = 2 et les 71,5 de D11. À trancher par la nomenclature.
2. **Tourillon en C45+C**, rond étiré h9, au lieu de S355JR : choix fait pour aligner sur un stock étiré courant et sur le C45 déjà écrit sur la planche 06. À valider ; revenir en arrière tient en une ligne, `TOURILLON_MATIERE`.
3. **V2, tige M10 x 80** : elle n'admet pas une tôle mesurée au-delà de 8,3. verifie() le dira à la réception ; prendre alors une M10 x 90. Le commentaire de TRAVERSE_TIRANT_L le signale.
4. **Le profil du coin a changé** (rebord bas gauche, 02-06 c). La planche 02 et le DXF éventuel du coin suivent automatiquement, mais la cote de hors tout vaut 61,0 en boîte englobante (61,24 sans le congé R1 de l'angle bas).
5. out/plans, out/dxf, out/step, out/stl, out/fcstd et masses.json **n'ont pas été régénérés** par moi, comme convenu (LIVRABLES, D14). La copie de test reste dans `scratchpad/correction/modele/bac/`.
6. Les textes de spec.py, nomenclature.py et plans.py qui recalculent encore à la main (1,6·RE_TOLE_CHAUD, portee_coin()*PLAQ_B, support_sigma…) donnent maintenant des chiffres périmés par rapport à params. Ils sont à rebrancher sur les fonctions listées plus haut.
