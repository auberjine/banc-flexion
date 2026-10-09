# Banc de flexion 3 points - nomenclature

Indice B du 05/10/2026. Fichier engendre par `nomenclature.py` ; ne pas le modifier a la main.

Poutrelle beton non arme 103 x 107 x 840, portee 750, capacite 12 kN.

Encombrement des flancs 960 x 440 x 76 mm ; selon y, de -85,5 (coin recule) a +160 (bout des vis de chape), soit 245,5 ; pieds de 518.4.


## Exigences de commande

- **Tole de 8 en 42CrMo4** (flancs, platines de butee imbriquees dans les chutes des flancs) : 42CrMo4 recuit +A, tole 8 mm : certificat 3.1 EN 10204 avec essai de traction, Re >= 430 MPa a 20 C. C est elle qui porte toute la marge du flanc. Les cartouches et la colonne brut l abregent en "tole 8 mm, cert. 3.1, Re >= 430".
- **Tole de 8 en S355JR** (pieds, crochets, plaques de traverse, plateaux du poussoir) : S355JR, tole 8 mm du commerce : certificat 2.2 EN 10204, sans autre exigence ; abregee en "tole 8 mm, cert. 2.2". Ces pieces travaillent a quelques dizaines de MPa au plus (traverse 8 MPa en flexion et 26 au matage).
- **Finition des flancs** : apres decoupe et aretes cassees : SABLAGE corindon des deux faces a l identique, pression moderee (planeite), puis BRUNISSAGE noir (oxydation a chaud), aspect mat ; degraisser l huile de sortie de bain, puis film d huile ESTER synthetique haute temperature passe au chiffon et ESSUYE ; ni huile minerale ni silicone ; graduation gravee a 0.2 de profondeur au moins, traits repasses a la peinture blanche haute temperature apres brunissage. Noir mat pour la correlation d images, et quasi sans epaisseur : ni les jeux des encoches ni les serrages des entretoises n en dependent. Les autres pieces restent brutes.
- **Epaisseurs reelles** : mesurer les deux toles livrees, regler EP_TOLE_REELLE_42 (42CrMo4) et EP_TOLE_REELLE_S355 (S355JR) et regenerer les DXF avant decoupe. Chaque decoupe suit la tole qu elle RECOIT : EP_TOLE_REELLE_S355 (8 aujourd hui) pour les encoches a mi-bois et la mortaise de traverse du flanc et les fentes de calage du pied ; EP_TOLE_REELLE_42 (8) pour les encoches et nodes du pied et les rainures des patins.
- **Entretoises** : E235+C EN 10305-1, tube de precision 20 x 2 ; 9 coupees a 60 +0,1/0 et 2 a 71,5 +/-0,2, faces dressees // 0,05 : ce sont elles qui fixent l ecart des flancs.

## Pieces fabriquees

