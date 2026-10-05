# Banc de flexion 3 points - nomenclature

Indice B du 05/10/2026. Fichier engendre par `nomenclature.py` ; ne pas le modifier a la main.

Poutrelle beton non arme 103 x 107 x 840, portee 750, capacite 12 kN.

Encombrement des flancs 960 x 440 x 76 mm ; selon y, de -85,5 (coin recule) a +160 (bout des vis de chape), soit 245,5 ; pieds de 510.


## Exigences de commande

- **Tole de 8 en 42CrMo4** (flancs, traverse, poussoir, platines, pieds, crochets) : 42CrMo4 recuit +A, tole 8 mm : certificat 3.1 EN 10204 avec essai de traction, Re >= 430 MPa a 20 C. C est elle qui porte toute la marge du flanc. Les cartouches et la colonne brut l abregent en "tole 8 mm, cert. 3.1, Re >= 430".
- **Epaisseur reelle** : mesurer la tole livree, regler EP_TOLE_REELLE et regenerer les DXF avant decoupe. Encoches a mi-bois, nodes, fentes de calage, mortaise de traverse et rainures des patins en derivent (EP_TOLE_REELLE = 8 aujourd hui).
- **Entretoises** : E235+C EN 10305-1, tube de precision 20 x 4,5 ; 9 coupees a 60 +0,1/0 et 2 a 71,5 +/-0,2, faces dressees // 0,05 : ce sont elles qui fixent l ecart des flancs.

## Pieces fabriquees

| rep | designation | qte | matiere | brut | masse u. | masse tot. | operations |
|---|---|---|---|---|---|---|---|
| 01 | Flanc en treillis | 2 | 42CrMo4 +A | tole 8 mm, cert. 3.1, Re >= 430 | 10.21 kg | 20.41 kg | decoupe laser, aretes cassees 0,8 x 45 deg, bossages non repris ; encoches a mi-bois et mortaise taillees sur la tole REELLE : mesurer la tole livree, regler EP_TOLE_REELLE et regenerer les DXF avant decoupe ; graduation de charge gravee (calque GRAVURE) d un seul cote de la lumiere, face gravee montee a l exterieur |
| 03 | Plaque de traverse | 6 | 42CrMo4 +A | tole 8 mm, cert. 3.1, Re >= 430 | 0.26 kg | 1.54 kg | DXF = brut : chant du bas + 1 (65 / 39) ; chants du bas FRAISES EN PAQUET serre, paquet aligne sur les faces HAUTES des tenons, a la cote finie 64 / 38, Ra 1,6 : c est le plan de glissement |
| 02b | Plateau de poussoir | 3 | 42CrMo4 +A | tole 8 mm, cert. 3.1, Re >= 430 | 0.32 kg | 0.97 kg | 3 plateaux perces : alesage 25,4 traversant ; 2 trous de passage 8,3 decoupes au laser a +/- 35, goupilles 8 m6 x 30 libres, serrees dans le patin de charge qui fait fond |
| 02a | Coulisseau a tete inclinee | 1 | S355JR | plat 65 x 40, L 120 (fini 58 x 36,2 x 114) | 1.45 kg | 1.45 kg | dessus a 12 degres sur toute la section ; alesage 25,4 prof. 20 par dessous ; 4 taraudages M8 prof. 16 dans les faces laterales (avant-trou 6,8 prof. 19), axe a 12 du dessous, x = +/- 44 |
| 06a | Tourillon de centrage | 1 | C45+C | rond etire 25 h9 x 76 | 0.29 kg | 0.29 kg | rond etire h9 NON repris : tronconne, chanfrein 1,5 x 45 deg aux deux bouts ; flottant, centre la pile et enfile le poussoir et le coulisseau |
| 02c | Coin de commande | 1 | C45 | plat 65 x 45, L 120 (fini 61 x 40 x 114,5) | 1.37 kg | 1.37 kg | acier taraude M16 sur 80 depuis le bout EPAIS, passage 18 au dela ; porte les deux plaques de frottement du commerce entre rebords de 3 : dessus 7,05, dessous 8,15 (faces normales a la pente) |
| 07 | Platine de butee de la vis | 2 | 42CrMo4 +A | tole 8 mm, cert. 3.1, Re >= 430 | 0.45 kg | 0.90 kg | meme tole que les flancs, empilees et serrees par les deux vis H M10 x 200 de la chape |
| 07b | Entretoise de butee | 2 | E235+C EN 10305-1 | tube de precision 20 x 4,5 | 0.12 kg | 0.25 kg | coupee a 71,5 +/-0,2, faces dressees ; en compression pure : c est elle qui porte l effort de commande |
| 04a | Patin d'appui rainure | 4 | S355JR | tole 10 mm | 0.13 kg | 0.52 kg | decoupe laser PUIS rainure 9,5 x 1,5 fraisee sur toute la longueur de la face d appui (0,75 de jeu par cote sur la tole reelle du flanc) ; colle en place, cadre monte, sous 0,5 kN de precharge ; un jeu par eprouvette |
| 04b | Patin de charge | 1 | S355JR | tole 10 mm | 0.77 kg | 0.77 kg | DXF = 2 avant-trous 6 a +/- 35, PERCES ET ALESES 8 H7 apres decoupe (goupilles 8 m6 serrees) ; colle en place en meme temps que les patins d appui ; un par eprouvette |
| 06b | Entretoise tubulaire | 9 | E235+C EN 10305-1 | tube de precision 20 x 4,5 | 0.10 kg | 0.93 kg | coupee a 60 +0,1/0, faces dressees // 0,05 : c est elle qui fixe l ecart des flancs ; 7 serrees par vis TH M10 x 100 + ecrou ISO 7042 classe 8, autofreine tout metal, les 2 de la chape par les vis H M10 x 200 |
| 05 | Pied a mi-bois | 4 | 42CrMo4 +A | tole 8 mm, cert. 3.1, Re >= 430 | 0.86 kg | 3.45 kg | ajoure, bossages aux deux bouts qui posent sur les crochets d etuve, fente de calage 8,4 x 7 a 5 du bout ; encoches, nodes et fente taillees sur la tole REELLE : mesurer la tole livree, regler EP_TOLE_REELLE et regenerer les DXF avant decoupe ; meme plaque pour les deux positions : 2 dans le chant bas (couche), 2 aux coins de l about a 38 degres (debout), aretes de pose a 447 |
| 05c | Crochet d etuve | 4 | 42CrMo4 +A | tole 8 mm, cert. 3.1, Re >= 430 | 0.17 kg | 0.69 kg | cadre DEBOUT : pend par 4 langues a bec dans la colonne de trous carres de 10 (paroi 1), dans le plan des flancs ; l arete du pied en V pose sur son appui, calee par la dent dans la fente du pied. Le fond de l etuve ne porte rien ; dent a 47,2 de la paroi pour une etuve de 538 |

