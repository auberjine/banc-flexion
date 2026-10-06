# -*- coding: utf-8 -*-
"""
Export DXF de toutes les pieces planes a decouper, sans FreeCAD.

    python export_dxf.py

Vide d'abord out/dxf (ses .dxf et LISTE.txt : aucun fichier d'une generation
precedente n'y survit, c'est ainsi que des pieces supprimees, achetees ou d'une
autre nuance y etaient restees a cote des bonnes), puis ecrit :

    out/dxf/<piece>.dxf            une piece, profil de DECOUPE (parts.decoupe :
                                   brut laser quand il differe du fini)
    out/dxf/tole_<ep>mm_<nuance>.dxf
                                   par epaisseur et nuance, tous les exemplaires
                                   a decouper, ranges en etageres de
                                   LARGEUR_GROUPE de large au plus (ce n'est pas
                                   une imbrication : le decoupeur imbrique sur
                                   son format)
    out/dxf/tole_<ep>mm_<nuance>_EN_ATTENTE.dxf
                                   les pieces qui portent un avertissement (pied
                                   et crochet tant que l'etuve n'est pas
                                   confirmee), tenues HORS du groupe a decouper
    out/dxf/LISTE.txt              fichiers, epaisseur, nuance, quantite, statut

Calques : DECOUPE = contour a couper ; GRAVURE = marquage laser, ne pas couper ;
TEXTE = indications, ni coupe ni marquage. Chaque fichier porte l'indice de
revision et la date d'edition de params et, pour les pieces des deux toles de
8 (42CrMo4 : flancs, platines ; S355JR : pieds, crochets, traverse, poussoir),
l'epaisseur REELLE de la tole pour laquelle ses fentes, encoches et mortaises
ont ete taillees : celle de la tole qu'elles RECOIVENT (voir tole_reelle).
"""

import os
import params as p
import geom2d as G
import dxf as DXF
import parts as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "dxf")
LISTE = "LISTE.txt"

LARGEUR_GROUPE = 3000.0     # mm : largeur des plus grands formats de tole (3000 x 1500)
MARGE_X = 25.0              # entre deux pieces d'une etagere
ECART_ETAGERES = 40.0       # entre deux etageres, etiquettes comprises
H_ETIQUETTE = 6.0

LEGENDE = ("calques : DECOUPE = couper ; GRAVURE = marquer sans couper ;"
           " TEXTE = ni couper ni marquer")


def fr(v):
    s = "%.2f" % v
    s = s.rstrip("0").rstrip(".") if "." in s else s
    return s.replace(".", ",")


def edition():
    return "ind. %s du %s" % (p.INDICE_REVISION, p.DATE_EDITION)


def mm(v):
    return ("%.2f" % v).replace(".", ",")


def ep_reelle(matiere):
    """Epaisseur reelle de la tole de 8 d'ou sort une piece de cette matiere."""
    return p.EP_TOLE_REELLE_42 if matiere == p.MATIERE_TOLE else p.EP_TOLE_REELLE_S355


def toles_reelles():
    """Les deux toles de 8, telles que mesurees (LISTE.txt)."""
    return ("toles reelles : %s %s mm (EP_TOLE_REELLE_42), %s %s mm (EP_TOLE_REELLE_S355)"
            % (p.NUANCE_TOLE, mm(p.EP_TOLE_REELLE_42), p.NUANCE_TOLE_COURANTE,
               mm(p.EP_TOLE_REELLE_S355)))


