#called opencvWarpAffineRotate, but changed into remap() in the progress
#%%
from utilref import *
m=cv.imread(r"C:\file\code\wtutility\exp\opencvWarpAffineRotate.png").astype(np.float32)/255
the=np.pi/6
npp=nestedPyPlot([2,3],[1,1], plt.figure(figsize=(16, 16)))
#actually -theta here, cuz i was calcing from unrot to rot, but remap() is from rot to unrot
rotmat=np.array([
    [np.cos(the),-np.sin(the)],
    [np.sin(the),np.cos(the)],
])
shapeorg=np.array(m.shape)
Y,X=np.arange(shapeorg[0],dtype=np.float32),np.arange(shapeorg[1],dtype=np.float32)
X,Y=np.meshgrid(X,Y)
Y-=shapeorg[0]*0.5
X-=shapeorg[1]*0.5
Xp=rotmat[0,0]*X+rotmat[0,1]*Y
Yp=rotmat[1,0]*X+rotmat[1,1]*Y
X=Xp
Y=Yp
Y+=shapeorg[0]*0.5
X+=shapeorg[1]*0.5
m=cv.remap(m,Xp,Yp,cv.INTER_LINEAR)
npp.subplot(0,0)
plt.imshow(m)

#assert right squared img0 here
l0=shapeorg[0]
l1=int(l0/((np.tan(np.abs(the))+1)*np.cos(np.abs(the)))) #theta in [-pi/2,pi/2]
offset=int((l0-l1)*0.5)
matcut=np.array([
    [1,0,-offset],
    [0,1,-offset],
],dtype=np.float32)
m=cv.warpAffine(m,matcut,[l1,l1])
npp.subplot(1,0)
plt.imshow(m)

matzoomback=np.array([
    [l0/l1, 0, 0],
    [0, l0/l1, 0],
],dtype=np.float32)
m=cv.warpAffine(m,matzoomback,[l0,l0])
npp.subplot(2,0)
plt.imshow(m)
m=np.flip(m,axis=-2)
npp.subplot(3,0)
plt.imshow(m)


def zoom(m,rate):
    l0=m.shape[0]
    X=np.arange(l0).reshape([1,l0]).astype(np.float32)
    Y=np.arange(l0).reshape([l0,1]).astype(np.float32)
    XY=np.array(np.meshgrid(X,Y))
    XY-=l0/2
    XY/=rate
    XY+=l0/2
    return cv.remap(m,*XY,cv.INTER_LINEAR)
m=zoom(m,0.5)
npp.subplot(4,0)
plt.imshow(m)