## Pieces du commerce

| rep | designation | qte | reference | matiere | masse u. | remarque |
|---|---|---|---|---|---|---|
| 02f | Vis de guidage CHC M8 x 12 | 4 | CHC M8 x 12 ISO 4762 8.8, tete lisse (non moletee) | 8.8 | 0.01 kg | piece du commerce ; 12 sous tete, toute la tige dans le taraudage de 16 ; c est la TETE (13 x 8) qui guide : cylindre sur plan, contact lineique |
| 06c | Plaque de frottement, dessus | 1 | norelem 23765-01-038100, 38 x 100 x 5 | CuZn25Al5Mn4Fe3-C + graphite | 0.15 kg | piece du commerce, autolubrifiante ; entre ses deux rebords sur le dessus du coin, trous remplis de silicone HT, glisse sous la traverse |
| 06d | Plaque de frottement, dessous | 1 | norelem 23765-01-038100, 38 x 100 x 5 | CuZn25Al5Mn4Fe3-C + graphite | 0.15 kg | meme plaque du commerce ; entre ses deux rebords sous le coin, trous remplis de silicone HT, glisse sur la pente du coulisseau |
| 02d | Tige filetee de commande M16 | 1 | tige filetee M16 classe 8.8, coupee a 185 | 8.8 | 0.41 kg | piece du commerce, coupee a longueur, montee a la pate cuivre ; ecrous et butee figures : ils montrent l arret axial dans les deux sens |
| 04c | Plat de renfort colle | 2 | feuillard 20 x 2 S235, coupe a 840 | S235 | 0.26 kg | piece du commerce, coupee a longueur, bavures retirees ; collee sur toute la longueur a y = +/- 34, poncer et degraisser les deux faces ; un jeu par eprouvette |
| 02e | Pile de 12 rondelles Belleville | 1 | 12 rondelles DIN 2093 A50 | 51CrV4 | 0.41 kg | piece du commerce : 12 rondelles 50 x 25,4 x 3 montees TETE-BECHE, grand diametre aux deux bouts ; 18,5 kN a plat, course 15,6 mm ; cales de rattrapage 1 et 2 mm (50 / 26) entre poussoir et pile si l empilement est court |

