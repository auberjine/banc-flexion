# Agent DOCUMENTS : compte rendu du 02/10/2026

Fichiers modifies (dossier banc-flexion) : `spec.py`, `nomenclature.py`, `README.md`, `DEBOUT.md`, `SUITE.md`, et par generation `SPEC.md` et `NOMENCLATURE.md`. Aucun autre fichier n'a ete touche. Les fins de ligne d'origine sont conservees : `nomenclature.py` et `DEBOUT.md` en CRLF, les trois autres en LF, tout en ASCII. Les versions d'avant sont copiees dans `scratchpad/correction/documents/*_avant.*`.

Pendant mon travail, l'agent LIVRABLES a regenere `out/` : masses.json, DXF, LISTE.txt, groupe `_EN_ATTENTE` et `perime_2026-10-02/`. SPEC et NOMENCLATURE lisent donc des masses a jour (cadre 35,2 kg).

## Controles

- `python spec.py` donne SPEC.md (462 lignes), `python nomenclature.py` donne NOMENCLATURE.md (167 lignes, cadre 35,2 kg). Les deux documents sont relus en entier.
- `python params.py` : 0 probleme(s), fichier non modifie.
- Avec `BANC_ENTR_SOMMET=0`, les deux generateurs suivent : 6 vis V1, « 4 de coin, 2 de bielle ».
- Grep de controle sur les 5 fichiers et les 2 documents generes. Il ne reste que des occurrences justifiees :
  - « tole de 10 » : en-tete et remarques historiques de SUITE.md.
  - « M10 x 90 » : V2, consigne de repli si la tole mesuree depasse 8,33.
  - « x 140 » : faux positif, il s'agit de « 540 x 540 x 1400 ».
  - « voile » : seulement dans « voilement » (flambement).
  - « butee d'about » : historique de DEBOUT par. 6 et de SUITE.
  - « +/- 35 » : position des goupilles du poussoir (POUSSOIR_GOUPILLE_X), pas l'ancien Y_FLANC.
  - « 13,7 couche » et « six entretoises » : historique du flambement dans README (13,7 puis 33,1 puis 39,0).
  - « CHC M10 », « M10 x 70 », « logette », « levage », « 10,6 », « 206 MPa », « 2,09 », « 36,9 » : aucune occurrence.

## Fait

### spec.py (genere SPEC.md)

- **En-tete** : indice A du 02/10/2026 (INDICE_REVISION, DATE_EDITION). Rappel dans la docstring : l'accumulateur s'appelle L.
- **Hertz (D3, conc-09, docu-30)** : 339 MPa sur hertz_largeur() = 6,4 mm portants, limite HERTZ_LIM (480, patin S355 a chaud), coefficient hertz_coef() = 1,42.
- **Etuve (docu-09, conc-11, conc-31)** :
  - par. 5 : ETUVE_INTERIEUR x ETUVE_HAUTEUR (A CONFIRMER) ; le banc travaille debout dans l'etuve et couche sur la paillasse ; encombrement reel selon y (-85,5 a +160).
  - par. 7 bis : paroi a (ETUVE_INTERIEUR - H_FLANC)/2 = 50.
  - par. 7 ter : DEGAGEMENT_DOUILLE = 95 (115 cadre centre), avec la consigne de douille (conc-52).
  - par. 11 « Points ouverts » : etuve, tole reelle, calage debout.
- **Textes figes (docu-10)** : coin d'acier C45 a plaques de bronze, traverse a tenons, guidage par tetes de CHC M8 x 12, poussoir de 3 plateaux goupilles, tourillon C45+C, vis H M10 x 200 (tete derriere le flanc oppose), platines, tole de EP_FLANC.
- **R22 (docu-11)** : le paragraphe « optimum, 152 MPa a R25 » est remplace par le resultat lu dans out/balayage_R_FEN_BAS.json (151 a 160 MPa, bruit de maillage). L'asymetrie 213 / 187 MPa est expliquee par le bruit de maillage (conc-10).
- **Points chauds (docu-27)** : etiquettes refaites (angle de mortaise, ligament fente / lumiere, angle bas du noeud...). L'etiquette « vis de traverse » est supprimee.
- **Masses et pressions (docu-27)** : la masse des plaques et celle du coin sont lues dans masses.json ; le brut du coin vient du PartSpec. Les pressions passent par pressions_plaquettes() (7,7 et 6,5).
- **Traverse (conc-34)** : « 4 de jeu en largeur » est remplace par TRAVERSE_JEU_Y.
- **Nuance (D4, conc-10, conc-41)** :
  - le paragraphe NUANCE passe au par. 6, avec EXIGENCE_TOLE ;
  - coefficients 2,02 / 1,83 ;
  - la mention « 1,91 a chaud » du 10 mm S355 est donnee comme comparaison, et non plus comme « la meme marge ».
