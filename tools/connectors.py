import sys, os, glob, json, time, numpy as np
sys.path.insert(0,'tools'); import holes
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN, TopAbs_ON
from OCP.gp import gp_Pnt
SRC='/mnt/user-data/uploads/GO kit 2021-05-17'

def perp(d):
    a=np.array([1,0,0]) if abs(d[0])<0.9 else np.array([0,1,0])
    u=np.cross(d,a); u/=np.linalg.norm(u); v=np.cross(d,u); return u,v

def faces_of_hole(cls,c,d,r):
    u,v=perp(d); R=r+2.4
    ring=[c+R*(np.cos(a)*u+np.sin(a)*v) for a in np.linspace(0,2*np.pi,8,endpoint=False)]
    def inside(p):
        cls.Perform(gp_Pnt(*p),1e-3); return cls.State() in (TopAbs_IN,TopAbs_ON)
    res=[]
    for sgn in (1,-1):
        t=0; last=None
        # must start inside
        while t<60:
            n_in=sum(inside(q+sgn*t*d) for q in ring)
            if n_in<2: break
            last=t; t+=0.5
        if last is None: res.append(None); continue
        # refine
        lo,hi=last,t
        for _ in range(6):
            m=(lo+hi)/2
            if sum(inside(q+sgn*m*d) for q in ring)>=2: lo=m
            else: hi=m
        res.append(sgn*(lo+hi)/2)
    return res

def r3(a): return [round(float(x),2) for x in a]

def part_connectors(pid,path):
    s,G,lo,hi=holes.groups(path,2.3,3.3)
    cls=BRepClass3d_SolidClassifier(s)
    C=[]
    for g in G:
        r=float(np.mean(g['r'])); d=g['d']
        kind='P' if r>=2.9 else 'S'
        if g['state']=='OUT':
            tm=(g['t'][0]+g['t'][1])/2; c=g['p0']+tm*d
            a,b=faces_of_hole(cls,c,d,r)
            if a is None: a=0
            if b is None: b=0
            hw=3.05 if kind=='P' else 3.05
            a=max(a,hw); b=min(b,-hw)
            C.append(dict(p=r3(c+a*d),n=r3(d),k='F'+kind))
            C.append(dict(p=r3(c+b*d),n=r3(-d),k='F'+kind))
        elif g['state']=='IN' and kind=='P' and g['t'][1]-g['t'][0]<1.5 and abs(g['t'][0])<0.05:
            C.append(dict(p=r3(g['p0']+g['t'][0]*d),n=r3(d),k='MP'))
    return C,lo,hi

if __name__=='__main__':
    ids=sys.argv[1:]
    os.makedirs('conn',exist_ok=True)
    for pid in ids:
        g=glob.glob(f'{SRC}/**/{pid}[ .]*STEP',recursive=True) or glob.glob(f'{SRC}/**/{pid}*STEP',recursive=True)
        if not g: print(pid,'MISSING'); continue
        t=time.time(); C,lo,hi=part_connectors(pid,g[0])
        json.dump(dict(c=C,lo=r3(lo),hi=r3(hi)),open(f'conn/{pid}.json','w'))
        print(pid,len(C),round(time.time()-t,1),flush=True)
