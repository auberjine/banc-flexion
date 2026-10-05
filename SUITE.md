# Ce qui a ete corrige, ce qui reste a gagner, ce qu'il faut savoir

> **HISTORIQUE -- etat au 11/09/2026** : flanc en tole de 10 S355, vis de
> charge verticale M20, banc couche seulement. La conception a beaucoup change
> depuis : tole de 8 en 42CrMo4, commande par coin normale aux flancs, position
> debout dans l'etuve, traverse a tenons, guidage par tetes de vis. Ce document
> n'est garde que pour la trace des decisions ; les chiffres ci-dessous sont
> ceux du 11/09. Pour l'etat courant, voir `SPEC.md`, `NOMENCLATURE.md` et
> `DEBOUT.md`. Les remarques entre crochets et la section 5, ajoutees le
> 02/10/2026, disent ce que chaque point est devenu.

Huit revues independantes ont produit 89 propositions et 70 signalements
d'incoherence, tous conserves dans `out/revue_brute.json`. Voici le tri.

## 1. Corrige dans le modele

| point | avant | apres |
|---|---|---|
| Rondelles Belleville | A50 donnee a 12,9 kN et 0,77 kN/mm, loi lineaire | DIN 2093 reelle : l0 4,3, h0 1,3, 18,5 kN a plat, loi d'Almen-Laszlo, 1243 N/mm en secant a 12 kN |
| Ecrasement a 12 kN | 15,6 mm annonces | 9,65 mm calcules |
| Graduation de charge | un pas constant | non lineaire, tabulee et gravee |
| Axe neutre de la poutrelle | 53,5 mm, beton nu | 50,86 mm, section homogeneisee avec les deux plats |
| Point de contact d'appui | face inferieure du patin | fond de la rainure, 1,5 mm plus haut |
| Justification du rayon R65 | roulement sans glissement | faux : c'est un balancier. Rayon porte a R150, choisi pour la pression de contact |
| Pression de Hertz | 412 MPa, conclusion elastique a 20 degres | 271 MPa, coefficient 1,77 sur l'ecoulement au contact a 150 degres [02/10 : flanc de 8 portant sur 6,4 mm, 339 MPa ; limite 480, celle du patin S355 a chaud ; coefficient 1,42] |
| Aplatissement de la pile | rien ne l'empechait | le bas de la lumiere est une butee : effort plafonne a 14,4 kN |
| Rainure du patin | 10,5 mm, 0,25 de jeu, moins que la planeite d'une tole | 11,5 mm, 0,75 de jeu [sur la tole de 10 ; depuis le 02/10, 9,5 sur la tole de 8 : tole reelle + 2 x 0,75] |
| Patin d'appui | 80 mm, plus court que le bossage elargi | 90 mm |
| Manoeuvre de la vis | tete six pans creux, douille difficile a engager | tete percee 8 mm pour barre traversante [sans objet : la vis verticale a disparu avec la commande par coin, tige M16 manoeuvree a la douille] |
| Temoin thermique | plat de 3 mm decoupe dans une tole de 10 | tole de 10 [supprime depuis] |
| Orientation debout | presentee comme possible | impossible, le cadre fait 960 de long dans une etuve de 500 [rendue possible depuis par la commande par coin : voir DEBOUT.md ; etuve supposee 540, a confirmer] |
| Butee d'about | dans la nomenclature | supprimee, elle ne servait qu'a l'orientation debout [reprise pour la position debout, puis de nouveau supprimee le 22/09] |
| Col de mesure | 8 x 10, entaille dans la membrure | supprime : la membrure pleine donne 16 microdeformations par kN, soit 62 N de resolution |
| Specification | fichier a la main, perime des la premiere modification | engendre par `spec.py` depuis `params.py` |

## 2. Tranche par le calcul

Le flanc a ete calcule aux elements finis sous CalculiX, 146 000 noeuds,
elements du second ordre, appuis glissants, 6 kN au noeud.