| rep | designation | qte | matiere | brut | masse u. | masse tot. | operations |
|---|---|---|---|---|---|---|---|
| 01 | Flanc en treillis | 2 | 42CrMo4 +A | tole 8 mm, cert. 3.1, Re >= 430 | 10.21 kg | 20.41 kg | decoupe laser, aretes cassees 0,8 x 45 deg, bossages non repris ; encoches a mi-bois et mortaise taillees sur la tole REELLE S355 des pieces qu elles recoivent : mesurer les deux toles livrees, regler EP_TOLE_REELLE_42 (42CrMo4) et EP_TOLE_REELLE_S355 (S355JR) et regenerer les DXF avant decoupe ; graduation de charge gravee (calque GRAVURE) d un seul cote de la lumiere, face gravee montee a l exterieur ; finition : apres decoupe et aretes cassees : SABLAGE corindon des deux faces a l identique, pression moderee (planeite), puis BRUNISSAGE noir (oxydation a chaud), aspect mat ; degraisser l huile de sortie de bain, puis film d huile ESTER synthetique haute temperature passe au chiffon et ESSUYE ; ni huile minerale ni silicone ; graduation gravee a 0.2 de profondeur au moins, traits repasses a la peinture blanche haute temperature apres brunissage |
| 03 | Plaque de traverse | 6 | S355JR | tole 8 mm, cert. 2.2 | 0.25 kg | 1.50 kg | DXF = brut : chant du bas + 1 (65 / 39) ; chants du bas FRAISES EN PAQUET serre, paquet aligne sur les faces HAUTES des tenons, a la cote finie 64 / 38, Ra 1,6 : c est le plan de glissement |
| 02b | Plateau de poussoir | 3 | S355JR | tole 8 mm, cert. 2.2 | 0.33 kg | 0.97 kg | 3 plateaux perces : alesage 25,4 traversant ; 2 trous de passage 6,6 decoupes au laser a +/- 38 ; assembles en bloc par 2 vis H M6 x 35, tete en dessous, ecrou au dessus, 8 N.m ; le patin de charge fait fond |
| 02a | Coulisseau a tete inclinee | 1 | S355JR | plat 65 x 40, L 120 (fini 58 x 36,2 x 114) | 1.46 kg | 1.46 kg | dessus a 12 degres sur toute la section ; alesage 25 H8 prof. 20 par dessous ; 4 taraudages M8 prof. 16 dans les faces laterales (avant-trou 6,8 prof. 19), axe a 12 du dessous, x = +/- 44 |
| 06a | Tourillon de centrage | 1 | C45+C | rond etire 25 h9 x 79.5 | 0.31 kg | 0.31 kg | rond etire h9 NON repris : tronconne, chanfrein 1,5 x 45 deg aux deux bouts ; COLLE au fond de l alesage du coulisseau (Loctite 648 (tient 175 C), alesage 25 H8 degraisse) ; centre la pile et coulisse dans le poussoir : 7,9 au repos, 4,3 de garde au dessus du patin a la butee |
| 02c | Coin de commande | 1 | C45 | plat 65 x 45, L 120 (fini 61 x 40 x 114,5) | 1.37 kg | 1.37 kg | acier taraude M16 sur 80 depuis le bout EPAIS, passage 18 au dela ; porte les deux plaques de frottement en bronze entre rebords de 3 : dessus 5,25, dessous 5,41 (faces normales a la pente) |
| 06c | Plaque de frottement, dessus | 1 | CuSn12-C | plat 40 x 6 | 0.17 kg | 0.17 kg | fraisee 38 x 102 x 5, sans trou, faces planes et paralleles a 0,02, Ra 0,8 cote glissement, aretes cassees 0,3 ; entre ses deux rebords sur le dessus du coin, points de silicone HT au montage ; pate graphite haute temperature sur la face qui glisse sous la traverse |
| 06d | Plaque de frottement, dessous | 1 | CuSn12-C | plat 40 x 6 | 0.17 kg | 0.17 kg | comme la haute, mais 38 x 104 x 5 ; entre ses deux rebords sous le coin, points de silicone HT au montage ; pate graphite haute temperature sur la face qui glisse sur la pente du coulisseau |
| 07 | Platine de butee de la vis | 2 | 42CrMo4 +A | tole 8 mm, cert. 3.1, Re >= 430 | 0.45 kg | 0.90 kg | meme tole 42CrMo4 que les flancs (imbriquees dans leurs chutes), empilees et serrees par les deux vis H M10 x 200 de la chape |
| 07b | Entretoise de butee | 2 | E235+C EN 10305-1 | tube de precision 20 x 2 | 0.06 kg | 0.13 kg | coupee a 71,5 +/-0,2, faces dressees ; en compression pure : c est elle qui porte l effort de commande |
| 04a | Patin d'appui rainure | 4 | S355JR | tole 10 mm | 0.13 kg | 0.52 kg | decoupe laser PUIS rainure 9,5 x 1,5 fraisee sur toute la longueur de la face d appui (0,75 de jeu par cote sur la tole reelle du flanc) ; colle en place, cadre monte, sous 0,5 kN de precharge ; un jeu par eprouvette |
| 04b | Patin de charge | 1 | S355JR | tole 10 mm | 0.45 kg | 0.45 kg | sans trou, 58 de long selon x pour laisser passer les tetes des vis du poussoir ; dessus BOMBE R1000 fraise (cylindre d axe transversal, 10 au milieu, 9,58 aux bords) : le poussoir y porte sur une ligne ; dessous plat, colle centre au trace en meme temps que les patins d appui ; un par eprouvette |
| 06b | Entretoise tubulaire | 9 | E235+C EN 10305-1 | tube de precision 20 x 2 | 0.05 kg | 0.48 kg | coupee a 60 +0,1/0, faces dressees // 0,05 : c est elle qui fixe l ecart des flancs ; 7 serrees par vis TH M10 x 100 + ecrou ISO 7042 classe 8, autofreine tout metal, les 2 de la chape par les vis H M10 x 200 |
| 05 | Pied a mi-bois | 4 | S355JR | tole 8 mm, cert. 2.2 | 0.87 kg | 3.48 kg | ajoure, bossages aux deux bouts qui posent sur les crochets d etuve, fente de calage 8,4 x 7 a 5 du bout ; encoches et nodes taillees sur la tole REELLE du flanc (42CrMo4), fente sur celle du crochet (S355) : mesurer les deux toles livrees, regler EP_TOLE_REELLE_42 (42CrMo4) et EP_TOLE_REELLE_S355 (S355JR) et regenerer les DXF avant decoupe ; meme plaque pour les deux positions : 2 dans le chant bas (couche), 2 aux coins de l about a 38 degres (debout), aretes de pose a 447 |
| 05c | Crochet d etuve | 4 | S355JR | tole 8 mm, cert. 2.2 | 0.17 kg | 0.69 kg | cadre DEBOUT : pend par 4 langues a bec dans la colonne de trous carres de 10 (paroi 1), dans le plan des flancs ; l arete du pied en V pose sur son appui, calee par la dent dans la fente du pied. Le fond de l etuve ne porte rien ; dent a 47,2 de la paroi pour une etuve de 538 |

