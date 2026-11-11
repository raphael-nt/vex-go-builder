import json
conn=json.load(open('conn.json'))
meta=json.load(open('cache/meta.json'))
C={'red':'#d9372f','green':'#7cc63a','yellow':'#f4c21b','blue':'#2c6fd6','orange':'#f2801f','pink':'#ea5ca0','dgray':'#4b5157','white':'#eef0f2','black':'#2a2c30','gray':'#a3a9b0','steel':'#bfc4ca','elec':'#c3c6ca'}
# shape id, name, category, [(color, qty)]
P=[
('001','Beam 1x2','beam',[('red',5)]),('002','Beam 1x3','beam',[('green',9)]),('003','Beam 1x4','beam',[('yellow',5)]),
('004','Beam 1x5','beam',[('blue',2)]),('005','Beam 1x6','beam',[('orange',6)]),('006','Beam 1x7','beam',[('pink',2)]),
('007','Beam 1x8','beam',[('dgray',2)]),('009','Beam 1x10','beam',[('white',2)]),('011','Beam 1x12','beam',[('black',2)]),('013','Beam 1x14','beam',[('gray',2)]),
('018','Large Beam 2x3','beam',[('green',4)]),('019','Large Beam 2x4','beam',[('yellow',3)]),('020','Large Beam 2x5','beam',[('blue',2)]),
('021','Large Beam 2x6','beam',[('orange',3)]),('023','Large Beam 2x8','beam',[('dgray',2)]),('025','Large Beam 2x10','beam',[('white',3)]),
('026','Large Beam 2x12','beam',[('black',3)]),('027','Large Beam 2x14','beam',[('gray',2)]),
('1140','Square Beam 2x2','beam',[('red',6)]),('1548','Thin Beam','beam',[('blue',2)]),('157','Slotted Beam','beam',[('pink',4)]),
('145','Angle Beam 90','beam',[('green',3)]),('148','Angle Beam 45','beam',[('yellow',4)]),('150','Angle Beam L','beam',[('orange',2)]),('1199','Angle Beam 60','beam',[('red',2)]),
('031','Plate 3x3','plate',[('white',2)]),('032','Plate 3x4','plate',[('black',2)]),('035','Plate 3x8','plate',[('gray',2)]),
('042','Plate 4x6','plate',[('white',2)]),('043','Plate 4x8','plate',[('dgray',3)]),
('2260','Red Pin','pin',[('red',53)]),('2261','Green Pin','pin',[('green',7)]),('2258','Pink Pin','pin',[('pink',5)]),('328','Gray Pin','pin',[('gray',2)]),
('2268','Standoff 1','pin',[('yellow',7)]),('2269','Standoff 2','pin',[('blue',8)]),('2271','Standoff 4','pin',[('orange',5)]),
('2288','Connector 1','pin',[('red',9)]),('2295','Connector 2','pin',[('yellow',8)]),('2296','Connector 3','pin',[('blue',5)]),
('2308','Connector 4','pin',[('green',4)]),('277','Connector 5','pin',[('orange',3)]),
('154','Spacer','pin',[('dgray',8)]),
('2234','Red Shaft','motion',[('red',4)]),('2238','Green Shaft','motion',[('green',4)]),('2221','Capped Shaft','motion',[('steel',2)]),('124','Plain Shaft','motion',[('steel',2)]),
('143','Shaft Collar','motion',[('steel',6)]),
('2180','Gear 8T','motion',[('red',6)]),('2181','Gear 16T','motion',[('green',3)]),('2182','Gear 24T','motion',[('blue',5)]),('2191','Gear 24T Pink','motion',[('pink',2)]),
('164','Pulley Small','motion',[('green',3)]),('165','Pulley Large','motion',[('orange',2)]),
('1383','Wheel + Tire','motion',[('black',2)]),('1384','Blue Wheel','motion',[('blue',2)]),('207','Tire Small','motion',[('black',2)]),
('2250','Disk','other',[('red',1),('green',1)]),('3196-2250','Disk Blue','other',[('blue',1)]),
('473','Knob','other',[('orange',2)]),('1456','Slide Beam','other',[('gray',2)]),('1469','Slide Block','other',[('gray',2)]),
('3167-010','North Magnet','other',[('red',1)]),('3167-020','South Magnet','other',[('black',1)]),
('430','Short Rope','other',[('black',2)]),('438','Long Rope','other',[('white',2)]),('468','Rubber Band','other',[('orange',2)]),
('269-6685','Brain','elec',[('elec',1)]),('269-6686','Battery','elec',[('elec',1)]),('269-6687','Switch','elec',[('elec',1)]),
('269-6690','Motor','elec',[('elec',3)]),('269-6695','Eye Sensor','elec',[('elec',1)]),('269-6696','LED Bumper','elec',[('elec',1)]),('269-6702','Electromagnet','elec',[('elec',1)]),
]
def file_of(s):
    if s.startswith('269'): return s+'-000'
    if '-' in s: return '228-'+s
    return '228-2500-'+s
def mz(z,d): return dict(p=[0,0,z],n=[0,0,d],k='MP')
def shaft(top,bottom):
    out=[];z=top
    while z>bottom+2:
        out+= [dict(p=[0,0,round(z,2)],n=[0,0,1],k='MS'),dict(p=[0,0,round(z,2)],n=[0,0,-1],k='MS')]; z-=6.35
    return out
manual={
 '2260':[mz(0,1),mz(0,-1)], '2258':[mz(0,1),mz(0,-1)],
 '2261':[mz(0,1),mz(0,-1),mz(-6.35,-1)],
 '2268':[mz(0,1),mz(-6.35,-1)], '2269':[mz(0,1),mz(-12.7,-1)], '2271':[mz(0,1),mz(-25.4,-1)],
 '2234':shaft(0,-27.69),'2238':shaft(0,-53.09),'2221':shaft(0,-34.04),'328':shaft(0,-15.73),'124':shaft(46.8,-49.91),
}
parts=[]
for s,name,cat,cols in P:
    f=file_of(s); m=meta[f]
    c=manual.get(s, conn.get(f,{}).get('c',[]))
    parts.append(dict(id=s,file=f,name=name,cat=cat,colors=[dict(c=k,hex=C[k],qty=q) for k,q in cols],conn=c,bounds=m['bounds']))
json.dump(dict(colors=C,parts=parts),open('site/parts.json','w'),separators=(',',':'))
print(len(parts), sum(len(p['conn']) for p in parts), [p['id'] for p in parts if not p['conn']])
