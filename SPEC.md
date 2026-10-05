# Banc de flexion 3 points - specification

Indice B du 05/10/2026. Fichier engendre par `spec.py` a partir de `params.py`,
du calcul elements finis et du modele 3D. Ne pas le modifier a la main.

## 1. Objet

Fissuration controlee d'une poutrelle beton non arme instrumentee fibre
optique, en etuve jusqu'a 150 degres C, avec correlation d'images sur une
face laterale. Le cadre est auto-reactif : aucune reaction exterieure. Il
travaille COUCHE sur la paillasse et DEBOUT, sur son about, dans l'etuve
(voir `DEBOUT.md`).

## 2. Eprouvette et renfort

| grandeur | valeur |
|---|---|
| Poutrelle | 103 x 107 x 840 mm, beton non arme |
| Plats de renfort colles | 2 x 20 x 2 x 840, feuillard S235 du commerce, a y = +/- 34 (axe des flancs) |
| Colle | epoxy haute temperature (Duralco 4420) |
| Axe neutre de la section homogeneisee | 50.86 mm au dessus de la face inferieure |
| Inertie homogeneisee | 1.21e+07 mm4 |
| Effort a la fissuration (beton a 4 MPa) | 5.07 kN |
| Fleche a la fissuration | 0.123 mm |

Le renfort rend la fissuration progressive et pilote l'ouverture. Il
descend l'axe neutre de 2.6 mm par rapport au beton nu.

Les deux plats, les quatre patins d'appui et le patin de charge sont colles
sur la poutrelle et partent avec elle : il en faut un jeu par eprouvette.

## 3. Chargement

| grandeur | valeur |
|---|---|
| Schema | 3 points, portee 750 mm |
| Charge de dimensionnement du cadre | 12 kN |
| Commande | coin d'acier C45 a 12 deg garni de deux plaques de bronze du commerce, tige filetee M16 pas 2.0 normale aux flancs |
| Pile de rondelles | 12 x DIN 2093 A50 (50 x 25.4 x 3.0), montees tete-beche |
| Hauteur libre de la pile | 51.6 mm |
| Effort de la pile a plat | 18.5 kN |
| Course totale | 15.6 mm |
| Ecrasement a 12 kN | 9.65 mm (raideur secante 1243 N/mm) |
| Butee de course en bas de lumiere | 11.8 mm, plafonne l'effort a 14.4 kN |
| Rattrapage d'empilement | 2.4 mm de course en reserve au dela des 12 kN (2 exiges) ; cales de 1 et 2 mm, D50 / D26, entre poussoir et pile |
| Precharge de collage, 0,5 kN | 0.36 mm de pile, 1.68 mm de coin, 0.84 tour de tige apres le contact |

La loi des rondelles Belleville n'est pas lineaire. Graduation gravee :

| charge | descente du coulisseau |
|---|---|
| 2 kN | 1.45 mm |
| 4 kN | 2.97 mm |
| 6 kN | 4.55 mm |
| 8 kN | 6.19 mm |
| 10 kN | 7.89 mm |
| 12 kN | 9.65 mm |

Cette lecture est un indicateur a quelques pour cent pres : elle englobe la
souplesse propre du cadre (0.335 mm a 12 kN) et la fleche de la poutre.
La mesure de reference est la fibre collee sur la membrure haute.

## 4. Appuis

Les flancs sont RENTRES sous les plats de renfort : ils portent dessous, et
la face laterale de la poutrelle reste entierement degagee pour la camera.

| poste | cote |
|---|---|
| Largeur de la poutrelle | 103 |
| Debord de la poutrelle de chaque cote | 13.5 |
| Epaisseur d'un flanc | 8 |
| Ecart interieur entre flancs | 60 (impose par les rondelles 50) |
| Largeur hors tout des flancs | 76 |
| Face inferieure libre au centre | 48 (passage du cable) |

Le contact se fait au FOND de la rainure du patin, 1.5 mm au dessus de sa
face inferieure.

