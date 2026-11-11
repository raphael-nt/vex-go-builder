import sys, json, math; sys.path.insert(0,'.')
from lib import *
import base as B      # reuses Competition Base geometry (pre-shift coords)
from base import mirror, M
m=Model('Competition Advanced')
# step 1: the whole Competition Base
for p in B.m.parts:
    q=dict(p); q['step']=1; m.parts.append(q)
SYM={'023':'z','019':'z','026':'z','003':'z','2288':'x','2308':('x',-6.35),'2260':'x','2269':'x','2271':'x','2268':'x','2258':'x','2261':'x','143':'x','277':('x',-6.35),'1548':'y','011':'z','013':'z','006':'z','2180':'x','2182':'x'}
def mir(i,step=None):
    s=SYM[m.parts[i]['sid']]; ax,off=(s if isinstance(s,tuple) else (s,0.0))
    return mirror(m,i,ax,off,step)
def at(st): m.step=st
RP_X=frame(z='+X',x='+Y')            # red pin along X
# ---- step 1: green connectors on the brain ears (pegs down into the ear holes)
at(1)
for X in (-31.75,31.75):
    m.add('2308','green',frame(z='-Z',x='+Y'),(0,0,0),(X,-44.45,31.4),dir='-Z')
# ---- left tower geometry
Yt=-38.1; Zb=89.0; Zd=Zb+25.4
XbL=-59.95; XdL=-41.15
Rbeam=frame(x='+Z',y='+Y')           # vertical large beams, normal +X... z = x*y
def dg(hx,hy,face):                 # world point on left dark gray face
    return (XdL+3.05*face, Yt+hy, Zd+hx)
at(2)
DG=m.add('023','dgray',Rbeam,(0,0,0),(XdL,Yt,Zd),dir='+X')
RPk=frame(z='-X',x='+Y')
for hx in (-25.4,-12.7): m.add('2258','pink',RPk,(0,0,0),dg(hx,0,-1),dir='+X')
at(3)
for (hx,hy) in [(44.45,-6.35),(6.35,6.35)]: m.add('2260','red',RP_X,(0,0,0),dg(hx,hy,+1),dir='-X')
at(4)
m.add('019','yellow',Rbeam,(0,0,3.05),(XdL+3.05,Yt,Zd+25.4),dir='-X')
at(5)
RM=frame(y='-X',x='-Z')
Sx=-38.1
MOT=m.add('269-6690','elec',RM,(0,31.63,0),dg(Sx,0,+1),dir='-X')
for lp in [(6.35,31.63,6.35),(-6.35,31.63,6.35),(-19.05,31.63,6.35)]:
    m.add('2260','red',RP_X,(0,0,0),m.w(MOT,lp),dir='-X')
at(6)
m.add('2234','red',frame(z='-X',x='+Y'),(0,0,0),dg(Sx,0,+1),dir='+X')
m.add('2260','red',RP_X,(0,0,0),m.w(MOT,(6.35,31.63,-6.35)),dir='-X')
# gears on the outer face (toward -X)
RG=frame(z='-X',x='+Y')
at(8); m.add('2180','red',RG,(0,0,-3.18),dg(-25.4,0,-1),dir='+X')
at(9); m.add('2180','red',RG,(0,0,-3.18),dg(-12.7,0,-1),dir='+X')
at(10); m.add('2180','red',RG,(0,0,-3.18),dg(Sx,0,-1),dir='+X')
at(11)
RS=frame(z='+X',x='+Y')
for (hx,hy) in [(44.45,-6.35),(-44.45,6.35),(-44.45,-6.35)]:
    m.add('2269','blue',RS,(0,0,-12.7),(XbL+3.05,Yt+hy,Zd+hx),dir='+X')
at(12)
ZA=Zd+12.7; ZG=Zd+38.1
m.add('124','steel',frame(z='+X',x='+Y'),(0,0,0),(0,Yt,ZA),dir='+X')
m.add('2182','blue',RG,(0,0,-3.18),dg(12.7,0,-1),dir='+X')
m.add('143','steel',frame(y='-X',x='+Y'),(0,3.18,0),(XdL-3.05-8.7,Yt,ZA),dir='+X')
at(14)
BL=m.add('026','black',Rbeam,(0,0,0),(XbL,Yt,Zb),dir='+X')
for (hx,hy) in [(-57.15,-6.35),(-57.15,6.35)]: m.add('2260','red',frame(z='-X',x='+Y'),(0,0,0),(XbL-3.05,Yt+hy,Zb+hx),dir='-X')
at(16)
RY=frame(x='+Y',y='+Z')
YB=m.add('003','yellow',RY,(0,0,0),(XbL-3.05-3.05,Yt-6.35,Zb-57.15),dir='-X')
for lx in (-19.05,-6.35):
    p=m.w(YB,(lx,0,-3.05))
    m.add('2288','red',frame(z='+X',x='+Y'),(0,0,0),p+np.array([-0.0,0,0]),dir='+X')