## Pieces du commerce

| rep | designation | qte | reference | matiere | masse u. | remarque |
|---|---|---|---|---|---|---|
| 02f | Vis de guidage CHC M8 x 12 | 4 | CHC M8 x 12 ISO 4762 8.8, tete lisse (non moletee) | 8.8 | 0.01 kg | piece du commerce ; 12 sous tete, toute la tige dans le taraudage de 16 ; c est la TETE (13 x 8) qui guide : cylindre sur plan, contact lineique |
| 02d | Vis de commande H M16 x 160 | 1 | vis H M16 x 160 ISO 4017 8.8 brute, filetee jusqu a la tete | 8.8 | 0.34 kg | piece du commerce, filetee jusqu a la tete, montee a la pate cuivre ; tete de 10 (douille de 24) sur la butee ; ecrous et butee figures : ils montrent l arret axial dans les deux sens |
| 04c | Plat de renfort colle | 2 | feuillard 20 x 2 S235, coupe a 840 | S235 | 0.26 kg | piece du commerce, coupee a longueur, bavures retirees ; collee sur toute la longueur a y = +/- 34, poncer et degraisser les deux faces ; un jeu par eprouvette |
| 02e | Pile de 12 rondelles Belleville | 1 | 12 rondelles EN 16983 A50 | 51CrV4 (1.8159) | 0.41 kg | piece du commerce : 12 rondelles 50 x 25,4 x 3 (ex-DIN 2093, PAS en C60S) montees TETE-BECHE, grand diametre aux deux bouts ; 18,5 kN a plat, course 15,6 mm ; cales de rattrapage 1 et 2 mm (50 / 26) entre poussoir et pile si l empilement est court |

**Masse du cadre complet : 34.3 kg.** Poutrelle beton : 22.2 kg. Masses du modele 3D (out/masses.json du 09/10/2026).

## Visserie et petites pieces du commerce

