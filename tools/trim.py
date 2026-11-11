import pickle, numpy as np, trimesh, fast_simplification as fs, base64, json, subprocess, os
cuts={'269-6690-000':(0,-50,None),'269-6695-000':(2,None,26),'269-6686-000':(2,None,40),'269-6696-000':(0,-26,None),'269-6702-000':(0,-26,None)}
for pid,(ax,lo,hi) in cuts.items():
    d=pickle.load(open(f'cache/cache_{pid}.pkl','rb')); V,F=d['V'],d['F']
    c=V[F].mean(axis=1)[:,ax]
    keep=np.ones(len(F),bool)
    if lo is not None: keep&=c>=lo
    if hi is not None: keep&=c<=hi
    F2=F[keep]; m=trimesh.Trimesh(V,F2,process=False); m.remove_unreferenced_vertices()
    n=len(m.faces); tgt=9000
    if n>tgt:
        v2,f2=fs.simplify(m.vertices.astype(np.float32),m.faces.astype(np.int32),target_reduction=1-tgt/n); m=trimesh.Trimesh(v2,f2,process=False)
    print(pid,len(F),'->',len(m.faces),np.round(m.bounds,1).tolist())
    m.export(f'glb/{pid}.glb')
    subprocess.run(['npx','gltfpack','-i',f'glb/{pid}.glb','-o',f'dev/tmp.glb','-cc','-noq'],check=True,capture_output=True)
    json.dump({'glb':base64.b64encode(open('dev/tmp.glb','rb').read()).decode()},open(f'site/m/{pid}.json','w'))
