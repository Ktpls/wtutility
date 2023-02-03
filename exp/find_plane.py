
import sys
sys.path.append('.')
from utility import *

m=cv.imread(r"D:\output\pycammot\TagNEnv.jpg")
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
m=np.array(m,np.float32)
savemat(m,'org')

def regionsum(m,r):
    k=np.ones([r,r],np.float32)
    m=cv.filter2D(m,-1,k)
    return m

def regionave(m,r):
    return regionsum(m,r)/(r**2)

def regionavewithmask(mat,mask,r):
    maskedmat=mat*mask
    rsum=regionsum(maskedmat,r)
    rnum=regionsum(mask,r)
    return rsum/rnum

def spanMask(m,r):
    m=cv.GaussianBlur(m,[r,r],0)
    m=cv.threshold(m,0,1,cv.THRESH_BINARY)[1]
    return m


#adaptive thresh
rave=regionave(m,31)
savemat(rave,'rave')
err=m-rave
cv.normalize(err,err,0,1,cv.NORM_MINMAX)
savematflt(err,'err')

#get plane
plane=cv.threshold(err,0.5,1,cv.THRESH_BINARY_INV)[1]
savematn(plane,'plane')

#deplane
planespanned=spanMask(plane,11)
savematflt(planespanned,'planespanned')
ravem=regionavewithmask(err,1-planespanned,31)
err=err*(1-planespanned)+planespanned*ravem
savematflt(err,'errdeplane')
#and smooth
err=cv.GaussianBlur(err,[5,5],0)
savematflt(err,'errdeplanesmooth')

#get could edge
cloudedge=cv.threshold(np.array(err*256,np.uint8),127,256,cv.THRESH_BINARY+cv.THRESH_TRIANGLE)[1]
savemat(cloudedge,'cloudedge')