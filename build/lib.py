import json, numpy as np
CAT=json.load(open('/home/claude/vexgo/site/parts.json'))
P={p['id']:p for p in CAT['parts']}
AX={'+X':(1,0,0),'-X':(-1,0,0),'+Y':(0,1,0),'-Y':(0,-1,0),'+Z':(0,0,1),'-Z':(0,0,-1)}
def frame(x=None,y=None,z=None):
    """rotation from local axes to world axes given as '+X' etc (two of three)"""
    c={}
    if x: c['x']=np.array(AX[x],float)
    if y: c['y']=np.array(AX[y],float)
    if z: c['z']=np.array(AX[z],float)
    if 'x' not in c: c['x']=np.cross(c['y'],c['z'])
    if 'y' not in c: c['y']=np.cross(c['z'],c['x'])
    if 'z' not in c: c['z']=np.cross(c['x'],c['y'])
    R=np.column_stack([c['x'],c['y'],c['z']])
    assert abs(np.linalg.det(R)-1)<1e-6, ('left-handed',x,y,z)
    assert np.allclose(np.cross(c['x'],c['y']),c['z'])
    return R
def quat(R):
    m=R; t=np.trace(m)
    if t>0:
        s=np.sqrt(t+1)*2; w=.25*s; x=(m[2,1]-m[1,2])/s; y=(m[0,2]-m[2,0])/s; z=(m[1,0]-m[0,1])/s
    elif m[0,0]>m[1,1] and m[0,0]>m[2,2]:
        s=np.sqrt(1+m[0,0]-m[1,1]-m[2,2])*2; w=(m[2,1]-m[1,2])/s; x=.25*s; y=(m[0,1]+m[1,0])/s; z=(m[0,2]+m[2,0])/s
    elif m[1,1]>m[2,2]:
        s=np.sqrt(1+m[1,1]-m[0,0]-m[2,2])*2; w=(m[0,2]-m[2,0])/s; x=(m[0,1]+m[1,0])/s; y=.25*s; z=(m[1,2]+m[2,1])/s
    else:
        s=np.sqrt(1+m[2,2]-m[0,0]-m[1,1])*2; w=(m[1,0]-m[0,1])/s; x=(m[0,2]+m[2,0])/s; y=(m[1,2]+m[2,1])/s; z=.25*s
    return [round(float(v),6) for v in (x,y,z,w)]
class Model:
    def __init__(s,name): s.name=name; s.parts=[]; s.step=1
    def add(s,sid,col,R,local,world,dir='+Z',note=''):
        """place part so that local point maps to world point"""
        t=np.array(world,float)-R@np.array(local,float)
        s.parts.append(dict(sid=sid,col=col,R=R,t=t,step=s.step,dir=AX[dir] if isinstance(dir,str) else dir,note=note))
        return len(s.parts)-1
    def w(s,i,local):
        p=s.parts[i]; return p['R']@np.array(local,float)+p['t']
    def next(s): s.step+=1
    def mirror_copy(s,idxs,plane='X'):
        pass
    def dump(s,path,shift=None):
        pts=np.array([p['t'] for p in s.parts])
        out=[]
        for p in s.parts:
            t=p['t']+(np.array(shift) if shift is not None else 0)
            out.append(dict(sid=p['sid'],col=p['col'],p=[round(float(v),3) for v in t],q=quat(p['R']),dir=[float(v) for v in p['dir']],step=p['step']))
        json.dump(dict(name=s.name,step=s.step,parts=out),open(path,'w'),ensure_ascii=False)
