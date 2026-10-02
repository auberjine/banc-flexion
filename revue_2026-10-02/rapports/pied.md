# Planche 05_pied : compte rendu de l'agent PIED (02/10/2026)

## Fichiers touchés

- `plans.py` : seulement le bloc de la planche 05. Il va du bandeau `# ==== pied` jusqu'à `def plan_petites` (exclu). Il contient `plan_pied()` et cinq aides locales préfixées `p05_` : `p05_titre`, `p05_rogne`, `p05_morceaux`, `p05_detail` et `p05_arc`. Avant et après le bloc, plans.py est identique à la copie témoin (`correction/pied/temoin/plans.py`). Le fichier reste en LF et en ASCII.
- `draw.py` : **non modifié**. La planche utilise les ajouts ISO déjà présents : `cote_hx`, `cote_vx`, `bulle`, `rupture`, ainsi que `View.d_of`, `axe`, `rayon` et `D.table`. Elle n'appelle plus `cote_h`, `cote_v` ni `note`.
- SVG 00 à 04, 06 et 07 : identiques à l'octet près à ceux d'avant mon travail.
- Outils, dans `scratchpad/correction/pied/` :
  - `p05_new.py`, la source du bloc ;
  - `splice.py` et `run.sh`. run.sh enchaîne splice, plans, verif_plans, params, `../flanc/chk01.py`, `../traverse/chk_croix.py`, la comparaison des autres SVG et de draw.py, puis le rendu ;
  - `robust.py` et `etuve_bornes.py`, les essais de robustesse dans la copie `bac/` ;
  - `crop.py` (7,559 px/mm) et les découpes (`f_*`, `final_full.png`).

## Nouvelle planche

**Cartouche**, entièrement lu dans les PartSpec et `nomenclature.REPERES` :
- matière « 42CrMo4 +A » ;
- brut « tole 8 mm, cert. 3.1, Re >= 430 » (BRUT_TOLE, D4) ;
- quantité « 4 + 4 (05, 05c) » ;
- échelle « 1:2 - details 2:1 et 5:1 ». Toutes les échelles sont normalisées ISO 5455 et vraies.

Indice A et date viennent de draw.py.

**05 PIED A MI-BOIS (1:2)**, avec le sous-titre « matière, 4 ex., brut ».
- Contour et 3 ajours.
- Axe de symétrie, qui sert d'origine des y.
- Axes des deux encoches. Ils servent d'attaches à la cote **68**.
- Cotes **510** et **58**.
- **2 x R6** sur les angles du chant haut.
- Bulles **A** (bout) et **B** (encoche).

**Tableau AJOURS DU PIED 05 (angles R6)**. Les valeurs sont lues sur les trous du profil :
- central : -19,8 à 19,8 ;
- extérieurs : ±48,2 à ±205 ;
- z de 16 à 50.

Une ligne d'origine accompagne le tableau : y depuis l'axe, z depuis le plan de pose.

**DETAIL A (2:1), bout du pied**. La fenêtre est rognée sur le vrai profil et tracée ouverte, avec des traits de rupture fins.
- Chaîne **5 / 8,4** et cote **40** dessous (8 mm entre les lignes).
- **7** dans la fente et **8** sous le creux, toutes deux dans le vide.
- **R2** fléché : c'est l'arête de pose debout.
- Le sous-titre donne R0,5 pour la fente et R2 pour le bossage.

**DETAIL B (2:1), encoche à nodes**.
- **8,4** au-dessus, attaches aux angles vifs fictifs.
- **7,8** au node, dans le vide de l'encoche.
- **20** sur le montant droit, attache prise sur la poche.
- Chaîne **6 / 8** sur le montant gauche : position et longueur du node.
- Trois lignes sous la vue : poche carrée de 2,1 tournée à 45°, centrée sur l'angle vif (3 traits), entrée R1, rampes du node à 45°.

