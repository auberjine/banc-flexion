# Reprise

Etat au 06/10/2026, indice B. `python make.py` se termine par
« termine, 0 etape(s) en echec ». La derniere relecture complete des planches
est dans `revue_finale/BILAN.md` (constats contre-verifies dans
`revue_finale/constats/`).

## Decisions encore ouvertes, pour l'utilisateur

- Tourillon en C45+C etire h9 (choix actuel) ou S355JR : `TOURILLON_MATIERE`.
- V5 : 2 rondelles AS 1730 a la place d'une rondelle trempee 30 x 2 (introuvable en M16).
- Centrage selon x du paquet de traverse dans sa mortaise.
- Hauteur d'etuve 1400 a confirmer (largeur 538 confirmee le 05/10/2026).
- Calage de la poutrelle en position debout : point ouvert assume.
- Points D-09, C-04, C-05, D-08 de `revue_finale/BILAN.md`.

## Environnement

- Python 3 avec Pillow et openpyxl : `pip install pillow openpyxl`.
- Rendu des planches et PDF : Chrome / Edge / Chromium sans interface ;
  `outils.py` le trouve seul, ou par la variable `BANC_NAVIGATEUR`.
- Modele 3D et controle d'interference : FreeCAD 1.0 (`freecadcmd`), variable
  `BANC_FREECAD` si hors du chemin habituel. Sans FreeCAD, tout le reste
  tourne : `params.py`, `verif_percages.py`, `plans.py`, `verif_plans.py`,
  `spec.py`, `nomenclature.py`, `export_dxf.py`.
- Les calculs EF (`fem_*.py`) ne sont pas a relancer tant que la geometrie du
  flanc ne change pas (213 MPa, coefficient 2,02 / 1,83 ; flambement 38,2 /
  38,3 avec les entretoises 20 x 2). Leurs dossiers de travail (`out/fem`,
  `out/flamb*`, plusieurs centaines de Mo) sont recrees au besoin ; seuls les
  resultats `out/fem_flanc.json` et `out/flambement*.json` sont gardes.

## Pieges connus

- Dans `spec.py`, l'accumulateur du document s'appelle `L` : ne jamais creer
  de variable locale `L`, cela vide SPEC.md sans erreur.
- Certains fichiers sont en CRLF : conserver les fins de ligne.
- `params.py` et `verif_interference.py` rendent 0 meme en cas de probleme :
  seul leur bilan imprime fait foi, et `make.py` l'exige.