- **Platine (conc-36)** : platine_contrainte() donne 130 MPa, coefficient 3,3 a froid et 3,0 a chaud, et 12,6 MPa par tube.
- **Irreversibilite (conc-37)** :
  - coin autobloquant au-dela de 0,106 ;
  - filet juge a VIS_MU_MIN = 0,08, marge x2,13 ;
  - le Tr16x4 est recalcule au meme frottement : marge 0,91, il serait reversible (avant : « 1,36 » en dur) ;
  - FILET_P_ADM.
- **Sens d'effort (conc-40)** : le coin tire la tige vers l'INTERIEUR, la tete appuie sur la face exterieure des platines. Desserrage par coin_desserrage().
- **Boulonnerie (D6)** : tableau tire de boulonnerie() ; ecrous ECROU_FREIN_REF ; composition des entretoises calculee.
- **Masses** : designations prises dans les PartSpec, date de masses.json affichee.
- **Nouvelles fonctions partagees avec nomenclature.py** :
  - `lire_json()` ;
  - `encombrement_y()` ;
  - `entretoises_de_cadre()` ;
  - `COUPLE_M10 = 35` N.m (voir « reste »).

### nomenclature.py (genere NOMENCLATURE.md)

- **Source des donnees** : designation, matiere, brut, quantite et operations sont pris dans `P.all_parts()` (toujours a jour) ; masses.json ne sert plus qu'aux masses.
- **En-tete** : indice et date, encombrement reel.
- **Exigences de commande (D4, D5, D11, D15, conc-15)** :
  - EXIGENCE_TOLE et BRUT_TOLE ;
  - NOTE_TOLE_REELLE ;
  - entretoises E235+C, 60 +0,1/0 et 71,5 +/-0,2 ;
  - etuve A CONFIRMER, avec la liste des pieces en attente.