| rep | designation | qte | remarque |
|---|---|---|---|
| V1 | Vis TH M10 x 100 ISO 4017 8.8 zinguee (filetage total) + ecrou ISO 7042 classe 8, autofreine tout metal + 2 rondelles ISO 7089 M10 | 7 | entretoises de cadre : 4 de coin, 2 de bielle, 1 de sommet. Serrage 80, filetage total : la vis depasse de l ecrou de 10 ; 25 N.m. Pas d ecrou a bague polyamide (ISO 7040, DIN 985) : elle ne freine plus a 150 C. Acier, pas inox : meme dilatation que les flancs, la precharge tient a chaud |
| V2 | Vis TH M10 x 100 ISO 4017 8.8 zinguee (filetage total) + ecrou ISO 7042 classe 8, autofreine tout metal + 2 rondelles ISO 7089 M10 : MEME ARTICLE QUE V1 | 2 | paquet de plaques de traverse, a y = +/- 17 : les deux vis tiennent les plaques alignees pour dresser le chant en paquet ; elles ne reprennent aucune charge. Serrage 52, la vis depasse de l ecrou de 38, entre les flancs ; 25 N.m |
| V3 | Vis H M6 x 35 ISO 4017 8.8 zinguee + rondelle ISO 7089 M6 + ecrou ISO 7042 M6 classe 8 tout metal | 2 | serrent les 3 plateaux du poussoir en un bloc, dans les trous de 6,6 a +/- 38 : TETE EN DESSOUS, rondelle et ecrou au dessus, a cote de la pile. Sous le plateau bas il n y a que les 10 du patin de charge jusqu a la poutrelle : une tete de 4 y tient (6 de garde), un ecrou non. Serrage modere, 8 N.m ; la vis depasse de l ecrou de 3,4 ; restent sur le poussoir |
| V4 | Cale de rattrapage D50 / D26, feuillard acier, ep. 1 et 2 mm | 2 | une de chaque, entre le poussoir et la pile, si l empilement mesure au montage est court : le coin doit toucher a moins de 5 mm de son repos |
| V5 | Rondelle trempee AS 1730 (17 x 30 x 1) | 2 | cote interieur des platines, sous les ecrous V7 : deux empilees font les 2 mm de rondelle trempee (une rondelle trempee 30 x 2 n existe pas en M16) |
| V6 | Rondelle trempee AS 1730 (17 x 30 x 1) : MEME ARTICLE QUE V5 | 2 | sous la tete de la vis de commande, face EXTERIEURE des platines : elles encaissent les 5.5 kN de commande ; pate graphite haute temperature entre elles, la tete tourne dessus |
| V7 | Ecrou M16 HM ISO 4035 | 2 | bloques l un sur l autre cote interieur des platines, sur les rondelles V5, avec 0,1 a 0,3 de jeu axial : ils ne retiennent la vis qu au desserrage, 329 N |
| V8 | Vis H M10 x 200 ISO 4014 8.8 zinguee (filetee sur 32) + 2 ecrous H M10 ISO 4032 classe 8 + 5 rondelles ISO 7089 M10 | 2 | vis de chape : tete et 1 rondelle derriere le flanc oppose, flanc, entretoise de cadre, flanc, entretoise de butee, platines, 4 rondelles, ecrou serre puis contre-ecrou bloque contre lui. Serrage 173,5, filet a partir de 168 : le premier ecrou y tombe avec 5,5 de marge, la vis depasse du contre-ecrou de 9,7 ; 25 N.m sur le premier |

## Pieces planes a decouper

Fichiers DXF dans `out/dxf/`, cotes en millimetres, contours fermes, indice B du 05/10/2026 ; la liste tenue a jour par `export_dxf.py` est `out/dxf/LISTE.txt`.

- **Calques** : DECOUPE = contour a couper ; GRAVURE = marquage laser, sans traverser, sur la face superieure de decoupe (graduation de charge du flanc, d un seul cote de la lumiere : face gravee montee a l exterieur) ; TEXTE = identification, ni coupe ni marquage.
- **Toles reelles** : mesurer les deux toles livrees, regler EP_TOLE_REELLE_42 (42CrMo4) et EP_TOLE_REELLE_S355 (S355JR) et regenerer les DXF avant decoupe. Le texte de chaque DXF cite l epaisseur pour laquelle ses fentes et encoches ont ete taillees.
- **Brut de decoupe** : le DXF de la traverse porte 1 mm de surepaisseur sur le chant du bas (fraise ensuite en paquet).
- **Groupes** : `tole_<ep>mm_<nuance>.dxf` reprend tous les exemplaires d une epaisseur et d une nuance, ranges en etageres de 3000 mm de large au plus. C est un controle de quantites, pas une imbrication : le decoupeur imbrique sur son format. Les pieces en attente sont dans un groupe a part, suffixe `_EN_ATTENTE`.
- Les pieces du commerce n ont pas de DXF.