| grandeur | valeur |
|---|---|
| Patins d'appui | 90 x 20 x 10, S355JR, colles en place |
| Rainure de guidage | 9.5 x 1.5, fraisee apres decoupe, jeu 0.75 par cote sur la tole reelle |
| Bossage | R150, relief 3.5, largeur totale 66.6 |
| Pression de Hertz a 12 kN | 339 MPa sur 6.4 mm portants (flanc de 8 moins ses deux aretes cassees de 0.8) |
| Limite au contact a 150 degres C | 480 MPa, 1,6 Re a chaud du corps le plus mou (le patin S355JR) ; coefficient 1.42 |
| Pression sur le beton sous un patin | 1.67 MPa |
| Bras contact - axe neutre | 61.36 mm |

Le bossage est un BALANCIER, pas un galet. Il donne une ligne de contact
nette et laisse tourner la poutrelle, mais il n'absorbe pas le recul de
0.060 mm de la fibre basse a la fissuration, qui passe en frottement et
coute quelques pour cent sur le moment. Pour le supprimer il faudrait un
vrai galet libre sur une des deux lignes d'appui.

Les patins sont colles sur le plat par leur face SUPERIEURE seulement : la
rainure reste seche sur le bossage, qui doit pouvoir basculer.

## 5. Empilement vertical

z = 0 au bord inferieur du flanc.

| z | element |
|---|---|
| 40.0 | dessus de la membrure basse |
| 42.0 | dessous du patin d'appui |
| 43.5 | sommet du bossage, fond de rainure, point de contact |
| 52.0 | dessous du plat de renfort |
| 54.0 | face inferieure de la poutrelle |
| 161.0 | face superieure de la poutrelle |
| 171.0 | dessus du patin de charge |
| 195.0 | dessus du poussoir |
| 246.6 | dessous du coulisseau, pile libre |
| 236.9 | dessous du coulisseau a 12 kN |
| 276.6 | dessus du coulisseau, pile libre |
| 323.7 | dessous de la traverse a tenons, plan de glissement du coin |
| 420.0 | dessous de la membrure haute |
| 440.0 | hors tout |

Encombrement des flancs 960 x 440 x 76 mm. Selon y, le banc va de -85.5
(coin recule) a +160 (bout des vis de chape), soit 245.5 mm ; les pieds font 518.4.
Etuve 538 x 538 x 1400 mm (largeur confirmee, hauteur a confirmer) : le cadre y travaille DEBOUT sur son
about, pose par deux pieds en V sur quatre crochets pendus aux parois ; sur
la paillasse il travaille couche sur deux pieds. Voir `DEBOUT.md`.

## 6. Flanc en treillis

Le moment est triangulaire et la profondeur du treillis suit, donc l'effort
dans la membrure haute est constant sur toute sa longueur.

| membre | section | valeur |
|---|---|---|
| Membrure haute | 20 x 8 | 7.58 kN de traction, 47.4 MPa |
| Bielles | 35 x 8, pente 17.97 degres | compression |
| Montants | 45 x 8 | traction |
| Membrure basse | 40 x 8 | moment constant de 180 N.m entre appuis |
| Profondeur du treillis | 148.4 mm | |

Calcul elements finis CalculiX, 259107 noeuds, elements du second ordre,
charge de 6000 N au noeud, appuis glissants sur les deux bossages :

| grandeur | valeur |
|---|---|
| von Mises maxi | 213 MPa |
| Coefficient a froid, 42CrMo4 +A (Re 430) | 2.02 |
| Coefficient a 150 degres C (Re 390) | 1.83 |
| Fleche du flanc | 0.335 mm |
| Flambement hors plan, mode symetrique (fem_flamb3, 22/09/2026) | facteur 39.0 couche, 39.1 debout, avec les 9 entretoises |
| Flambement, flancs en sens contraire (fem_flambement, 18/09/2026) | facteur 31.9 au moins : calcul fait avant les entretoises de chape et de sommet, qui ne peuvent que le relever |

Points les plus charges :

