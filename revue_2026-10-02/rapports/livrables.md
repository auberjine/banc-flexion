# Agent LIVRABLES : compte rendu du 02/10/2026

Fichiers modifiés : `export_dxf.py` (réécrit), `build_freecad.py`, `draw.py` (cartouche seulement, ajout pur). Fins de ligne CRLF et ASCII conservées. Les originaux sont copiés dans `scratchpad/correction/livrables/*.orig.py`. Dans `out/`, les dossiers dxf, step, stl et fcstd sont régénérés, ainsi que masses.json, iso.json, plans/*.svg, plans.html et banc_3d.html. Je n'ai touché ni params.py, ni parts.py, ni plans.py, ni spec.py, ni nomenclature.py, ni les .md.

## Contrôles finaux

| contrôle | résultat |
|---|---|
| `freecadcmd build_freecad.py` | OK. Cadre 35,23 kg, total 57,45 kg, identique à la copie de MODELE. La purge n'a rien eu à retirer, puisque les dossiers avaient été vidés par déplacement au préalable. Les messages « arête cassée ramenée à 0,3 » sur le pied et le crochet existaient déjà dans make_chanfrein.log : ce n'est pas une régression. |
| `freecadcmd verif_interference.py` | **0 interférence réelle sur 104 paires, 16 contacts vérifiés, 0 rompu.** Les engrènements attendus sont présents : flanc/pied 12 mm³, coulisseau/guide 167-173 mm³. |
| `python export_dxf.py` | 8 DXF de pièce, 3 DXF de groupe et LISTE.txt. Groupes : `tole_8mm_42crmo4.dxf` (13 pièces, 2 étagères, **2905 x 538**), `tole_8mm_42crmo4_EN_ATTENTE.dxf` (8 pièces, 1 étagère, **2491 x 127**) et `tole_10mm_s355.dxf` (5 pièces, **560 x 100**). Tous font moins de 3000 de large ; le script lève une erreur au-delà. |
| contenu de out/ comparé à `all_parts()` (script `correction/livrables/inventaire.py`) | out/step : 21 fichiers sur 21 attendus, aucun en trop. out/stl : 41 sur 41, aucun en trop. out/fcstd : banc.FCStd seul, sans .FCBak. out/dxf : les 10 fichiers attendus, plus `tole_8mm_42crmo4_EN_ATTENTE.dxf` et `LISTE.txt`, qui sont nouveaux et voulus. Aucun plat_renfort, plaquette, témoin ni groupe bronze. |
| géométrie des DXF, comparée à la génération du 22/09 (calques DECOUPE et GRAVURE, au 1e-3) | **flanc, pied, support et patin_appui sont IDENTIQUES** (D17, et D5 avec sa valeur par défaut). Seuls changent les quatre fichiers attendus : crochet (D9), patin_charge (avant-trous de 6, D7), poussoir (trous de 8,3, D7) et traverse (brut 65, D8). |
| essai avec ETUVE_CONFIRMEE = True, écrit dans le scratch | Plus de fichier EN_ATTENTE. Le groupe 8 mm reprend les 21 pièces (2 étagères, 2966 x 545) et pied.dxf ne porte plus l'alerte. Un .dxf étranger est purgé, un .txt étranger est conservé. |
| `python plans.py` puis `python verif_plans.py` | **0 faute sur 428 textes** et 8 planches. Le cartouche de la planche 01 est vérifié sur le rendu : la case du repère est coupée en deux, « rep. 01 » à gauche, « indice A / 02/10/2026 » à droite. |
| `python params.py` / `python verif_percages.py` | 0 problème / 0 faute. |

## Fait

### D14 : fichiers périmés et purge

1. **Inventaire**, fait avant tout déplacement. Les fichiers ont été comparés à `parts.all_parts()` et à ce que le code exporte.
   - 47 fichiers concernent des pièces supprimées, des pièces achetées ou d'anciennes nuances :
     - 10 DXF : entretoise_haute, plaquette_basse, plaquette_coin, plaquette_coul, plaquette_haute, plat_renfort, temoin, tole_10mm_42crmo4, tole_2mm_s235, tole_8mm_bronze ;
     - 12 STEP et 24 STL : arbre_vsf, bague, bague_ecrou, butee, butee_oreille, entretoise_haute, plaquette_coin, plaquette_coul, poussoir_fond, roue, temoin, vis_sans_fin ;
     - 1 fichier .FCBak.
   - Ces chiffres confirment conc-02, conc-07, conc-12 et docu-22. S'y ajoutent plat_renfort.dxf et tole_2mm_s235.dxf, devenus périmés avec D10.
2. **Déplacement, sans aucune suppression**, de 120 fichiers vers `out/perime_2026-10-02/{dxf,step,stl,fcstd}/` : les 47 ci-dessus et la génération du 22/09 des pièces actuelles, soit 73 fichiers, dont l'ancien banc.FCStd.
   - Avec ce choix, la première purge ne détruit rien.
   - Il évite aussi que FreeCAD refasse un .FCBak en sauvegardant par-dessus l'ancien fichier.
   - masses.json et iso.json ont été **copiés** dans ce dossier, pas déplacés.
   - Le fichier `LISEZMOI.txt` sépare les deux catégories, avec date et taille de chaque fichier.
3. **export_dxf.py** calcule et contrôle d'abord tous les profils (contours fermés), puis vide out/dxf, puis écrit. Il ne retire que ce qu'il produit lui-même, `*.dxf` et `LISTE.txt` (conc-02, conc-07, docu-22).
4. **build_freecad.py** : la nouvelle fonction `purger()`, appelée en tête de `main()`, retire `out/step/*.step|*.stp`, `out/stl/*.stl`, `out/fcstd/*.FCBak` et l'ancien `banc.FCStd` (conc-12). Sans ce dernier fichier, saveAs ne crée plus de sauvegarde .FCBak.
5. **Bloc DXF de build_freecad supprimé** (ancien l.221-230). Il écrivait out/dxf/<pièce>.dxf à partir du profil FINI, y compris pour les pièces achetées : c'est lui qui avait recréé plaquette_haute.dxf et plaquette_basse.dxf le 22/09 à 16:54. Il n'aurait porté ni la surépaisseur, ni l'indice, ni l'alerte. Le sous-dossier dxf n'est plus créé par ce script, l'import `dxf` disparaît et la docstring est mise à jour.
6. **Étagères (conc-49)** : algorithme « premier qui tient, hauteur décroissante », sur une largeur de `LARGEUR_GROUPE = 3000` au plus. L'en-tête du groupe précise qu'il ne s'agit pas d'une imbrication.
7. **Indice et date (conc-48)** :
   - `draw.py` : nouvelle fonction `edition()`, qui lit `INDICE_REVISION` et `DATE_EDITION` dans params, et nouveaux arguments facultatifs `indice=` et `date=` de `Sheet`. La case du repère est coupée en x0+160 : repère à gauche (il rétrécit s'il déborde), « indice A » et « 02/10/2026 » à droite. Les appels existants de plans.py ne changent pas.
   - DXF : « ind. A du 02/10/2026 » sur chaque pièce et dans l'en-tête de chaque groupe.
   - masses.json : clés `indice` et `date` ajoutées. Les lecteurs existants ne sont pas touchés.
8. **Calques** : la légende « DECOUPE = couper ; GRAVURE = marquer sans couper ; TEXTE = ni couper ni marquer » figure dans chaque DXF et dans LISTE.txt. Il reste à l'écrire dans la nomenclature (DOCS).
9. **LISTE.txt**, nouveau, proposé par conc-02 : indice, épaisseur de tôle réelle, légende, pièces du commerce sans DXF (liste tirée de `spec.achete`), puis pour chaque fichier l'épaisseur, la matière, la quantité et le statut.

### D15 : étuve

- `pied.dxf` et `crochet.dxf` portent `spec.dxf_avertissement`, c'est-à-dire ALERTE_ETUVE tant que `ETUVE_CONFIRMEE` est faux. Le texte « NE PAS DECOUPER AVANT CONFIRMATION DE LA LARGEUR D'ETUVE » est écrit en hauteur 10 au-dessus de la pièce, calque TEXTE.
- Le groupe 8 mm est **scindé**. `tole_8mm_42crmo4.dxf` ne contient que les pièces prêtes (flanc, traverse, poussoir, support) et peut partir tel quel. Le pied et le crochet sont dans `tole_8mm_42crmo4_EN_ATTENTE.dxf`, dont l'en-tête porte l'alerte en hauteur 14.
- Raison : les logiciels d'imbrication ignorent souvent les TEXT. Un avertissement noyé dans un fichier « à découper » ne protège donc pas.
- Dès que `ETUVE_CONFIRMEE = True`, tout revient dans un seul groupe, sans retouche (vérifié).
- LISTE.txt donne le statut de chaque fichier.

### D8, D7, D10, D4, D5 branchés sur le modèle

- Les profils viennent de `P.decoupe(spec)`.
- Traverse : le DXF est le brut de 65 (fini 64). Il porte « PROFIL BRUT : chant du bas +1, a fraiser en paquet a 64 de haut (fini) ».
- Patin de charge : avant-trous de 6, avec « percer-aleser 8 H7 ».
- Plat de renfort : il n'a plus de DXF (achete=True).
- Chaque DXF de pièce porte son brut (`spec.stock`, donc « tole 8 mm, cert. 3.1, Re >= 430 », D4).
- Les pièces dans la tôle des flancs portent aussi « fentes et encoches taillées pour une tôle réelle de 8,00 mm ». L'en-tête du groupe y ajoute NOTE_TOLE_REELLE (D5). Les patins de 10 ne portent pas cette mention, car elle ne les concerne pas.

### Autres

- La docstring de `casse_aretes` parlait encore de « cinq tôles de 10 » et d'un « bloc de 50 ». Elle est réécrite à partir de TRAVERSE_N et CHANFREIN (D13).
- `viewer3d.py` a été relancé : out/banc_3d.html est construit sur les STL régénérés, avec le nouveau coin, le nouveau crochet et le nouveau poussoir.

## Écarté, avec la raison

- **conc-24, variante « dossier out/dxf/EN_ATTENTE/ »** : pied.dxf et crochet.dxf restent dans out/dxf, parce que D15 les nomme ainsi et que la nomenclature les cherche là. Seul le groupe est séparé.
- **conc-02, variante « écrire dans un dossier temporaire puis renommer »** : remplacée par une autre solution, qui calcule et contrôle tous les profils avant de purger. Une erreur de profil laisse donc out/dxf intact.
- **conc-49, variante « renommer en controle_quantites »** : inutile, puisque les étagères respectent maintenant 3000.
- **Vider out/dxf de tout fichier** : la purge est limitée à ce que le script écrit (.dxf, LISTE.txt). Un fichier déposé à la main n'est pas détruit.
- **Désactiver les sauvegardes FreeCAD (préférence CreateBackupFiles)** : écarté. Ce serait un changement persistant de la configuration de l'utilisateur. Supprimer l'ancien banc.FCStd avant saveAs suffit.
- **00-08 / 00-11, variante « tourner iso.json dans build_freecad »** : écartée. La correction amendée la place dans plans.py et interdit de la faire aux deux endroits, sous peine de l'annuler. iso.json garde son repère d'origine.
- **Défauts de bibliothèque de draw.py** (texte des cotes verticales barré, lignes d'attache arrêtées 2 mm avant, lignes de repère sans terminaison) : non traités. Mon mandat sur draw.py se limite au cartouche, en ajout pur, et ces corrections déplacent tous les textes de cote de toutes les planches (voir « reste »).

## Reste

1. **draw.py, défauts systématiques signalés par les relectures**, à confier à PLANCHES ou à trancher. Toutes les planches en dépendent.
   - Texte des cotes verticales barré par sa ligne : `_ligne_cote` décale le texte de +1,6 mm du mauvais côté pour un texte tourné de -90° (00-06, 00-10, 01-09, 02-10, 02-11, 03-01, 03-16, 04-09, 04-14, 05-08, 06-07, 06-08, 07-03, 07-05).
   - Lignes d'attache arrêtées 2 mm avant la ligne de cote : dans `cote_h` et `cote_v`, il faut `ya - copysign(2, dz)` et `xa + copysign(2, dx)` (01-10, 02-24, 03-03, 05-07 ; voir la correction amendée de 00-07).
   - `View.note` sans terminaison ISO 128-22 (00-28, 01-32, 02-33, 03-18).
   - Ces corrections déplacent tous les textes de cote : il faudra relancer verif_plans.
2. **Planche 00** : la perspective est maintenant tirée d'un iso.json frais, mais elle est toujours à 180° (00-08). La rotation est à faire dans plans.py SEULEMENT.
3. **out/plans/plans.pdf date du 22/09.** plans.py ne le produit pas : make.py le refait par Edge. À relancer quand les planches seront définitives.
4. **DOCS (nomenclature, README)** :
   - nommer les deux fichiers nouveaux, `tole_8mm_42crmo4_EN_ATTENTE.dxf` et `out/dxf/LISTE.txt` ;
   - écrire la signification des calques (D14) ;
   - ajouter le statut « NE PAS DECOUPER… » au tableau des DXF (D15, conc-24 ; le champ `spec.dxf_avertissement` le donne) ;
   - indiquer que build_freecad n'écrit plus de DXF, et que out/dxf, out/step et out/stl sont purgés à chaque génération ;
   - la ligne 18 du README (« toutes les pièces d'une même épaisseur, disposées en bande ») devient « rangées en étagères de 3000 mm au plus, à imbriquer par le découpeur ; pièces en attente à part (`_EN_ATTENTE`) ».
5. **parts.py** : le champ `PartSpec.text_at` ne servait qu'au bloc DXF supprimé de build_freecad. Il n'est plus lu nulle part et peut être retiré par le propriétaire de parts.py.
6. **Case brut du cartouche** : BRUT_TOLE (« tole 8 mm, cert. 3.1, Re >= 430 ») occupe environ 54,6 mm sur 56 mm utiles. Il tient, mais sans marge si PLANCHES l'utilise ; verif_plans le dira.
7. Restent dans out/, hors du périmètre de D14 : les anciens logs (fem_*, flamb*, make_*), les dossiers fem/ et flamb*/, balayage_*.json et revue_brute.json. Je n'y ai pas touché.