**05c CROCHET D ETUVE (1:2)**. Sous-titre : « y = 0 : face intérieure de la paroi » et « dent à 48,2 de la paroi : étuve de 540 A CONFIRMER ». Ce texte devient « confirmée » quand ETUVE_CONFIRMEE vaut True.
- **21** hors tout en haut.
- Chaîne **40 / 50** du dessus des langues, et **127** au second niveau.
- **20** pour l'appui.
- **48,2** pour la position de la dent (D15). Elle est cotée sur l'axe de la dent, qui sert d'attache.
- **60** au second niveau.
- Bulles **C** (dent) et **D** (langue).

**DETAIL C (5:1), dent**.
- Largeur **6**.
- Hauteurs d'arête **6,84** côté paroi et **2,16** côté intérieur.
- Le sous-titre précise « dessus à 38 deg, comme le fond de fente du pied en V ».

**DETAIL D (2:1), langue, 3 ex. identiques**.
- **9** : saillie depuis la face du corps.
- **12** : langue et bec.
- **5** : retombée du bec, dans la gorge.
- **4** : encoche de bec (D9), sous le bec.

**Alerte en gras** au-dessus des notes, tant que ETUVE_CONFIRMEE est faux : « ETUVE 540 A CONFIRMER : NE PAS DECOUPER AVANT CONFIRMATION DE LA LARGEUR D'ETUVE » (D15).

**Notes** (9 lignes, toutes calculées) :
1. Découpe d'après pied.dxf et crochet.dxf (calque DECOUPE). Arêtes cassées 0,8 x 45° sur les deux faces (`spec.chanfrein`).
2. Matière : EXIGENCE_TOLE (D4).
3. Tôle réelle e (EP_TOLE_REELLE) : encoches 8,4 = e + 0,4 ; fentes 8,4 = e + 2 x 0,2 ; passage aux nodes 7,8 = e - 2 x 0,1 (serrage) (D5, 05-02).
4. NOTE_TOLE_REELLE (D5).
5. 05 : 2 pieds couchés et 2 en V à 38°. Arêtes de pose à 447.
6. 05 : l'encoche (20) porte fond sur fond dans celle du flanc (8, planche 01, détail W). Plan de pose à 30 sous le chant du flanc.
7. 05 : fentes à ±245,8 (entraxe 491,6). Les crochets sont à 24,2 des parois latérales. Colonnes de trous A CONFIRMER (05-25).
8. 05c : 3 langues dans les trous carrés de 10 (pas 40 / 50) de la paroi de 1, qui passe dans la gorge. La dent cale le pied.
9. 05c : rayons R3, R1 et R0,5.

Aucune valeur n'est en dur. Les congés qui n'ont pas de paramètre (6, 2, 0,5, 1, 3) sont lus sur le profil lui-même par `p05_arc`. PIED_COIN_R et PIED_AJOUR_R sont pris dans params.

## Constats appliqués

