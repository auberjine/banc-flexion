# -*- coding: utf-8 -*-
"""
Calcul elements finis du flanc sous CalculiX, en console.

    <freecadcmd> fem_flanc.py

Chargement : 6 kN vers le haut aux deux trous de traverse (le noeud), appuis
verticaux sur les deux bossages. C'est la statique reelle d'un flanc quand la
vis pousse a 12 kN. Sortie : von Mises, fleche, points chauds.

Repere du calcul : x = x du modele, y = z du modele, z = epaisseur du flanc.
"""

import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def p(*a):
    print(*a)
    sys.stdout.flush()


import FreeCAD as App
import Part
import ObjectsFem
from FreeCAD import Vector
from femmesh import gmshtools
from femtools import ccxtools

import geom2d as G
import params as par
import parts as P


TAILLE_MAILLE = 4.5   # 6 mm donnait +/- 8 % d un calcul a l autre a l angle d appui (149 a 164 MPa)
                      # et une dissymetrie entre les deux appuis d un flanc symetrique ;
                      # a 4,5 mm (288 000 noeuds) les deux appuis tombent a 157 tous les deux
import os as _os
if _os.environ.get('BANC_MAILLE'):       # etude de convergence, sans toucher au fichier
    TAILLE_MAILLE = float(_os.environ['BANC_MAILLE'])
    print('taille de maille imposee : %g mm' % TAILLE_MAILLE)
CHARGE_NOEUD = 6000.0


# ------------------------------------------------------------- geometrie

def edge_of(seg):
    if seg[0] == 'L':
        p0, p1 = seg[1], seg[2]
        return Part.LineSegment(Vector(p0[0], p0[1], 0), Vector(p1[0], p1[1], 0)).toShape()
    _, c, r, a0, a1, ccw = seg
    circ = Part.Circle(Vector(c[0], c[1], 0), Vector(0, 0, 1), r)
    if ccw:
        return Part.ArcOfCircle(circ, a0, a1).toShape()
    return Part.ArcOfCircle(circ, a1, a0).toShape()


def wire_of(segs):
    edges = [edge_of(s) for s in segs if G.seg_length(s) > 1e-7]
    return Part.Wire(Part.__sortEdges__(edges))


def face_of(outer, holes):
    f = Part.Face(wire_of(outer))
    for h in holes:
        f = f.cut(Part.Face(wire_of(h)))
    return f


# ------------------------------------------------------------- reperage

def axe_cylindre(f):
    s = f.Surface
    return (s.Center.x, s.Center.y)


def faces_rayon(solid, rayon, cibles=None, tol=0.8):
    out = []
    for i, f in enumerate(solid.Faces):
        s = f.Surface
        if not hasattr(s, "Radius") or abs(s.Radius - rayon) > 0.05:
            continue
        if cibles is None:
            out.append((i + 1, f))
            continue
        cx, cy = axe_cylindre(f)
        for (tx, ty) in cibles:
            if abs(cx - tx) < tol and abs(cy - ty) < tol:
                out.append((i + 1, f))
                break
    return out


def face_normale_x(solid):
    """
    Blocage du mode de corps rigide en x : la PLUS GRANDE face plane de normale
    +x parmi celles du chant d extremite. Depuis que ce chant porte les
    encoches de pied, il est coupe en trois ; prendre "la plus a droite" tombait
    sur le morceau du haut, contre l angle de la membrure, et la reaction
    residuelle en x y fabriquait un point chaud de 197 MPa qui n existe pas.
    """
    cands = []
    for i, f in enumerate(solid.Faces):
        if f.Surface.TypeId != 'Part::GeomPlane':
            continue
        n = f.normalAt(0.5, 0.5)
        if n.x > 0.999:
            cands.append((f.BoundBox.Center.x, f.Area, i + 1))
    if not cands:
        return None
    xmax = max(c[0] for c in cands)
    bord = [c for c in cands if c[0] > xmax - 0.01]
    _x, aire, idx = max(bord, key=lambda c: c[1])
    return (idx, xmax, aire)


def face_fond_encoche(solid, x_pied):
    """Face plane au fond de l encoche de pied situee a x_pied (normale -Y du solide EF)."""
    for i, f in enumerate(solid.Faces):
        if f.Surface.TypeId != 'Part::GeomPlane':
            continue
        n = f.normalAt(0.5, 0.5)
        c = f.BoundBox.Center
        # le profil est extrude selon Z : la hauteur du modele est Y, et le fond
        # d une encoche ouverte vers le bas regarde vers -Y
        if n.y < -0.999 and abs(c.x - x_pied) < 1.0 and abs(c.y - par.PIED_CROIX_FLANC) < 0.5:
            return (i + 1, c.x, f.Area)
    return None


