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

## Tranche par l'utilisateur et applique

- **C-01** : crochet, langue 6 + bec 3 (tete de 9 dans le trou de 10), pose de
  face puis descente ; nouveau controle dans `verifie()`.
- **C-02** : V2 en M10 x 90, V9 avec 4 rondelles sous l'ecrou. `verifie()`
  passe de 7,25 a 9,2 mm de tole mesuree.
- **C-03 et D-03** : hauteurs ISO. Ecrou H M10 ISO 4032 = 8,4 ; tete V7 =
  22,8 (ISO 4032 + ISO 4035 M16). La tige depasse desormais de 2,7 de la tete
  (plus d'un pas).

## A trancher

- **D-10** : l'ecrou de V9 n'est pas freine, contrairement a la
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
