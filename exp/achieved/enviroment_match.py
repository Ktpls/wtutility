
import sys
sys.path.append('.')
from utility import *
import time


envsize=101
targetpos=[1211,602]

#load and preprocess source pics
m=[
    cv.imread(r"D:\output\pycammot\shot 2022.07.09 20.50.11.jpg"),
    cv.imread(r"D:\output\pycammot\shot 2022.07.09 20.50.12.jpg")
]
t0=time.perf_counter()
for i in range(len(m)):
    m[i]=cv.cvtColor(m[i],cv.COLOR_BGR2GRAY)
    m[i]=np.array(m[i],np.float32)/256
    #m[i]=feature_polarize_effect(m[i])
    savematflt(m[i])

#get enviroment pic
menv=cv.getRectSubPix(m[0],[envsize,envsize],targetpos)
savematflt(menv)

#set plane transparent->which is 0
menv=cv.normalize(menv,menv,0,1,cv.NORM_MINMAX)
maqua=cv.threshold(menv,0.70,1,cv.THRESH_BINARY)[1]
savematflt(maqua)

#fill plane with menv averange color
#so that feature polarization wont regard dark plane as something serious
#maqua.sum==num of opaque pixs
menvave=menv.sum()/maqua.sum()
#set plane black and add ave color
menv=menv*maqua+(1-maqua)*menvave
savematflt(menv)
menv=feature_polarize_effect(menv)
#menv=cv.normalize(menv,menv,0,1,cv.NORM_MINMAX)
savematflt(menv)

#set plane back to zero
menv=menv*maqua
savematflt(menv)

#norm menv
total2=(menv*menv).sum()
menv=menv/ math.sqrt(total2)

#preparation for in-range norm of m1
m1=m[1].copy()
#convolve sumer to finish in-range sum, transparent parts are not counted
sumer=maqua.copy()
m1_2=m1**2
m1_2sum=cv.filter2D(m1_2,-1,sumer)+0.001
m1_2sum2=np.sqrt(m1_2sum)

#in-range norm result
mr=cv.filter2D(m[1],-1,menv)
mr=mr/m1_2sum2


#cal coor
coor=mr.argmax()
y=coor/mr.shape[1]
x=coor%mr.shape[1]
print(coor,x,y)

t1=time.perf_counter()
print('time cost:',t1-t0)

mr=cv.normalize(mr,mr,0,256,cv.NORM_MINMAX)
savemat(mr)
mr=cv.threshold(mr,254,255,cv.THRESH_BINARY)[1]
savemat(mr)

cv.circle(m[1], [int(x), int(y)], int(envsize*0.5),  0);
savematflt(m[1])