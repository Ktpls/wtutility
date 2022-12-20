from telescope import *

def gridmap():
    XY=[np.arange(i) for i in sizescopefar]
    XY=np.array(np.meshgrid(XY[1],XY[0]))
    Z=(XY%10==0)
    Z=np.any(Z,axis=0)
    Z=Z.astype('int')*255
    return Z

def throughFishEye_test():
    savemat(transformation_SimpleZoom (gridmap()))

throughFishEye_test()