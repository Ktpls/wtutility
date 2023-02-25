#called opencvWarpAffineRotate, but changed into remap() in the progress
#%%
from utilref import *
m=cv.imread(r"C:\file\code\wtutility\exp\opencvWarpAffineRotate.png").astype(np.float32)/255
the=np.pi/6

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
plt.subplot(2,2,1)
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
plt.subplot(2,2,2)
plt.imshow(m)

matzoomback=np.array([
    [l0/l1, 0, 0],
    [0, l0/l1, 0],
],dtype=np.float32)
m=cv.warpAffine(m,matzoomback,[l0,l0])
plt.subplot(2,2,3)
plt.imshow(m)
m=np.flip(m,axis=-2)
plt.subplot(2,2,4)
plt.imshow(m)
