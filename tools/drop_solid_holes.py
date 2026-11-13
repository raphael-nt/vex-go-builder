"""Remove female connectors that sit on solid faces (no real hole there).

The list comes from tools/holes_audit.js: a ray from 1 mm outside each hole, pointing in,
hits material within 1.5 mm. Those faces have no hole, so nothing should plug in there.
Usage: python3 tools/drop_solid_holes.py site/parts.json solid.json   (solid.json from tools/holes_audit.js)
Run after tools/fixconn.py. Safe to run twice.
"""
import json, sys
SOLID = {   # part id -> connector positions (rounded to 0.1 mm) to drop
    '269-6695': [(-6.3,18.8,-6.3),(6.3,18.8,-6.3),(6.3,18.8,6.3),(-6.3,18.8,6.3)],   # Eye Sensor: sensor face has no holes
}
KEEP = {    # real holes the ray test misreads (a raised ring inside): the Competition Base instructions put red pins here
    '269-6690': [(-6.3,-19,-6.3),(-6.3,-19,6.3)],
}
path = sys.argv[1] if len(sys.argv) > 1 else 'site/parts.json'
audit = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
d = json.load(open(path))
r = lambda p: tuple(round(x, 1) for x in p)
total = 0
for p in d['parts']:
    drop = (set(map(tuple, audit.get(p['id'], []))) | set(SOLID.get(p['id']) or [])) - set(KEEP.get(p['id'], []))
    if not drop: continue
    keep = [c for c in p['conn'] if not (c['k'][0] == 'F' and r(c['p']) in drop)]
    total += len(p['conn']) - len(keep); print(p['id'], p['name'], len(p['conn']), '->', len(keep))
    p['conn'] = keep
json.dump(d, open(path, 'w'), separators=(',', ':'))
print('dropped', total)
