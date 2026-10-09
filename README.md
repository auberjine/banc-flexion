# Banc de flexion 3 points auto-reactif

Poutrelle beton non arme 103 x 107 x 840, portee 750, capacite 12 kN, pour
fissuration controlee en etuve avec fibre optique et correlation d'images.

Cadre 960 x 440 x 76 mm (flancs), 35,2 kg. Flancs et platines de butee en tole
de 8 mm 42CrMo4 recuit +A, commandee avec certificat 3.1 et Re >= 430 MPa ;
pieds, crochets, plaques de traverse et plateaux du poussoir en tole de 8 mm
S355JR du commerce (seul le flanc a besoin du 42CrMo4). Tout est parametrique : une cote
se change dans `params.py`, et `make.py` refait le 3D, les DXF, les plans et la
notice. Indice B du 05/10/2026.

## Ce qu'il y a dans `out/`

| dossier | contenu |
|---|---|
| `banc_3d.html` | visionneuse 3D autonome, double-clic, aucune installation |
| `fcstd/banc.FCStd` | assemblage FreeCAD, une piece par objet |
| `step/*.step` | geometrie exacte, une piece par fichier, plus l'assemblage |
| `stl/*.stl` | maillages ; `*_montes.stl` contient tous les exemplaires places |
| `dxf/*.dxf` | profils de DECOUPE, contours fermes, arcs exacts ; la traverse y est au brut (surepaisseur a fraiser) |
| `dxf/tole_*.dxf` | tous les exemplaires d'une epaisseur et d'une nuance, ranges en etageres de 3000 mm de large au plus : controle de quantites, pas une imbrication |
| `dxf/*_EN_ATTENTE.dxf` | pieces a NE PAS decouper encore, si `ETUVE_CONFIRMEE` est faux (aucune depuis le 05/10/2026 : largeur de 538 confirmee) |
| `dxf/LISTE.txt` | fichiers, epaisseur, nuance, quantite et statut ; signification des calques |
| `plans/*.svg` | une feuille A3 cotee PAR PIECE fabriquee (`<repere>_<piece>.svg`, cartouche a son repere), plus l'ensemble (00) et le montage de la chape (07m) |
| `plans/plans.pdf` | les memes feuilles en un seul PDF, dans l'ordre des reperes |
| `plans/pdf/*.pdf` | un PDF par feuille, au nom de la feuille (`pdf_feuilles.py`, lance par `make.py`) |
| `masses.json` | masse, volume, matiere et brut de chaque piece |
| `fem_flanc.json` | resultat du calcul elements finis du flanc |
| `flambement3.json` | flambement hors plan, mode symetrique (le facteur a retenir) |
| `iso.json` | projection isometrique de l'assemblage, utilisee par les plans |

`export_dxf.py` vide `out/dxf` avant d'exporter et `build_freecad.py` vide
`out/step` et `out/stl` : aucun fichier d'une generation precedente n'y survit.

Les documents de tete sont `SPEC.md` (engendre, ne pas editer a la main),
`NOMENCLATURE.md` (engendree : commande, visserie, ordre de montage, changement
d'eprouvette) et `DEBOUT.md` (acces a la vis en position verticale et ce que
cette position impose). `SUITE.md` est un HISTORIQUE : la revue du 11/09 et la
suite qui lui a ete donnee.

## Reconstruire

```
python make.py
```

Enchaine le controle des cotes et des ligaments de percage, le modele 3D
FreeCAD (STEP, STL, masses, projection), les DXF, les plans et leur controle de
lisibilite, le PDF des planches, la visionneuse, la nomenclature, la
specification et le controle d'interference ; il termine par le nombre
d'etapes en echec, qui doit etre 0. Il faut Python 3 avec Pillow et openpyxl, FreeCAD 1.0
(`freecadcmd`) et un navigateur Chromium sans interface (Edge, Chrome ou
Chromium) pour le PDF. `outils.py` les trouve, sous Windows comme sous Linux :
variable d'environnement `BANC_FREECAD`, `BANC_CCX` ou `BANC_NAVIGATEUR`
d'abord, puis l'emplacement Windows habituel, puis le PATH.