- **von Mises maxi 134 MPa, coefficient 2,65 sur S355, fleche 0,197 mm.**
  Le point chaud est au raccordement membrure basse / montant, cote appui.
  [02/10 : flanc de 8 en 42CrMo4, 213 MPa, 2,02 a froid et 1,83 a 150 C,
  0,335 mm de fleche ; le point chaud est dans la membrure basse sous le
  montant.]
- **Le conge de ce raccordement est un optimum a R22.** Porte a R25, la
  contrainte monte a 152 MPa : le conge mange la matiere du chemin d'effort au
  lieu d'adoucir une entaille. C'est le seul endroit du cadre ou agrandir un
  conge est nuisible. [CONTREDIT depuis : rejoue le 16/09 avec un blocage
  propre, le balayage R10 a R26 donne 151 a 160 MPa sans tendance, du bruit de
  maillage. Le rayon n'est pas le levier.]
- **Les sept trous d'allegement de la membrure basse coutent 6 MPa** sur le pic
  (134 contre 127 sans) et economisent 0,2 kg par flanc. Ils ne sont pas a
  l'origine du point chaud. Deux revues se contredisaient sur ce point : l'une
  voulait amincir la membrure basse a 18 mm, l'autre interdisait d'y percer.
  Les deux avaient tort. La membrure basse porte un moment CONSTANT de 180 N.m
  entre les appuis : on ne peut pas l'amincir a 18, mais on peut l'ajourer.
- **Une proposition ne survit pas a la geometrie reelle** : mettre les montants
  au droit des appuis pour supprimer la console de 55 mm. Impossible, les
  appuis sont a +/- 375 et les abouts de la poutrelle a +/- 420 : les montants
  passeraient dans la poutrelle.

## 3. A gagner, non applique

Chaque ligne est chiffree et independante. Rien n'est bloquant.

| gain | ce qu'il faut faire | ce qu'il coute |
|---|---|---|
| **-5,3 kg** (15 % du cadre) | flanc en tole de 8 au lieu de 10 | Hertz passe de 271 a 303 MPa (coefficient 1,58 au lieu de 1,77), pic de von Mises a 167 MPa (coefficient 2,1), rainure du patin ramenee a 9,5. Les deux entretoises de mi-bielle sont deja au plan, le flambement reste couvert. |
| **-1 taraudage M20** | poche hexagonale decoupee dans la traverse + ecrou M20 standard | la poche dans 45 mm est a la limite du laser, le jet d'eau la fait. Le filet devient un consommable remplacable. |
| **4 patins d'appui -> 2, 4 fraisages -> 0** | un patin unique 100 x 100 x 10 pontant les deux flancs par ligne d'appui, la rainure etant menagee par deux cales rapportees | +2 cales plates. Pression sur beton 1,5 MPa au lieu de 1,7. Tolerance de pose en y bien plus confortable. |
| **couple de manoeuvre divise par 2** | pointe de vis spherique R50 trempee, portant sur une rondelle trempee lamee dans le coulisseau | 1 tournage + trempe, 1 lamage, 1 rondelle du commerce. Sans la rondelle trempee la pointe indente le S355 des le premier chargement. |
| **6 kN en appui matiere au lieu du frottement de deux boulons** | traverse en tenon-mortaise : tenon 40 x 10 sur chaque about, mortaise correspondante dans le noeud | mortaise cotee au plus juste en hauteur. Les boulons deviennent de simples retenues. |
| **-1 piece** | supprimer le contre-ecrou M20 | le filetage M20 pas 2,5 est autobloquant avec une marge de 4 sur l'angle de frottement. A vide et sous la ventilation, la vis peut bouger seule. |
| **-0,5 kg, retenue a la rupture** | prolonger la lumiere vers le bas et dimensionner son fond pour encaisser les 52 J stockes dans la pile si la poutrelle disparait d'un coup | ecrasement local d'environ 1 mm en fond de lumiere apres un evenement pleine energie, a controler. |

Le passage du flanc a 8 mm est le seul gain de masse important. Pour un banc
manipule a deux, 36,6 kg n'est pas genant, et les coefficients actuels (2,65 en
von Mises, 1,77 au contact) sont confortables. Je le laisse en option plutot
qu'en decision. [Il a ete applique le 17/09, en 42CrMo4 : voir la section 5.]

