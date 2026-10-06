# Reprise : relecture finale des plans (session cloud)

Etat au 02/10/2026, indice A. Le projet sort d'une relecture complete
(317 constats) suivie de corrections ; `python make.py` se termine par
« termine, 0 etape(s) en echec ». Les constats et les comptes rendus des
agents correcteurs sont dans `revue_2026-10-02/` (un JSON par planche dans
`constats/`, un compte rendu par agent dans `rapports/`).

## Ce qui reste a faire

Demande de l'utilisateur : « verifie la conception, eventuellement un petit
coup de polish, et surtout verifie bien les plans : lisibles, toutes les cotes,
bien placees ».

1. **Relecture finale independante des 8 planches** (`out/plans/0X_*.svg`) :
   par planche, une lentille « completude et justesse des cotes » (chaque
   element de chaque piece defini en taille et position, valeurs contre
   params / parts, cartouche, echelles vraies) et une lentille « lisibilite et
   placement » (aucun texte touche par un trait, fin compris ; cotes paralleles
   a 6 mm au moins ; attaches qui ne croisent rien ; cotes hors piece). Chaque
   constat est contre-verifie avant correction.
2. **Controle des changements de conception du 02/10** : diff de `params.py`
   et `parts.py` (voir `revue_2026-10-02/rapports/modele.md` et
   `integration.md`) ; en particulier le rebord bas du coin, le crochet elargi,
   les guides M8 x 12, la rainure 9,5, les longueurs de vis V1 / V2 / V9, la
   surepaisseur de la traverse, la borne d'etuve de verifie().
3. **Coherence entre documents** : planches, NOMENCLATURE.md, SPEC.md,
   README.md, DEBOUT.md, `out/dxf/LISTE.txt`.
4. **Renforcer `verif_plans.py`** : il ignore encore les traits fins (largeur
   < 0,3), donc une cote qui coupe une autre cote lui echappe. Les agents du
   02/10 l'ont signale. Il doit voir tout trait (ligne, arc, cercle, chemin)
   qui traverse la boite, orientee, d'un texte, sauf le trait qui porte ce
   texte.
5. Corriger planche par planche (une seule fonction de `plans.py` a la fois),
   puis `python make.py` jusqu'a « 0 etape(s) en echec ».

## Decisions encore ouvertes, pour l'utilisateur

- Tourillon en C45+C etire h9 (choix actuel) ou S355JR : `TOURILLON_MATIERE`.
- V5 : 2 rondelles AS 1730 a la place d'une rondelle trempee 30 x 2 (introuvable en M16).
- (tranche le 06/10) Couple de serrage M10 : 25 N.m, dans params.py (COUPLE_M10).
- Centrage selon x du paquet de traverse dans sa mortaise (constat 03-11).
- Largeur d'etuve : 538, CONFIRMEE le 05/10/2026 (hauteur 1400 encore a confirmer).
- Calage de la poutrelle en position debout : point ouvert assume.

## Environnement (Linux)

- Python 3 avec Pillow : `pip install pillow`.
- Rendu des planches et PDF : un Chromium sans interface
  (`apt-get install -y chromium` ou google-chrome). `outils.py` le trouve dans
  le PATH, ou par la variable `BANC_NAVIGATEUR`.
  `python rendu_planches.py` ecrit les PNG dans `out/rendus/` (3200 x 2264 px,
  7,619 px par mm de feuille).
- Modele 3D et controle d'interference : FreeCAD 1.0 en ligne de commande
  (`freecadcmd`), par exemple via conda-forge (`conda install -c conda-forge
  freecad`) ou l'AppImage ; variable `BANC_FREECAD` si hors du PATH. Sans
  FreeCAD, tout le reste tourne : `params.py`, `verif_percages.py`,
  `plans.py`, `verif_plans.py`, `spec.py`, `nomenclature.py`,
  `export_dxf.py`.
- Les calculs EF (`fem_*.py`) ne sont pas a relancer : la geometrie du flanc
  n'a pas change (213 MPa, coefficient 2,02 / 1,83 ; flambement 38,2 / 38,3 avec les entretoises 20 x 2).

## Pieges connus

- Dans `spec.py`, l'accumulateur du document s'appelle `L` : ne jamais creer
  de variable locale `L`, cela vide SPEC.md sans erreur.
- Certains fichiers sont en CRLF : conserver les fins de ligne.
- `params.py` et `verif_interference.py` rendent 0 meme en cas de probleme :
  seul leur bilan imprime fait foi, et `make.py` l'exige.
