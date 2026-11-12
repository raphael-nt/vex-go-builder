"""Write CAD bounds and kit colors into site/parts.json.

Kit colors use the VEX GO Pantone values found in the STEP files.
Per color variant, `ov` maps a GLB material name to the hex that replaces it.
Rule: if the kit color already exists in the CAD part, keep CAD colors as they are.
Otherwise the "main" material (largest area) takes the kit color.
"""
import json
PAL = {'red':'#d22630','green':'#97d700','yellow':'#ffcd00','blue':'#004c97','orange':'#ff671f','pink':'#e10098',
       'dgray':'#54585a','white':'#d9d9d6','black':'#25282a','gray':'#b2b4b2','steel':'#d3d6d3'}
KEEP_CAD = {'228-3167-010','228-3167-020','228-2500-1469','228-3196-2250'}          # magnets and slide block: CAD colors are the real ones
RENAME = {('228-2500-143','steel'):'black',('228-3167-010','red'):'dgray',('228-3167-020','black'):'dgray'}                            # rubber shaft collar is black
SPECIAL = {'228-2500-2234':{'red':{'cad_d22630':PAL['red']}},          # shafts: metal body, kit color is the stop ring
           '228-2500-2238':{'green':{'cad_d22630':PAL['green']}}}
B = json.load(open('glb2/bounds.json'))
cat = json.load(open('site/parts.json'))
for P in cat['parts']:
    f = P['file']; info = B[f]; mats = info['mats']
    P['bounds'] = [[round(v, 2) for v in info['b'][0]], [round(v, 2) for v in info['b'][1]]]
    main = next(m for m in mats if m.startswith('main_')); mainhex = '#' + main[5:]
    cadhex = {'#' + m.split('_', 1)[1] for m in mats}
    P['mats'] = mats
    for c in P['colors']:
        c['c'] = RENAME.get((f, c['c']), c['c'])
        if P['cat'] == 'elec' or f in KEEP_CAD:
            c['hex'] = mainhex; c['ov'] = {}; continue
        kh = PAL[c['c']]; c['hex'] = kh
        if f in SPECIAL: c['ov'] = SPECIAL[f][c['c']]
        elif kh in cadhex: c['ov'] = {}
        else: c['ov'] = {main: kh}
    print(f.ljust(14), P['name'].ljust(16), [(c['c'], c['hex'], c['ov']) for c in P['colors']])
cat['colors'] = PAL
json.dump(cat, open('site/parts.json', 'w'), ensure_ascii=False, separators=(',', ':'))
