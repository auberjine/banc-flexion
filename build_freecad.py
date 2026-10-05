# -*- coding: utf-8 -*-
"""
Construction du modele 3D sous FreeCAD, en console.

    <freecadcmd> build_freecad.py

Produit dans out/ :
    fcstd/banc.FCStd          assemblage complet, arbre par piece
    step/<piece>.step         geometrie exacte, une par piece (cote FINIE)
    step/banc.step            assemblage complet
    stl/<piece>.stl           maillage, pour visualisation et impression
    masses.json               masse et volume de chaque piece
    iso.json                  projection isometrique pour la planche 00

out/step et out/stl sont VIDES au depart (ainsi que les sauvegardes .FCBak et
l'ancien banc.FCStd) : un fichier de piece supprimee n'y survit plus a cote des
bons. Les DXF de decoupe ne sont PAS ecrits ici mais par export_dxf.py, seul a
prendre le profil de DECOUPE (parts.decoupe : surepaisseurs, avant-trous),
l'indice de revision et les avertissements.
"""

import os
import sys
import json
import math
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import FreeCAD as App
import Part
import Mesh
import MeshPart
import Import

from FreeCAD import Vector
import geom2d as G
import params as p
import parts as P
import outils


OUT = os.path.join(HERE, "out")
for sub in ("fcstd", "step", "stl"):
    d = os.path.join(OUT, sub)
    if not os.path.isdir(d):
        os.makedirs(d)


def purger():
    """
    Vide ce que ce script regenere : out/step/*.step, out/stl/*.stl, les
    sauvegardes out/fcstd/*.FCBak et l'ancien banc.FCStd (sans lui, saveAs en
    fait une nouvelle sauvegarde .FCBak). Rien d'autre n'est touche.
    """
    motifs = [("step", "*.step"), ("step", "*.stp"), ("stl", "*.stl"),
              ("fcstd", "*.FCBak"), ("fcstd", "banc.FCStd")]
    n = 0
    for sub, motif in motifs:
        for f in glob.glob(os.path.join(OUT, sub, motif)):
            if os.path.isfile(f):
                os.remove(f)
                n += 1
    print("out/step, out/stl, out/fcstd : %d fichier(s) de la generation precedente retires" % n)
    return n


# ------------------------------------------------------------- 2D -> edges

def edge_of(seg):
    if seg[0] == 'L':
        p0, p1 = seg[1], seg[2]
        return Part.LineSegment(Vector(p0[0], p0[1], 0), Vector(p1[0], p1[1], 0)).toShape()
    _, c, r, a0, a1, ccw = seg
    circ = Part.Circle(Vector(c[0], c[1], 0), Vector(0, 0, 1), r)
    if ccw:
        return Part.ArcOfCircle(circ, a0, a1).toShape()
    return Part.ArcOfCircle(circ, a1, a0).toShape()


def wire_of(segs, name=""):
    errs = G.check_closed(segs)
    if errs:
        raise ValueError("%s : contour non ferme, %d discontinuites, max %.4f mm"
                         % (name, len(errs), max(e[1] for e in errs)))
    edges = [edge_of(s) for s in segs if G.seg_length(s) > 1e-7]
    w = Part.Wire(Part.__sortEdges__(edges))
    if not w.isClosed():
        raise ValueError("%s : fil non ferme apres assemblage" % name)
    return w


def face_of(outer, holes, name=""):
    f = Part.Face(wire_of(outer, name + " contour"))
    for i, h in enumerate(holes):
        hf = Part.Face(wire_of(h, "%s trou %d" % (name, i)))
        f = f.cut(hf)
    if len(f.Faces) != 1:
        raise ValueError("%s : %d faces apres percage, contours qui se croisent ?"
                         % (name, len(f.Faces)))
    return f


# ------------------------------------------------------------- placement

# repere local (u, v, w) -> repere global. w est la direction d'extrusion.
PLANES = {
    'xz': (Vector(1, 0, 0), Vector(0, 0, 1), Vector(0, 1, 0)),
    'xy': (Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)),
    'yz': (Vector(0, 1, 0), Vector(0, 0, 1), Vector(1, 0, 0)),
    'zx': (Vector(0, 0, 1), Vector(1, 0, 0), Vector(0, 1, 0)),
}


