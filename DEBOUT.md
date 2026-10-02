# Position debout : commande normale aux flancs

Etuve 540 x 540 x 1400 mm utiles (A CONFIRMER), aucun passage de paroi
utilisable. La poutrelle est verticale, le cadre repose sur son about bas par
deux pieds en V, poses sur quatre crochets pendus aux parois.

| direction | cote du cadre | cote d'etuve | degagement |
|---|---|---|---|
| verticale | 960 ; 969,5 avec les pieds en V | 1400 | 430 mm en tout, partages entre dessus et dessous selon la hauteur des crochets |
| axe des 440 mm du cadre | 440 ; 447 entre les aretes de pose des pieds en V | 540 | 50 mm de chaque cote du cadre, ou se logent les pieds en V et les crochets |
| epaisseur du cadre | 76 aux flancs ; 245,5 avec le coin et la chape (y -85,5 a +160) ; pieds de 510 | 540 | 232 mm de chaque cote des flancs ; 15 aux bouts des pieds |

Toute la place est dans la direction de l'EPAISSEUR du cadre. La commande doit
donc y arriver, en traversant les flancs.

Les chiffres ci-dessous sont ceux de l'indice A (02/10/2026). Ceux qui changent
avec une cote sont aussi dans `SPEC.md` et `NOMENCLATURE.md`, qui se
regenerent : en cas d'ecart, ce sont eux qui font foi.

## 1. Pourquoi un coin, et pas autre chose

Un axe de vis dirige vers les parois laterales est inaccessible, quoi qu'on
mette au bout : il reste 50 mm, que les pieds en V et les crochets occupent
deja. Trois solutions sans mecanisme ont ete ecartees, toutes pour la meme
raison : barre, cle ou volant balaient le plan perpendiculaire a l'axe, celui
qui contient l'epaisseur du cadre, et heurtent les flancs des 30 mm de rayon
(le demi-ecart des flancs). Un volant est de toute facon limite a 60 mm de
diametre par l'ecart entre flancs, soit 6 N.m quand il en faut 9,4.

Un renvoi d'angle a roue et vis sans fin a d'abord ete monte, puis remplace par
le coin : le coin fait le meme travail avec moins de pieces et une vis en prise
directe.

## 2. Ce qui est monte

Un coin en ACIER C45, taraude M16, coulisse selon y entre le DESSOUS PLAT de la
traverse et le DESSUS du coulisseau taille au meme angle. Ses DEUX faces de
glissement portent une plaque de bronze du commerce.

Le sens des faces est ce qui rend le montage possible : si le coin glissait sur
une rampe fixe, il descendrait en avancant et la vis devrait suivre ce mouvement
vertical. Avec le dessus du coin plat sous la traverse, le coin ne se deplace
que selon y, et l'axe de la vis reste fixe.

| grandeur | valeur |
|---|---|
| Angle | 12 degres |
| Coin | acier C45, 40 de large, 30,8 a 55,2 d'epaisseur, 114,5 de long |
| Plaque haute | norelem 23765-01-038100, bronze graphite 38 x 100 x 5, entre deux rebords de 7,05 |
| Plaque basse | la meme plaque, sur la pente, entre deux rebords de 8,15 |
| Taraudage | M16 sur 80 mm depuis le bout epais, passage a 18 au dela |
| Course utile | 56,5 mm selon y |
| Effort moteur a 12 kN | 5,5 kN |
| Couple sur la tige | 9,4 N.m |
| Course par tour | 0,425 mm de coulisseau, environ 549 N |
| Pression de contact, fin de course | 7,7 MPa en haut (30 nets x 51,8), 6,5 en bas (38 x 48,6) |
| Guidage | 4 tetes de CHC M8 x 12, diametre 13, dans des lumieres de 14 |
| Rendement | 46 pour cent |

