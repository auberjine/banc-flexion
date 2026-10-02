# Agent INTEGRATION : compte rendu du 02/10/2026

Travail fait sur le dossier banc-flexion après le passage de tous les agents. Il comprend deux exécutions complètes de `python make.py` : la première sur l'état livré par les agents, la seconde après mes corrections résiduelles. Les deux journaux sont dans `scratchpad/correction/integration/make1.log` et `make2.log`, et ont été lus en entier.

Fichiers modifiés :
- `params.py`
- `parts.py` (docstring seulement)
- `nomenclature.py`
- `make.py`
- `README.md`

Sont aussi régénérés : `SPEC.md`, `NOMENCLATURE.md` et tout `out/` (hors fem, flamb et anciens logs). Les fins de ligne sont conservées, puisque toutes les éditions ont été faites avec l'outil Edit.

## Contrôles (2e exécution, état final)

La première exécution, sur l'état des agents, était déjà au vert, avec les mêmes chiffres. La seconde tourne avec le make.py durci (voir plus bas) et se termine par **« termine, 0 etape(s) en echec »**.

| étape | résultat |
|---|---|
| `params.py` | **0 problème(s)** ; Hertz 339 MPa sur 6,4, limite 480, coefficient 1,42 ; rainure 9,5 x 1,5 |
| `verif_percages.py` | **0 faute** (15 lignes, profils DXF de la traverse et du patin de charge compris) |
| `build_freecad.py` | cadre 35,23 kg, total 57,45 kg ; 63 fichiers de la génération précédente purgés |
| `export_dxf.py` | 8 DXF de pièce, 3 groupes en étagères (2905 x 538, 2491 x 127, 560 x 100, tous sous 3000) et LISTE.txt |
| `plans.py` | 8 SVG et plans.html |
| `verif_plans.py` | **0 faute sur 777 textes** |
| PDF (Edge) | out/plans/plans.pdf réécrit à 16:36 : 8 pages A3 de 420 x 297, 1,28 Mo, non verrouillé |
| `viewer3d.py` | banc_3d.html, 5,0 Mo |
| `nomenclature.py` / `spec.py` | cadre 35,2 kg / 462 lignes |
| `verif_interference.py` | **104 paires, 0 interférence réelle, 16 contacts vérifiés, 0 rompu**. Seuls les engrènements attendus apparaissent : flanc/pied 12 mm³ (nodes), coulisseau/guide 167 à 173 mm³ (tige de 8 dans l'avant-trou de 6,8 figuré) |

Messages FreeCAD « chanfrein 0.5 impossible sur pied / crochet, arete ramenee a 0.3 » : ils existaient déjà dans les journaux du 18/09. Ils ne concernent que l'arête cassée du modèle 3D (les DXF n'en portent pas). Ce n'est pas une régression.

Inventaire de out/, comparé à `parts.all_parts()` :

| dossier | contenu |
|---|---|
| out/step | 21 fichiers : 20 pièces et banc.step |
| out/stl | 41 fichiers : 20 x 2 et l'assemblage |
| out/fcstd | banc.FCStd seul, sans .FCBak |
| out/dxf | les 8 pièces non achetées planes, les 3 groupes et LISTE.txt |

- Aucune pièce périmée : plus de plaquette, plat_renfort, témoin, butée, vis sans fin, bague ni tôle de 10 en 42CrMo4.
- Les fichiers périmés sont dans out/perime_2026-10-02 (dxf 20, step 33, stl 65, fcstd 2, LISEZMOI).
- L'alerte « NE PAS DECOUPER... » figure dans pied.dxf, crochet.dxf et le groupe _EN_ATTENTE, et nulle part ailleurs.
- « ind. A du 02/10/2026 » figure dans les 11 DXF.
- « PROFIL BRUT » figure dans traverse.dxf et patin_charge.dxf.

