# Planche 06_petites : compte rendu de l'agent PETITES (02/10/2026)

## Fichiers touchés

- `plans.py` : seulement le bloc qui va de `def plan_petites():` à `def seg_tourne(sg):` (exclu). Il contient la nouvelle `plan_petites()` et sept aides locales préfixées `p06_` : `p06_titre`, `p06_ligne`, `p06_poly`, `p06_ajustement`, `p06_parallelisme`, `p06_famille`, `p06_rayon_coin`. Hors de ce bloc, plans.py est identique à la copie témoin (`correction/petites/temoin/plans.py`, diff limité aux lignes 1559-1720). Le fichier reste en LF et en ASCII.
- `draw.py` : **non modifié**. La planche n'utilise que les ajouts ISO déjà présents : `cote_hx`, `cote_vx`, `renvoi`, `zone`, `rayon`, `axe` et `Sheet.motif`. Elle n'appelle plus `cote_h`, `cote_v` ni `note`.
- SVG 00 à 05 et 07 : identiques à l'octet près à ceux d'avant mon travail.
- Outils, dans `scratchpad/correction/petites/` :
  - `p06_new.py`, la source du bloc ;
  - `splice.py` et `run.sh`. run.sh enchaîne splice, plans, verif_plans, params, `../flanc/chk01.py`, `../traverse/chk_croix.py`, la comparaison des autres SVG et de draw.py, puis le rendu ;
  - `robust.py`, les essais de robustesse (paramètres changés en mémoire, sortie dans `robust/`, rien n'est écrit dans le projet) ;
  - `crop.py` et les découpes : `avant_full.png` (état d'avant), `f_full.png`, `g_A.png`, `f_C.png`, etc.

## Nouvelle planche

**Cartouche**, entièrement lu dans les PartSpec, `nomenclature.REPERES` et params :
- titre « TOURILLON, ENTRETOISES, PLAQUES » ;
- rep. 06 ;
- matière « C45+C / E235+C / CuZn (achat) » ;
- brut « rond 25 h9 / tube 20 x 4,5 » ;
- quantité « 1 + 9 + 1 + 1 (06a a 06d) » ;
- échelle « 2:1 - plaque 06c/06d 1:1 ».

Toutes les échelles sont vraies et normalisées. Chaque titre de vue porte son échelle.

Le titre long « ..., ENTRETOISE DE CADRE, PLAQUE DE FROTTEMENT » a été essayé puis raccourci. `Sheet.cartouche` réduit la hauteur du titre en comptant 0,55 h par caractère, alors qu'une capitale grasse en fait environ 0,60. Au-delà d'environ 37 caractères, le titre déborde donc sur la case « rep. », et verif_plans ne le voit pas. Je l'ai constaté sur le rendu.

**06a TOURILLON (2:1)**. Sous-titre : « C45+C, 1 ex. » et « brut rond etire 25 h9 x 76 ».
- Contour chanfreiné à TOURILLON_CHANFREIN. Les arêtes chanfrein / cylindre sont en trait fort.
- Axe : il ne dépasse que de 3 mm.
- Cotes **76** et **diam. 25 h9**. Leurs attaches sont prises aux angles vifs fictifs, si bien qu'elles se rejoignent au coin sans se croiser.
- Renvoi fléché sur le chanfrein, à gauche dans le vide : « 1,5 x 45 deg / aux 2 bouts ».

**06b ENTRETOISE DE CADRE, COUPE AXIALE (2:1)**. Sous-titre : « E235+C EN 10305-1, 9 ex. » et « brut tube de precision 20 x 4,5 ».
- Les deux parois coupées sont hachurées (motif `p06_h`).
- Cotes **60 +0,1/0** (D11), **diam. 11** et **diam. 20**, sous la pièce, à 8 mm l'une de l'autre, la plus petite au plus près.
- Renvoi fléché sur la face d'about : « 2 faces dressees / paralleles a 0,05 ».

**06c / 06d PLAQUE DE FROTTEMENT (1:1)**, une seule vue. Sous-titre :
- « piece du commerce : norelem 23765-01-038100 » ;
- « CuZn25Al5Mn4Fe3-C + graphite, epaisseur 5 » ;
- « 1 dessus (06c) + 1 dessous (06d), identiques ».

La vue montre :
- les trous, qui étaient jetés jusque-là ;
- les axes, dont l'axe de symétrie vertical : les trous sont à ±35 du milieu ;
- les cotes **100**, **38** (attaches aux angles vifs fictifs) et **70** (attaches dans le prolongement des axes des trous) ;
- le renvoi fléché **2 x diam. 9** ;
- **(4 x R4)** en cote auxiliaire. Le rayon est lu sur le profil, puisqu'aucun paramètre ne le donne.

**Notes** (4 lignes, toutes calculées) :
1. 06a : flottant, il centre la pile 02e. Rond étiré h9 NON repris, avec un jeu d'au moins 0,4 dans les diam. 25,4 de la pile et des alésages. Le jeu vaut ALESAGE_D - TOURILLON_D.
2. 06b : 7 entretoises serrées chacune par une V1 (vis TH M10 x 100 + écrou autofreiné tout métal), les 2 de la chape par les V9 (vis H M10 x 200). Ces nombres viennent de n_entretoises et TROU_SUPPORT, les longueurs de ENTR_VIS_L et SUPPORT_TIRANT_L.
3. 06b : la longueur 60 +0,1/0 fixe l'écart des flancs, il faut couper les 9 en série. Ne pas confondre avec 07b (même tube, L 71,5, planche 07).
4. 06c / 06d : pièces du commerce. Elles se posent entre les rebords du coin 02c, larges de 7,05 dessus et 8,15 dessous (avec virgule). Leurs trous sont remplis de silicone HT.

Aucune valeur n'est écrite en dur quand un paramètre existe :
- « h9 » est lu dans le brut du PartSpec ;
- « 0,05 » est lu dans la note du PartSpec de l'entretoise ;
- R4 est lu sur le profil ;
- les matières, bruts, quantités et repères sont lus dans les PartSpec et dans REPERES.

## Constats appliqués

| constat | ce qui est fait |
|---|---|
| 06-01, 06-13 (vérifié : exact avant correction), conc-39, docu-07 | « diam. 25 h9 ». Matière et brut lus dans parts : la planche et la nomenclature disent désormais la même chose (C45+C, rond étiré h9). La consigne « NON repris » est dans la note 1. |
| 06-03, 06-12, 06-17, conc-06, conc-19, docu-13 | Quantités calculées depuis all_parts (1 + 9 + 1 + 1). Repères 06a / 06b / 06c / 06d dans les titres, quantité par pièce dans les sous-titres. 06b est distinguée de 07b (note 3). |
| 06-04, 06-05 (partie planche), 06-12, conc-46 (3), docu-12 (partie planche) | La « tige filetée M10 » a disparu. La note 2 donne V1 / V9 et lit les longueurs dans params (V1 x 100 et écrou ISO 7042, réglés par MODELE). |
| 06-06, conc-47, D11 | « 60 +0,1/0 » (ENTRETOISE_TOL) ; faces dressées, parallèles à 0,05 ; tube EN 10305-1 E235+C dans le sous-titre et le cartouche. |
| 06-07, 06-08 | Toutes les cotes passent par cote_hx / cote_vx. Le texte d'une cote verticale est à gauche de sa ligne et n'est plus barré. |
| 06-09, 06-02 (rejeté sur la gravité, mais le défaut existait) | Trous dessinés, entraxe 70, « 2 x diam. 9 », axes. |
| 06-10, 06-18 | Chanfrein dessiné (TOURILLON_CHANFREIN). Le renvoi fléché passe à gauche, il ne surplombe plus l'entretoise. |
| 06-11, 06-15 | « 20 / 11 » est remplacé par deux cotes diam. 11 et diam. 20 sur une coupe, où l'alésage est un trait vu. Préfixe « diam. », comme sur les planches 02 et 04. |
| 06-14, 06-20 | Les axes dépassent de 3 mm (2 mm pour l'axe de symétrie de la plaque) et ne touchent plus aucun texte. |
| 06-16, 06-21 | Une seule vue de plaque, au 1:1. « cotes SUR LA PENTE » est supprimé. |
| 06-19, 06-23 (vérifié : exact) | Brut complet. Virgule décimale partout (D.fmt). |
| 06-22 (vérifié : exact) | Les trois vues sont réparties sur toute la largeur, avec les titres alignés sur une ligne et le haut des pièces aligné. Les deux pièces de révolution sont passées au 2:1. |

## Écartés, avec la raison

- **Ø et ° en UTF-8 (06-11)** : non appliqués.
  - Ils obligeraient à changer `Sheet.save`, partagé par toutes les planches, et `index_html`.
  - Le projet écrit « diam. » et « deg » partout (planches 02 et 04 déjà corrigées).
- **Correction de `draw._ligne_cote` (06-07, 06-08)** : non faite. C'est une fonction partagée. La planche 06 ne l'appelle plus.
- **Cote « 25 f8 » (variante de 06-01)** : écartée. Le h9 étiré non repris suffit (jeu de 0,4 à 0,66) et c'est ce que dit parts.py.
- **« +0,2/0 » (06-06) et « E235+N » (06-19)** : remplacés par D11, soit +0,1/0 et E235+C.
- **R4 en cote ferme (06-02, 06-16)** : porté en cote auxiliaire (4 x R4).
  - C'est une pièce achetée, que sa référence définit.
  - Le rayon n'est pas un paramètre : il est lu sur le profil de parts.py, qui le suppose.
- **Vue de chant de la plaque pour l'épaisseur** : non dessinée. L'épaisseur 5 est donnée dans le sous-titre (« note explicite »).
- **Report de la phrase sur les rebords vers la planche 02 (06-23)** : non fait, car c'est la planche d'un autre agent. La phrase reste ici, en note 4, parce qu'elle explique pourquoi la même plaque sert dessus et dessous.
- **Mises en page proposées dans les constats (06-02, 06-09, 06-16, 06-21, 06-22)** : remplacées par la mienne. Plusieurs créaient des chevauchements, que les vérificateurs avaient d'ailleurs signalés.
- **Titres longs proposés (« 06b entretoise de cadre, 9 ex. », etc.)** : la quantité est passée dans le sous-titre.
- **Matière S355JR du tourillon (consigne conc-39)** : non imposée par la planche, qui lit `TOURILLON_MATIERE`. MODELE l'a mise à C45+C, choix qu'il signale « à valider ». Essai fait : avec S355JR, la planche suit (`robust.py`, cas s355jr, 0 faute).

## Ce qui reste

1. **Matière du tourillon à trancher** : C45+C (MODELE) ou S355JR (consigne conc-39). Une seule ligne à changer dans params.py (`TOURILLON_MATIERE`) ; la planche et la nomenclature suivent.
2. **Cales de rattrapage V4** (diam. 50 / 26, ép. 1 et 2, « feuillard acier ») : elles n'ont aucun plan. Si on les découpe au lieu de les acheter, on peut ajouter une petite vue sur la 06, où le bas gauche est libre. Décision à prendre.
3. Le parallélisme 0,05 et le rayon R4 n'ont pas de paramètre : la planche les lit dans parts.py (note et profil). On pourrait créer `ENTRETOISE_PARALLELISME` et `PLAQ_R`.
4. `Sheet.cartouche` sous-estime la largeur du titre gras (0,55 h par caractère au lieu d'environ 0,60). Un titre de plus de 37 caractères visibles déborde sur la case « rep. », sans que verif_plans le voie. Toutes les planches tiennent aujourd'hui, la 07 de justesse.
5. out/plans/plans.pdf n'est pas régénéré par plans.py (make.py).

## Contrôles (état final)

| contrôle | résultat |
|---|---|
| `python plans.py` | sans erreur |
| `python verif_plans.py` | 0 faute sur les 8 planches (739 textes, 44 sur la 06), complétude bonne |
| `python params.py` | 0 problème |
| `python verif_percages.py` | 0 faute |
| `chk01.py 06_petites 0.25` (tous les traits, fins compris, contre tous les textes) | 0 remarque (44 textes, 263 traits) |
| `chk_croix.py 06_petites` | 3 croisements, tous des croix d'axes voulues au centre des trous et au milieu de la plaque ; aucune attache ni ligne de cote croisée |
| SVG 00-05, 07 et draw.py | identiques à la copie témoin |
| plans.py hors du bloc | identique au témoin, LF, ASCII |
| robustesse (`robust.py`, en mémoire) | nominal, TOURILLON_MATIERE = S355JR, ENTR_SOMMET = False (1 + 8 + 1 + 1, note « 6 serrees »), PLAQ_TROU_L1 = 60 avec chanfrein 1, TOURILLON_L = 80 : 0 faute chaque fois |
| rendu | `scratchpad/planches/06_petites.png` |

Relecture finale du rendu, découpe par découpe, comme un contrôleur :
- planche entière ;
- tourillon, avec zooms x2,5 et x3 sur les deux coins chanfreinés ;
- entretoise, avec zooms sur la face d'about et les cotes de diamètre ;
- plaque, avec zooms sur les deux coins et le renvoi des trous ;
- notes et cartouche.

Résultat :
- aucun texte n'est traversé ;
- aucune attache ne croise une autre attache, une cote ou un texte ;
- les lignes de cote parallèles sont à 8 mm ;
- toutes les cotes sont hors de la pièce.
