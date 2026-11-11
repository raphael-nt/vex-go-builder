import sys, json, os, glob, numpy as np, trimesh
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED, TopAbs_SOLID
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def load(p):
    r=STEPControl_Reader(); r.ReadFile(p); r.TransferRoots(); return r.OneShape()

def process(p, out, lin=0.08, ang=0.35):
    s=load(p)
    BRepMesh_IncrementalMesh(s, lin, False, ang, True)
    V=[];F=[];cyl=[];off=0
    ex=TopExp_Explorer(s,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face(ex.Current()); loc=TopLoc_Location()
        tri=BRep_Tool.Triangulation_s(f,loc)
        if tri is not None:
            tr=loc.Transformation()
            n=tri.NbNodes()
            pts=[tri.Node(i).Transformed(tr) for i in range(1,n+1)]
            V+= [(p_.X(),p_.Y(),p_.Z()) for p_ in pts]
            rev = f.Orientation()==TopAbs_REVERSED
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get()
                if rev: b,c=c,b
                F.append((a-1+off,b-1+off,c-1+off))
            off+=n
        ad=BRepAdaptor_Surface(f)
        if ad.GetType()==GeomAbs_Cylinder:
            c=ad.Cylinder(); ax=c.Axis(); l=ax.Location(); d=ax.Direction()
            # face extent along axis
            bb=Bnd_Box(); BRepBndLib.Add_s(f,bb); 
            g=GProp_GProps(); BRepGProp.SurfaceProperties_s(f,g); cm=g.CentreOfMass()
            cyl.append(dict(r=round(c.Radius(),3),p=[l.X(),l.Y(),l.Z()],d=[d.X(),d.Y(),d.Z()],cm=[cm.X(),cm.Y(),cm.Z()],area=g.Mass(),inner=None,rev=f.Orientation()==TopAbs_REVERSED,bb=[bb.CornerMin().X(),bb.CornerMin().Y(),bb.CornerMin().Z(),bb.CornerMax().X(),bb.CornerMax().Y(),bb.CornerMax().Z()]))
        ex.Next()
    m=trimesh.Trimesh(np.array(V),np.array(F),process=True)
    m.merge_vertices()
    return s,m,cyl

if __name__=='__main__':
    p=sys.argv[1]
    s,m,cyl=process(p,None)
    print(os.path.basename(p), 'tris',len(m.faces),'bounds',np.round(m.bounds,2).tolist())
    from collections import Counter
    print(Counter([c['r'] for c in cyl]).most_common(12))
