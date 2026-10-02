# Relecture finale du 02/10/2026 : bilan

Six relecteurs independants :
- 8 planches, deux lentilles chacune (cotes, lisibilite) ;
- changements de conception du 02/10 ;
- coherence entre documents.

Leurs constats sont dans `constats/*.json`. Chacun a ete contre-verifie avant
correction. Apres corrections : `params.py` 0 probleme, `verif_percages.py`
0 faute, `verif_plans.py` 777 textes, 0 faute.

## Corrige

| constat | correction |
|---|---|
| outillage | `verif_plans.py` voit tout trait (fins, arcs, cercles, cadres) contre la boite ORIENTEE des textes, chasses Helvetica reelles |
| outillage | `rendu_planches.py` : PNG de la feuille entiere (ils s'arretaient a 274 mm) |
| 00-04, D-02 | dates et empreinte du modele ecrites DANS les JSON de resultat : plus de faux « PERIME », dates de flambement justes, paragraphe du balayage conserve |
| 00-01 (bulle 01), 00-02 | reperes de l'assemblage hors des fenetres et des hachures |
| 01-01, 01-02, 01-04 | bulle C, entraxe 500 sur axes, loi de la mortaise |
| 02-01, 02-02 | degagement du detail C, appels B et C |
| 03-01 | noms de variables retires de la planche |
| 04-01, 04-02 | entraxe 70 sur axes ; 3 kN par patin (et par bossage sur la 01) |
| 06-01, 06-02, 06-03 | aretes de l'alesage, angles vifs fictifs, note 4 |
| 07-01 | hachures des deux platines differenciees |
| D-01, D-04 a D-07, D-11 a D-13 | README (Linux, outils), DEBOUT, arrondis, support.dxf, ISO 2338 |

## Laisse en l'etat, motive

- **00-01, V9 et 02f** : la ligne de repere traverse l'arete du lobe. Les
  bulles n'ont pas de place dans le lobe sans croiser une lumiere.
- **00-03 et 01-05** : echelles 1:2,5 et 1,5:1, justes et annoncees.
  Elles sont admises par l'ISO 5455 comme echelles d'exception ; a 1:2 ou
  2:1, la vue ne tient pas.
- **01-03** : trois cotes de detail posees dans la matiere. Une cote dans
  la matiere est admise quand elle est plus claire, et dehors elle
  croiserait d'autres traits.

## A trancher (modifie la conception ou la visserie)

- **C-01, bloquant** : le crochet d'etuve ne peut pas s'accrocher.
  - La tete de langue fait 12 mm (langue 7 + bec 5) pour un trou de 10.
  - Le crochet est rigide, a trois langues : on ne peut pas l'incliner de
    plus de 12,7 deg.
  - Proposition : langue 6 + bec 3, pose de face puis descente, et
    controle `langue + bec <= trou - 1` dans `verifie()`.
  - La piece est deja NE PAS DECOUPER.
- **C-02, important** : V2 et V9 ne conviennent qu'a une tole mesuree de
  7,75 a 8,33 mm, alors que la tolerance de livraison va de 7,5 a 9,2.
  - Proposition : V2 en M10 x 90, et 4 rondelles sous l'ecrou de V9.
  - Ainsi, aucun probleme de 7,25 a 9,2.
- **C-03 et D-03 : hauteurs d'ecrous ISO.**
  - ISO 4032 M10 = 8,4 et non 8.
  - ISO 4032 + ISO 4035 M16 = 22,8 et non 21 (ces 21 sont les cotes
    DIN 934).
  - Choisir la norme commandee et regler `params.py` en consequence.
- **D-10 et C-03** : l'ecrou de V9 n'est pas freine, contrairement a la
  regle « autofreine tout metal » de la visserie M10. Proposition : ISO 7042.
- **D-09** : 12,6 MPa (SPEC, DEBOUT) contre 92 MPa avec precharge
  (planche 07). Le controle de `verifie()` ne compte que les 12,6.
- **C-04** : la note de traverse donne 64 / 38 ; depuis les faces hautes
  des tenons, la cote vaut 58 (comme sur la planche 03).
- **C-05** : deux controles de `verifie()` sont toujours vrais par
  construction.
- **D-08** : pate graphite ou cuivre sur la tige. L'irreversibilite du
  filet n'est chiffree que pour la pate cuivre.
- **Decisions de REPRISE.md, toujours ouvertes** :
  - tourillon (C45 ou S355) ;
  - rondelles V5 ;
  - couple de serrage M10 ;
  - centrage de la traverse (constat 03-11) ;
  - largeur d'etuve 540 ;
  - calage de la poutrelle en position debout.
- **Non relance ici** : FreeCAD n'est pas installe dans la session cloud.
  Le modele 3D et le controle d'interference n'ont pas ete relances, mais
  `params.py` et `parts.py` sont inchanges.