at(19)
m.add('2260','red',frame(z='+X',x='+Y'),(0,0,0),m.w(MOT,(-6.35,-18.98,6.35)),dir='+X')
# ---- black arm (steps 20-26)
alpha=math.radians(45); d=np.array([0,math.cos(alpha),-math.sin(alpha)])
L=139.7
A=np.array([0,Yt,ZA]); G=np.array([0,Yt,ZG])
def armframe(X):
    xax=-d; zax=np.array([1.,0,0]); yax=np.cross(zax,xax); return np.column_stack([xax,yax,zax])
RA=armframe(0)
def armpt(P,X,s): return P+d*s+np.array([X,0,0])   # s = distance from pivot along arm
at(20)
BA1=m.add('011','black',RA,(69.85,0,0),armpt(A,-15.75,0),dir='-X')
TB1=m.add('1548','blue',RA@np.diag([-1,1,1])@np.diag([1,1,1]) if False else RA,(0,0,0),armpt(A,-15.75+3.05+3.18,0),dir='+X')
for s in (12.7,38.1): m.add('2260','red',frame(z='+X',x='+Y'),(0,0,0),armpt(A,-12.7,s),dir='+X')
at(21)
TB2=m.add('1548','blue',RA,(0,0,0),armpt(A,12.7-3.18,0),dir='+X')
for s in (19.05,31.75): m.add('2269','blue',RS,(0,0,-12.7),armpt(A,6.35,s),dir='+X')
at(22)
for s in (12.7,38.1): m.add('2260','red',frame(z='+X',x='+Y'),(0,0,0),armpt(A,12.7,s),dir='+X')
at(23)
m.add('2271','orange',RS,(0,0,-25.4),armpt(A,12.7,101.6),dir='+X')
at(24)
BA2=m.add('011','black',RA,(69.85,0,0),armpt(A,15.75,0),dir='+X')
at(25)
for X in (-18.8,18.8): m.add('2260','red',frame(z='+X',x='+Y'),(0,0,0),armpt(A,X,L),dir='+X')
# ---- gray arm (steps 27-32)
at(27)
GA1=m.add('013','gray',RA,(69.85,0,0),armpt(G,-15.75,0),dir='-X')
for s in (25.4,76.2,127.0): m.add('2271','orange',RS,(0,0,0),armpt(G,-12.7,s),dir='+X')
at(28)
m.add('124','steel',frame(z='+X',x='+Y'),(0,0,0),(0,Yt,ZG),dir='+X')
for X in (-9.6,-3.2): m.add('143','steel',frame(y='+X',x='+Y'),(0,0,0),(X,Yt,ZG),dir='+X')
at(30)
GA2=m.add('013','gray',RA,(69.85,0,0),armpt(G,15.75,0),dir='+X')
at(31)
for X in (-18.8,18.8): m.add('2260','red',frame(z='+X',x='+Y'),(0,0,0),armpt(G,X,L),dir='+X')
# ---- right tower (steps 33-41) = mirror of left tower without motor/gears
left_tower={2:[DG],3:None,4:None,11:None,14:None,16:None}
idx_by_step={}
for i,p in enumerate(m.parts):
    idx_by_step.setdefault(p['step'],[]).append(i)
def mirror_step(src,dst,skip_sids=()):
    for i in idx_by_step.get(src,[]):
        if m.parts[i]['sid'] in skip_sids: continue
        mir(i,dst)
mirror_step(2,33,skip_sids=('2258',)); mirror_step(3,33)
mirror_step(4,34); mirror_step(11,35)
m.add('143','steel',frame(y='+X',x='+Y'),(0,0,0),(-(XdL-3.05-8.7)-6.36,Yt,ZG),dir='-X',) ; m.parts[-1]['step']=37
mirror_step(14,38); mirror_step(16,39)
# ---- forks (steps 42-46)
Ap=A+d*L; Gp=G+d*L
def fork(sign,st_build,st_attach):
    at(st_build)
    XO=sign*19.05
    Ro=frame(z='+Z',y=('+X' if sign<0 else '-X'))
    O=m.add('277','orange',Ro,(-6.35,0,6.35),(XO,Ap[1],Ap[2]),dir='-Z')
    pk=m.w(O,(0,0,0))
    Rk=frame(x='+Y',z='+Z')
    m.add('006','pink',Rk,(-38.1,0,3.05),(XO,pk[1],pk[2]),dir='+Z')
    tip=np.array([XO,pk[1]+76.2,pk[2]])
    m.add('2268','yellow',frame(z='+Z',x='+Y'),(0,0,-6.35),tip,dir='-Z')
    return O
O1=fork(-1,42,43); O2=fork(1,44,45)
at(46)
top=m.w(O1,(0,0,38.1))
m.add('1199','red',frame(x='+X',z='+Z'),(0,0,-3.05),top,dir='-Z')
# ---- steps 48-49: green pins into the side plates under the tower feet
at(48)
for sgn in (-1,1):
    m.add('2261','green',frame(z=('+X' if sgn<0 else '-X'),x='+Y'),(0,0,0),(sgn*56.9,-44.45,19.05),dir=('+X' if sgn<0 else '-X'))
    m.step=49
m.step=51
out='/home/claude/vexgo/build/adv.json'
m.dump(out,shift=(0,0,37.95))
from collections import Counter
c=Counter(p['sid'] for p in m.parts if p['step']>1)
print(len(m.parts),'parts', dict(c))
