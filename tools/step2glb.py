"""STEP -> GLB with CAD colors and full tessellation (no simplification).

usage: python3 tools/step2glb.py <step dir> <out dir> [part id ...]

Each part becomes one GLB with one mesh per CAD color. The material that covers
the largest area is named "main" so the web app can recolor it to the kit color;
other materials are named "cad" and keep their CAD color.
Electronics cables are removed per face (see CABLE_CUTS), so cut edges follow
CAD face boundaries instead of slicing triangles.
"""
import sys, os, glob, json, subprocess, numpy as np, trimesh
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_ColorTool, XCAFDoc_DocumentTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen, XCAFDoc_ColorCurv
from OCP.TDF import TDF_Label, TDF_ChildIterator
from OCP.Quantity import Quantity_Color, Quantity_TOC_sRGB
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepLib import BRepLib_ToolTriangulatedShape
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID, TopAbs_REVERSED
from OCP.TopoDS import TopoDS, TopoDS_Shape
from OCP.TopLoc import TopLoc_Location
from OCP.BRep import BRep_Tool
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

LIN, ANG = 0.06, 0.3   # same tessellation as the original cache (about 870k triangles for the kit)
# axis, keep >= lo, keep <= hi  (whole-face test)
CABLE_CUTS = {'269-6690-000':(0,-50,None),'269-6695-000':(2,None,26),'269-6686-000':(2,None,40),
              '269-6696-000':(0,-26,None),'269-6702-000':(0,-26,None)}
GLTFPACK = os.path.join(os.path.dirname(__file__), '..', 'node_modules', '.bin', 'gltfpack')

_keep = []
def read(path):
    doc = TDocStd_Document(TCollection_ExtendedString("doc"))
    r = STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True)
    if r.ReadFile(path) != 1: raise RuntimeError('read failed')
    r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    it = TDF_ChildIterator(st.Label(), False); lab = None
    while it.More():
        l = it.Value()
        if st.IsFree_s(l) and st.IsTopLevel(l): lab = l; break
        it.Next()
    shape = st.GetShape_s(lab)
    _keep.append((doc, r))   # the XCAF document must outlive every shape and label taken from it
    return shape, st, ct, lab

def color_of(ct, shp):
    c = Quantity_Color()
    for t in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen):
        try: ok = ct.GetColor(shp, t, c)
        except Exception: ok = False
        if ok:
            r, g, b = c.Values(Quantity_TOC_sRGB)
            return '#%02x%02x%02x' % tuple(int(round(max(0, min(1, v)) * 255)) for v in (r, g, b))
    return None

def label_color(ct, lab):
    if lab.IsNull(): return None
    c = Quantity_Color()
    for t in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen):
        if XCAFDoc_ColorTool.GetColor_s(lab, t, c):
            r, g, b = c.Values(Quantity_TOC_sRGB)
            return '#%02x%02x%02x' % tuple(int(round(max(0, min(1, v)) * 255)) for v in (r, g, b))
    return None

def colored_faces(st, ct, lab, loc, inherited):
    """Yield (located face, hex) for every face under an XCAF label.
    Assemblies are walked through their components so colors set on prototype
    shapes, solids or single faces all survive the component locations."""
    own = label_color(ct, lab) or inherited
    if st.IsAssembly_s(lab):
        it = TDF_ChildIterator(lab, False)
        while it.More():
            comp = it.Value(); it.Next()
            if not st.IsComponent_s(comp): continue
            ref = TDF_Label()
            if not st.GetReferredShape_s(comp, ref): continue
            yield from colored_faces(st, ct, ref, loc.Multiplied(st.GetLocation_s(comp)), label_color(ct, comp) or own)
        return
    proto = st.GetShape_s(lab)
    sx = TopExp_Explorer(proto, TopAbs_SOLID); seen = False
    def faces_of(shp, base):
        fx = TopExp_Explorer(shp, TopAbs_FACE)
        while fx.More():
            f = TopoDS.Face(fx.Current()); fx.Next()
            yield TopoDS.Face(f.Moved(loc)), color_of(ct, f) or base
    while sx.More():
        sol = sx.Current(); sx.Next(); seen = True
        yield from faces_of(sol, color_of(ct, sol) or own)
    if not seen: yield from faces_of(proto, own)