| constat | ce qui est fait |
|---|---|
| 05-01, 05-19, 05-20, conc-06, conc-19, docu-06, docu-13 | Cartouche : quantité, repères, matière et brut lus dans le modèle ; échelle vraie et normalisée. Les titres portent le repère et la quantité. |
| 05-02 | Note des nodes juste : passage 8,4 → 7,8, serrage 0,1 par côté. La cote 7,8 est portée au détail B. |
| 05-03, 05-11 | Détail B (encoche, node, poches, R1) et détail A (fente, bossage, R2). Tableau des ajours. |
| 05-04, 05-09, 05-10 | Plus de cote 30 sans arête, plus de cotes partielles à l'extérieur des cotes globales. 40 et 8 sont passées au détail A. |
| 05-05, 05-14, 05-15, 05-16 | Crochet entièrement coté. La chaîne 40 / 50 remplace le 97. Le 127 est attaché à de vraies arêtes. 20, 21, 48,2, 60, dent et langue sont cotés en détail. |
| 05-07, 05-08 | `cote_hx` / `cote_vx` : attaches ISO (écart 1 mm, dépassement 2 mm), texte des cotes verticales à gauche de la ligne. |
| 05-12, 05-13, 05-21 | Notes à ligne de repère du crochet supprimées : la dent et les langues sont cotées. Aucune attache ne traverse plus rien. |
| 05-22 | Rayons fonctionnels fléchés (R2 de pose, 2 x R6). Les autres sont dans les sous-titres et la note 9. L'arête cassée est dans la note 1. |
| 05-23 | Tableau des ajours avec son origine. |
| 05-26, 05-28 | Tous les nombres passent par `D.fmt` / `P.fr` (virgule). Note historique et doublons supprimés. |
| 05-27 | Les attaches du 68 sont les axes des encoches. |
| 05-29 | Paroi et trous retirés de la vue du crochet. La paroi est décrite par la note 8 et le sous-titre. |
| 05-31 | Titres à distance régulière. Le tiers droit de la feuille est utilisé. |
| conc-10, D4 | BRUT_TOLE dans le cartouche, EXIGENCE_TOLE en note. |
| conc-11, conc-24, D15 | Cote 48,2 de la dent, « A CONFIRMER » dans le sous-titre, alerte en gras. |
| conc-15, D5 | Note des ajustements rapportés à e, et NOTE_TOLE_REELLE. |
| conc-43, D9 | Encoche de bec de 4 cotée (détail D). |
| 05-25 | Entraxe des fentes et distance des crochets aux parois dans la note 7. |

Les constats « non_verifie » ont été contrôlés sur le code et sur le rendu d'avant : `avant_full.png`, `vals.txt` pour la géométrie relevée segment par segment. Ils étaient exacts. Une seule correction : les constats décrivent encore l'ancienne langue (saillie 8, gorge 3), alors que MODELE est déjà passé à 9 / 4 (D9).

## Écartés, avec la raison

- **Vue « encoche du flanc » (05-17, 05-18, 05-24, 05-30, et le report du 30 proposé en 05-09)** : vue **supprimée** plutôt que corrigée.
  - Elle répétait les cotes 8,4 et 8 du flanc, définies planche 01, détail W.
  - Elle était fausse : vu selon y, le pied passe DEVANT le flanc et cache son encoche ; ce n'était ni une coupe ni une vue cachée.
  - Le montage reste décrit par la note 6 (renvoi au détail W) et par la planche 00, dont l'élévation porte la garde au sol de 30.
- **Tolérances serrées « 8,4 +0,1/0 », « 7,8 0/-0,1 » (05-06)** : non portées.
  - Avec la tôle mesurée et EP_TOLE_REELLE réglé (D5), la tolérance ISO 2768-m de ±0,2 garde tous les ajustements bons : jeu de 0,2 à 0,6, serrage de 0 à 0,2 par côté.
  - Une tolérance de ±0,1 n'est de toute façon pas garantie par une découpe laser.
  - La note 3 donne les ajustements rapportés à e.
- **Correction de `draw._ligne_cote`, `cote_h`, `cote_v` (05-07, 05-08)** : non faite. Ce sont des fonctions partagées, et mon mandat sur draw.py se limite aux ajouts. La planche 05 ne les appelle plus.
- **Échelles 3:1, 3:5 et 1:3 proposées (05-03, 05-19)** : remplacées par 1:2, 2:1 et 5:1, qui sont normalisées.
- **Cote 12 du corps du crochet (05-05, 05-16)** : remplacée par **21** hors tout et **9** au détail D, d'où 12 se déduit. La face y = 0 n'a aucune arête sur le dessus : coter 12 obligeait à tirer une attache à travers la langue.
- **Dent cotée « 4,5 + 38° » (05-05)** : remplacée par les hauteurs d'arête 6,84 et 2,16, mesurables au pied à coulisse ; 38° figure dans le sous-titre. Les deux cotes ensemble feraient doublon.
- **(491,6) en cote auxiliaire (05-25)** : la valeur est mise en note. Elle se déduit de 510, 5 et 8,4. En cote, l'axe de fente servant d'attache aurait croisé la cote 510.
- **Cotes des ajours sur la vue 1:2 (05-11)** : remplacées par un tableau, plus lisible.
- **Rayon fléché sur chaque congé (05-22)** : seulement pour les rayons fonctionnels (R2 de pose) et pour R6. Les autres sont en sous-titre et en note, pour ne pas surcharger.
- **conc-23 (supprimer le chanfrein)** : D3 garde l'arête cassée, la note 1 la reprend.
- **Paroi en trait mixte dans le détail de langue (05-29)** : non dessinée. Elle passait dans la gorge, où se trouvent les cotes 5 et 4. La note 8 et le sous-titre du crochet la décrivent.