def tole_reelle(nom, matiere):
    """
    Texte du DXF d'une piece des toles de 8. Chaque fente, encoche ou mortaise
    suit l'epaisseur de la tole qu'elle RECOIT : le flanc (42CrMo4) recoit les
    pieds et le paquet de traverse (S355) ; le pied (S355) recoit le flanc
    (42CrMo4) dans ses encoches et la dent du crochet (S355) dans ses fentes.
    Les autres pieces n'ont pas de fente : leur propre tole regle celles qui
    les recoivent.
    """
    if nom == "flanc":
        return ("encoches et mortaise taillees pour la tole %s reelle de %s mm (pieds, traverse)"
                % (p.NUANCE_TOLE_COURANTE, mm(p.EP_TOLE_REELLE_S355)))
    if nom == "pied":
        return ("encoches et nodes taillees pour la tole %s reelle de %s mm (flanc),"
                " fentes pour la tole %s reelle de %s mm (crochet)"
                % (p.NUANCE_TOLE, mm(p.EP_TOLE_REELLE_42), p.NUANCE_TOLE_COURANTE,
                   mm(p.EP_TOLE_REELLE_S355)))
    return ("tole %s reelle prise a %s mm (fentes ou serrages qui recoivent cette piece)"
            % (matiere.split()[0], mm(ep_reelle(matiere))))


def de_la_tole(ep, matiere):
    """Piece de l'une des deux toles de 8 : ses fentes et encoches (ou celles
    qui la recoivent) suivent EP_TOLE_REELLE_42 ou EP_TOLE_REELLE_S355. Les
    patins de 10 n'en dependent pas."""
    return ep == p.EP_FLANC and matiere in (p.MATIERE_TOLE, p.MATIERE_TOLE_COURANTE)


# Pieces dont le DXF n'est PAS la piece finie (PartSpec.dxf_profile) : ce que
# l'atelier doit reprendre apres la decoupe, ecrit sur le DXF.
REPRISES = {
    "traverse": lambda: ("PROFIL BRUT : chant du bas +%s, a fraiser en paquet a %s de haut (fini)"
                         % (fr(p.TRAVERSE_SUREP), fr(p.TRAVERSE_H))),
}


def translate(segs, dx, dz):
    out = []
    for s in segs:
        if s[0] == 'L':
            out.append(('L', (s[1][0] + dx, s[1][1] + dz), (s[2][0] + dx, s[2][1] + dz)))
        else:
            out.append(('A', (s[1][0] + dx, s[1][1] + dz), s[2], s[3], s[4], s[5]))
    return out


def court(matiere):
    return matiere.split()[0].lower().replace("jr", "")


def toutes():
    """
    Toutes les pieces a decouper, PRISES DANS LE MODELE : tout ce que
    parts.all_parts() declare plat et non achete. Ne rien lister a la main ici :
    c'est ainsi que la platine de butee avait ete oubliee du debit. Le profil est
    celui de DECOUPE (parts.decoupe), controle ferme avant toute ecriture.
    """
    lst = []
    for spec in P.all_parts():
        if not spec.flat or getattr(spec, "achete", False):
            continue
        o, h = P.decoupe(spec)
        for nom, c in [("contour", o)] + [("trou %d" % i, t) for i, t in enumerate(h)]:
            errs = G.check_closed(c)
            if errs:
                raise ValueError("%s, %s : contour non ferme, %d discontinuite(s), max %.4f mm"
                                 % (spec.name, nom, len(errs), max(e[1] for e in errs)))
        reprise = REPRISES.get(spec.name)
        if spec.dxf_profile and not reprise:
            reprise = lambda: "PROFIL BRUT : reprise d'usinage apres decoupe, voir le plan"
        lst.append(dict(nom=spec.name, outer=o, holes=h, ep=spec.thickness,
                        mat=spec.material, brut=spec.stock, qte=spec.qty,
                        gravure=spec.engrave(),
                        alerte=getattr(spec, "dxf_avertissement", "") or "",
                        reprise=reprise() if reprise else ""))
    return lst


def purger():
    """Vide out/dxf de ce que ce script y ecrit (.dxf et LISTE.txt)."""
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
        return 0
    n = 0
    for f in os.listdir(OUT):
        chemin = os.path.join(OUT, f)
        if os.path.isfile(chemin) and (f.lower().endswith(".dxf") or f == LISTE):
            os.remove(chemin)
            n += 1
    return n