## 4. A savoir pour la conduite d'essai

- **Le frottement d'appui coute quelques pour cent sur le moment.** Le bossage
  est un balancier : il n'absorbe pas le recul de 0,06 mm de la fibre basse a
  la fissuration. Pour le supprimer il faudrait un vrai galet libre sur une des
  deux lignes d'appui.
- **La lecture de charge par le coulisseau est un indicateur**, pas une mesure.
  Elle englobe la souplesse du cadre (0,20 mm a 12 kN ; 0,335 mm avec le flanc
  de 8) et la fleche de la poutrelle. La reference est la fibre sur la membrure haute.
- **Le revetement de la fibre est a verifier.** L'acrylate standard ne tient pas
  150 degres C. Il faut du polyimide, ou de l'or pour les temperatures hautes.
- **Palier de stabilisation d'au moins 2 heures** avant toute lecture : avec
  107 mm d'epaisseur, la constante de temps de la poutrelle est d'environ
  90 minutes.
- **Reprendre la charge a chaque palier** : les rondelles relaxent de quelques
  pour cent au dela de 100 degres C.
- **Coller les patins en place**, cadre monte, sous 0,5 kN de precharge. C'est
  l'epoxy qui rattrape l'hyperstaticite des quatre contacts. Post-cuire selon
  la notice Duralco avant toute mise en charge.
- **Effort a la fissuration estime a 5,1 kN** pour un beton a 4 MPa, section
  homogeneisee. La butee de course intervient a 14,4 kN, le cadre est calcule
  pour 12 kN : trois marges bien separees.
- **La profondeur de l'enceinte n'est pas connue.** C'est elle qui fixe le
  recul possible de la camera et donc la faisabilite optique de la correlation
  d'images. A verifier avant de commander la tole. [02/10 : etuve supposee
  540 x 540 x 1400, toujours A CONFIRMER ; le pied et le crochet en
  dependent. 05/10 : largeur 538 confirmee.]
- **Planeite de la tole a la livraison** : l'EN 10029 autorise 9 mm de fleche
  sur 1000 mm en classe N. Demander la classe A, ou faire dresser les flancs
  avant percage des appuis.
- **Precision utile** : l'entraxe des bossages a +/- 0,3 mm et leur coplanarite
  a 0,3 mm suffisent, puisque les patins sont colles en place. Ne pas
  sur-specifier.

## 5. Suite donnee (etat au 02/10/2026)

| point du paragraphe 3 | suite |
|---|---|
| flanc en tole de 8 | APPLIQUE le 17/09, en 42CrMo4 recuit +A, Re >= 430 exige au certificat 3.1 : 213 MPa a l'EF, 2,02 a froid, 1,83 a 150 C, cadre de 35,2 kg. Rainure du patin ramenee a 9,5 le 02/10. |
| -1 taraudage M20, -1 contre-ecrou M20, pointe de vis spherique | SANS OBJET : la vis verticale M20 a disparu avec la commande par coin (tige M16 normale aux flancs, coin d'acier garni de deux plaques de bronze du commerce). |
| 4 patins d'appui -> 2 | NON applique : quatre patins rainures 90 x 20 x 10, colles en place, un jeu par eprouvette. |
| traverse en tenon-mortaise | APPLIQUE : six plaques de 8 a tenons, portees par l'arete haute d'une mortaise des flancs ; plus aucune vis de traverse. |
| retenue a la rupture | NON applique en tant que tel : le bas de la lumiere est la butee de course (contact conforme entre la tete de guide et le bout de lumiere) ; l'energie de rupture n'y a pas ete rechiffree. |

Ce qui est venu depuis, hors de cette revue : position debout dans l'etuve
(pieds en V et crochets), guidage du coulisseau par les tetes de quatre CHC M8,
poussoir en plateaux goupilles, butee de vis en platines de tole, entretoise de
sommet (flambement 39 au lieu de 13,7), visserie M10 a ecrous autofreines tout
metal. Le detail est dans `SPEC.md` et `DEBOUT.md`.