**Masse du cadre complet : 35.2 kg.** Poutrelle beton : 22.2 kg. Masses du modele 3D (out/masses.json du 05/10/2026).

## Visserie et petites pieces du commerce

| rep | designation | qte | remarque |
|---|---|---|---|
| V1 | Vis TH M10 x 100 ISO 4014 8.8 zinguee + ecrou ISO 7042 classe 8, autofreine tout metal + 2 rondelles ISO 7089 M10 | 7 | entretoises de cadre : 4 de coin, 2 de bielle, 1 de sommet. Serrage 80 : l ecrou tombe sur le filet avec 6 de marge, la vis en depasse de 10 ; 35 N.m. Pas d ecrou a bague polyamide (ISO 7040, DIN 985) : elle ne freine plus a 150 C. Acier, pas inox : meme dilatation que les flancs, la precharge tient a chaud |
| V2 | Tige filetee M10 x 90 classe 8.8 + 2 rondelles ISO 7089 M10 + 2 ecrous ISO 7042 classe 8, autofreine tout metal | 1 | tirant du paquet de plaques de traverse, ne reprend aucune charge. Serrage 52, depasse de 9 a chaque bout. Tole mesuree au dela de 10 : prendre une M10 x 100 (verifie() le signale) |
| V3 | Goupille cylindrique ISO 2338 8 m6 x 30 | 2 | reperage des plateaux du poussoir : serrees dans le patin de charge (8 H7, enfoncees de 6), libres dans les trous de 8,3 des plateaux ; partent avec l eprouvette |
| V4 | Cale de rattrapage D50 / D26, feuillard acier, ep. 1 et 2 mm | 2 | une de chaque, entre le poussoir et la pile, si l empilement mesure au montage est court : le coin doit toucher a moins de 5 mm de son repos |
| V5 | Rondelle trempee AS 1730 (17 x 30 x 1) | 2 | cote interieur des platines, sous les ecrous V8 : deux empilees font les 2 mm de rondelle trempee (une rondelle trempee 30 x 2 n existe pas en M16) |
| V6 | Butee a aiguilles AXK 1730 + 2 rondelles AS 1730 | 1 | face EXTERIEURE des platines : c est elle qui encaisse les 5.5 kN de commande |
| V7 | Ecrou M16 H ISO 4032 classe 8 + ecrou M16 HM ISO 4035, bloques | 1 | tete de manoeuvre, 22,8 de haut, en appui sur la butee a aiguilles. Douille de 24 et cliquet : une cle plate bute sur les bouts des vis V9 |
| V8 | Ecrou M16 HM ISO 4035 | 2 | bloques l un sur l autre cote interieur des platines, sur les rondelles V5, avec 0,1 a 0,3 de jeu axial : ils ne retiennent la tige qu au desserrage, 329 N |
| V9 | Vis H M10 x 200 ISO 4014 8.8 zinguee (filetee sur 32) + 2 ecrous H M10 ISO 4032 classe 8 + 5 rondelles ISO 7089 M10 | 2 | vis de chape : tete et 1 rondelle derriere le flanc oppose, flanc, entretoise de cadre, flanc, entretoise de butee, platines, 4 rondelles, ecrou serre puis contre-ecrou bloque contre lui. Serrage 173,5, filet a partir de 168 : le premier ecrou y tombe avec 5,5 de marge, la vis depasse du contre-ecrou de 9,7 ; 35 N.m sur le premier |

## Pieces planes a decouper

Fichiers DXF dans `out/dxf/`, cotes en millimetres, contours fermes, indice B du 05/10/2026 ; la liste tenue a jour par `export_dxf.py` est `out/dxf/LISTE.txt`.