LE BRONZE N'EST PLUS QUE DEUX PLAQUES DU COMMERCE, TOUTES DEUX SUR LE COIN. Un
coin de bronze plein aurait pese 2,7 kg de barre, une section qui ne se trouve
pas en stock ; les deux plaques autolubrifiantes en font 0,30 kg. La plaque
basse pourrait etre posee sur la pente du coulisseau, ou elle ne ferait que 58
de long au lieu de 100 ; la mettre sur le coin rend le coulisseau a l'etat de
bloc nu -- un percage et un plan a 12 degres, ni poche ni taraudage -- fait
sortir les deux faces d'usure ensemble avec le coin, et n'oblige a usiner que
deux fois le meme rebord. Ce que cela coute : la plaque basse traverse la fente
du flanc avec le coin, qui s'approfondit donc de 5,1 mm.

Le filet est taraude DIRECTEMENT DANS L'ACIER. A la vitesse de manoeuvre d'un
banc a la main, ce n'est pas la vitesse qui use un filet, et le couple tige 8.8
sur C45 brut tient monte a la pate cuivre. La tige est la plus dure : c'est le
taraudage qui s'use, et il se refait. Il ne court que sur 80 mm ; au dela le
percage est repris a 18, si bien que le taraud debouche dans un trou plus grand
et qu'il n'y a que 5 d a tarauder au lieu de 7. Si le filet devait un jour
lacher, le lamage d'une bague de bronze reste possible.

AUCUNE VIS SUR LES PLAQUES : le coin ne fait que 40 de large et le percage de
la tige en prend le milieu, il ne reste pas de quoi noyer une tete fraisee a un
ligament d'epaisseur. Chaque plaque est prise entre DEUX REBORDS usines dans la
masse, 7,05 (dessus) et 8,15 (dessous) de large pour 3 de haut, qui encaissent
les 1,44 kN d'entrainement dans l'axe de la vis : flexion 6,5 MPa au pied,
matage du chant 12 MPa. Il n'y a pas de colle structurale : une epoxy
fissurerait au premier chauffage, bronze et acier ne se dilatant pas pareil.
Quelques points de silicone haute temperature tiennent la plaque pendant le
montage ; la dilatation differentielle n'y met que 0,14 MPa de cisaillement.
Aucune pate sur les plaques ni sur leurs sieges : elles sont autolubrifiantes,
et le silicone ne prend pas sur une pate.

Pied de rebord DEGAGE et non conge : l'angle vif de la plaque doit porter sur
toute la hauteur. Sur la face inclinee, la face interieure du rebord est
NORMALE A LA PENTE et non verticale, comme le chant de la plaque : dessinees
verticales, elles la mordaient de 1,1 mm en bas.

Les rebords s'arretent 2 mm SOUS la surface du bronze. Aux deux bouts de course
ils passent sous la piece conjuguee, et s'ils affleuraient ce serait de l'acier
sur acier qu'on ferait glisser. Ils coutent de la portee : la plaque haute
porte sur 51,8 mm au lieu de 60, la basse sur 48,6 au lieu de 58.

Le coin n'est autobloquant que si le frottement de ses deux faces depasse
0,106 (tan 12 / 2) : avec le bronze graphite on y est a peine, on ne compte
donc pas dessus. C'est la tige M16 qui tient la charge, son angle d'helice
(2,5 degres) etant tres inferieur a l'angle de frottement, meme au frottement
bas d'un filet acier sur acier monte a la pate cuivre (0,08 : 5,3 degres,
marge x2,1).

Le bout de la tige sort a y 155. Dans l'etuve de 540, cadre centre, il reste
115 mm jusqu'a la paroi ; 95 si le cadre est decentre au pire (les pieds de 510
laissent 15 mm de chaque cote, plus 5 de marge). Une douille de 24 et un
cliquet y passent. Une douille SEULEMENT : les vis de chape depassent de leur
ecrou jusqu'a y 160, a 52 mm de l'axe de la tige et dans son plan ; une cle
plate posee sur la tete de manoeuvre bute dessus deux fois par tour.

## 3. Sens de montage du coin, et arret axial de la tige

Le bout **epais** du coin est du cote **oppose a la chape** : le coin avance
donc VERS elle en chargeant. Ce sens, et lui seul, rend l'arret axial de la
tige possible.