Les textes des 8 planches sont identiques avant et après mes corrections (diff de `textes_planches.txt`). Les 8 rendus PNG ont été regardés en entier : rien de cassé à l'intégration, et la perspective de la planche 00 est tirée du modèle 3D du 02/10/2026.

## Sondage de concordance params / SPEC / NOMENCLATURE / planches

Tous les chiffres ont été lus dans params (python), dans SPEC.md et NOMENCLATURE.md, dans les textes des SVG (`textes_planches.txt`) et sur les rendus PNG des 8 planches, regardés en entier.

| grandeur | params | SPEC | NOMENCLATURE | planches |
|---|---|---|---|---|
| rainure (D2) | RAINURE_B 9,5 = 8 + 2 x 0,75, prof. 1,5 | par. 4 : 9.5 x 1.5, jeu 0.75 | 04a : 9,5 x 1,5, 0,75 par côté | 04 : cote 9,5, coupe A-A, note « 9,5 = tôle REELLE + 2 x 0,75 » ; 01 : détail Y 9,5 (graduation, sans lien) |
| guides (D1) | CHC M8 x 12 sous tête, taraudage 16, avant-trou 6,8, perçage 19 | par. 7 : CHC M8 x 12 ISO 4762, tête lisse, taraudage M8 prof. 16 | 02f : CHC M8 x 12 ; 02a : 4 x M8 prof. 16, avant-trou 6,8 prof. 19 | 02 : « 4 x M8 prof. 16 / avant-trou 6,8 prof. 19 » ; 00 : bulle 02f. Plus aucun M10 ni 8,5 pour les guides (grep) |
| V1 (D6) | TH M10 x 100, serrage 80, dépassement 10, marge 6 | tableau boulonnerie identique ; ISO 7042, pas de bague nylon | V1 : TH M10 x 100 ISO 4014 8.8 zinguée + ISO 7042 + 2 rondelles, qté 7 | 06 : « 7 serrées chacune par une V1 (vis TH M10 x 100 + écrou autofreiné tout métal) » |
| V2 (D6) | tige M10 x 80, serrage 52, dépasse 4 | identique | V2 : tige M10 x 80 + 2 rondelles + 2 ISO 7042 | 03 : passage du tirant V2 |
| V9 (D6) | H M10 x 200, 3 rondelles sous écrou, serrage 171,5, marge 3,5, dépasse 20,5 | identique | V9 : 4 rondelles (1 + 3), marge 3,5, dépasse 20,5 | 07 : « vis H M10 x 200 + écrou + 4 rondelles », marge 3,5, 3 rondelles dessinées |
| Hertz (D3) | 339 MPa sur 6,4, limite 480 = 1,6 x min(300, 390), coefficient 1,42 | par. 4 : 339 / 6.4 / 480 / 1.42 | réglages : 339 / 480 / 1.42 | 01 : note du détail X ; 04 : note 04a |
| goupilles (D7) | passage 8,3, avant-trou 6 | par. 7 | 02b : 8,3 laser ; 04b : avant-trous 6, percés-alésés 8 H7 | 02 : « 2 x diam. 8,3 (passage) » ; 04 : « 2 x diam. 8 H7 percés-alésés » |
| traverse (D8) | surépaisseur 1 | par. 7 | 03 : DXF = brut 65 / 39, fini 64 / 38 | 03 : note du brut ; traverse.dxf « PROFIL BRUT : chant du bas +1 » |
| matière (D4) | BRUT_TOLE « tole 8 mm, cert. 3.1, Re >= 430 » | par. 6 : EXIGENCE_TOLE | exigences de commande, colonne brut | cartouches 01, 03, 05 : BRUT_TOLE ; 07 : abrégé, en entier dans la note |
| étuve (D15) | ETUVE_CONFIRMEE faux | par. 11 | exigences et statut des DXF | 05 : bandeau ETUVE ; pied.dxf, crochet.dxf et groupe _EN_ATTENTE : alerte (grep) |

Quantités des cartouches, comparées aux PartSpec :