def ecrire_piece(it):
    d = DXF.Dxf()
    d.contour(it["outer"], "DECOUPE")
    for hh in it["holes"]:
        d.contour(hh, "DECOUPE")
    for g in it["gravure"]:
        d.contour(g, "GRAVURE")
    x0, z0, x1, z1 = G.bbox(it["outer"])
    lignes = [(8.0, "%s  ep%g  %s  x%d" % (it["nom"].upper(), it["ep"], it["mat"], it["qte"])),
              (5.0, "brut : %s" % it["brut"]),
              (5.0, "%s  -  %s" % (edition(), tole_reelle(it["nom"], it["mat"]))
               if de_la_tole(it["ep"], it["mat"]) else edition())]
    if it["reprise"]:
        lignes.append((5.0, it["reprise"]))
    lignes.append((4.0, LEGENDE))
    z = z0 - 14.0
    for h, t in lignes:
        d.text((x0, z), h, t)
        z -= h + 4.0
    if it["alerte"]:
        # au dessus de la piece, en gros : c'est la premiere chose qu'on lit
        d.text((x0, z1 + 10.0), 10.0, it["alerte"])
    d.save(os.path.join(OUT, it["nom"] + ".dxf"))
    print("  %-18s %7.0f x %6.0f mm   ep %g%s" % (it["nom"], x1 - x0, z1 - z0, it["ep"],
                                                "   ATTENTE" if it["alerte"] else ""))


def etageres(items):
    """
    Range tous les exemplaires en etageres de LARGEUR_GROUPE de large au plus,
    les plus hautes d'abord (premier qui tient, hauteur decroissante). Renvoie
    [(item, n, dx, dz)] et (largeur, hauteur) du rangement.
    """
    inst = []
    for it in items:
        x0, z0, x1, z1 = G.bbox(it["outer"])
        for n in range(it["qte"]):
            inst.append((it, n, x1 - x0, z1 - z0))
    inst.sort(key=lambda e: (-e[3], e[0]["nom"], e[1]))
    rangees, cur, larg = [], [], 0.0
    for e in inst:
        w = e[2]
        if cur and larg + MARGE_X + w > LARGEUR_GROUPE:
            rangees.append(cur)
            cur, larg = [], 0.0
        larg = w if not cur else larg + MARGE_X + w
        cur.append(e)
    if cur:
        rangees.append(cur)

    places, z_haut, largeur = [], 0.0, 0.0
    for r in rangees:
        h = max(e[3] for e in r)
        z_bas = z_haut - h
        x = 0.0
        for it, n, w, _hh in r:
            x0, z0, _x1, _z1 = G.bbox(it["outer"])
            places.append((it, n, x - x0, z_bas - z0))
            x += w + MARGE_X
        largeur = max(largeur, x - MARGE_X)
        z_haut = z_bas - ECART_ETAGERES
    hauteur = -(z_haut + ECART_ETAGERES)
    return places, (largeur, hauteur), len(rangees)


def ecrire_groupe(nom_fichier, items, alerte=""):
    d = DXF.Dxf()
    places, (largeur, hauteur), n_rang = etageres(items)
    for it, n, dx, dz in places:
        d.contour(translate(it["outer"], dx, dz), "DECOUPE")
        for hh in it["holes"]:
            d.contour(translate(hh, dx, dz), "DECOUPE")
        for g in it["gravure"]:
            d.contour(translate(g, dx, dz), "GRAVURE")
        x0, z0, _x1, _z1 = G.bbox(it["outer"])
        d.text((x0 + dx, z0 + dz - 12.0), H_ETIQUETTE, "%s %d/%d" % (it["nom"], n + 1, it["qte"]))
    it0 = items[0]
    bruts = sorted(set(it["brut"] for it in items))
    entete = [(8.0, "TOLE %g mm  %s  -  %d pieces  -  %s"
               % (it0["ep"], it0["mat"], sum(i["qte"] for i in items), edition())),
              (5.0, "brut : %s" % " / ".join(bruts))]
    if de_la_tole(it0["ep"], it0["mat"]):
        entete.append((5.0, "tole %s reelle prise a %s mm : %s"
                       % (it0["mat"].split()[0], mm(ep_reelle(it0["mat"])), p.NOTE_TOLE_REELLE)))
        for it in items:
            if it["nom"] in ("flanc", "pied"):
                entete.append((5.0, "%s : %s" % (it["nom"], tole_reelle(it["nom"], it["mat"]))))
    entete += [(5.0, "rangement en etageres de %g mm au plus, pas une imbrication :"
                    " le decoupeur imbrique sur son format" % LARGEUR_GROUPE),
              (4.0, LEGENDE)]
    if alerte:
        entete.insert(0, (14.0, alerte))
    z = 20.0
    for h, t in reversed(entete):
        d.text((0.0, z), h, t)
        z += h + 5.0
    d.save(os.path.join(OUT, nom_fichier))
    print("  groupe %-34s %2d pieces, %d etagere(s), %.0f x %.0f mm"
          % (nom_fichier, sum(i["qte"] for i in items), n_rang, largeur, hauteur))
    if largeur > LARGEUR_GROUPE + 1e-6:
        raise ValueError("%s : %.0f mm de large, plus que %g (piece plus large que le format ?)"
                         % (nom_fichier, largeur, LARGEUR_GROUPE))
    return largeur, hauteur, n_rang