| fichier | epaisseur | matiere | nombre | statut |
|---|---|---|---|---|
| flanc.dxf | 8 mm | 42CrMo4 +A | 2 | a decouper |
| traverse.dxf | 8 mm | S355JR | 6 | a decouper ; DXF = brut, reprise apres decoupe |
| poussoir.dxf | 8 mm | S355JR | 3 | a decouper |
| support.dxf | 8 mm | 42CrMo4 +A | 2 | a decouper |
| patin_appui.dxf | 10 mm | S355JR | 4 | a decouper |
| patin_charge.dxf | 10 mm | S355JR | 1 | a decouper |
| pied.dxf | 8 mm | S355JR | 4 | a decouper |
| crochet.dxf | 8 mm | S355JR | 4 | a decouper |
| tole_8mm_42crmo4.dxf | 8 mm | 42CrMo4 +A | 4 | groupe : flanc, support |
| tole_8mm_s355.dxf | 8 mm | S355JR | 17 | groupe : traverse, poussoir, pied, crochet |
| tole_10mm_s355.dxf | 10 mm | S355JR | 5 | groupe : patin_appui, patin_charge |

## Reglages et constantes d'essai

| grandeur | valeur |
|---|---|
| Portee entre bossages | 750 mm |
| Bossages | R150, balancier, 339 MPa de Hertz sur 6,4 mm portants |
| Pression de Hertz aux appuis | 339 MPa ; limite 480 MPa, 1,6 Re a chaud du patin S355JR, le plus mou des deux corps ; coefficient 1.42 |
| Pile Belleville | 12 x EN 16983 A50 en 51CrV4 (1.8159), hauteur libre 51.6 mm |
| Effort de la pile a plat | 18.5 kN |
| Course totale de la pile | 15.6 mm |
| Ecrasement a 12 kN | 9.65 mm, soit 1243 N/mm en secant |
| Butee de course (bas de lumiere) | 11.8 mm, plafonne l'effort a 14.4 kN |
| Rattrapage d empilement | 2.4 mm en reserve au dela des 12 kN ; cales V4 de 1 et 2 mm |
| Commande | coin acier a 12 degres, vis M16 normale aux flancs |
| Course par tour | 0.425 mm de coulisseau, environ 549 N |
| Precharge de collage, 0,5 kN | 0.84 tour de vis apres le contact (0.36 mm de pile, 1.7 mm de coin) |
| Couple sur la vis a 12 kN | 14.5 N.m |
| Couple de serrage des vis M10 (V1, V8) | 25 N.m |
| Irreversibilite du filet | helice 2.48 deg / frottement 5.28 deg a mu 0.08 (acier sur acier, pate cuivre), marge x2.13 |
| Coin | autobloquant seulement si mu > 0.106 ; desserrage 329 N a mu 0.12 |
| Flancs du filet, taraude dans l acier | 9.2 MPa pour 12 admis, 80 mm filetes, engagement utile 24 mm |
| Plaques de frottement | usinees en CuSn12-C, 38 x 102 (dessus) et 38 x 104 (dessous) x 5 ; pate graphite haute temperature ; 7.6 MPa au plus pour 25 admis |
| Rebords des plaquettes | 5.25 (dessus) et 5.41 (dessous) x 3, 11.8 MPa de flexion, garde 2 sous le bronze |
| Portee de la plaquette haute | 30.0 x 52.8 mm (sur 60) en fin de course, 7.6 MPa |
| Portee de la plaquette basse | 38.0 x 50.6 mm (sur 58) en fin de course, 6.2 MPa |
| Arete cassee des pieces de tole | 0.8 x 45 degres sur les deux faces |
| Effort estime a la fissuration (beton a 4 MPa) | 5.1 kN |
| Fleche a la fissuration | 0.12 mm |
| Jauge fibre sur la membrure haute | 18.8 microdef/kN |
| Calcul EF du flanc a 12 kN | von Mises 213 MPa, coefficient 2.02 a froid, fleche 0.335 mm |
| Coefficient a 150 C | 1.83 en 42CrMo4 +A de 8 mm (Re 390 a chaud, pour 430 a 20 C EXIGES au certificat) |
| Flambement hors plan des flancs | facteur critique 38.2 couche, 38.3 debout (les deux flancs penchent ensemble, tenus par la flexion des 9 entretoises tubulaires, bouts serres) |
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
2. **Coin, a l avance.** Degraisser les deux sieges ; poser chaque plaque de frottement ENTRE SES DEUX REBORDS (la plus longue, 104, dessous), quelques points de silicone haute temperature sur le siege degraisse -- PAS d epoxy, bronze et acier ne se dilatent pas pareil ; laisser prendre. PUIS seulement, pate graphite haute temperature sur les faces de glissement, rien sur les sieges : le silicone ne prend pas sur une pate.
3. **Poussoir, a l avance.** Empiler les 3 plateaux, alesages alignes sur un rond de 25 ; passer les deux vis V3 PAR DESSOUS (tete sous le plateau bas), rondelle et ecrou au dessus, serrer a 8 N.m. Le poussoir est desormais un bloc ; il sert a toutes les eprouvettes.
4. **Sous-ensemble de chape, sur l etabli.** Sur la vis H M16 x 160 (02d), enfiler sous la tete les deux rondelles AS (V6), pate graphite entre elles, les deux platines, les deux rondelles trempees (V5), puis visser les deux ecrous HM (V7) : 0,1 a 0,3 mm de jeu axial, contre-bloquer. Pate cuivre sur le filet de la vis.
5. **Empilement.** Mesurer la poutrelle avec ses plats, les patins d appui sous la rainure, le patin de charge, le poussoir et la pile libre. Du sommet des bossages au dessous du coulisseau, le nominal fait 203,1 (8,5 + 2 + 107 + 10 + 24 + 51,6). S il manque plus de 1 mm, prevoir entre poussoir et pile la cale de 1, de 2 ou les deux (V4) : au dela des 12 kN le coin ne garde que 2,4 mm de reserve en hauteur.
6. **Premier flanc.** Poser a plat, sur cales de 20, le flanc OPPOSE a la chape, face gravee DESSOUS : la graduation doit finir a l exterieur. Passer par dessous, rondelle sous tete, les 7 vis V1 (4 de coin, 2 de bielle, 1 de sommet) et les 2 vis V8 (chape, x = +/- 52). Enfiler une entretoise de 60 sur chacune des 9 vis.
7. **Traverse.** Engager dans la mortaise le paquet des 6 plaques, serre par les deux vis V2 (rondelle sous tete et sous ecrou ISO 7042, 25 N.m) ; chants dresses du cote du coin.
8. **Poutrelle.** La coucher dans la fenetre du flanc, plats vers les bossages, SANS ses patins d appui, sur cales de 6,5 sous sa face laterale (elle descend de 13,5 sous le flanc).
9. **Tete de charge.** Encoller le patin de charge sur sa face inferieure et le poser au milieu de la poutrelle, centre au trace, bombe vers la tete ; poser dessus le poussoir visse (3 plateaux), tetes de vis en bas de part et d autre du patin ; poser la cale eventuelle (V4), la pile TETE-BECHE (grand diametre aux deux bouts) puis le coulisseau, tourillon colle dessous a l avance (Loctite 648 dans l alesage degraisse, polymeriser avant montage), cote epais de sa pente vers la chape. De cet encollage a la precharge, tout doit tenir dans la vie en pot de la colle : faire d abord les etapes 2 a 5 et preparer la visserie. Si elle est trop courte, coller le patin de charge la veille sur la poutrelle, centre au trace, sous une masse.
10. **Second flanc.** Le presenter face gravee DESSUS : il enfile les 9 vis, les tenons de la traverse et la poutrelle dans sa fenetre. Poser les 7 ecrous V1 sur rondelle, serres sans bloquer.
11. **Chape.** Enfiler sur les deux vis V8 les entretoises de butee de 71,5, puis le sous-ensemble de chape, la vis passant par la fente du coin ; 4 rondelles et un ecrou H par vis, 25 N.m, puis le contre-ecrou H bloque contre lui en tenant le premier.
12. **Pieds.** Dresser le cadre et le poser dans ses deux pieds couches, encoche dans encoche : les nodes serrent de 0,1 par cote, chasser au maillet. Bloquer les V1 a 25 N.m. La poutrelle, sans patins, repose sur les bossages.
13. **Patins d appui, coin non engage.** Soulever la poutrelle d environ 9,5 mm, glisser les 4 patins par la fenetre, rainure SECHE sur le bossage (c est un balancier, il doit basculer) et colle sur la face superieure seulement, contre le plat ; reposer.
14. **Guides.** Visser les 4 CHC M8 x 12 au travers des lumieres dans les taraudages du coulisseau. C est la TETE qui guide : jamais de vis a tete fraisee.
15. **Coin.** Pate cuivre dans son taraudage ; l engager du cote des tetes de V8, bout MINCE en premier, par la fente du flanc, entre la traverse et le coulisseau ; visser la vis jusqu au contact. Le bout epais doit alors etre a moins de 5 mm de sa position de repos, 47,5 mm hors de la face exterieure du flanc ; sinon revoir les cales (etape 5).
16. **Precharge.** 0,84 tour de vis au dela du contact (0,36 mm de pile, 1,7 mm de coin) donne 0,5 kN. Laisser polymeriser sous cette precharge : l epoxy rattrape l hyperstaticite des quatre appuis. Post-cuire selon la notice Duralco avant toute mise en charge.
17. **Etalonnage.** Etalonner la graduation de charge sur presse, ou par la fibre de la membrure.