Avant de lancer une decoupe : mesurer SEPAREMENT les deux toles livrees,
regler `EP_TOLE_REELLE_42` (42CrMo4) et `EP_TOLE_REELLE_S355` (S355JR) dans
`params.py` et regenerer les DXF. Chaque decoupe suit la tole qu'elle RECOIT :
S355 pour les encoches a mi-bois et la mortaise de traverse du flanc et les
fentes de calage du pied ; 42CrMo4 pour les encoches et nodes du pied et les
rainures des patins. Le 3D et le calcul restent a la cote nominale.

Pour refaire seulement les plans et leur PDF (make.py le fait deja) :

```
python plans.py
"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless --no-pdf-header-footer --print-to-pdf=out/plans/plans.pdf out/plans/plans.html
```

Sous Linux : `chromium --headless --no-sandbox --no-pdf-header-footer
--print-to-pdf=out/plans/plans.pdf out/plans/plans.html`. Pour relire les
planches a l'oeil, `python rendu_planches.py` les rend en PNG dans `out/rendus/`.

Pour le calcul elements finis, en deux temps parce qu'il dure plusieurs minutes :

```
freecadcmd fem_flanc.py        (sous Windows : "C:/Program Files/FreeCAD 1.0/bin/freecadcmd.exe")
python fem_run.py
```

Le premier maille et ecrit le fichier CalculiX, le second y injecte la charge
nodale, lance le solveur et depouille le `.frd`.

## Les fichiers source

| fichier | role |
|---|---|
| `params.py` | toutes les cotes, la loi des rondelles Belleville, les calculs (Hertz, coin, filet, platines, tenons, boulonnerie) et les verifications |
| `geom2d.py` | geometrie 2D : contours, conges, bossages, gorges, lumieres |
| `parts.py` | profil de chaque piece et nomenclature du modele : matiere, brut, notes d'operations, pieces du commerce |
| `build_freecad.py` | construction 3D, exports STEP / STL, masses |
| `export_dxf.py` | DXF de decoupe, sans FreeCAD : la liste des pieces plates vient de `parts.all_parts()`, les pieces du commerce n'en ont pas |
| `dxf.py` | ecriture DXF R12 |
| `draw.py` | primitives de dessin technique : vues, cotes, cartouche (indice et date) |
| `plans.py` | les feuilles de plan, une par piece ; `draw.Sheet.fin_piece()` recentre chaque dessin au-dessus des notes |
| `viewer3d.py` | visionneuse 3D autonome : maillages ET three.js (`vendor/three.min.js`, r160) embarques dans `out/banc_3d.html`, qui s ouvre sans reseau |
| `spec.py` | engendre `SPEC.md` depuis le modele |
| `nomenclature.py` | engendre `NOMENCLATURE.md` |
| `nomenclature_xlsx.py` | engendre `out/NOMENCLATURE.xlsx` depuis `NOMENCLATURE.md` (un onglet par tableau, montage ; masses totales en formules) |
| `fem_flanc.py`, `fem_run.py` | calcul elements finis du flanc |
| `fem_balayage.py` | balaye un parametre par le calcul EF (remaille, resout, restaure) ; resultat dans `out/balayage_<param>.json` |
| | `fem_run` refuse un `.inp` deja charge, et ne charge que l arete DROITE |
| | maille de 4,5 mm : a 6 mm l angle d appui variait de 149 a 164 MPa d un calcul a l autre ; a 4,5 mm il converge aux deux appuis. `BANC_MAILLE=<mm>` impose une autre taille sans toucher au fichier |
| | le mode rigide en x est bloque sur UN SOMMET : bloquer une face epingle tous ses noeuds et raidit la tole (197 puis 145 MPa d artefacts au bord de la face) |
| | tole de 8 mm en 42CrMo4 recuit (Re 430, 390 a chaud) : flanc a 213 MPa a l appui (187 a l autre appui de cette piece symetrique : bruit de maillage), 2,02 a froid et 1,83 a 150 C, contre 1,91 a chaud pour le 10 mm S355 ; cadre de 35,2 kg au lieu de 44,5 ; repli EP_FLANC = 10 en S355 ou S460 |
| `fem_flambement.py` | flambement hors plan du flanc (CalculiX *BUCKLE, maille 9 mm), bornes : diaphragmes seuls (pieds, poutrelle ; les tubes negliges) et tubes tenus en z (mode antisymetrique, 31,9 le 18/09, avant les entretoises de chape et de sommet). `--seul x:z ...` essaie des appuis supplementaires |
| `fem_flamb3.py` | le facteur A RETENIR : mode symetrique (les deux flancs penchent ensemble), chaque tube est un ressort de rotation 6EI/L sur sa couronne serree. 13,7 couche avec les six entretoises d'origine, 33,1 avec les deux de chape, 39,0 couche et 39,1 debout avec celle du sommet (9 en tout) ; 38,2 / 38,3 avec les tubes 20 x 2 retenus le 06/10. Une plaque de 600 au dessus ne le porte qu'a 41,9 : inutile |
| `verif_interference.py` | controle d interference sur l assemblage, et des CONTACTS obligatoires |
| `verif_percages.py` | ligaments : chaque percage face aux autres et au contour ; largeur des fentes et des encoches ouvertes du contour |
| `verif_plans.py` | planches : textes superposes, hors feuille ou traverses par un trait (traits fins compris, boite orientee) ; chaque piece nommee sur une planche |
| `pdf_feuilles.py` | decoupe `plans.pdf` en un PDF par feuille dans `out/plans/pdf/` (pypdf) |
| `rendu_planches.py` | rend les planches en PNG (`out/rendus/`) pour les relire a l'oeil |
| `outils.py` | chemins des outils externes (FreeCAD, CalculiX, navigateur), Windows et Linux ; empreinte du modele et date des resultats |