def convert(path, out_glb, pid):
    shape, st, ct, root = read(path)
    BRepMesh_IncrementalMesh(shape, LIN, False, ANG, True)
    default = label_color(ct, root) or '#9a9a9a'
    cut = CABLE_CUTS.get(pid)
    groups = {}   # hex -> [V, N, F, area, nverts]
    dropped = 0
    for f, col in colored_faces(st, ct, root, TopLoc_Location(), default):
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f, loc)
        if tri is None: continue
        tr = loc.Transformation(); n = tri.NbNodes()
        V = np.array([[p.X(), p.Y(), p.Z()] for p in (tri.Node(i).Transformed(tr) for i in range(1, n + 1))])
        if cut:
            ax, lo, hi = cut   # drop any face that reaches past the cut; body faces never do, cable faces always do
            if (lo is not None and V[:, ax].min() < lo) or (hi is not None and V[:, ax].max() > hi): dropped += 1; continue
        if not tri.HasNormals(): BRepLib_ToolTriangulatedShape.ComputeNormals_s(f, tri)
        rev = f.Orientation() == TopAbs_REVERSED
        Nn = []
        for i in range(1, n + 1):
            d = tri.Normal(i).Transformed(tr)
            Nn.append([d.X(), d.Y(), d.Z()])
        Nn = np.array(Nn)
        if rev: Nn = -Nn
        F = np.array([tri.Triangle(i).Get() for i in range(1, tri.NbTriangles() + 1)]) - 1
        if rev: F = F[:, [0, 2, 1]]
        g = groups.setdefault(col, [[], [], [], 0.0, 0])
        g[2].append(F + g[4]); g[0].append(V); g[1].append(Nn); g[4] += n
        gp = GProp_GProps(); BRepGProp.SurfaceProperties_s(f, gp); g[3] += gp.Mass()
    main = max(groups, key=lambda k: groups[k][3])
    scene = trimesh.Scene(); stats = []
    for col, (Vs, Ns, Fs, area, _) in sorted(groups.items(), key=lambda kv: -kv[1][3]):
        V = np.vstack(Vs); N = np.vstack(Ns); F = np.vstack(Fs)
        N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
        rgb = [int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        name = ('main_' if col == main else 'cad_') + col[1:]
        mat = trimesh.visual.material.PBRMaterial(name=name, baseColorFactor=rgb + [1.0], metallicFactor=0.0, roughnessFactor=0.55)
        m = trimesh.Trimesh(V, F, vertex_normals=N, process=False, visual=trimesh.visual.TextureVisuals(material=mat))
        scene.add_geometry(m, node_name=name, geom_name=name)
        stats.append((col, len(F), round(area)))
    raw = out_glb + '.raw.glb'
    scene.export(raw)
    subprocess.run([GLTFPACK, '-i', raw, '-o', out_glb, '-cc', '-km', '-kn', '-vp', '16'], check=True, capture_output=True)
    os.remove(raw)
    return dict(main=main, groups=stats, dropped=dropped, tris=sum(s[1] for s in stats))

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]; only = set(sys.argv[3:])
    os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(src + '/*.STEP') + glob.glob(src + '/*/*.STEP'))
    report = {}
    for p in files:
        pid = os.path.basename(p).split(' ')[0].replace('.STEP', '')
        if only and pid not in only: continue
        try:
            r = convert(p, os.path.join(out, pid + '.glb'), pid)
            r['kb'] = os.path.getsize(os.path.join(out, pid + '.glb')) // 1024
            report[pid] = r; print(pid, r['tris'], 'tris', r['kb'], 'KB', 'main', r['main'], [g[0] for g in r['groups']], 'dropped', r['dropped'], flush=True)
        except Exception as e:
            print(pid, 'ERR', repr(e), flush=True)
    rp = os.path.join(out, '_report.json')
    old = json.load(open(rp)) if os.path.exists(rp) else {}
    old.update(report); json.dump(old, open(rp, 'w'), indent=1)
