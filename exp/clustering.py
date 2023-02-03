
import sys
sys.path.append('.')
from utility import *

#m got inved, zero threshed, normed
def density(m,eps=5):
    flter=np.ones([eps,eps])
    flter*=1/flter.size
    return cv.filter2D(m,-1,flter)

eps=10
routhresh=0.2
m=cv.imread(r"D:\output\pycammot\flawless_wt_screen_savor0.png")
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
imgshape=m.shape
m=m.astype('float32')
ave=regionave(m,eps)
m=ave-m
m=cv.threshold(m,0,0,cv.THRESH_TOZERO)[1]
m=cv.normalize(m,m,0,1,cv.NORM_MINMAX)
d=density(m,eps)
savematflt(m,'m')
Xc=m*cv.threshold(d,routhresh,1,cv.THRESH_BINARY)[1]
Xcspan=regionsum(Xc,eps)
validregion=cv.threshold(Xcspan,0,1,cv.THRESH_BINARY)[1]
savematflt(validregion,'validregion')
Xbdc=m*validregion
savematflt(Xbdc,'Xbdc')
Xbdcbinary=cv.threshold(Xbdc,0,1,cv.THRESH_BINARY)[1]
savematflt(Xbdcbinary,'Xbdcbinary')
contours=cv.findContours(validregion.astype('uint8'),cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)[0]
mcontour=np.zeros(np.concatenate(([len(contours)],imgshape)))
for c in range(len(contours)):
    cv.drawContours(mcontour[c],contours,c,1,thickness=cv.FILLED)
clusters=mcontour*np.repeat(m.reshape(np.concatenate(([1],imgshape))),len(contours),axis=0)