## Position debout, dans l'etuve

1. Accrocher d abord les 4 crochets aux parois de l etuve : crochet a l horizontale, engager les trois tetes de langue DE FACE dans leurs trous carres, puis laisser descendre : les becs retombent derriere la paroi.
2. Le cadre couche sur ses pieds, engager les deux pieds en V UN PAR UN sur les deux coins d un meme about, chacun chasse le long de sa propre encoche a 38 degres (maillet, nodes). Ils ne se montent pas ensemble : leurs encoches font 76 degres entre elles.
3. Soulever le cadre hors des pieds couches, qui restent sur la paillasse, et le dresser sur ses pieds en V.
4. L entrer dans l etuve vis vers la porte, pieds tenus 5 mm au dessus des appuis jusqu au fond, puis descendre les quatre fentes des pieds sur les dents des crochets.
5. Calage de la poutrelle debout : point ouvert, assume (voir `DEBOUT.md`, paragraphe 6).

## Changement d'eprouvette

Les plats, les patins d appui et le patin de charge sont colles sur la poutrelle et partent avec elle : il faut un jeu neuf par eprouvette (4 patins d appui, 1 patin de charge, 2 plats ; colle). Le poussoir visse porte sur le patin de charge, centre par le tourillon, et la tete ne peut remonter que de 9,9 avant que le coulisseau touche les entretoises de chape : l eprouvette ne sort pas cadre ferme, on rouvre le flanc cote chape.

1. Decharger : devisser la vis jusqu a liberer la pile, puis jusqu a degager le filet ; sortir le coin du cote des tetes de V8.
2. Deposer les 4 guides. Sortir le cadre de l etuve ou de ses pieds et le coucher a plat, chape en haut, sur cales de 20.
3. Deposer les ecrous et rondelles des deux V8, le sous-ensemble de chape d un bloc (platines et vis), puis les deux entretoises de butee.
4. Deposer les 7 ecrous V1 et soulever le flanc cote chape.
5. Sortir l eprouvette avec sa tete de charge ; sur l etabli, soulever le poussoir visse, qui resservira tel quel : le patin de charge reste colle sur la poutrelle.
6. Remonter la nouvelle eprouvette, preparee aux etapes 1 et 5 de l ordre de montage, en reprenant a l etape 8 : le premier flanc a garde ses vis, ses entretoises et la traverse.