L'equilibre du coin le dit : la composante horizontale de la reaction du
coulisseau, plus les deux frottements, valent 5,5 kN, et c'est la tige qui doit
les fournir. La face inclinee repousse le coin vers son bout EPAIS : le filet
tire donc la tige vers l'**interieur** du cadre, et sa tete vient appuyer sur
la **face exterieure** des platines, a travers la butee a aiguilles. Cote
interieur, deux rondelles trempees et deux ecrous minces ne reprennent que le
desserrage : 329 N quand le coin est autobloquant, rien en dessous.

Monte a l'envers, le coin s'eloignerait de la chape en chargeant : la tige
serait tiree hors de son alesage et ne pousserait rien. Il faudrait alors loger
la butee a aiguilles entre les platines et le bout du coin, ou elle ne tient
pas. `params.verifie()` refuse ce sens.

## 3 bis. Position de repos du coin, et ce qu'elle impose

Le coin est monte au repos **bout mince affleurant le bord du coulisseau**, et
non centre sur lui. C'est la seule position qui garde le contact sur toute la
largeur du coulisseau d'un bout a l'autre de la course : centre au repos, le
coin aurait glisse a moitie hors du coulisseau en fin de course, avec un appui
de 29 mm au lieu de 58, une pression doublee et surtout une resultante decalee
de 14,5 mm, donc une tete qui bascule sur la pile de rondelles.

Le prix a payer est que le bout mince atteint y 85,5 en fin de course, soit
47,5 mm hors du flanc. Le bout epais sort autant de l'autre cote au repos.
C'est cette cote qui fixe la profondeur de la chape.

## 4. La butee de la vis

Le coin tire la tige vers l'interieur ; sa tete pousse la butee, donc les
platines, contre le flanc. Platines en flexion, entretoises en compression :
rien ne travaille en traction, il n'y a donc rien a usiner. Deux platines de la
meme tole de 8 que les flancs, portees par deux entretoises du meme tube que le
cadre, de part et d'autre de la vis, dans le plan de son axe.

| grandeur | valeur |
|---|---|
| Platines | 2 x tole 8, 70 de haut au droit de l'alesage, 140 de long |
| Flexion d'une platine | 130 MPa, coefficient 3,3 a froid et 3,0 a 150 C, fleche 0,14 mm |
| Entretoises | tube de precision 20 x 4,5, L = 71,5 +/- 0,2, **12,6 MPa de compression chacune** |
| Fixation | 2 vis H M10 x 200 filetees sur 32, a x = +/- 52 dans le plan de l'axe de vis ; tete et 1 rondelle derriere le flanc oppose, 4 rondelles + ecrou H ISO 4032 (8,4) cote platines. Empilement sous tete 173,5, filet a partir de 168 : l'ecrou tombe sur le filet avec 5,5 de marge, la vis depasse de 18,1 |
| Serrage | 35 N.m, aucun taraudage : les vis traversent les deux flancs et une entretoise de cadre |
| Butee a aiguilles | AXK 1730 + 2 rondelles AS, a plat sur la face EXTERIEURE |
| Retenue interieure | 2 rondelles trempees AS 1730 (17 x 30 x 1) + 2 ecrous HM : 329 N au desserrage seulement |

Quatre rondelles sous l'ecrou : l'empilement additionne quatre toles et deux
tubes coupes. Avec deux rondelles il faisait 169,5 pour un filet qui commence a
168 ; avec trois, une tole mesuree sous 7,75 faisait encore tomber la marge sous
2,5. Avec quatre, verifie() accepte toute la tolerance de livraison (7,5 a 9,2) :
l'ecrou ne vient jamais buter en fin de filet sans serrer.

L'AXK 1528 de la version precedente etait une erreur : son alesage de 15 ne
passe pas un M16.

Les deux percages sont dans LES DEUX flancs, et les vis les traversent tous les
deux avec une entretoise de cadre entre eux : deux entretoises de plus sans
piece de plus, et la commande se monte du cote que l'on veut en retournant le
coin.

Une entretoise de sommet, dans l'axe au dessus de la mortaise de traverse
(z 411), tient la membrure haute, qui n'avait aucune liaison sur 500 mm.
Voilement symetrique (fem_flamb3, ressorts 6EI/L) : 13,7 avec les six
entretoises d'origine, 33,1 avec les deux de chape a +/- 52, 39,0 couche et
39,1 debout avec celle du sommet. Ce n'est pas un serrage des flancs sur le
paquet de traverse : le tube de 60 fixe l'ecart des flancs, et les epaulements
de la traverse gardent 0,4 de jeu selon y.

