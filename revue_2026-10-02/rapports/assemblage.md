# Planche 00_assemblage : compte rendu de l'agent ASSEMBLAGE (02/10/2026)

## Fichiers touches

- `plans.py` : seulement le bloc « assemblage », c'est-a-dire les aides locales `a00_*` et `plan_assemblage()`. Le debut du fichier, jusqu'au bandeau, et la fin, a partir de `index_html`, sont identiques a l'octet pres a la copie temoin (`correction/assemblage/temoin/plans.py`). Le fichier reste en LF et en ASCII.
- `draw.py` : ajouts seulement, aucune fonction existante n'est modifiee. Les CRLF sont conserves. Les ajouts sont `Sheet.motif` (motif de hachures) et, dans `View`, `cote_hx` / `cote_vx` (cotes ISO 129-1 : le texte est du cote ou pointe le haut des lettres, donc a GAUCHE d'une cote verticale ; les lignes d'attache partent a 1 mm de l'arete et depassent la ligne de cote de 2 mm ; on peut omettre l'attache d'un bout pour s'appuyer sur un axe ; le texte peut glisser le long de sa ligne). S'y ajoutent `bulle` (bulle de repere), `renvoi` (ligne de repere avec texte, terminee par un point ou une fleche selon ISO 128-22), `zone` (region a fond blanc masquant, hachuree ou non), `clip_debut` / `clip_fin`, `trace_coupe` (ISO 128-44), `rupture` et `_fin_repere`.
- Les SVG 01 a 07 sont identiques a l'octet pres a ceux d'avant mes changements. `params.py`, `parts.py`, `spec.py`, `nomenclature.py` et les autres scripts n'ont pas change.
- Mes outils sont dans `scratchpad/correction/assemblage/` : `pa_new.py` (source du bloc), `splice.py` (le remet dans plans.py), `run.sh` (splice, plans, controles, rendu de la 00) et `chk00.py`. Ce dernier controle plus severement que verif_plans : il prend en compte TOUS les traits, fins compris, qui traversent un texte, les bulles qui touchent un texte ou une autre bulle, les textes sur une zone hachuree et les textes a moins de 11 mm du cadre.

## Ce qui est fait (par constat)

**Echelles (00-01, 00-13, 00-33).** L'elevation est a k = 0,2, soit un vrai 1:5. La coupe A-A est a 1:2, la coupe B-B a 1:2,5. Chaque titre de vue porte son echelle. La perspective est notee « sans echelle », parce que c'est une axonometrie aux axes raccourcis. Le cartouche porte « 1:5 sauf indication », matiere « voir nomenclature », brut « - », quantite 1. L'indice A et la date du 02/10/2026 viennent de draw.py (agent LIVRABLES).

**Encombrement (00-02, 00-14, conc-11 pour sa part qui touche la planche 00).** Les notes donnent : « Hors tout couche sur pieds : 960 x 510 x 470 (x, y, z) ; flancs 76 », puis « Debout dans l etuve : 969,5 de haut, 458,6 x 510 en plan ; etuve 540 x 540 x 1400 A CONFIRMER ». Tous ces chiffres sont calcules (`pied_debout_encombrement`, `ETUVE_*`). Le suffixe « A CONFIRMER » disparait de lui-meme quand `ETUVE_CONFIRMEE` passe a vrai. L'etendue du cadre equipe selon y (-85,5 / +155 / +160) est cotee sur B-B.

**Commande par coin (00-03, 00-15, 00-20, 00-21).** L'ancienne vue est remplacee par une vraie coupe B-B, prise dans le plan median x = 0 et tracee sur l'elevation, a 1:2,5. Elle est hachuree, les sections minces (rondelles Belleville, plats) sont noircies, et les pieces non coupees (tige, tourillon, ecrous, rondelles, butee) sont laissees blanches. On y voit la tige 02d, la butee V6, les ecrous V7 et V8, les rondelles V5, les platines 07, les entretoises 07b et le bout des vis V9 au-dela du plan. S'y ajoutent la traverse 03 avec son tirant V2, les plaques 06c et 06d, le coin 02c avec son taraudage M16 puis son passage, le coulisseau 02a, le tourillon 06a, la pile 02e, le poussoir 02b, le patin 04b et les flancs 01. La poutrelle est rompue. Le coin en fin de course est figure par son enveloppe decalee de `COIN_COURSE`, en trait mixte a deux tirets. Les cotes depuis le plan median sont 85,5 (bout epais au repos), 155 (bout de tige) et 160 (bout des vis V9). Les lignes paralleles sont espacees de 7 mm. La course de 56,5 est donnee en note explicite.