def sommet_proche(solid, pt):
    """Indice (1-base) et point du sommet du solide le plus proche de pt."""
    best = None
    for i, v in enumerate(solid.Vertexes):
        d = (v.Point - pt).Length
        if best is None or d < best[2]:
            best = (i + 1, v.Point, d)
    return best


def face_normale_y(solid):
    """Une face plane dont la normale est verticale : sert de reference de direction."""
    for i, f in enumerate(solid.Faces):
        if f.Surface.TypeId != 'Part::GeomPlane':
            continue
        n = f.normalAt(0.5, 0.5)
        if abs(n.y) > 0.999:
            return i + 1, (1.0 if n.y > 0 else -1.0)
    return None, 0.0


def main():
    doc = App.newDocument("fem")

    outer, holes = P.flanc_profile()
    solid = face_of(outer, holes).extrude(Vector(0, 0, par.EP_FLANC))
    obj = doc.addObject("Part::Feature", "flanc")
    obj.Shape = solid
    doc.recompute()
    p("flanc : %d faces, volume %.0f cm3" % (len(solid.Faces), solid.Volume / 1000.0))

    boss = faces_rayon(solid, par.BOSSAGE_R)
    # la charge entre par l'arete SUPERIEURE de la mortaise de traverse ; le
    # profil est extrude selon Z, donc le z du modele est le Y de la forme
    trous = [(i + 1, f) for i, f in enumerate(solid.Faces)
             if abs(f.CenterOfMass.y - (par.Z_TAB1 + par.TRAVERSE_JEU / 2.0)) < 0.3
             and abs(f.CenterOfMass.x) < par.TRAVERSE_LX / 2.0]
    idir, signe = face_normale_y(solid)
    p("bossages %d   faces de mortaise %d   face de direction %s (normale y %+.0f)"
      % (len(boss), len(trous), idir, signe))
    if len(boss) != 2 or len(trous) < 1 or idir is None:
        p("ECHEC : reperage des faces")
        return 1
    boss.sort(key=lambda t: axe_cylindre(t[1])[0])

    analyse = ObjectsFem.makeAnalysis(doc, "analyse")

    mat = ObjectsFem.makeMaterialSolid(doc, "tole")
    m = mat.Material
    m["Name"] = par.NUANCE_TOLE
    m["YoungsModulus"] = "210000 MPa"
    m["PoissonRatio"] = "0.30"
    m["Density"] = "7850 kg/m^3"
    mat.Material = m
    analyse.addObject(mat)

    c1 = ObjectsFem.makeConstraintDisplacement(doc, "appui_gauche")
    c1.References = [(obj, "Face%d" % boss[0][0])]
    c1.xFree, c1.yFree, c1.zFree = True, False, False
    c1.yDisplacement = c1.zDisplacement = 0.0
    analyse.addObject(c1)

    # Blocage du seul mode de corps rigide restant, x, sur UN SOMMET. Un blocage
    # sur une face epingle tous ses noeuds : la face ne peut plus se deformer en
    # x, ce qui est une raideur parasite la ou la tole travaille. Sur le chant
    # d extremite cela fabriquait 197 puis 145 MPa au bord de la face ; au fond
    # d une encoche de membrure, 152 MPa a l appui voisin. Un sommet ne
    # transmet aucune raideur, et l effort qu il reprend est nul par symetrie.
    iv = sommet_proche(solid, Vector(par.L_FLANC / 2.0, par.H_FLANC / 2.0, 0.0))
    c3 = ObjectsFem.makeConstraintDisplacement(doc, "blocage_x")
    c3.References = [(obj, "Vertex%d" % iv[0])]
    c3.xFree, c3.yFree, c3.zFree = False, True, True
    c3.xDisplacement = 0.0
    ix = (iv[0], iv[1].x, 0.0)
    if True:
        analyse.addObject(c3)
        p("blocage x sur le sommet %d a x = %.0f, y = %.0f" % (iv[0], iv[1].x, iv[1].y))

    c2 = ObjectsFem.makeConstraintDisplacement(doc, "appui_droit")
    c2.References = [(obj, "Face%d" % boss[1][0])]
    c2.xFree, c2.yFree, c2.zFree = True, False, False
    c2.yDisplacement = c2.zDisplacement = 0.0
    analyse.addObject(c2)

    ch = ObjectsFem.makeConstraintForce(doc, "charge_noeud")
    ch.References = [(obj, "Face%d" % i) for (i, _f) in trous]
    ch.Force = CHARGE_NOEUD
    ch.Direction = (obj, ["Face%d" % idir])
    ch.Reversed = (signe < 0)          # on veut la charge vers le haut
    analyse.addObject(ch)

    maillage = ObjectsFem.makeMeshGmsh(doc, "maillage")
    maillage.Shape = obj
    maillage.CharacteristicLengthMax = "%f mm" % TAILLE_MAILLE
    maillage.CharacteristicLengthMin = "%f mm" % (TAILLE_MAILLE / 4.0)
    maillage.ElementOrder = "2nd"
    maillage.OptimizeStd = True
    maillage.OptimizeNetgen = True
    maillage.HighOrderOptimize = "Optimization"
    maillage.MeshSizeFromCurvature = 12
    maillage.SecondOrderLinear = True      # noeuds milieux sur la corde : pas de jacobien negatif
    analyse.addObject(maillage)
    doc.recompute()

    p("maillage...")
    gm = gmshtools.GmshTools(maillage, analyse)
    err = gm.create_mesh()
    if err:
        p("gmsh :", str(err)[:300])
    doc.recompute()
    fm = maillage.FemMesh
    p("maillage : %d noeuds, %d volumes" % (fm.NodeCount, fm.VolumeCount))
    if fm.VolumeCount == 0:
        p("ECHEC : maillage vide")
        return 1

    solveur = ObjectsFem.makeSolverCalculiXCcxTools(doc, "ccx")
    solveur.AnalysisType = "static"
    solveur.GeometricalNonlinearity = "linear"
    solveur.ThermoMechSteadyState = False
    analyse.addObject(solveur)
    doc.recompute()

    p("resolution CalculiX...")
    travail = os.path.join(HERE, "out", "fem")
    if not os.path.isdir(travail):
        os.makedirs(travail)
    fea = ccxtools.FemToolsCcx(analyse, solveur)
    fea.setup_working_dir(travail)
    import outils
    fea.ccx_binary = outils.CCX
    fea.ccx_binary_present = True
    fea.purge_results()
    fea.update_objects()
    import traceback
    try:
        fea.write_inp_file()
        p("inp ecrit :", os.listdir(travail))
        fea.ccx_run()
        p("ccx termine :", os.listdir(travail))
        fea.load_results()
        p("resultats charges")
    except Exception:
        p(traceback.format_exc()[-1500:])
        return 1

    res = None
    for o in doc.Objects:
        if o.isDerivedFrom("Fem::FemResultObject"):
            res = o
    if res is None or not res.vonMises:
        p("ECHEC : pas de resultat exploitable")
        return 1

    vm = list(res.vonMises)
    dep = list(res.DisplacementLengths)
    vm_max = max(vm)
    vmt = sorted(vm)
    p("")
    p("=" * 62)
    p("von Mises maxi         %8.1f MPa" % vm_max)
    p("99,9e centile          %8.1f MPa" % vmt[int(0.999 * len(vmt))])
    p("99e centile            %8.1f MPa" % vmt[int(0.99 * len(vmt))])
    p("95e centile            %8.1f MPa" % vmt[int(0.95 * len(vmt))])
    p("coefficient sur %-7s %8.2f" % (par.NUANCE_TOLE, par.RE_TOLE / vm_max))
    p("deplacement maxi       %8.3f mm" % max(dep))
    p("=" * 62)

    noeuds = res.Mesh.FemMesh.Nodes
    ids = list(res.NodeNumbers)
    chauds = sorted(zip(vm, ids), reverse=True)[:600]
    zones = {}
    for v, nid in chauds:
        n = noeuds[nid]
        cle = (int(round(n.x / 30.0) * 30), int(round(n.y / 30.0) * 30))
        if cle not in zones or zones[cle] < v:
            zones[cle] = v
    tri = sorted(zones.items(), key=lambda t: -t[1])[:14]
    p("")
    p("points chauds :")
    for (cle, v) in tri:
        p("   x %6d   z %6d   %7.1f MPa" % (cle[0], cle[1], v))

    out = dict(von_mises_max=round(vm_max, 1),
               centile_999=round(vmt[int(0.999 * len(vmt))], 1),
               centile_99=round(vmt[int(0.99 * len(vmt))], 1),
               coef_securite=round(par.RE_TOLE / vm_max, 2),
               deplacement_max=round(max(dep), 3),
               noeuds=fm.NodeCount, volumes=fm.VolumeCount,
               charge_noeud_N=CHARGE_NOEUD,
               points_chauds=[dict(x=k[0], z=k[1], mpa=round(v, 1)) for k, v in tri])
    with open(os.path.join(HERE, "out", "fem_flanc.json"), "w") as f:
        json.dump(out, f, indent=1)
    p("")
    p("resultat ecrit dans out/fem_flanc.json")
    return 0


if not getattr(App, '_fem_flanc_lance', False):
    App._fem_flanc_lance = True
    main()