## 4 bis. La traverse, et le poussoir

Ni l'une ni l'autre n'est plus un bloc.

**La traverse** est faite de **six plaques verticales de 8, jointives**, dont
le chant du bas forme la portee de 48 x 60 sur laquelle glisse le coin. Deux
tenons par plaque s'engagent dans une mortaise de 52 x 20,4 percee dans le
flanc a z 361,5 - 381,9, et prennent appui sur son arete SUPERIEURE. Chaque
plaque est une poutre de 64 de haut appuyee a 68,5 d'entraxe : 7,6 MPa de
flexion en majorant la charge concentree, coefficient 56. Le tenon mate a
26,5 MPa sur sa portee nette (38,4 x 5,9 par flanc, aretes cassees et
degagements deduits), et sa racine travaille a 11,5 MPa.

Le jeu de la mortaise en largeur, 4 mm, vaut exactement deux fois le rayon de
ses conges : l'arete portante droite fait donc tout juste les 48 mm du paquet
de tenons. Six toles empilees cumulent six fois la tolerance d'epaisseur
(EN 10029) : c'est pourquoi la mortaise est taillee sur la tole MESUREE
(`EP_TOLE_REELLE`), et non sur la cote nominale. En hauteur au contraire le jeu
reste a 0,4, parce que la hauteur du tenon est une cote de DECOUPE, pas
d'empilage.

Les pieds de tenon portent un **degagement** droit R1,5 et non un conge : un conge
deborderait de l'epaulement et viendrait mordre la face interieure du flanc --
le controle d'interference l'avait trouve. Les coins de la mortaise, eux, sont
de simples **conges** : un degagement en os de chien n'a de sens que si la
piece conjuguee doit porter DANS l'angle, et ici le paquet a 2 mm de jeu par
cote. Essaye sur le flanc de 10, il creusait une entaille au bout meme de la
ligne d'appui : 209 MPa au lieu de 130.

Il n'y a plus ni barreau 60 x 45, ni quatre taraudages, ni quatre vis, ni
quatre trous dans le flanc. Une tige filetee M10 x 90 tient le paquet au
montage ; elle ne reprend aucune charge. Le chant du bas est fraise **les
plaques serrees en paquet**, en une seule passe, alignees sur les faces hautes
des tenons ; le DXF porte 1 mm de surepaisseur sur ce chant.

Le paquet pese 1,54 kg. Ses plaques font 64 de haut parce que la mortaise est a
36 mm au dessus de la fente du coin, une valeur historique fixee quand
l'entretoise haute de la chape enjambait encore la fente ; la reduire
raccourcirait la traverse, mais deplacerait la mortaise et donc le calcul EF du
flanc. Le gain du tenon-mortaise est ailleurs : plus de barreau a acheter, plus
de taraudage, et une charge qui entre dans le flanc a 38 mm sous la membrure
haute.

**Le coulisseau** ne flechit pas : le coin appuie a la VERTICALE de la pile, sur
la meme empreinte, et la piece ne fait que transmettre 12 kN en compression,
soit 5,2 MPa. Son epaisseur de reference est donc passee de 36 a **30**, la
seule valeur que deux details imposent encore : 5 mm de matiere au dessus des
taraudages de guide du cote MINCE de la pente (12 + 4 + 5 = 21 minimum, il y en
a 23,8) et un chapeau au dessus de l'alesage du tourillon (20 + 2,7 + 6 = 28,7
minimum ; il fait 7,3). La piece pese 1,45 kg, et tout l'etage au dessus est
descendu de 6 mm.

**Le poussoir** n'etale que l'effort de la pile sur le patin de charge : aucune
surface fonctionnelle. C'est un empilage de **trois plateaux de 8, tous
perces** au diametre du tourillon ; c'est le patin de charge colle qui fait
fond. Debout, les plateaux glisseraient l'un sur l'autre : deux goupilles 8 m6,
serrees dans le patin de charge et libres dans les plateaux, les reperent.
0,97 kg, et plus d'alesage borgne a usiner.