- **Calques** : DECOUPE = contour a couper ; GRAVURE = marquage laser, sans traverser, sur la face superieure de decoupe (graduation de charge du flanc, d un seul cote de la lumiere : face gravee montee a l exterieur) ; TEXTE = identification, ni coupe ni marquage.
- **Tole reelle** : mesurer la tole livree, regler EP_TOLE_REELLE et regenerer les DXF avant decoupe.
- **Brut de decoupe** : le DXF de la traverse porte 1 mm de surepaisseur sur le chant du bas (fraise ensuite en paquet), celui du patin de charge des avant-trous de 6 (perces et aleses 8 H7 ensuite).
- **Groupes** : `tole_<ep>mm_<nuance>.dxf` reprend tous les exemplaires d une epaisseur et d une nuance, ranges en etageres de 3000 mm de large au plus. C est un controle de quantites, pas une imbrication : le decoupeur imbrique sur son format. Les pieces en attente sont dans un groupe a part, suffixe `_EN_ATTENTE`.
- Les pieces du commerce n ont pas de DXF.

| fichier | epaisseur | matiere | nombre | statut |
|---|---|---|---|---|
| flanc.dxf | 8 mm | 42CrMo4 +A | 2 | a decouper |
| traverse.dxf | 8 mm | 42CrMo4 +A | 6 | a decouper ; DXF = brut, reprise apres decoupe |
| poussoir.dxf | 8 mm | 42CrMo4 +A | 3 | a decouper |
| support.dxf | 8 mm | 42CrMo4 +A | 2 | a decouper |
| patin_appui.dxf | 10 mm | S355JR | 4 | a decouper |
| patin_charge.dxf | 10 mm | S355JR | 1 | a decouper ; DXF = brut, reprise apres decoupe |
| pied.dxf | 8 mm | 42CrMo4 +A | 4 | a decouper |
| crochet.dxf | 8 mm | 42CrMo4 +A | 4 | a decouper |

## Reglages et constantes d'essai

| grandeur | valeur |
|---|---|
| Portee entre bossages | 750 mm |
| Bossages | R150, balancier, 339 MPa de Hertz sur 6,4 mm portants |
| Pression de Hertz aux appuis | 339 MPa ; limite 480 MPa, 1,6 Re a chaud du patin S355JR, le plus mou des deux corps ; coefficient 1.42 |
| Pile Belleville | 12 x DIN 2093 A50, hauteur libre 51.6 mm |
| Effort de la pile a plat | 18.5 kN |
| Course totale de la pile | 15.6 mm |
| Ecrasement a 12 kN | 9.65 mm, soit 1243 N/mm en secant |
| Butee de course (bas de lumiere) | 11.8 mm, plafonne l'effort a 14.4 kN |
| Rattrapage d empilement | 2.4 mm en reserve au dela des 12 kN ; cales V4 de 1 et 2 mm |
| Commande | coin acier a 12 degres, vis M16 normale aux flancs |
| Course par tour | 0.425 mm de coulisseau, environ 549 N |
| Precharge de collage, 0,5 kN | 0.84 tour de tige apres le contact (0.36 mm de pile, 1.7 mm de coin) |
| Couple sur la vis a 12 kN | 9.4 N.m |
| Couple de serrage des vis M10 (V1, V9) | 35 N.m |
| Irreversibilite du filet | helice 2.48 deg / frottement 5.28 deg a mu 0.08 (acier sur acier, pate cuivre), marge x2.13 |
| Coin | autobloquant seulement si mu > 0.106 ; desserrage 329 N a mu 0.12 |
| Flancs du filet, taraude dans l acier | 9.2 MPa pour 12 admis, 80 mm filetes, engagement utile 24 mm |
| Plaques de frottement | norelem 23765-01-038100, 38 x 100 x 5, CuZn25Al5Mn4Fe3-C + graphite ; 7.7 MPa au plus pour 35 admis |
| Rebords des plaquettes | 7.05 (dessus) et 8.15 (dessous) x 3, 6.5 MPa de flexion, garde 2 sous le bronze |
| Portee de la plaquette haute | 30.0 x 51.8 mm (sur 60) en fin de course, 7.7 MPa |
| Portee de la plaquette basse | 38.0 x 48.6 mm (sur 58) en fin de course, 6.5 MPa |
| Arete cassee des pieces de tole | 0.8 x 45 degres sur les deux faces |
| Effort estime a la fissuration (beton a 4 MPa) | 5.1 kN |
| Fleche a la fissuration | 0.12 mm |
| Jauge fibre sur la membrure haute | 18.8 microdef/kN |
| Calcul EF du flanc a 12 kN | von Mises 213 MPa, coefficient 2.02 a froid, fleche 0.335 mm |
| Coefficient a 150 C | 1.83 en 42CrMo4 +A de 8 mm (Re 390 a chaud, pour 430 a 20 C EXIGES au certificat) |
| Flambement hors plan des flancs | facteur critique 39.0 couche, 39.1 debout (les deux flancs penchent ensemble, tenus par la flexion des 9 entretoises tubulaires, bouts serres) |
| Flambement, flancs en sens contraire | au moins 31.9 (calcul du 18/09/2026, avant les entretoises de chape et de sommet) |