def place(shape, plane, origin):
    u, v, w = PLANES[plane]
    m = App.Matrix(u.x, v.x, w.x, origin[0],
                   u.y, v.y, w.y, origin[1],
                   u.z, v.z, w.z, origin[2],
                   0, 0, 0, 1)
    s = shape.copy()
    s.transformShape(m, True)
    return s


def casse_aretes(solid, taille, epaisseur, nom):
    """
    Arete cassee a 45 degres sur les deux faces plates de la piece.

    Sans elle, le paquet de traverse (TRAVERSE_N toles jointives) se lit comme
    un bloc plein, a l'ecran comme a la main. Avec elle, chaque joint devient
    une rainure en V de 2 x CHANFREIN. C'est aussi la cote reelle : une tole
    decoupee laser se debavure toujours.
    """
    if not taille:
        return solid
    aretes = []
    for e in solid.Edges:
        zs = [vx.Point.z for vx in e.Vertexes]
        if not zs:
            continue
        if all(abs(z) < 1e-6 for z in zs) or all(abs(z - epaisseur) < 1e-6 for z in zs):
            aretes.append(e)
    if not aretes:
        return solid
    # Un chanfrein plus grand que les petits conges du contour (0,5 aux fentes
    # de calage, 0 aux racines de langue) rend le solide INVALIDE sans lever
    # d'erreur : les grandes faces disparaissent du maillage et la piece se
    # dessine en fil de fer. On controle isValid() et on reduit le chanfrein
    # jusqu'a ce que ca tienne, sinon on laisse l'arete vive.
    for t in (taille, 0.5, 0.3, 0.2):
        if t > taille:
            continue
        try:
            c = solid.makeChamfer(t, aretes)
        except Exception as exc:
            print("   chanfrein %g impossible sur %s (%d aretes) : %s" % (t, nom, len(aretes), exc))
            continue
        if c.isValid() and len(c.Faces) >= len(solid.Faces):
            if t < taille:
                print("   %s : arete cassee ramenee a %g, %g rendait le solide invalide" % (nom, t, taille))
            return c
    print("   %s : arete laissee vive, aucun chanfrein ne donne un solide valide" % nom)
    return solid


def build_part(spec):
    """spec : objet PartSpec de parts.py -> (shape, face2d)"""
    outer, holes = spec.profile()
    f = face_of(outer, holes, spec.name)
    u, v, w = PLANES[spec.plane]
    solid = f.extrude(Vector(0, 0, spec.thickness))
    if spec.features:
        solid = spec.features(solid, Part, Vector)
    solid = casse_aretes(solid, spec.chanfrein, spec.thickness, spec.name)
    solid = place(solid, spec.plane, spec.origin)
    if spec.rotate:
        ax, ang_deg, ctr = spec.rotate
        solid.rotate(Vector(*ctr), Vector(*ax), ang_deg)
    return solid, (outer, holes)


# ------------------------------------------------------------- main