`params.py` porte une fonction `verifie()` qui controle l'empilement vertical,
la course de la pile et du coin, la butee, le contact de Hertz, la place du
bossage sous le patin, la tete de charge, la chape, la boulonnerie M10 (ecrou
sur le filet, bout qui depasse), les bruts d'usinage et l'etuve (douille, pieds,
crochets). `python params.py` l'execute et affiche le bilan.

## Points de conception a ne pas defaire

- **Les flancs sont rentres sous les plats colles.** C'est ce qui degage
  entierement la face laterale de la poutrelle pour la camera. Un flanc au ras
  de la face ne porterait rien.
- **Le contact a lieu au fond de la rainure du patin**, 1,5 mm au dessus de sa
  face inferieure. Tout l'empilement en decoule.
- **Le bossage est un balancier, pas un galet.** Il laisse tourner la poutrelle
  mais n'absorbe pas le recul de 0,06 mm de la fibre basse, qui passe en
  frottement.
- **Le bossage ne porte que sur 6,4 mm** : l'epaisseur du flanc moins ses deux
  aretes cassees. Hertz y vaut 339 MPa, a comparer a 1,6 Re a chaud du corps le
  plus mou, le patin S355JR (480 MPa) : coefficient 1,42.
- **Le bas de la lumiere est une butee de course.** Il interdit d'ecraser la
  pile a plat et plafonne l'effort a 14,4 kN.
- **Le conge R22 au raccordement membrure basse / montant n'est pas le
  levier.** Le point chaud est dans la membrure basse sous le montant, pas sur
  l'arc : un balayage EF de R10 a R26 (16/09/2026, sur le flanc de 10 mm S355
  de l'epoque) donne 151 a 160 MPa sans tendance, du bruit de maillage.
- **Les patins se collent en place**, cadre monte, sous 0,5 kN de precharge.
  C'est l'epoxy qui rattrape l'hyperstaticite des quatre contacts. Colle sur la
  face superieure seulement : la rainure reste seche sur le bossage, qui doit
  basculer. Patins, plats et patin de charge partent avec la poutrelle : un jeu
  par eprouvette.