def main():
    lst = toutes()                       # tout est calcule et controle AVANT de vider
    n = purger()
    print("out/dxf vide : %d fichier(s) de la generation precedente retires" % n)

    liste = []
    for it in lst:
        ecrire_piece(it)
        liste.append((it["nom"] + ".dxf", it["ep"], it["mat"], it["qte"],
                      it["alerte"] or "a decouper" + (" (brut, reprise)" if it["reprise"] else "")))

    # Regroupement par epaisseur ET PAR MATIERE : deux nuances ne partagent
    # jamais une bande. Les pieces en attente (avertissement) ont leur propre
    # fichier : le groupe a decouper doit pouvoir partir tel quel.
    par_ep = {}
    for it in lst:
        par_ep.setdefault((it["ep"], it["mat"]), []).append(it)
    for (ep, mat), items in sorted(par_ep.items()):
        base = "tole_%gmm_%s" % (ep, court(mat))
        prets = [i for i in items if not i["alerte"]]
        attente = [i for i in items if i["alerte"]]
        if prets:
            w, h, nr = ecrire_groupe(base + ".dxf", prets)
            liste.append((base + ".dxf", ep, mat, sum(i["qte"] for i in prets),
                          "groupe a decouper : %s ; %d etagere(s), %.0f x %.0f"
                          % (", ".join(i["nom"] for i in prets), nr, w, h)))
        if attente:
            alertes = sorted(set(i["alerte"] for i in attente))
            w, h, nr = ecrire_groupe(base + "_EN_ATTENTE.dxf", attente, " / ".join(alertes))
            liste.append((base + "_EN_ATTENTE.dxf", ep, mat, sum(i["qte"] for i in attente),
                          "%s : %s" % (" / ".join(alertes), ", ".join(i["nom"] for i in attente))))

    with open(os.path.join(OUT, LISTE), "w", newline="\r\n") as fh:
        fh.write("DXF de decoupe, %s\n" % edition())
        fh.write("%s : %s\n" % (toles_reelles(), p.NOTE_TOLE_REELLE))
        fh.write("Fentes, encoches et mortaises : chacune suit la tole qu elle RECOIT (flanc : tole"
                 " %s ; pied : %s pour les encoches et nodes, %s pour les fentes).\n"
                 % (p.NUANCE_TOLE_COURANTE, p.NUANCE_TOLE, p.NUANCE_TOLE_COURANTE))
        fh.write("%s\n" % LEGENDE)
        achetees = [s.name for s in P.all_parts() if getattr(s, "achete", False)]
        fh.write("Pieces du commerce, sans DXF : %s.\n\n" % ", ".join(achetees))
        fh.write("%-34s %5s  %-12s %4s  %s\n" % ("fichier", "ep", "matiere", "qte", "statut"))
        for f, ep, mat, q, st in liste:
            fh.write("%-34s %5g  %-12s %4d  %s\n" % (f, ep, mat, q, st))
    print("  %s : %d fichiers" % (LISTE, len(liste)))


if __name__ == "__main__":
    main()
