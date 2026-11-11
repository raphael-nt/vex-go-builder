import sys, os, glob, json, numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_IN, TopAbs_OUT, TopAbs_ON
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

def load(p):
    r=STEPControl_Reader(); r.ReadFile(p); r.TransferRoots(); return r.OneShape()

def groups(p, rmin=2.95, rmax=3.3):
    s=load(p)
    bb=Bnd_Box(); BRepBndLib.Add_s(s,bb)
    lo=np.array([bb.CornerMin().X(),bb.CornerMin().Y(),bb.CornerMin().Z()]); hi=np.array([bb.CornerMax().X(),bb.CornerMax().Y(),bb.CornerMax().Z()])
    G=[]
    ex=TopExp_Explorer(s,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face(ex.Current()); ad=BRepAdaptor_Surface(f)
        if ad.GetType()==GeomAbs_Cylinder:
            c=ad.Cylinder(); r=c.Radius()
            if rmin<=r<=rmax:
                ax=c.Axis(); l=ax.Location(); d=np.array([ax.Direction().X(),ax.Direction().Y(),ax.Direction().Z()])
                # canonical dir
                k=np.argmax(abs(d)); 
                if d[k]<0: d=-d; sgn=-1
                else: sgn=1
                L=np.array([l.X(),l.Y(),l.Z()])
                v1,v2=ad.FirstVParameter(),ad.LastVParameter()
                t=sorted([np.dot(L,d)+sgn*v1, np.dot(L,d)+sgn*v2])
                p0=L-np.dot(L,d)*d  # point on line closest to origin
                ang=ad.LastUParameter()-ad.FirstUParameter()
                for g in G:
                    if np.allclose(g['d'],d,atol=1e-3) and np.linalg.norm(g['p0']-p0)<0.05:
                        g['t'][0]=min(g['t'][0],t[0]); g['t'][1]=max(g['t'][1],t[1]); g['ang']+=ang; g['r'].append(r); break
                else:
                    G.append(dict(d=d,p0=p0,t=t,ang=ang,r=[r]))
        ex.Next()
    cls=BRepClass3d_SolidClassifier(s)
    out=[]
    for g in G:
        tm=(g['t'][0]+g['t'][1])/2; c=g['p0']+tm*g['d']
        cls.Perform(gp_Pnt(*c),1e-4); st=cls.State()
        g['state']={TopAbs_IN:'IN',TopAbs_OUT:'OUT',TopAbs_ON:'ON'}.get(st,str(st))
        out.append(g)
    return s,out,lo,hi

if __name__=='__main__':
    for pid in sys.argv[1:]:
        p=glob.glob(f'/mnt/user-data/uploads/GO kit 2021-05-17/**/{pid}*.STEP',recursive=True)[0]
        s,G,lo,hi=groups(p)
        print(pid,'bbox',lo.round(2),hi.round(2),len(G))
        for g in G: print('  ',g['state'],g['d'].round(2),(g['p0']).round(2),np.round(g['t'],2),round(g['ang'],2),sorted(set(np.round(g['r'],3))))
