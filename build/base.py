import sys; sys.path.insert(0,'.')
from lib import *
M=np.diag([-1.,1,1])
def mirror(m,i,axis,off=0.0,step=None):
    """mirror part i through world plane X=0; local reflection on `axis` about `off` keeps it proper"""
    p=m.parts[i]; F=np.eye(3); f0=np.zeros(3); k='xyz'.index(axis); F[k,k]=-1; f0[k]=2*off
    R=M@p['R']@F; t=M@(p['R']@f0+p['t'])
    m.parts.append(dict(sid=p['sid'],col=p['col'],R=R,t=t,step=m.step if step is None else step,dir=list(M@np.array(p['dir'])),note=''))
    return len(m.parts)-1
SYM={'043':'z','145':'z','2260':'x','2261':'x','2295':('x',-6.35),'269-6690':'z','2234':'x','1383':'x','1384':'x','143':'x'}
def mir(m,i):
    s=SYM[m.parts[i]['sid']]; ax,off=(s if isinstance(s,tuple) else (s,0.0)); return mirror(m,i,ax,off)

m=Model('Competition Base')
XA=-50.8
def hole(c,r): return (-44.45+(c-1)*12.7, -19.05+(r-1)*12.7)
RP=frame(z='+X',x='+Y')
side=[]   # indices of left-side parts per step for mirroring
def S(i): side.append((m.step,i)); return i
# 1
S(m.add('043','dgray',frame(x='+Y',y='+Z',z='+X'),(0,0,0),(XA-3.05,0,0),dir='+X'))
S(m.add('145','green',frame(x='+Z',y='+Y'),(0,0,3.05),(XA,-6.35,-19.05),dir='+X'))
for (Y,Z) in [hole(2,1),hole(4,2)]: S(m.add('2260','red',RP,(0,0,0),(XA,Y,Z),dir='+X'))
m.next()
# 2-3 connector with green pins on top of the angle beam
C1=S(m.add('2295','yellow',frame(y='+Z',z='-X'),(0,0,0),(XA,-19.05,6.35),dir='+X'))
for lx in (0,-12.7):
    top=m.w(C1,(lx,-0.12,-19.05))
    S(m.add('2261','green',frame(z='+Z',x='+X'),(0,0,0),top,dir='-Z'))
m.next(); m.next()
# 4 end connectors
S(m.add('2295','yellow',frame(x='+Z',y='+Y'),(0,0,0),(XA,-44.45,6.35),dir='+X'))
S(m.add('2295','yellow',frame(y='-Y',z='-X'),(0,0,0),(XA,44.45,-6.35),dir='+X'))
m.next()
# 5 motor with 4 red pins (motor shaft face toward plate)
RM=frame(y='-X',x='-Z')        # cable (local -x) up, shaft face (local +y) toward left plate
Ys,Zs=25.4,-12.7
MA=S(m.add('269-6690','elec',RM,(0,31.63,0),(XA,Ys,Zs),dir='-X'))
for lp in [(6.35,31.63,6.35),(6.35,31.63,-6.35),(-19.05,31.63,6.35),(-19.05,31.63,-6.35)]:
    S(m.add('2260','red',RP,(0,0,0),m.w(MA,lp),dir='-X'))
m.next()
# 6 red shaft into motor
S(m.add('2234','red',frame(z='+X',x='+Y'),(0,0,0),(XA,Ys,Zs),dir='-X'))
m.next(); m.next()   # 7 attach motor sub-assembly to plate
# 8-14 mirror of 1-7 on the right plate
for st in range(1,8):
    for (s0,i) in side:
        if s0==st: mir(m,i)
    m.next()
# 15 two red pins on the back of motor A
for lp in [(-6.35,-18.98,6.35),(-6.35,-18.98,-6.35)]:
    m.add('2260','red',frame(z='+X',x='+Y'),(0,0,0),m.w(MA,lp),dir='+X')
m.next(); m.next()   # 16 join halves
# 17 front gray plate (motor side) on the end connectors, 4 red pins
YF=50.68
for (X,Z) in [(-31.75,6.35),(-44.45,-6.35),(31.75,6.35),(44.45,-6.35)]:
    m.add('2260','red',frame(z='+Y',x='+X'),(0,0,0),(X,YF,Z),dir='+Y')
m.add('035','gray',frame(y='+Z',z='+Y'),(0,0,-3.05),(0,YF,-6.35),dir='+Y')
m.next()
# 18 brain on the green pins
m.add('269-6685','elec',frame(y='+Z',z='+Y'),(0,-12.57,0),(0,-25.4,6.23),dir='-Z')
m.next()
# 19 battery under the green pins
m.add('269-6686','elec',frame(y='-Z',z='+X'),(0,0,0),(0,-12.7,0.12),dir='+Z')
m.next(); m.next(); m.next()   # 20-21 cables
# 22 back gray plate on the other end connectors
YB=-50.68
for (X,Z) in [(-31.75,6.35),(-44.45,-6.35),(31.75,6.35),(44.45,-6.35)]:
    m.add('2260','red',frame(z='-Y',x='+X'),(0,0,0),(X,YB,Z),dir='-Y')
m.add('035','gray',frame(x='+X',y='+Z',z='-Y'),(0,0,-3.05),(0,YB,-6.35),dir='-Y')
m.next(); m.next()   # 23 name plate (no CAD part)
# 24-27 wheels
XO=-56.9
def wheels(sign):
    X=sign*XO
    m.add('1383','black',frame(z='-X' if sign>0 else '+X',x='+Y'),(0,0,-3.18),(X,25.4,-12.7),dir=('-X' if sign>0 else '+X'))
    m.add('143','steel',frame(y='-X' if sign>0 else '+X',x='+Y'),(0,3.18,0),(X+sign*(-19.0),25.4,-12.7),dir=('-X' if sign>0 else '+X'))
    m.next()
    m.add('2260','red',frame(z='+X',x='+Y'),(0,0,0),(sign*(XA-6.1),-25.4,-12.7),dir=('-X' if sign>0 else '+X'))
    m.add('1384','blue',frame(z='-X' if sign>0 else '+X',x='+Y'),(0,0,-3.05),(X,-25.4,-12.7),dir=('-X' if sign>0 else '+X'))
    m.next()
wheels(1); wheels(-1)
# 28 eye sensor on the front plate with 2 red pins
YFo=YF+6.1
for (X,Z) in [(-6.35,6.35),(6.35,-6.35)]:
    m.add('2260','red',frame(z='+Y',x='+X'),(0,0,0),(X,YFo,Z),dir='+Y')
m.add('269-6695','elec',frame(y='+Y',x='-X'),(0,0,0),(0,YFo,0),dir='+Y')
m.next()
m.dump('/home/claude/vexgo/build/base.json',shift=(0,0,37.95))
from collections import Counter
print(len(m.parts),'parts; last step',m.step-1)
print(Counter(p['sid'] for p in m.parts))