Graduation de charge gravee sur le flanc, loi non lineaire :

| charge | descente du coulisseau |
|---|---|
| 2 kN | 1.45 mm |
| 4 kN | 2.97 mm |
| 6 kN | 4.55 mm |
| 8 kN | 6.19 mm |
| 10 kN | 7.89 mm |
| 12 kN | 9.65 mm |

## Ordre de montage

Le cadre se monte A PLAT : les entretoises, la traverse et la tete de charge doivent etre en place avant de presenter le second flanc. Les numeros V renvoient a la visserie.

1. **Eprouvette, a l avance.** Coller les deux plats 20 x 2 sous la poutrelle, a y = +/- 34 (axe des flancs), sur toute la longueur ; poncer P80 et degraisser les deux faces ; polymeriser.
2. **Coin, a l avance.** Degraisser les deux sieges ; poser chaque plaque de frottement ENTRE SES DEUX REBORDS, trous remplis et quelques points de silicone haute temperature -- PAS d epoxy, bronze et acier ne se dilatent pas pareil ; laisser prendre. Aucune pate sur les plaques ni sur les sieges : elles sont autolubrifiantes, et le silicone ne prend pas sur une pate.
3. **Patin de charge.** Chasser les deux goupilles V3 dans ses trous 8 H7, enfoncees de 6 : elles depassent de 24, la hauteur du poussoir.
4. **Sous-ensemble de chape, sur l etabli.** Sur la tige M16, visser par son bout exterieur l ecrou H et l ecrou HM de manoeuvre (V7), bloques a 2,7 du bout ; enfiler par l autre bout une rondelle AS, la butee AXK 1730 et la seconde AS (V6), les deux platines, les deux rondelles trempees (V5), puis visser les deux ecrous HM (V8) : 0,1 a 0,3 mm de jeu axial, contre-bloquer. Pate cuivre sur le filet de la tige.
5. **Empilement.** Mesurer la poutrelle avec ses plats, les patins d appui sous la rainure, le patin de charge, le poussoir et la pile libre. Du sommet des bossages au dessous du coulisseau, le nominal fait 203,1 (8,5 + 2 + 107 + 10 + 24 + 51,6). S il manque plus de 1 mm, prevoir entre poussoir et pile la cale de 1, de 2 ou les deux (V4) : au dela des 12 kN le coin ne garde que 2,4 mm de reserve en hauteur.
6. **Premier flanc.** Poser a plat, sur cales de 20, le flanc OPPOSE a la chape, face gravee DESSOUS : la graduation doit finir a l exterieur. Passer par dessous, rondelle sous tete, les 7 vis V1 (4 de coin, 2 de bielle, 1 de sommet) et les 2 vis V9 (chape, x = +/- 52). Enfiler une entretoise de 60 sur chacune des 9 vis.
7. **Traverse.** Engager dans la mortaise le paquet des 6 plaques, serre par la tige V2 (rondelles et ecrous ISO 7042) ; chants fraises du cote du coin.
8. **Poutrelle.** La coucher dans la fenetre du flanc, plats vers les bossages, SANS ses patins d appui, sur cales de 6,5 sous sa face laterale (elle descend de 13,5 sous le flanc).
9. **Tete de charge.** Encoller le patin de charge sur sa face inferieure et le poser au milieu de la poutrelle, goupilles vers la tete ; enfiler sur les goupilles les 3 plateaux du poussoir, poser la cale eventuelle (V4), le tourillon, la pile TETE-BECHE (grand diametre aux deux bouts) et le coulisseau, cote epais de sa pente vers la chape. De cet encollage a la precharge, tout doit tenir dans la vie en pot de la colle : faire d abord les etapes 2 a 5 et preparer la visserie. Si elle est trop courte, coller le patin de charge la veille sur la poutrelle, centre au trace, sous une masse.
10. **Second flanc.** Le presenter face gravee DESSUS : il enfile les 9 vis, les tenons de la traverse et la poutrelle dans sa fenetre. Poser les 7 ecrous V1 sur rondelle, serres sans bloquer.
11. **Chape.** Enfiler sur les deux vis V9 les entretoises de butee de 71,5, puis le sous-ensemble de chape, la tige passant par la fente du coin ; 4 rondelles et un ecrou H par vis, 35 N.m, puis le contre-ecrou H bloque contre lui en tenant le premier.
12. **Pieds.** Dresser le cadre et le poser dans ses deux pieds couches, encoche dans encoche : les nodes serrent de 0,1 par cote, chasser au maillet. Bloquer les V1 a 35 N.m. La poutrelle, sans patins, repose sur les bossages.
13. **Patins d appui, coin non engage.** Soulever la poutrelle d environ 9,5 mm, glisser les 4 patins par la fenetre, rainure SECHE sur le bossage (c est un balancier, il doit basculer) et colle sur la face superieure seulement, contre le plat ; reposer.
14. **Guides.** Visser les 4 CHC M8 x 12 au travers des lumieres dans les taraudages du coulisseau. C est la TETE qui guide : jamais de vis a tete fraisee.
15. **Coin.** Pate cuivre dans son taraudage ; l engager du cote des tetes de V9, bout MINCE en premier, par la fente du flanc, entre la traverse et le coulisseau ; visser la tige jusqu au contact. Le bout epais doit alors etre a moins de 5 mm de sa position de repos, 47,5 mm hors de la face exterieure du flanc ; sinon revoir les cales (etape 5).
16. **Precharge.** 0,84 tour de tige au dela du contact (0,36 mm de pile, 1,7 mm de coin) donne 0,5 kN. Laisser polymeriser sous cette precharge : l epoxy rattrape l hyperstaticite des quatre appuis. Post-cuire selon la notice Duralco avant toute mise en charge.
17. **Etalonnage.** Etalonner la graduation de charge sur presse, ou par la fibre de la membrure.