## Ce qui reste

1. **Défaut de modèle trouvé en testant (hors périmètre, pour MODELE).**
   - Constat : `verifie()` déclare l'étuve valable de 530 à 553 (commentaire de params.py et modele.md). Or `crochet_profile()` ne se construit plus au-delà d'environ 551,7 : à 552 et 553, la construction échoue sur « crochet sommet 2 : conge R3.00 trop grand ». La cause : entre la dent et l'angle R3 haut de l'appui, il reste moins de 3 mm. plans.py plante alors.
   - Correction proposée : dans verifie(), la borne de la dent doit être `CROCHET_S - CROCHET_DENT_B/2 - 3` (le R3 de l'angle), au lieu de `- 2`, soit une étuve d'au plus 551.
   - Essais faits (`etuve_bornes.py`) : le profil se construit de 530 à 550, il échoue à 552 et 553. La planche, régénérée à 530 et à 550, donne 0 faute.
2. **Position horizontale des colonnes de trous de l'étuve** : aucun paramètre ne la décrit. La note 7 dit ce qu'il faut vérifier (crochets à 24,2 des parois latérales, entraxe 491,6) : à confirmer avec l'étuve, comme sa largeur.
3. **Congés du pied et du crochet sans paramètre** (6, 2, 0,5, 1, 3, écrits en dur dans parts.py). La planche les lit sur le profil ; leur créer des paramètres relève de MODELE.
4. **Le bas-gauche de la feuille est libre.** On peut y ajouter un croquis de montage à mi-bois si l'utilisateur le souhaite ; j'ai préféré renvoyer aux planches 00 et 01.

## Contrôles (état final)

| contrôle | résultat |
|---|---|
| `python plans.py` | sans erreur |
| `python verif_plans.py` | 0 faute sur les 8 planches (729 textes, 97 sur la 05) |
| `python params.py` | 0 problème |
| `python verif_percages.py` | 0 faute |
| `chk01.py 05_pied 0.25` (tous traits, fins compris) | 0 remarque (97 textes, 2054 traits) |
| `chk_croix.py 05_pied` | 0 croisement (82 traits fins) |
| SVG 00-04, 06, 07 et draw.py | identiques à la copie témoin |
| plans.py hors du bloc | identique au témoin, LF, ASCII |
| robustesse (copie `bac/`) | EP_TOLE_REELLE = 8,25 : 8,65 / 8,05 / 19,68 partout, 0 faute. Étuve 530 et 550 : dent 43,2 / 53,2, 0 faute. ETUVE_CONFIRMEE = True : alerte retirée, « confirmée », 0 faute. |
| rendu | `scratchpad/planches/05_pied.png` |

Relecture finale du rendu, découpe par découpe, comme un contrôleur :
- planche entière ;
- pied, moitié gauche puis moitié droite ;
- crochet ;
- détails A, B, C et D ;
- tableau, notes, cartouche ;
- zoom x5 sur l'axe central et le texte 510.

Résultat :
- aucun texte n'est traversé ;
- aucune attache ne croise un texte ou une autre cote ;
- les lignes parallèles sont à 8 mm ;
- toutes les cotes sont hors pièce, sauf trois au détail B : 20 et la chaîne 6 / 8, posées sur le montant faute de tout autre chemin d'attache. Le détail W de la planche 01 fait de même.
