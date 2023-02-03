
import sys
sys.path.append('.')
from utility import *

m=[
    cv.imread(r"D:\output\pycammot\shot 2022.07.09 20.50.11.jpg"),
    cv.imread(r"D:\output\pycammot\shot 2022.07.09 20.50.12.jpg")
]
#answer is 231,32
for i in range(len(m)):
    m[i]=cv.cvtColor(m[i],cv.COLOR_BGR2GRAY)
    m[i]=np.array(m[i],np.float32)/256
    m[i]=feature_polarize_effect(m[i])
    savematflt(m[i])



def f(X):
    return evaluateOffset(m[0],m[1],X)

Y=range(-500,500,10)
r=np.zeros_like(m[0])
center=np.floor_divide(np.array(r.shape),2)

xstart=-500
xend=500
pointnum=50
def coortrans(x):
    return (xend-xstart)/pointnum*x+xstart

for x in range(pointnum):
    for y in range(pointnum):
        v=int(f([coortrans(x),coortrans(y)]))
        p1=np.array([int(coortrans(x)+center[1]), int(coortrans(y)+center[0])])
        p2=np.array([int(coortrans(x+1)+center[1]), int(coortrans(y+1)+center[0])])
        # rec=[
        #     int(coortrans(x)+center[1]),
        #     int(coortrans(y)+center[0]),
        #     int(coortrans(x+1)+center[1]),
        #     int(coortrans(y+1)+center[0])]
        cv.rectangle(
            r,
            p1,
            p2,
            v,
            cv.FILLED)
    print(x)
# cv.rectangle(
#     r,
#     [int(-500+center[1]), int(-500+center[0])],
#     [int(500+center[1]), int(500+center[0])],
#     289054.56,
#     -1)

r=cv.normalize(r,r,0,256,cv.NORM_MINMAX)
savemat(r)
