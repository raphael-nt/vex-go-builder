"""Manual connector fixes for parts where automatic hole detection failed or was wrong.
Checked against the STEP geometry with line probes (see the audit notes in README)."""
import json
p='site/parts.json'; cat=json.load(open(p)); P={x['id']:x for x in cat['parts']}
def fp(x,y,z,n,k='FP'): return {'k':k,'p':[x,y,z],'n':n}
# Switch: its holes take pins like every other GO housing, they were tagged as shaft holes
for c in P['269-6687']['conn']: c['k']='FP'
# LED Bumper and Electromagnet: 4 pin holes on the mounting face, same pattern as the Eye Sensor
P['269-6696']['conn']=[fp(x,-6.1,z,[0,-1,0]) for x in (-6.35,6.35) for z in (-6.35,6.35)]
P['269-6702']['conn']=[fp(x,-3.05,z,[0,-1,0]) for x in (-6.35,6.35) for z in (-6.35,6.35)]
# South Magnet has the same body as the North Magnet
P['3167-020']['conn']=json.loads(json.dumps(P['3167-010']['conn']))
# Slide Beam: 5 pin holes through the web
P['1456']['conn']=[fp(x,s*2.29,0,[0,s,0]) for x in (-25.4,-12.7,0,12.7,25.4) for s in (1,-1)]
# Green Connector 4: the 4 points on the top and bottom are molded pegs, not holes
for c in P['2308']['conn']:
    if abs(c['n'][2])>0.9: c['k']='MP'
# Tire Small goes around the Pulley Small rim: special pair MT (pulley) and FT (tire), centered on the axis
P['207']['conn']=[fp(0,0,3.17,[0,0,-1],'FT'),fp(0,0,-3.17,[0,0,1],'FT')]   # point on one face, normal pointing back in: snaps coaxial
P['164']['conn']=[c for c in P['164']['conn'] if c['k']!='MT']+[fp(0,0,3.17,[0,0,1],'MT'),fp(0,0,-3.17,[0,0,-1],'MT')]
json.dump(cat,open(p,'w'),ensure_ascii=False,separators=(',',':'))
for sid in ['269-6687','269-6696','269-6702','3167-020','1456','2308','207','164']:
    from collections import Counter; print(sid,P[sid]['name'],dict(Counter(c['k'] for c in P[sid]['conn'])))
# Red and Green Shaft: the stop ring sits at the top station, so that station only works from one side
cat=json.load(open(p)); P={x['id']:x for x in cat['parts']}
for sid in ('2234','2238'):
    P[sid]['conn']=[c for c in P[sid]['conn'] if not (abs(c['p'][2])<0.01 and c['n'][2]<-0.9)]
json.dump(cat,open(p,'w'),ensure_ascii=False,separators=(',',':'))
print('shafts',[len(P[s]['conn']) for s in ('2234','2238')])
