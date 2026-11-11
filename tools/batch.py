import sys, os, glob, json, numpy as np, trimesh, pickle
sys.path.insert(0,'tools'); from conv import process
import fast_simplification as fs
src="/mnt/user-data/uploads/GO kit 2021-05-17"
files=sorted(glob.glob(src+'/*.STEP')+glob.glob(src+'/Electronics/*.STEP'))
meta={}
for p in files:
    pid=os.path.basename(p).split(' ')[0].replace('.STEP','')
    try:
        s,m,cyl=process(p,None,lin=0.06,ang=0.3)
    except Exception as e:
        print(pid,'ERR',e); continue
    n=len(m.faces)
    pickle.dump(dict(V=m.vertices,F=m.faces,cyl=cyl),open(f'cache_{pid}.pkl','wb'))
    ext=(m.bounds[1]-m.bounds[0]).round(1).tolist()
    meta[pid]=dict(tris=n,ext=ext,bounds=m.bounds.round(2).tolist(),ncyl=len(cyl))
    print(pid,n,ext,len(cyl),flush=True)
json.dump(meta,open('meta.json','w'),indent=1)