- **La vis de commande ne bouge pas.** Vis H M16 x 160 ISO 4017 filetee
  jusqu'a la tete : elle tourne en place, retenue axialement dans la chape, et
  c'est le coin qui porte le taraudage et avance. Sa tete reste donc toujours a
  y 137,5, ou une douille l'atteint. Une douille seulement : les bouts des vis
  de chape, a y 160, arretent une cle plate.
- **La commande est normale aux flancs.** Un coin d'acier C45 a 12 degres,
  garni de deux plaques de bronze usinees, coulisse entre le dessous PLAT de
  la traverse et le dessus incline du coulisseau. Le sens des faces est
  essentiel : c'est lui qui fait que le coin ne se deplace que selon y et que
  l'axe de la vis reste fixe. Voir `DEBOUT.md`.
- **Le noeud fait 65 mm de demi-largeur** et porte quatre ouvertures : la fente
  du coin au centre, les deux lumieres de guidage a x = +/- 44 et, plus haut,
  la mortaise de traverse ; les deux trous
  des vis de chape sont au dessus, a x = +/- 52. C'est la zone la plus
  sollicitee apres les appuis. Ne pas y ajouter d'ouverture : il reste 14 mm de
  ligament du cote du bord du noeud et 15 du cote de la fente.
- **Le coin est au repos bout mince affleurant le coulisseau, pas centre.**
  C'est la seule position qui garde le contact sur toute la largeur du
  coulisseau d'un bout a l'autre de la course. Le centrer ferait glisser le
  coin a moitie dehors en fin de course, et la tete basculerait sur la pile.
  C'est aussi ce qui fixe la profondeur de la chape. Voir `DEBOUT.md`.
- **Le dessus du coulisseau est incline sur TOUTE sa section.** La piece fait
  donc 36,2 de haut et non 30 : 30 est l'epaisseur au milieu. Les bruts du
  coulisseau et du coin se calculent sur la boite englobante de la piece finie
  (`parts.bruts_usinage`).
- **Le bout EPAIS du coin est du cote oppose a la chape.** Le coin avance donc
  vers elle en chargeant. La face inclinee le repousse vers son bout epais : le
  filet tire la tige vers l'INTERIEUR du cadre, et sa tete appuie sur la FACE
  EXTERIEURE des platines, a travers deux rondelles trempees. Monte a
  l'envers, la tige serait tiree hors de son alesage et ne pousserait rien :
  c'est le seul sens qui marche, et `verifie()` le controle.
- **Le jeu en largeur de la mortaise vaut DEUX FOIS le rayon de ses conges.**
  L'arete portante droite fait alors exactement la largeur du paquet de tenons.
  Le paquet cumule six fois la tolerance d'epaisseur de tole : la mortaise est
  taillee sur la tole S355 mesuree des plaques (`EP_TOLE_REELLE_S355`), pas sur
  la cote nominale.
- **Les coins de la mortaise sont des CONGES, pas des degagements d'angle.** Un
  os de chien ne se justifie que si la piece conjuguee doit porter dans l'angle.
  Ici le paquet a 2 mm de jeu par cote, et le degagement creusait une entaille
  au bout de la ligne d'appui : 209 MPa au calcul EF contre 130 (flanc de 10).
- **Les pieds de tenon portent un DEGAGEMENT, jamais un conge** -- traverse
  comme coulisseau. Un conge a un angle rentrant ajoute de la matiere dans
  l'angle : il deborde de l'epaulement et vient mordre la face du flanc.
  `geom2d.relief_ll()` fait cela, `Contour.add(..., relief=True)` l'appelle.
- **`COULISSEAU_E` n'est PAS `POUSSOIR_H`.** Depuis que le poussoir est un
  empilage de tole, ce sont deux cotes sans rapport. Les confondre dans
  `f_coulisseau` a laisse 5,9 mm de jeu entre le coin et le coulisseau pendant
  deux versions : la chaine d'effort etait ouverte dans le modele et aucun
  controle ne bronchait, un jeu n'etant pas une interference.
- **`verif_interference.py` verifie aussi les CONTACTS obligatoires.** La liste
  `CONTACTS` suit l'effort du coin jusqu'aux appuis ; c'est elle qui garantit
  que la chaine est fermee. Y ajouter tout nouveau maillon.