**Toutes les pieces de tole ont l'arete cassee a 0,8 x 45 degres** sur leurs
deux faces. Ce n'est pas une coquetterie de dessin : sans elle, six plaques de
8 jointives se lisent comme un bloc de 48, a l'ecran comme a la main. Avec
elle, chaque joint est une rainure en V de 1,6 mm. Sous le coin, ces rainures
servent de reserve de graisse ; les cinq qui passent sous la plaque de bronze
coutent 8 mm de portee sur ses 38, d'ou 7,7 MPa de contact au lieu de 6,1.

## 5. Les lumieres

Reportees a x = +/- 44, de part et d'autre de la fente du coin, avec 15 mm de
matiere du cote de la fente et 14 mm du cote du bord du noeud. Le noeud porte
maintenant quatre ouvertures -- la fente du coin, les deux lumieres, et la
mortaise de traverse plus haut -- et les deux trous des vis de chape.

Les pattes prismatiques du coulisseau ont disparu. Le guidage se fait par les
**tetes de quatre CHC M8 x 12 ISO 4762**, tete lisse, vissees apres coup au
travers des lumieres dans quatre taraudages M8 des faces laterales. La tete,
diametre 13 et haute de 8, fait exactement l'epaisseur du flanc. La longueur
12 se compte sous la tete : toute la tige entre dans le taraudage de 16.

Un cylindre sur un plan ne porte que sur une LIGNE. Il ne peut donc pas se
coincer en biais comme le faisait la patte prismatique, dont les deux faces
devaient rester paralleles aux joues de la lumiere, et il est insensible aux
rotations autour de son axe comme autour de la ligne de contact. C'est le vrai
remede a l'hyperstatisme des quatre guidages, bien plus que la reduction de
section qui l'avait precede.

Le montage y gagne autant : on ferme le cadre sur le coulisseau, PUIS on visse
les quatre guides au travers des lumieres. Plus besoin d'engager des tenons a
l'aveugle en presentant le second flanc.

La butee de course y gagne aussi : la tete, diametre 13, talonne dans un bout
de lumiere de rayon 7. Deux cercles de rayons voisins, c'est un contact
CONFORME de rayon equivalent 91 mm, la ou le chant d'une patte sur un
demi-cercle etait un contact quasi ponctuel.

Et les lumieres se reduisent beaucoup : **14 x 28,8**, contre 17 x 31,8 avec
les guides M10 de la version precedente et 20,6 x 63,4 avec les pattes.

Le calcul elements finis donne **213 MPa au maximum**, coefficient 2,02 a froid
et 1,83 a 150 C, dans la membrure basse sous le montant cote appui, et 0,335 mm
de fleche. Le meme point vaut 187 MPa a l'autre appui : sur une piece
symetrique, c'est le bruit de maillage. Viennent ensuite 187 MPa a l'angle de
la mortaise ou portent les tenons, 130 et 125 MPa aux consoles d'appui,
103 MPa dans les ligaments entre fente du coin et lumiere, et 90 MPa aux angles
bas du noeud. Le 99,9e centile est a 87 MPa.

Si le maximum devait etre repris, le levier n'est ni le conge R22 du
raccordement membrure basse / montant (balayage R10 a R26 : bruit de maillage)
ni les ouvertures du noeud, mais l'epaisseur ou la nuance de la tole : repli
10 mm en S355 ou S460.

## 6. Le reste de ce que la position debout impose

- **Butee d'about : supprimee le 22/09/2026**, avec ses oreilles et ses deux
  tiges transversales.
- **Calage de la poutrelle debout : POINT OUVERT, ASSUME.** Debout, rien ne
  retient la poutrelle selon x, devenu vertical, que le frottement aux appuis,
  environ 0,15 F acier sur acier : il ne depasse son poids (218 N sur l'about
  bas) qu'au dela de 1,5 kN environ. En dessous -- mise en place, precharge de
  0,5 kN, dechargement, et apres rupture -- le poids passe par la chaine de
  mesure : patin de charge, goupilles, poussoir, tourillon (jeu de 0,4),
  coulisseau, tetes de guide (jeu de 0,5), et pousse la tete de charge de
  cote. Les patins rainures ne tiennent que y. Deux pistes, non retenues a ce
  jour : une cale amovible de 14 entre l'about bas de la poutrelle (x -420) et
  le bord de fenetre des deux montants (x -435), retiree une fois la charge
  au dessus de 1,5 kN ; ou la consigne de ne dresser le cadre que charge au
  dela de ce seuil.
