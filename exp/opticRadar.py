
import sys
from time import sleep
sys.path.append('.')
from utility import *

def regionsum(m,r):
    k=np.ones([r,r],np.float32)
    m=cv.filter2D(m,-1,k)
    return m

def regionave(m,r):
    return regionsum(m,r)/(r**2)

def planetracker(m,p0,searchrange=100):
    #adaptive thresh
    pul=(p0-searchrange).astype('int32')
    pbr=(p0+searchrange).astype('int32')
    m=m[pul[0]:pbr[0],pul[1]:pbr[1]]
    rave=regionave(m,31)
    err=m-rave
    cv.normalize(err,err,0,1,cv.NORM_MINMAX)
    savemat(err*255)

    #get plane
    plane=cv.threshold(err,0.5,1,cv.THRESH_BINARY_INV)[1]
    savemat(plane*255)
    X=np.arange(-searchrange,searchrange)
    Y=X.copy()
    X,Y=np.meshgrid(X,Y)
    newpos=[
        (X*plane).sum()/plane.sum(),
        (Y*plane).sum()/plane.sum()]
    print(newpos)
    return p0+newpos

m=cv.imread(r"D:\output\pycammot\moved_blackspot.png")
m = cv.cvtColor(m, cv.COLOR_BGR2GRAY) 
p0=np.array([500,500])
ret=planetracker(m,p0)
print(ret)