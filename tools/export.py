import pickle, glob, os, json, numpy as np, trimesh, fast_simplification as fs
os.makedirs('glb',exist_ok=True)
tot=0
for f in sorted(glob.glob('cache/cache_*.pkl')):
    pid=f.split('cache_')[1][:-4]
    d=pickle.load(open(f,'rb'))
    V,F=d['V'],d['F']; n=len(F)
    if pid.startswith('269'): tgt=8000
    else: tgt=max(1200, min(n, int(2500+ n*0.3)))
    if n>tgt:
        V2,F2=fs.simplify(V.astype(np.float32),F.astype(np.int32),target_reduction=1-tgt/n)
    else: V2,F2=V,F
    m=trimesh.Trimesh(V2,F2,process=False)
    m.export(f'glb/{pid}.glb')
    tot+=len(F2)
    print(pid,n,'->',len(F2))
print('total',tot)