| planche | cartouche | PartSpec |
|---|---|---|
| 01 | 2 | 2 |
| 02 | 1 + 3 + 1 | coulisseau 1, poussoir 3, coin 1 |
| 03 | 6 | 6 |
| 04 | 4 + 1 + 2 | 4 / 1 / 2 |
| 05 | 4 + 4 | 4 / 4 |
| 06 | 1 + 9 + 1 + 1 | 1 / 9 / 1 / 1 |
| 07 | 2 + 2 | 2 / 2 |

Les quantités concordent toutes. L'indice A et la date du 02/10/2026 figurent sur les 8 cartouches et sur les 11 DXF.

## Corrections résiduelles faites

1. **params.py, contrôle de la dent du crochet** (défaut signalé par l'agent PIED, confirmé).
   - verifie() bornait la dent à 2 mm du bout de l'appui. Or `crochet_profile()` met des congés R3 aux angles de l'appui : de 551,7 à 553, verifie() passait mais le profil ne se construisait plus (« conge R3.00 trop grand »), et plans.py plantait.
   - La borne est portée à 3 des deux côtés, avec un commentaire.
   - Balayage (`balayage_etuve.py`) : verifie() et le profil sont maintenant d'accord partout. Les deux passent de 530 à 551,5, et les deux refusent à 551,7, 552 et 553. Le commentaire « 530 a 553 » devient « 530 a 551 », avec la raison.
   - Avec 540, aucune valeur ne change.
2. **params.py** : l'alias transitoire `D_TARAUD` est supprimé, puisque plus aucun fichier ne le lit (grep).
3. **Commentaires périmés** :
   - params.py : `SUPPORT_RONDELLE` dit maintenant « 2 rondelles trempées AS 1730 de 1 (V5) » ;
   - parts.py, docstring de la chape : « deux rondelles trempées AS 1730 (V5) » au lieu de « une rondelle trempée ».
4. **nomenclature.py**, ligne « Coefficient a 150 C » : « Re 390 a chaud, EXIGE au certificat » était faux. Le certificat exige Re >= 430 à 20 °C, et 390 est la valeur à chaud qui en découle. La ligne devient « Re 390 a chaud, pour 430 a 20 C EXIGES au certificat ».
5. **make.py : le bilan « 0 étape(s) en échec » ne prouvait rien pour deux contrôles.**
   - params.py et verif_interference.py (sous freecadcmd) rendent 0 même quand ils trouvent un problème.
   - `etape()` prend maintenant `attendus=` : l'étape est en échec si l'un des bilans attendus manque à la sortie :
     - « 0 probleme(s) » pour params.py ;
     - « 0 faute(s) » pour les ligaments ;
     - « textes controles, 0 faute(s) » pour verif_plans ;
     - « 0 interference(s) reelle(s) » et « 0 rompu(s) » pour l'interférence.
   - Étape PDF : elle est en échec si plans.pdf n'est pas plus récent que plans.html, ce qui arrive avec un PDF verrouillé par une visionneuse ou avec Edge introuvable.
   - Le cas « 10 probleme(s) » et le cas « 10 interference(s) » sont bien refusés (essai direct de `etape()`).
   - La docstring est mise à jour.
6. **README.md** :
   - le paragraphe « Reconstruire » liste toutes les étapes réelles de make.py et dit que le bilan doit être 0 ;
   - la recette manuelle du PDF est présentée comme facultative, puisque make.py le fait.

## Écarté, avec la raison

- **Mention « fentes et encoches taillees pour une tole reelle de 8,00 mm » sur les DXF de la traverse, du poussoir, de la platine et du crochet** (signalée par TRAVERSE) : constat exact mais non corrigé.
  - Vérification par une tôle réelle de 8,2 (en mémoire) : seuls le flanc et le pied changent de profil.
  - La mention est inexacte mais sans conséquence : elle n'induit aucune cote fausse, et elle reste juste sur les deux DXF de groupe.
  - La corriger proprement demande un champ de dépendance dans PartSpec (parts.py) et son emploi dans export_dxf. Une liste de noms en dur dans export_dxf serait fragile. C'est à faire par MODELE et LIVRABLES, pas à l'intégration.
- **Défauts de `draw._ligne_cote`, `cote_h`, `cote_v` et `note`** (rapports LIVRABLES, FLANC, TRAVERSE, PATINS) : sans objet aujourd'hui. Plus aucune planche ne les appelle (grep sur plans.py) : toutes passent par `cote_hx`, `cote_vx` et `renvoi`. Le code mort reste en place ; on pourra le retirer quand on le voudra.
- **verif_plans.py, prise en compte des traits fins** (rapport FLANC) : non modifié. Le contexte commun fixe qu'il ignore les traits fins. Chaque agent a fait le contrôle complet (chk01, traits fins compris) sur sa planche, avec 0 remarque.
- **Relancer l'EF ou le flambement** : non, conformément à D17. La géométrie du flanc n'a pas changé : DXF du flanc identique, masse 10,206 kg.
- **Rien n'a été relancé ni modifié sur fem_*, flamb* et les anciens logs de out/** : hors du périmètre de D14.

## Reste

Décisions à prendre par l'utilisateur. Toutes sont signalées par les agents et ne sont pas tranchées par D1 à D17 :

1. **Tourillon** : C45+C étiré h9 (choix MODELE, aujourd'hui publié partout) ou S355JR. Le changement tient en une ligne, `TOURILLON_MATIERE`.
2. **V5** : 2 rondelles AS 1730 (17 x 30 x 1) à la place de la « rondelle trempée 30 x 2 », introuvable en M16. Ce choix est publié partout.
3. **COUPLE_M10 = 35 N.m** pour V1 et V9 :
   - la constante est dans spec.py, d'où nomenclature.py et la planche 07 la lisent, ce qui garantit la cohérence ;
   - le précharge-couple K = 0,2 est une constante locale de plans.py (`C07_K_COUPLE`) ;
   - si on valide ces valeurs, les déplacer dans params.py.
4. **Flottement latéral du paquet de traverse dans la mortaise** (TRAVERSE, constat 03-11) : rien ne centre le paquet selon x. Pistes : centrage au montage, ou chanfrein de 2,5 sur les tenons extrêmes.
5. **Vie en pot de la Duralco**, de l'encollage du patin de charge à la précharge (DOCUMENTS) : à vérifier sur la notice, sinon appliquer le repli décrit (collage la veille).
6. **Largeur d'étuve** : 540 à confirmer (D15), plage admise par verifie() de 530 à 551. **Hauteur** : 1400 à confirmer. Position horizontale des colonnes de trous à confirmer (note 7 de la planche 05).
7. **Calage de la poutrelle debout** : point ouvert assumé (D16).
8. **V2, tige M10 x 80** : refusée par verifie() au-delà d'une tôle mesurée de 8,3. Prendre alors une M10 x 90.

Petites dettes de paramétrage, sans effet sur les livrables actuels :

- `PartSpec.text_at`, que plus rien ne lit ;
- la longueur des goupilles (`GOUPILLE_L = 30` dans nomenclature.py) ;
- la précharge de collage 0,5 kN, en dur dans parts.py et nomenclature.py ;
- les congés du pied et du crochet ;
- le R1 des bouches ;
- les traits de graduation ;
- le parallélisme de 0,05 et le R4 des plaques ;
- la tolérance d'angle du coin ;
- la largeur du titre gras dans `Sheet.cartouche` (0,55 h par caractère contre environ 0,60 réels ; la 07 tient de justesse) ;
- `hertz_largeur()` calculée sur EP_FLANC nominal, et non sur EP_TOLE_REELLE.

**Cales V4** : elles n'ont pas de plan. Si on les découpe au lieu de les acheter, ajouter une vue sur la planche 06.
