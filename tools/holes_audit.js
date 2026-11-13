const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const pg=await b.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
await pg.route('https://cdn.jsdelivr.net/npm/three-mesh-bvh@0.7.8/**',r=>{const u=r.request().url().replace('https://cdn.jsdelivr.net/npm/three-mesh-bvh@0.7.8/','');r.fulfill({path:'node_modules/three-mesh-bvh/'+u,contentType:'application/javascript'});});
await pg.route('https://cdn.jsdelivr.net/npm/three@0.169.0/**',r=>{const u=r.request().url().replace('https://cdn.jsdelivr.net/npm/three@0.169.0/','');r.fulfill({path:'node_modules/three/'+u,contentType:'application/javascript'});});
await pg.goto('http://localhost:8765/site/index.html'); await pg.waitForFunction('document.getElementById("loading").hidden',null,{timeout:60000});
const res=await pg.evaluate(async()=>{ const T=__vx.THREE, P=__vx.PART(), out=[];
  for(const sid of Object.keys(P)){ const g=await __vx.ensureGeo(sid); const ms=g.prims.map(pr=>new T.Mesh(pr.g,new T.MeshBasicMaterial({side:T.DoubleSide})));
    const rc=new T.Raycaster(); const bad=[]; let nF=0;
    P[sid].conn.forEach((c,ci)=>{ if(c.k[0]!=='F') return; nF++; const p=new T.Vector3(...c.p), n=new T.Vector3(...c.n).normalize();
      rc.set(p.clone().addScaledVector(n,1.0),n.clone().negate()); rc.far=3.5; const h=rc.intersectObjects(ms,false);
      if(h.length&&h[0].distance<1.5) bad.push([ci,c.k,c.p.map(x=>+x.toFixed(1)),c.n.map(x=>Math.round(x)),+h[0].distance.toFixed(1)]); });
    if(bad.length) out.push([sid,P[sid].name,bad.length+'/'+nF,bad]); }
  return out; });
const A={}; for(const r of res){ A[r[0]]=r[3].map(x=>x[2]); console.log(r[0],r[1],r[2]); } require('fs').writeFileSync(process.argv[2]||'/tmp/solid.json',JSON.stringify(A));
console.log('errs',errs); await b.close();})();