- **L'epaisseur du coulisseau ne tient pas a la contrainte** (5,2 MPa de
  compression pure) mais a deux details : 5 mm de matiere au dessus des
  taraudages de guide du cote MINCE de la pente, et un chapeau au dessus de
  l'alesage du tourillon. `verifie()` controle les deux.
- **La graduation de charge se lit sur le HAUT DE TETE de guide**, pas sur le
  dessus du coulisseau, invisible entre les flancs. La tangente superieure du
  cylindre se lit comme une bulle de niveau. Elle n'est gravee que d'un cote de
  la lumiere : face gravee de chaque flanc montee a l'exterieur.
- **Le coulisseau est guide par les TETES de quatre CHC M8 x 12 ISO 4762**,
  tete lisse, vissees apres coup au travers des lumieres. Un cylindre sur un
  plan porte sur une ligne : il ne peut pas se coincer en biais et il encaisse
  les defauts angulaires. Ne pas revenir a des tenons prismatiques, et ne pas
  mettre de vis a tete fraisee.
- **La tete de CHC M8 fait 13 x 8** : le 8 est exactement l'epaisseur du
  flanc. C'est ce qui rend le montage possible, `verifie()` le controle. La
  longueur d'une CHC se compte SOUS la tete : les 12 mm entrent tout entiers
  dans le taraudage de 16. Une x 20 y talonnait et laissait la tete hors de sa
  face.
- **On visse les guides APRES avoir ferme le cadre.** C'est tout l'interet :
  plus de tenons a engager a l'aveugle en presentant le second flanc.
- **Le chant du bas des plaques de traverse se fraise EN PAQUET**, plaques
  serrees sur leur tirant et alignees sur les faces hautes des tenons. C'est le
  plan de glissement du coin : une plaque en saillie de 0,1 mm deviendrait une
  charge lineique sur le bronze. Le DXF porte 1 mm de surepaisseur sur ce chant.
- **Les pieces de tole n'ont AUCUN chanfrein au modele** (09/10/2026) :
  aretes ebavurees seulement. Un STEP a aretes vives passe mieux dans les
  analyseurs des sites de decoupe. Les calculs gardent 0,8 non portant a
  chaque bord (`CHANFREIN`) : bossage, plaque de bronze sous la traverse,
  tenons.
- **Les trois plateaux du poussoir sont PERCES** : c'est le patin de charge
  colle qui fait fond sous le tourillon. `verifie()` exige ALESAGE_P == POUSSOIR_H.
  Ils sont serres en un bloc par deux vis H M6 x 35, TETE EN DESSOUS : sous le
  plateau bas il n'y a que les 10 du patin au sommet du bombe jusqu'a la
  poutrelle, une tete de 4 y tient, un ecrou non. Le patin de charge, sans
  trou, est raccourci selon x (PATIN_CHARGE_L, tire de POUSSOIR_VIS_X) pour
  laisser passer les tetes ; `controle_vis_poussoir()` en verifie les gardes.
  Le bloc n'est pas localise sur le patin : le tourillon le centre.
- **La butee de vis est POUSSEE, pas tiree.** C'est une consequence du sens de
  montage du coin, et c'est ce qui permet de la faire en tole : deux platines
  de 8 sur deux entretoises tubulaires, en compression. Si l'on remontait le
  coin a l'envers, il faudrait revenir a une chape usinee.
- **Ecrous autofreines TOUT METAL (ISO 7042)** sur la visserie M10 du cadre :
  une bague polyamide flue vers 120 C et ne freine plus dans l'etuve. Toutes
  les longueurs de vis sont controlees par `verifie()` (`params.boulonnerie`).
- **`verif_percages.py` fait partie de `make.py`.** Il refuse tout ligament
  inferieur a 0,8 fois l'epaisseur, et toute fente ou encoche du contour plus
  etroite que la demi-epaisseur. C'est lui qui a trouve l'entretoise de coin
  centree sur l'arete du flanc et l'ajour qui recoupait un trou de pied.