def main():
    purger()
    doc = App.newDocument("banc")
    masses = []
    all_shapes = []

    specs = P.all_parts()
    print("=" * 68)
    print("%-26s %5s %9s %9s %8s" % ("piece", "qte", "volume cm3", "masse kg", "total kg"))
    print("=" * 68)

    total = 0.0
    for spec in specs:
        try:
            shape, prof = build_part(spec)
        except Exception as e:
            print("ECHEC %-20s : %s" % (spec.name, e))
            raise

        vol = shape.Volume / 1000.0                       # cm3
        m = vol * spec.density / 1.0e6                    # kg
        mt = m * spec.qty
        total += mt
        masses.append(dict(nom=spec.name, designation=spec.designation, qte=spec.qty,
                           volume_cm3=round(vol, 2), masse_kg=round(m, 3),
                           masse_totale_kg=round(mt, 3), matiere=spec.material,
                           brut=spec.stock))
        print("%-26s %5d %9.1f %9.3f %8.2f" % (spec.name, spec.qty, vol, m, mt))

        inst_shapes = []
        for i, pos in enumerate(spec.instances):
            s = shape.copy()
            if pos.get('mirror_y'):
                mm = App.Matrix()
                mm.scale(1, -1, 1)
                s = s.transformGeometry(mm)
            if pos.get('rot'):
                ax, ang, ctr = pos['rot']
                s.rotate(Vector(*ctr), Vector(*ax), ang)
            if pos.get('flip'):
                bb = s.BoundBox
                s.rotate(Vector(bb.Center.x, bb.Center.y, bb.Center.z),
                         Vector(1, 0, 0), 180.0)
            s.translate(Vector(*pos.get('t', (0, 0, 0))))
            o = doc.addObject("Part::Feature", "%s_%d" % (spec.name, i + 1))
            o.Shape = s
            o.Label = "%s %d" % (spec.designation, i + 1)
            all_shapes.append(s)
            inst_shapes.append(s)

        # exports individuels : STEP de la piece seule, STL de tous ses exemplaires
        Import.export([doc.getObject("%s_1" % spec.name)],
                      os.path.join(OUT, "step", spec.name + ".step"))
        mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.2,
                                      AngularDeflection=0.35, Relative=False)
        mesh.write(os.path.join(OUT, "stl", spec.name + ".stl"))
        mesh = MeshPart.meshFromShape(Shape=Part.makeCompound(inst_shapes),
                                      LinearDeflection=0.25,
                                      AngularDeflection=0.4, Relative=False)
        mesh.write(os.path.join(OUT, "stl", spec.name + "_montes.stl"))
        # Plus de DXF ici : ce bloc ecrivait out/dxf/<piece>.dxf depuis le
        # profil FINI et sans exclure les pieces achetees (plaquettes, plat),
        # sans indice ni avertissement. C'est le travail de export_dxf.py.

    print("=" * 68)
    cadre = sum(x['masse_totale_kg'] for x in masses if not x['nom'].startswith('poutre'))
    print("masse totale modelisee %.2f kg   dont cadre %.2f kg" % (total, cadre))

    doc.recompute()
    doc.saveAs(os.path.join(OUT, "fcstd", "banc.FCStd"))
    Import.export(doc.Objects, os.path.join(OUT, "step", "banc.step"))

    comp = Part.makeCompound(all_shapes)
    mesh = MeshPart.meshFromShape(Shape=comp, LinearDeflection=0.4,
                                  AngularDeflection=0.5, Relative=False)
    mesh.write(os.path.join(OUT, "stl", "banc_assemblage.stl"))

    # projection isometrique pour la planche d'ensemble
    try:
        import TechDraw
        iso = {}
        for nom, direction, shp in (("ensemble", (1.0, 1.0, 0.55), comp),):
            res = TechDraw.projectEx(shp, Vector(*direction))
            # projectEx rend (visibles vives, visibles lisses, coutures,
            # CONTOURS APPARENTS, isos, puis les cachees) : sans le 4e groupe,
            # un cylindre (tube, tige, ecrou) n'a pas de generatrices de bord.
            # Fleche de 0,03 : a 0,6 un trou de 11 n'avait que 6 cotes.
            polys = []
            for groupe in (res[0], res[3]):
                if groupe is None:
                    continue
                for e in groupe.Edges:
                    pts = e.discretize(Deflection=0.03)
                    polys.append([[round(q.x, 2), round(q.y, 2)] for q in pts])
            iso[nom] = polys
            print("projection %s : %d aretes visibles" % (nom, len(polys)))
        iso["date_calcul"] = outils.aujourdhui()
        iso["empreinte"] = outils.empreinte_modele()
        with open(os.path.join(OUT, "iso.json"), "w") as f:
            json.dump(iso, f)
    except Exception as e:
        print("projection isometrique impossible :", e)

    with open(os.path.join(OUT, "masses.json"), "w") as f:
        json.dump(dict(pieces=masses, total_kg=round(total, 2),
                       cadre_kg=round(cadre, 2), indice=p.INDICE_REVISION,
                       date=p.DATE_EDITION, date_calcul=outils.aujourdhui(),
                       empreinte=outils.empreinte_modele()), f, indent=1)

    print("\ncontrole d'interference : lancer verif_interference.py")
    sys.stdout.flush()
    return 0


if not getattr(App, '_banc_build_lance', False):
    App._banc_build_lance = True
    main()