**Coupe A-A (00-04, 00-30, 00-31).** C'est une vraie coupe, prise dans le plan x = +375 et tracee sur l'elevation. Elle est hachuree. Le patin d'appui y porte sa rainure `RAINURE_B` x `RAINURE_P` (D2), dans laquelle entre le bossage du flanc. Les plats sont noircis, la poutre est en trait mixte avec un trait de rupture, et l'axe y = 0 est trace. Les cotes sont 60 (calculee), 68 (entraxe des flancs, qui est aussi celui des plats, les axes servant de lignes d'attache) et (54), cote auxiliaire puisque la valeur figure deja au tableau des niveaux. Lors de la derniere passe, j'ai ajoute la note « Pieds 05, au-dela du plan, non figures ». Le pied couche de x = +250 est en effet au-dela du plan, et la vue est partielle.

**Portee (00-05, 00-17).** La cote 750 se mesure maintenant entre les axes d'appui. L'axe gauche descend du plat jusqu'au chant, l'axe droit est la trace de A-A. Le texte est calcule.

**Cotes verticales (00-06, 00-10).** Sur la planche 00, toutes les cotes passent par `cote_vx` / `cote_hx`, et le texte n'est plus barre. `_ligne_cote` n'est PAS modifiee (voir « Ce qui est ecarte »).

**Perspective (00-07, 00-08, 00-11, 00-12, conc-32).** La perspective est tournee de 180 degres, par rotation et sans miroir : z monte. J'ai verifie sur le rendu : les pieds couches sont en bas, la pile sous le lobe, la chape devant, et l'about x = -480 a droite, puisque la vue est prise depuis +x +y. Elle est placee en (318, 78), avec au moins 7 mm de jour avec l'elevation et ses cotes. Sa note dit : « Pieds couches, pieds en V et crochets d etuve figures ensemble : debout, les pieds couches restent sur la paillasse ». Le crochet porte la bulle 05c.

**Etuve et douille (00-09, conc-31, docu-09).** Le texte utilise `p.DEGAGEMENT_DOUILLE` (95 = `Y_ETUVE_LIBRE` - 155, avec 20 de garde de decentrage) et `ETUVE_INTERIEUR` suivi de « A CONFIRMER ». La valeur 250 n'est plus ecrite en dur.

**Pieds (00-16).** Les pieds couches (05) sont dessines dans leurs encoches, et la garde au sol de 30 est cotee. La longueur de 510 est donnee dans la note d'encombrement.

**Reperes (00-18, 00-19, 00-23, 00-27, 00-28, 00-29, docu-13).** Les notes a ligne d'attache sont toutes remplacees par des bulles de repere, terminees par un point dans le contour (ISO 128-22).
- Elevation : 01, 05, V1+06b (bulles accolees, coaxiales), V9, 02f.
- A-A : 04a, 04c.
- B-B : 03, 06c, 02c, 06d, 01, 02e, 02b, 04b, V2, 02d, 07b, 07, V6, 02a, 06a, V8, V5, V7, V9.
- Perspective : 05c.
- V3 et V4 sont cites dans le tableau des niveaux.

Les reperes des pieces sont lus dans `nomenclature.REPERES`. Seuls les numeros Vn sont ecrits en dur, faute de table. Je les ai controles un par un contre NOMENCLATURE.md.

**Tableau NIVEAUX.** Il donne z bas et z haut pour chaque piece de l'empilement vertical, plus l'axe de la tige. C'est ce qui positionne en z toutes les pieces du montage.

**Texte du coin (00-22, 00-24, docu-26, 00-34).** Le commentaire de B-B est place sous B-B, celui de A-A sous A-A, a 10 mm de la cote 68. Le texte est reecrit et le « voile » a disparu. Il dit : « Le coin AVANCE VERS LA CHAPE en chargeant ; repousse vers son bout epais, il TIRE la tige vers l interieur : la tete appuie, par la butee a aiguilles, sur la face exterieure des 2 platines ; monte a l envers, la tige ne retiendrait rien. » J'ai verifie ce sens sur la geometrie. La pente du coulisseau monte vers +y et le bout mince du coin est a +y. L'effort normal repousse donc le coin vers -y, et la tige est en traction. C'est coherent avec la nomenclature : 07b est « en compression pure », V8 « ne retient la tige qu'au desserrage ».

**Elevation (00-25, docu-26, 00-32).** Le coulisseau est dessine a `COULISSEAU_L`, et le coin du dessous de la plaque basse jusqu'a la traverse. Les types de traits suivent ISO 128 :
- la poutrelle, piece voisine, est en trait mixte fin a deux tirets ;
- les pieces logees entre les flancs ne se voient qu'a travers les ouvertures du flanc avant (decoupe SVG). Il n'y a donc aucun trait cache, et plus aucun contour ne se double ;
- devant le flanc, coin, patins, plats, tetes et ecrous M10 et pieds sont en trait moyen, sur fond blanc masquant.

**Valeurs (00-26, 00-34).** Plus aucune valeur n'est ecrite en dur : tous les textes passent par `D.fmt(params)`, avec la virgule decimale, et les cotes sont calculees. Les titres sont en minuscules. Le vocabulaire suit la nomenclature : « platines » pour la piece 07, « chape » pour le sous-ensemble.

**Fraicheur de la perspective (00-35).** La planche porte « modele 3D du 02/10/2026 ». Si iso.json est plus ancien que params.py ou parts.py, elle porte en plus « PERIME » et la console affiche un avertissement.

## Ce qui est ecarte, et pourquoi

- **00-06 / 00-10, correction de `View._ligne_cote` dans draw.py** : non faite. Elle deplace le texte de toutes les cotes verticales des planches 01 a 07, qui appartiennent aux autres agents, et mon mandat sur draw.py se limite a des ajouts. A la place, `cote_vx` / `cote_hx` sont disponibles (voir « Ce qui reste »).
- **00-16, cote 500 (entraxe des pieds couches)** : non ajoutee. Le pied est place par l'encoche du flanc, cotee sur la planche 01 : le monteur n'a aucun choix. Il faudrait en outre une troisieme ligne de cote sous l'elevation, qui tomberait sur le titre de B-B. La longueur de 510 est en note et la garde de 30 est cotee.
- **00-04, cotes 7,5 et 43,5** : non ajoutees, parce qu'elles sont redondantes. 7,5 = (103 - 68 - 20) / 2 se deduit de la cote 68, des plats centres sur les axes des flancs et de la poutre centree (axe de symetrie trace). 43,5 est la hauteur du contact : z bas des patins (42, au tableau) plus la profondeur de rainure (1,5, planche 04). La cote 54 est gardee, mais entre parentheses, puisqu'elle figure aussi au tableau.
- **00-07 / 00-12 / 00-13 / 00-33, « ech = 1/7 », « echelle 1:7 » et positions (300 ou 318, 112)** : remplaces. Une axonometrie n'a pas d'echelle vraie, d'ou « sans echelle ». La position est choisie pour la nouvelle mise en page.
- **00-31, `View.hachures` par clipPath et lignes** : le meme resultat est obtenu par un motif SVG (`Sheet.motif` + `View.zone`).
- **00-03 / 00-21, « dessiner comme sur la planche 07 en simple contour »** et **00-20, contour du coin decale** : remplaces par une vraie coupe et par l'enveloppe du coin en fin de course. Les degagements de pied de rebord sont omis dans l'enveloppe, parce qu'en tirets ils ne se lisaient plus.
- **00-18, 00-19, 00-27, 00-29 (replacer les notes)** et **00-22 (positions oy = 202, x = 250)** : sans objet. Les notes sont devenues des bulles et la mise en page a change.
- **00-34, « Le coin AVANCE VERS LA BUTEE »** : je garde « VERS LA CHAPE ». La nomenclature et l'ordre de montage appellent « chape » le sous-ensemble (platines, entretoises de butee, vis V9), et la phrase nomme explicitement les platines et la butee.
- **00-14, « reprendre la formule dans spec.py et nomenclature.py »**, **conc-11 (cote de la dent sur la planche 05, bornes de verifie)** et **conc-15 (EP_TOLE_REELLE)** : hors de ma planche. Ces points relevent des agents DOCUMENTS, de la planche 05 et MODELE. NOMENCLATURE.md l.7 donne deja -85,5 a +160.

## Ce qui reste

- **Cotes verticales des planches 01 a 07** : leur texte reste barre par la ligne. Chaque agent peut passer a `View.cote_vx` (texte a gauche, attaches ISO). Une fois toutes les planches replacees, on pourra aussi corriger `_ligne_cote` une fois pour toutes. `View.renvoi(p, texte, dx, dy, fin="point"|"fleche")` remplace `note()` avec la terminaison ISO 128-22 (constat 00-28, qui vaut pour toutes les planches).
- **Planche 07, a signaler a son agent** : sa phrase « AVANCE VERS LA BUTEE : il POUSSE la tige, qui pousse les platines contre les entretoises » est fausse ou au moins ambigue. La tige est TIREE vers l'interieur (07b en compression), comme le dit la planche 00.
- **Perspective** : elle depend de `out/iso.json`. Il faut relancer build_freecad.py apres toute modification de params.py ou parts.py ; l'avertissement « PERIME » le rappelle.
- **Etuve de 540, a confirmer** : la planche suit `ETUVE_INTERIEUR` et `ETUVE_CONFIRMEE` sans autre intervention.

## Controles (etat final)

- `python plans.py` s'execute sans erreur.
- `python verif_plans.py` : 0 faute sur les 8 planches, 521 textes.
- `python verif_percages.py` : 0 faute.
- `python params.py` : 0 probleme.
- `chk00.py`, sur la planche 00, traits fins compris : 0 remarque, 138 textes.
- SVG 01 a 07 identiques a l'octet pres a ceux d'avant mes changements. plans.py est inchange hors du bloc assemblage, et draw.py n'a recu que des ajouts, CRLF conserves.
- Relecture finale du rendu, decoupe par decoupe : planche entiere ; elevation (deux moities, centre, pied et cote 30, bulle V1) ; A-A (vue, rainure, texte) ; B-B (haut, droite, bas) ; perspective ; tableau et notes ; texte du bas ; cartouche. Aucun texte n'est traverse et aucune bulle ne se chevauche. Les lignes de cote paralleles sont a 7 mm, les cotes hors des pieces, et les echelles vraies et annoncees.