| x | z | von Mises | zone |
|---|---|---|---|
| -420 | 30 | 213 MPa | membrure basse sous le montant, cote appui ; encoche de pied du coin voisine |
| 420 | 30 | 187 MPa | membrure basse sous le montant, cote appui ; encoche de pied du coin voisine |
| -30 | 390 | 187 MPa | angle de la mortaise de traverse, arete ou portent les tenons |
| -390 | 30 | 130 MPa | console d'appui sous le bossage |
| 390 | 30 | 125 MPa | console d'appui sous le bossage |
| 30 | 270 | 103 MPa | ligament entre la fente du coin et la lumiere |
| -30 | 270 | 103 MPa | ligament entre la fente du coin et la lumiere |
| -60 | 240 | 90 MPa | angle bas du noeud |

La piece est symetrique, le calcul donne pourtant 213 MPa d'un cote et 187
de l'autre : c'est l'ordre de grandeur du bruit de maillage a l'appui, et
l'on retient la plus forte valeur.

Le point chaud est dans la membrure basse sous le montant, pas sur l'arc
du conge R22 du raccordement membrure basse / montant.
Un balayage du rayon de R10 a R26 (fem_balayage.py, 16/09/2026, sur le flanc de
l'epoque) donne 151 a 160 MPa sans tendance : c'est du bruit de maillage,
le rayon n'est pas le levier.

NUANCE ET EPAISSEUR. Le cadre est en tole de 8 mm 42CrMo4, etat recuit +A
(Re 430, 390 a 150 C). L'EN 10083-3 ne garantit a l'etat +A qu'une durete
maximale, pas de limite elastique : toute la marge du flanc repose sur Re,
qui est donc EXIGE a la commande -- 42CrMo4 recuit +A, tole 8 mm : certificat 3.1 EN 10204 avec essai de traction, Re >= 430 MPa a 20 C.
Le flanc travaille a 213 MPa a l'appui : 2.02 de coefficient a froid, 1.83 a
150 C, contre 1,91 a chaud pour le cadre precedent en 10 mm S355 (157 MPa)
et 35.3 kg de cadre au lieu de 44,5.
Si la tole de 8 en 42CrMo4 manque, le repli est le 10 mm S355 ou S460 :
EP_FLANC = 10 et tout suit.

## 7. Tete de charge

Chaine d'effort, de haut en bas : traverse a tenons portee par la mortaise
des flancs, coin de commande qui glisse sous elle sur ses plaques de bronze,
coulisseau guide par les tetes de quatre CHC M8 dans les lumieres, pile de
rondelles sur tourillon flottant, poussoir, patin de charge colle. La
reaction remonte par les montants et les bielles dans la membrure haute,
qui travaille en traction.

| piece | remarque |
|---|---|
| Traverse | 6 plaques de tole 8, tenons dans la mortaise des flancs, chant du bas fraise en paquet |
| Coulisseau | S355JR, dessus incline sur TOUTE sa section ; un bloc, sans tenon |
| Guidage | 4 tetes de CHC M8 x 12 ISO 4762, tete lisse, diametre 13, dans des lumieres de 14 ; taraudages M8 prof. 16 |
| Poussoir | 3 plateaux de tole 8 perces, reperes par 2 goupilles 8 m6 serrees dans le patin de charge, qui fait fond |
| Tourillon | C45+C, rond etire 25 h9 non repris, flottant, engage de 12.2 mm dans chaque alesage au repos |
| Tige filetee | immobile axialement dans la chape, le coin est son ecrou |
| Butee de course | bas de la lumiere, interdit l'aplatissement de la pile |

## 7 bis. Commande par coin

L'etuve fait 538 x 538 x 1400 (largeur confirmee) et n'offre aucun passage de paroi
utilisable. Le cadre y est debout : un axe de vis dans le plan des flancs
regarderait une paroi a 49 mm, inaccessible. La commande est donc NORMALE
AUX FLANCS. Un coin en ACIER, qui porte le taraudage, coulisse selon y entre
le dessous plat de la traverse et le dessus du coulisseau taille au meme
angle. Le coin ne se deplace que selon y : son dessus reste plaque sous la
traverse, donc l'axe de la vis est fixe.

| grandeur | valeur |
|---|---|
| Angle | 12 degres |
| Coin | acier C45, 40 de large, 30.8 a 55.2 d'epaisseur, 114.5 de long |
| Plaques de frottement | 2 plaques du commerce norelem 23765-01-038100, 38 x 100 x 5, CuZn25Al5Mn4Fe3-C + graphite, 0.30 kg en tout |
| Course utile | 56.5 mm selon y |
| Position de repos | bout epais a y -85.5, bout mince a y 29 |
| Sens de marche | vers la chape ; en fin de course le bout mince est a y 85.5 |
| Depassement hors cadre | 47.5 mm, d'un cote au repos, de l'autre en fin de course |
| Vis | M16 pas 2.0, taraudee dans le coin, immobile axialement |
| Effort moteur a 12 kN | 5.5 kN |
| Couple sur la vis | 9.4 N.m |
| Course par tour | 0.425 mm de coulisseau, environ 549 N |
| Pression de contact, fin de course | 7.7 MPa en haut sur 30.0 x 51.8 (joints de traverse deduits), 6.5 MPa en bas sur 38 x 48.6 ; 35 admis |
| Rendement | 46 pour cent |

Le coin n'est autobloquant que si le frottement de ses deux faces depasse
0.106 (tan a / 2) : avec le bronze graphite a chaud (0.12) on y est a peine,
on ne compte donc pas dessus. C'est la vis M16 qui tient la charge, son
angle d'helice etant tres inferieur a l'angle de frottement. Le filet est
de l'acier sur acier monte a la pate cuivre, et le cas dangereux est le
frottement BAS : a 0.08, helice 2.48 degres contre 5.28 degres de frottement
apparent, marge x2.13.

C'est pourquoi le filet reste METRIQUE a pas de 2 et non trapezoidal.
Au meme frottement de 0.08, un Tr16x4 tomberait a une marge de 0.91 :
il serait REVERSIBLE, et il doublerait le pas de charge a 1099 N par tour.
A pas egal, le profil trapezoidal ne gagne rien non plus : sa hauteur de
recouvrement vaut 0,5 P contre 0,541 P pour le metrique, soit MOINS de
flanc portant. Les flancs travaillent a 9.2 MPa, engagement plafonne a
1,5 d, pour 12 admis sur un taraudage C45 et une tige 8.8 en manoeuvre lente.

Le filet est TARAUDE DIRECTEMENT DANS L'ACIER du coin. Une bague-ecrou en
bronze a ete dessinee puis abandonnee : a la vitesse de manoeuvre d'un
banc a la main, ce n'est pas la vitesse qui use un filet, et le couple
tige 8.8 sur C45 brut tient sans probleme monte a la pate cuivre. La tige
est la plus dure : c'est le taraudage du coin qui s'use, et il se refait.
Il ne court que sur 80 mm et non sur toute la longueur du coin ; au dela
le percage est repris a 18, si bien que le taraud debouche dans un trou
plus grand : les copeaux s'evacuent vers l'avant et il n'y a que 5 d a
tarauder au lieu de 7. Si le filet devait un jour lacher, le lamage
d'une bague de bronze reste possible : rien ici n'est irreversible.

LE BRONZE N'EST PLUS QUE DEUX PLAQUES DU COMMERCE, TOUTES DEUX SUR LE COIN.
Un coin de bronze plein aurait demande 2,7 kg de barre, une section qu'il
faut faire debiter. Or le bronze n'est utile que sur les deux faces de
glissement : il est reporte sur deux plaques de frottement autolubrifiantes
norelem 23765-01-038100 (38 x 100 x 5), et le coin devient un bloc d'acier C45
de 1.37 kg, usine dans un plat 65 x 45, L 120 (fini 61 x 40 x 114,5).

La basse pourrait etre posee sur la pente du coulisseau, ou elle ne ferait
que 58 de long au lieu de 100. Elle est mise sur le coin comme la
haute : le coulisseau redevient un bloc nu -- un percage et un plan a 12
degres, ni poche ni taraudage -- les deux faces d'usure sortent ensemble
avec le coin, et c'est deux fois le meme rebord a usiner. Ce que cela
coute : la plaquette basse traverse la fente du flanc avec le coin, qui
s'approfondit donc de 5.1 mm.

Aucune vis : le coin ne fait que 40 de large et le percage de la tige en
prend le milieu, il ne reste pas de quoi noyer une tete fraisee a un
ligament d'epaisseur. Chaque plaquette est prise entre DEUX REBORDS usines
dans la masse, 7.05 (dessus) et 8.15 (dessous) x 3, qui encaissent les 1.44 kN
d'entrainement dans l'axe de la vis : flexion 6.5 MPa au pied, matage du chant 12 MPa.
Elles ne sont PAS collees a l epoxy. Bronze et acier ne se dilatent pas
pareil : a 150 C la plaquette s allonge de 0.08 mm de plus que son siege,
et un joint rigide sur toute la longueur encaisserait 30 a 80 MPa de
cisaillement en bout pour 15 a 20 tenus : il fissurerait au premier
chauffage. Les rebords prenant tout l entrainement, la fixation n a plus
qu a tenir la plaquette le temps du montage : quelques points de silicone
haute temperature, 1000 fois plus souple, y suffisent -- 0.141 MPa de
cisaillement thermique dans le joint. Aucune pate sur les plaques ni sur
leurs sieges : elles sont autolubrifiantes, et le silicone ne prend pas sur
une pate.

Pied de rebord DEGAGE et non conge : l'angle vif de la plaquette doit
porter sur toute la hauteur. Et sur la face inclinee, la face interieure
du rebord est NORMALE A LA PENTE et non verticale, comme le chant de la
plaquette : dessinees verticales, elles la mordaient de 1.1 mm en bas.

Les rebords s'arretent 2 mm SOUS la surface du bronze. Aux deux bouts de
course ils passent sous la conjuguee, et s'ils affleuraient ce serait de
l'acier sur acier qu'on ferait glisser. Il en coute de la portee : la
plaquette haute porte sur 51.8 mm au lieu de 60, la basse sur 48.6 au
lieu de 58, soit 7.7 et 6.5 MPa.

Le filet reste engage sur 24.5 mm coin recule, soit 1.5 d, ce qui est
tout ce qui porte : au dela de 1,5 d, l'ecart de pas entre la tige et le
taraudage fait que les derniers filets ne prennent plus rien.

Le coin traverse les deux flancs par une fente de 44 x 69, entre les
deux lumieres de guidage reportees a x = +/- 44. Il reste alors 58 mm
de section nette dans le noeud, soit 12.9 MPa nominal pour les 6000 N par flanc.

La suppression de la vis verticale a ramene la hauteur du cadre de 480 a
440 mm : debout dans l'etuve de 538, il reste 49 mm de chaque cote, ou se
logent les pieds en V et les crochets. Elle a aussi permis de descendre le
noeud : la profondeur du treillis passe de 139,5 a 148.4 mm.

### Sens de montage du coin, et arret axial de la tige

Le bout EPAIS du coin est du cote OPPOSE a la chape : le coin avance donc
VERS elle en chargeant. C'est ce sens, et lui seul, qui rend l'arret axial
de la tige possible. L'equilibre du coin le montre : la composante selon y
de la reaction du coulisseau, plus les deux frottements, valent 5.5 kN, et
la tige doit les fournir. La face inclinee repousse le coin vers son bout
EPAIS : le filet tire donc la tige vers l'INTERIEUR du cadre, et sa tete
vient appuyer sur la FACE EXTERIEURE des platines, a travers la butee a
aiguilles. Cote interieur, deux rondelles trempees et deux ecrous minces ne
reprennent que l'effort de desserrage : 329 N a un frottement de 0.12, quand
le coin est autobloquant ; en dessous de 0.106 la charge le chasse d'elle-meme
et ils ne voient rien.

Monte a l'envers, le coin s'eloignerait de la chape en chargeant : la tige
serait tiree hors de son alesage et ne pousserait rien. Il faudrait alors
loger la butee a aiguilles entre les platines et le bout du coin, ou elle
ne tient pas. Le controle des cotes refuse ce sens.

### Position de repos du coin

Le coin est dessine au repos bout mince AFFLEURANT le bord du coulisseau,
et non centre sur lui. C'est la seule position qui garde le contact sur
toute la largeur du coulisseau d'un bout a l'autre de la course. Centre au
repos, le coin aurait glisse a moitie hors du coulisseau en fin de course :
appui reduit a 29 mm au lieu de 58, pression doublee, et surtout
resultante decalee de 14.5 mm, donc basculement de la tete sur la pile.
Le prix a payer est que le bout mince atteint y 85.5 en fin de course, ce
qui fixe la position de la chape de butee.

## 7 ter. Butee axiale de la tige

Le coin avance VERS la butee en chargeant et tire la tige vers l'interieur
du cadre ; la tete de la tige pousse donc la butee, et les platines, contre
le flanc : platines en flexion, entretoises en compression, aucune piece de
la butee ne travaille en traction. Il n'y a aucune raison d'usiner une chape
dans la masse. Deux platines de la MEME tole que les flancs, portees par deux
entretoises du MEME tube que le cadre, de part et d'autre de la vis, dans le
plan de son axe. Deux vis H M10 x 200 traversent platines, entretoises de
butee, LES DEUX flancs et une entretoise de cadre entre eux, tete derriere
le flanc oppose, ecrou cote platines : plus aucun taraudage dans le flanc,
et deux entretoises de plus entre les flancs. Elles ne voient que la
precharge et les 329 N de desserrage.

| grandeur | valeur |
|---|---|
| Platines | 2 x tole 8, 70 de haut au droit de l'alesage, 140 de long |
| Flexion d'une platine | 130 MPa, coefficient 3.3 a froid, 3.0 a 150 C, fleche 0.139 mm |
| Entretoises de butee | tube de precision 20 x 4,5, L = 71.5 +/-0,2, 12.6 MPa de COMPRESSION chacune |
| Fixation | 2 vis H M10 x 200 ISO 4014 (filetees sur 32) a x = +/- 52, z 302.7, tete et 1 rondelle derriere le flanc oppose, 4 rondelles + 2 ecrous H contre-bloques cote platines |
| Serrage sous tete | 173.5 mm, filet a partir de 168 : ecrou sur le filet avec 5.5 de marge, 9.7 de depassement |
| Serrage | 35 N.m, aucun taraudage : les vis traversent les deux flancs |
| Butee a aiguilles | AXK 1730 + 2 rondelles AS 1730, a plat sur la face EXTERIEURE, centree par la tige |
| Retenue interieure | 2 rondelles trempees AS 1730 + 2 ecrous HM M16, 18 mm, desserrage seulement |
| Bout de tige | y 155, soit 94 mm de degagement pour la douille, cadre decentre au pire dans l'etuve de 538 (114 centre) |
| Manoeuvre | douille de 24 et cliquet SEULEMENT : les bouts des vis de chape (y 160) depassent la tete de manoeuvre dans son plan, une cle plate bute dessus |

Tout sort du debit deja commande : les platines nichent dans la tole de 8
des flancs, les entretoises sont coupees dans le meme tube que celles du
cadre. Rien a usiner. Les vis traversent LES DEUX flancs, avec une
entretoise de cadre entre eux : la commande se monte du cote que l'on veut,
en retournant le coin, et les deux percages servent dans les deux cas.

Une entretoise de sommet, dans l'axe a z 411, au dessus de la mortaise de
traverse : la membrure haute n'avait aucune liaison sur 500 mm et c'est la
que partait le mode de voilement symetrique. Meme tube de 60, meme vis TH
M10 x 100 que les autres entretoises de cadre. Ce n'est PAS un serrage des
flancs sur le paquet de traverse : le tube de 60 fixe l'ecart des flancs,
et les epaulements de la traverse gardent 0.4 de jeu selon y (0.2 de chaque
cote) : la traverse n'est jamais pincee.

Boulonnerie M10 du cadre, toutes longueurs controlees par `verifie()` sur la
tole reelle (EP_TOLE_REELLE) : l'ecrou doit tomber sur le filet avec 2.5 de
marge et le bout depasser de 3 pour que le freinage soit en prise.

| boulonnerie | serrage | ecrou | depassement | marge de filet |
|---|---|---|---|---|
| vis de cadre TH M10 x 100 | 80.0 | 10 | 10.0 | 6.0 |
| tige filetee M10 x 90 de traverse | 52.0 | 10 | 9.0 | - |
| vis de chape H M10 x 200 | 173.5 | 16.8 | 9.7 | 5.5 |

Ecrous de cadre et de traverse : ISO 7042 classe 8, autofreine tout metal. Pas d'ecrou a bague polyamide
(ISO 7040, DIN 985) : la bague flue vers 120 C et ne freine plus a 150 C.
7 vis de cadre (4 de coin, 2 de bielle, 1 de sommet) et 2 vis de chape
serrent les 9 entretoises.

## 8. Instrumentation

| poste | valeur |
|---|---|
| Fibre sur le chant de la membrure haute | 18.8 microdeformations par kN |
| Resolution a 1 microdeformation | 53 N |
| Lecture mecanique | position du coulisseau dans la lumiere |
| Correlation d'images | face laterale degagee sur 840 x 107 mm |

Il n'y a pas de col de mesure : la membrure pleine donne deja une
resolution suffisante, et un col serait une entaille de plus.

## 9. Masses

Masses du modele 3D (out/masses.json, construit le 05/10/2026).

| piece | qte | masse unitaire | total |
|---|---|---|---|
| Flanc en treillis | 2 | 10.21 kg | 20.41 kg |
| Plaque de traverse | 6 | 0.26 kg | 1.54 kg |
| Plateau de poussoir | 3 | 0.32 kg | 0.97 kg |
| Coulisseau a tete inclinee | 1 | 1.45 kg | 1.45 kg |
| Vis de guidage CHC M8 x 12 | 4 | 0.01 kg | 0.05 kg |
| Tourillon de centrage | 1 | 0.29 kg | 0.29 kg |
| Coin de commande | 1 | 1.37 kg | 1.37 kg |
| Plaque de frottement, dessus | 1 | 0.15 kg | 0.15 kg |
| Plaque de frottement, dessous | 1 | 0.15 kg | 0.15 kg |
| Tige filetee de commande M16 | 1 | 0.41 kg | 0.41 kg |
| Platine de butee de la vis | 2 | 0.45 kg | 0.90 kg |
| Entretoise de butee | 2 | 0.12 kg | 0.25 kg |
| Patin d'appui rainure | 4 | 0.13 kg | 0.52 kg |
| Patin de charge | 1 | 0.77 kg | 0.77 kg |
| Plat de renfort colle | 2 | 0.26 kg | 0.52 kg |
| Entretoise tubulaire | 9 | 0.10 kg | 0.93 kg |
| Pied a mi-bois | 4 | 0.87 kg | 3.48 kg |
| Crochet d etuve | 4 | 0.17 kg | 0.69 kg |
| Pile de 12 rondelles Belleville | 1 | 0.41 kg | 0.41 kg |
| Poutrelle beton | 1 | 22.22 kg | 22.22 kg |

**Cadre complet 35.3 kg**, poutrelle 22.2 kg.

## 10. Conduite d'essai

- rampes thermiques sous 0,2 degres C par minute : avec 107 mm d'epaisseur,
  une rampe de 1 degre par minute creee deja 5 MPa d'ecart entre coeur et peau
- palier de stabilisation d'au moins 2 heures avant toute lecture
- acier nu ou phosphate, pas de zingue au dela de 200 degres C
- pate graphite ou cuivre sur le filetage de la tige, rien sur les plaques de bronze
- relaxation des rondelles de quelques pour cent au dela de 100 degres C :
  reprendre la charge a chaque palier
- revetement de la fibre a verifier : l'acrylate standard ne tient pas 150 degres C
- manoeuvre a la douille de 24 et au cliquet

## 11. Points ouverts

- **Hauteur d'etuve 1400, a confirmer.** La largeur 538 est confirmee : elle
  place la dent du crochet a 47.2 de la paroi ; pied et crochet sont a decouper.
- **Epaisseur reelle de la tole** : mesurer la tole livree, regler EP_TOLE_REELLE et regenerer les DXF avant decoupe (EP_TOLE_REELLE = 8 pour une
  tole nominale de 8). Encoches, nodes, fentes, mortaise et rainures des
  patins en derivent ; le 3D et le calcul restent a la cote nominale.
- **Calage de la poutrelle debout** : rien ne la retient selon x, devenu
  vertical, que le frottement aux appuis. Point ouvert, assume : voir
  `DEBOUT.md`, paragraphe 6.