- **Socle : les memes pieds a mi-bois que couche, aux coins, inclines.**
  Chaque coin du flanc porte une encoche inclinee de 38 degres sur le grand
  cote (le conge R20 a disparu, l'encoche le remplace), profonde de 28 depuis
  le coin vif ; les deux pieds de l'about font un V, larges de 510, et posent
  par leur arete basse, 9,5 mm sous l'about, sur les appuis des crochets qui
  les calent par leurs dents : c'est la, et non a la largeur de la base (447
  entre aretes), que le cadre tient debout. Pourquoi 38 et non 45 : a 45, avec
  les trous de coin alors a z 40, le pied passait a 1 mm du tube d'entretoise
  du coin ; aujourd'hui, a 38 degres et trous a z 50, il en passe a 11,6 mm,
  11 de la rondelle de l'ecrou. L'encoche du coin bas entame le bout de la
  membrure basse : l'appui est a 213 MPa a l'EF, 2,02 a froid et 1,83 a 150 C
  en 42CrMo4. Au modele, au DXF et au plan 01.
- **Les pieds en V se montent UN PAR UN**, le cadre couche sur ses pieds :
  chacun s'emboite en coulissant le long de SA propre encoche, a +38 degres
  pour le coin bas de l'about, a -38 pour le coin haut. Ces deux directions
  font 76 degres entre elles et aucune n'est la verticale : on ne descend pas
  le cadre dans deux pieds deja poses. Les nodes serrent de 0,1 par cote :
  maillet. L'ordre complet est dans `NOMENCLATURE.md`.
- **Le fond de l'etuve ne porte pas le cadre.** Quatre crochets de la meme
  tole (05c), dans le plan des flancs, pendent aux parois qui font face aux
  aretes des deux pieds en V ; chaque pied pose par son arete basse sur deux
  appuis, a 245,8 de part et d'autre de l'axe, et la dent de chaque appui entre
  dans la fente du pied. Parois de 1 mm percees de trous carres de 10 au pas de
  40 et 50 en alternance : chaque crochet pend par trois langues de 6 a bec
  de 3 (tete de 9, qui passe le trou de face avant de descendre), et porte en bas un appui de 60 avec une dent
  qui entre dans une fente du pied a 5 du bout : le cadre est cale. La largeur
  interieure, supposee 540, est A CONFIRMER : c'est elle qui place la dent sur
  l'appui, a 48,2 de la paroi. Tant qu'elle ne l'est pas, les DXF du pied et
  du crochet portent NE PAS DECOUPER AVANT CONFIRMATION DE LA LARGEUR D'ETUVE.
- **Entree dans l'etuve.** On accroche d'abord les quatre crochets. La porte
  est du cote de la tige : les pieds de 510 entrent selon y, et leur bout
  arriere doit passer au dessus des dents de 4,5 mm des deux crochets cote
  porte. On entre donc le cadre pieds tenus 5 mm au dessus des appuis jusqu'au
  fond, puis on le descend sur les quatre dents.
- **Les deux pieds de la position couchee se retirent** : autour du cadre
  debout, la place est prise par les pieds en V et les crochets. On souleve le
  cadre, ils restent sur la paillasse.
- **Rien ne peut tomber** quand la tete devient horizontale : le tourillon est
  engage de 12,2 mm dans chaque alesage au repos, davantage sous charge, le
  poussoir est enfile dessus, et ses plateaux sont goupilles dans le patin de
  charge.

## 7. Orientation a respecter dans l'etuve

La tige de commande sort dans la direction de l'epaisseur du cadre. Il faut
placer le banc de facon que cette direction pointe vers la PORTE. Les 440 mm du
cadre se mettent alors en travers, avec 50 mm de jeu de chaque cote, ou se
logent les pieds en V et les crochets.
