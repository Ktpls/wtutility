
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
    m=m[pul[1]:pbr[1],pul[0]:pbr[0]]
    rave=regionave(m,31)
    err=m-rave
    cv.normalize(err,err,0,1,cv.NORM_MINMAX)

    #get plane
    plane=cv.threshold(err,0.5,1,cv.THRESH_BINARY_INV)[1]
    savematflt(plane)
    planeXdist=plane.sum(0)
    planeYdist=plane.sum(1)
    X=np.arange(-searchrange,searchrange)
    Y=np.arange(-searchrange,searchrange)
    offset=[
        (X*planeXdist).sum()/planeXdist.sum(),
        (Y*planeYdist).sum()/planeYdist.sum()]
    return p0+offset


#full screen tracker
def planetracker2(m,p0,searchrange=100):
    #adaptive thresh
    rave=regionave(m,31)
    err=m-rave
    cv.normalize(err,err,0,1,cv.NORM_MINMAX)

    #get plane
    plane=cv.threshold(err,0.5,1,cv.THRESH_BINARY_INV)[1]
    X=np.arange(m.shape[1])
    Y=np.arange(m.shape[0])
    X,Y=np.meshgrid(X,Y)
    newpos=[
        (X*plane).sum()/plane.sum(),
        (Y*plane).sum()/plane.sum()]
    return np.array(newpos)

tstnpa=np.ones([2,3,4])
sumed=tstnpa.sum(0)


cap = cv.VideoCapture(r"D:\output\f.avi")
n_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH)) 
h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
fourcc = cv.VideoWriter_fourcc(*'XVID')
fps = 10
out = cv.VideoWriter(r"D:\output\f_marked.avi", fourcc, fps, (w, h), False)


# Read first frame
p0=0.5*np.array([w,h])
for i in range(0,n_frames-2):
    success, frame = cap.read() 
    if not success:
        break
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) 
    pnew=planetracker(frame,p0)
    pdelta=(pnew-p0).astype('int32')
    print('{}:{},{}'.format(i,pnew.astype('int32'),pdelta.astype('int32')))
    orgpoint=np.array([w/2,h/2],np.int32)
    dstpoint=orgpoint+pdelta.astype('int32')
    output_gray=cv.line(
        frame,
        orgpoint,
        dstpoint,
        127)

    p0=pnew
    out.write(output_gray)
out.release()
win32api.Beep(1000,1000)