- **Sections de pieces (D10, D16, conc-46, conc-51, docu-28)** : « Pieces fabriquees », puis une nouvelle section « Pieces du commerce » (spec.achete : guide, plaques 06c/06d, tige M16, plat 04c, pile 02e).
- **Reperes (D16, conc-54, docu-13)** : pile 02e (le repere 07 n'est plus double), plaques norelem 06c/06d.
- **Visserie (D6, conc-08/18/30, docu-12/28)**, toutes longueurs et marges tirees de params :
  - V1 : vis TH M10 x ENTR_VIS_L + ECROU_FREIN_REF + 2 rondelles, quantite n_entretoises() - 2 = 7 ;
  - V2 : tige M10 x TRAVERSE_TIRANT_L + 2 rondelles + 2 ecrous ISO 7042, avec le seuil de tole 8,33 au-dela duquel il faut une x 90 ;
  - V3 : goupilles (ex-V11), serrees dans le patin, libres dans les plateaux de 8,3 (D7) ;
  - V4 : cales de rattrapage CALES_EP, D50 / D26 (conc-33) ;
  - V5 : 2 rondelles AS 1730 (17 x 30 x 1), a la place de la « rondelle trempee 30 x 2 » introuvable en M16 ;
  - V6 : AXK, effort coin_effort() ;
  - V7 : ecrous de manoeuvre, quantite 1 jeu (docu-28), douille de 24 ;
  - V8 : 2 HM, jeu axial 0,1 a 0,3 ;
  - V9 : vis H M10 x 200 + 4 rondelles (1 sous tete, 3 sous l'ecrou, SUPPORT_RONDELLES_ECROU), marge et depassement tires de boulonnerie(), 35 N.m.
  - « Voile » et « 5,4 kN » ont disparu.
- **DXF (D14, D15, D7, D8, conc-24, conc-50)** :
  - signification des calques DECOUPE / GRAVURE / TEXTE, face gravee montee a l'exterieur ;
  - note de tole reelle ;
  - bruts de decoupe : traverse +1 sur le chant du bas, patin de charge avec avant-trous de 6 ;
  - groupes en etageres de LARGEUR_GROUPE (lu dans export_dxf) et groupe `_EN_ATTENTE` ;
  - colonne statut (ALERTE_ETUVE, « DXF = brut ») ; renvoi a out/dxf/LISTE.txt.
- **Reglages (docu-15, conc-44, conc-35, conc-33, conc-26)** :
  - Hertz avec HERTZ_LIM ;
  - fissuration calculee par spec.charge_fissuration() : 5,1 kN, 0,12 mm (au lieu de « 4,2 kN » en dur) ;
  - pressions_plaquettes ;
  - precharge par coin_tours(500) : 0,84 tour ;
  - couple M10 ;
  - autoblocage et desserrage ;
  - flambement « des %d entretoises » (9) ;
  - mode antisymetrique donne « au moins 31,9, calcul du 18/09, avant les entretoises de chape et de sommet ».
- **Ordre de montage reecrit (D16, conc-26/27/28, docu-14, conc-53)** : 17 etapes, renvois par cle (CLES_MONTAGE / ETAPE), jamais par numero ecrit en dur.
  - Preparation : eprouvette (plats a y = +/- Y_FLANC) ; coin garni (silicone HT, aucune pate sur les plaques ni les sieges) ; goupilles chassees dans le patin de charge ; sous-ensemble de chape monte sur l'etabli ; mesure de l'empilement et choix des cales.
  - Montage A PLAT : premier flanc (oppose a la chape) sur cales de 20, 7 V1 et 2 V9 passees par-dessous, 9 entretoises ; traverse ; poutrelle sans patins ; tete de charge (patin de charge encolle, poussoir, cale, tourillon, pile tete-beche, coulisseau) ; second flanc ; chape (entretoises de 71,5, sous-ensemble, 3 rondelles, 35 N.m).
  - Cadre dresse : pieds couches au maillet (nodes), V1 a 35 N.m ; patins d'appui glisses en soulevant la poutrelle, colles sur la face superieure seulement, rainure seche ; guides CHC M8 x 12 ; coin engage du cote des tetes de V9, bout mince en premier, controle du contact a moins de 5 mm du repos ; precharge de 0,84 tour ; polymerisation et post-cuisson ; etalonnage.
- **Position debout (conc-28)** : crochets accroches d'abord ; pieds en V montes UN PAR UN (encoches a 76 degres l'une de l'autre) ; pieds couches laisses sur la paillasse ; entree tige vers la porte, pieds tenus 5 mm au-dessus des dents ; renvoi au point ouvert du calage.
- **Changement d'eprouvette (conc-56)** : jeu neuf par eprouvette ; decharger et sortir le coin, deposer les guides, coucher le cadre chape en haut, deposer la chape d'un bloc puis les ecrous V1, soulever le flanc cote chape, sortir l'eprouvette avec sa tete, reprendre a l'etape « poutrelle ».

### README.md (docu-16, docu-17, docu-23, docu-11, conc-41, conc-53)

- Masse 35,2 kg, exigence matiere, indice A.
- Tableau de out/ : brut des DXF, etageres, `_EN_ATTENTE`, LISTE.txt, `perime_2026-10-02/` ; purge par export_dxf et build_freecad.
- Ligne export_dxf en double supprimee. SUITE.md presente comme un historique. Consigne de mesure de la tole avant decoupe.
- EF : 213 MPa, 2,02 / 1,83, 35,2 contre 44,5 kg. Flambement : 13,7 puis 33,1 puis 39,0 / 39,1.
- verifie() decrit avec la boulonnerie, les bruts et l'etuve.
- Points a ne pas defaire :
  - R22 : n'est plus « un optimum » ;
  - Hertz 6,4 mm / 480 / 1,42 ;
  - coin d'acier ;
  - ligaments 14 et 15 ;
  - coulisseau de 36,2 de haut et bruts sur la boite englobante ;
  - puce « quatre tenons » supprimee ;
  - sens d'effort (conc-40) ;
  - mortaise sur la tole mesuree, six toles ;
  - CHC M8 x 12 et tete 13 x 8, longueur sous tete ;
  - six plaques de 8 / 48 ;
  - poussoir a 3 plateaux PERCES, le patin de charge fait fond (docu-17) ;
  - platines de 8 ;
  - ecrous tout metal ;
  - verif_percages avec les encoches.

### DEBOUT.md (docu-18 a 21, conc-28/29/31/40/52/55)

- **Intro** : etuve 540 x 540 x 1400 A CONFIRMER ; tableau refait (verticale 969,5 / 1400, 50 mm dans l'axe des 440, 232 et 15 selon y). Une note precise que SPEC et NOMENCLATURE font foi.
- **Par. 1** : 50 mm, 9,4 N.m.
- **Par. 2** :
  - valeurs generees : 5,5 kN, 9,4 N.m, 7,7 / 6,5 MPa, CHC M8 / 13 / 14, 46 % ;
  - plaques du commerce 0,30 kg, 100 de long ;
  - PLAQ_DROP 5,1 ;
  - rebords 7,05 / 8,15 x 3, 6,5 et 12 MPa, silicone 0,14 MPa ;
  - morsure 1,1 ; portees 51,8 et 48,6 ;
  - irreversibilite a 0,08 ;
  - douille : 115 centre, 95 au pire, cle plate impossible (conc-52).
- **Par. 3** : sens d'effort corrige (conc-40), voile et logette remplaces.
- **Par. 3 bis** : 47,5 et 14,5.
- **Par. 4** :
  - platines de 70 de haut et 140 de long, 130 MPa, 3,3 / 3,0, 0,14 ;
  - L = 71,5 +/- 0,2, 12,6 MPa par tube ;
  - empilement 171,5, filet a 168, marge 3,5, depassement 20,5 ; pourquoi 3 rondelles (conc-29) ;
  - retenue par AS 1730 ;
  - jeu selon y de la traverse.
- **Par. 4 bis** :
  - six plaques de 8, mortaise 52 x 20,4 a z 361,7 - 382,1 ;
  - 7,6 MPa, coefficient 56 ; matage 26,5 MPa et racine 11,5 MPa, par les fonctions de params ;
  - tolerance six fois, mortaise sur la tole mesuree ;
  - tige M10 x 80 ; 1,54 kg ; plaques de 64 expliquees par TRAVERSE_GARDE_FENTE ;
  - coulisseau : 5 mm au-dessus des taraudages, il y en a 23,8 ; 1,45 kg ;
  - poussoir a 3 plateaux de 8 perces, goupilles, 0,97 kg ;
  - aretes cassees : 30 nets sur 38, 7,7 au lieu de 6,1.
- **Par. 5** :
  - ligaments 15 et 14 ; CHC M8 x 12, rayon 7, rayon equivalent 91 ; lumieres 14 x 28,8 ;
  - EF 213 / 187 / 130 / 125 / 103 / 90, centile 87 ;
  - le levier n'est pas R22.
- **Par. 6** :
  - butee d'about en une ligne d'historique ;
  - CALAGE DEBOUT en point ouvert assume, avec les deux pistes de conc-55 non retenues ;
  - pieds : 9,5 sous l'about, base 447, garde 11,6 avec les trous a z 50, 213 MPa / 2,02 / 1,83, plan 01 ;
  - pieds en V montes un par un (conc-28) ;
  - dent du crochet a 48,2 et ALERTE_ETUVE (D15) ;
  - entree dans l'etuve ;
  - retrait des pieds couches justifie par la place des pieds en V et des crochets ;
  - goupilles.
- **Par. 7** : 50 mm.

### SUITE.md (docu-23)

- En-tete « HISTORIQUE -- etat au 11/09/2026 », avec renvoi a SPEC, NOMENCLATURE et DEBOUT.
- Remarques entre crochets sur les lignes trompeuses : Hertz, rainure, tete percee, temoin, orientation debout, butee d'about, EF 134 MPa, R22 « contredit », option 8 mm appliquee, souplesse, etuve.
- Nouvelle section 5 « Suite donnee » : 8 mm applique, M20 sans objet, patins non regroupes, tenon-mortaise applique, retenue a la rupture non rechiffree.

## Ecartes ou adaptes, avec la raison

- **conc-56, « relever la tete de 7 mm et sortir la poutrelle par les fenetres, cadre ferme »** : faux avec D7. Les goupilles sont serrees dans le patin de charge et montent de 24 (POUSSOIR_H) dans le poussoir. La tete ne peut monter que de 9,9 avant que le coulisseau touche les entretoises de chape. Le changement d'eprouvette rouvre donc le flanc cote chape, cadre couche.
- **conc-26, « soulever la poutrelle de 2 mm » pour glisser les patins** : adapte. Les patins d'appui ne sont pas poses pendant le montage a plat, donc la poutrelle repose sur les bossages et se souleve d'environ 9,5 (PATIN_E - RAINURE_P + 1). Les patins sont colles sur leur face superieure seulement : la rainure doit rester seche sur le bossage, qui est un balancier.
- **conc-26, option « coller le patin de charge a part la veille »** : gardee en repli seulement. La primaire colle le patin a l'empilage de la tete et enchaine jusqu'a la precharge dans la vie en pot, conformement a la note du PartSpec (« colle en place en meme temps que les patins d appui »), que je ne pouvais pas modifier.
- **conc-27, « rondelle 30 x 2 » de la retenue interieure** : remplacee par 2 rondelles AS 1730 (17 x 30 x 1), proposition de l'agent MODELE.
- **conc-18, ISO 7089 M16 300 HV de 3 mm** : ecartee. SUPPORT_RONDELLE passerait a 3, ce qui porterait les entretoises de butee a 72,5, contre les 71,5 de D11.
- **conc-46, encombrement « 960 x 440 x 201 »** : remplace par l'etendue reelle selon y, de -85,5 a +160 (soit 245,5). Le coin recule sort plus loin que les tetes de V9.
- **docu-28, « renumeroter V1 a V7 »** : V1, V2 et V9 sont gardes, parce que D6 et les autres agents les nomment ainsi. Les trous sont combles (V11 devient V3 ; V4 cales et V5 rondelles AS sont nouveaux) : la numerotation est continue de V1 a V9.
- **docu-20, matage du tenon 15,6 MPa (planche 03 : 16) et flexion 7,8 / 55** : remplaces par les fonctions de params (03-29, agent MODELE). matage_tenon() donne 26,5 MPa sur la portee nette, aretes cassees et degagements deduits ; flexion_traverse() donne 7,6 MPa, coefficient 56.
- **docu-15, « relancer fem_flambement.py »** : non fait (D17 : ne rien relancer). La valeur du 18/09 (31,9) est publiee comme borne basse, avec sa date : les entretoises ajoutees depuis ne peuvent que la relever.
- **docu-18, « remplacer le tableau de DEBOUT par un renvoi a SPEC »** : le tableau est garde a jour, et une note dit que SPEC et NOMENCLATURE font foi en cas d'ecart.
- **docu-23, « ou retirer SUITE.md des documents de tete »** : fait en plus de l'en-tete historique.
- **Constats sur plans.py, export_dxf.py, build_freecad.py, draw.py, params.py et parts.py** (docu-01/03 a 08 cote planches, docu-13 sous-reperes sur les planches, docu-22, 24 a 26, 29, conc-02/07/12/19/21/22/32/38/39/45/47/48/49) : hors de mon perimetre.

## Reste, ou demande une decision

1. **COUPLE_M10 = 35 N.m** : le constat conc-27 laissait ce couple « a fixer » pour V1. Je l'ai pris egal a celui de V9 : precharge d'environ 17 kN, 80 MPa dans un tube. La constante est dans spec.py, faute de pouvoir toucher params.py ; a valider, puis a deplacer dans params.
2. **Patin de charge** : colle a l'empilage de la tete, puis tout s'enchaine jusqu'a la precharge. Cela suppose une vie en pot suffisante de la Duralco (etapes 9 a 16). A verifier sur la notice, sinon appliquer le repli (collage la veille, centre au trace) et ajuster la note du PartSpec patin_charge.
3. **V5, 2 rondelles AS 1730** pour la retenue interieure : choix de l'agent MODELE, applique ici. A valider.
4. **Jeu axial de 0,1 a 0,3** des ecrous V8, cales de 20 sous le flanc et de 6,5 sous la poutrelle pendant le montage a plat : valeurs de procedure que j'ai fixees.
5. **Calage de la poutrelle debout** : point ouvert assume (D16). Les deux pistes sont decrites mais non retenues : cale de 14 entre l'about bas et le montant, ou dresser le cadre seulement au-dessus de 1,5 kN.
6. **params.py** : pas de parametre pour la longueur des goupilles. nomenclature.py porte GOUPILLE_L = 30 avec un commentaire ; un POUSSOIR_GOUPILLE_L dans params serait plus propre (la note du PartSpec poussoir a aussi « x 30 » en dur).
7. **PLANCHES** :
   - reperes 02e (pile), 06c et 06d (plaques norelem, dessinees sur la 06) ; V3 est l'ancien V11 ; mettre les sous-reperes dans les titres de vue (docu-13) ;
   - planche 07 : « douille de 24 seulement » ;
   - plus aucune « rondelle trempee 30 x 2 » : ce sont 2 AS 1730.
8. **Tourillon en C45+C** (choix MODELE) : SPEC et NOMENCLATURE le publient tel quel. A valider.
9. **Masses** : celles de SPEC et NOMENCLATURE viennent de out/masses.json, regenere par LIVRABLES le 02/10 a 10:25. Relancer spec.py et nomenclature.py apres toute reconstruction FreeCAD (make.py le fait).