## Position debout, dans l'etuve

1. Accrocher d abord les 4 crochets aux parois de l etuve : crochet a l horizontale, engager les trois tetes de langue DE FACE dans leurs trous carres, puis laisser descendre : les becs retombent derriere la paroi.
2. Le cadre couche sur ses pieds, engager les deux pieds en V UN PAR UN sur les deux coins d un meme about, chacun chasse le long de sa propre encoche a 38 degres (maillet, nodes). Ils ne se montent pas ensemble : leurs encoches font 76 degres entre elles.
3. Soulever le cadre hors des pieds couches, qui restent sur la paillasse, et le dresser sur ses pieds en V.
4. L entrer dans l etuve tige vers la porte, pieds tenus 5 mm au dessus des appuis jusqu au fond, puis descendre les quatre fentes des pieds sur les dents des crochets.
5. Calage de la poutrelle debout : point ouvert, assume (voir `DEBOUT.md`, paragraphe 6).

## Changement d'eprouvette

Les plats, les patins d appui et le patin de charge sont colles sur la poutrelle et partent avec elle : il faut un jeu neuf par eprouvette (4 patins d appui, 1 patin de charge et ses 2 goupilles, 2 plats ; colle). Les goupilles, serrees dans le patin de charge, montent de 24 dans le poussoir, et la tete ne peut remonter que de 9,9 avant que le coulisseau touche les entretoises de chape : l eprouvette ne sort pas cadre ferme, on rouvre le flanc cote chape.

1. Decharger : devisser la tige jusqu a liberer la pile, puis jusqu a degager le filet ; sortir le coin du cote des tetes de V9.
2. Deposer les 4 guides. Sortir le cadre de l etuve ou de ses pieds et le coucher a plat, chape en haut, sur cales de 20.
3. Deposer les ecrous et rondelles des deux V9, le sous-ensemble de chape d un bloc (platines et tige), puis les deux entretoises de butee.
4. Deposer les 7 ecrous V1 et soulever le flanc cote chape.
5. Sortir l eprouvette avec sa tete de charge ; sur l etabli, degager le poussoir des goupilles, qui restent dans le patin de charge.
6. Remonter la nouvelle eprouvette, preparee aux etapes 1, 3 et 5 de l ordre de montage, en reprenant a l etape 8 : le premier flanc a garde ses vis, ses entretoises et la traverse.
