
from utility import *
from telescope_config import *

sizescopefar = np.array(sizescopefar)
sizescopenear=np.array(sizescopenear)
transformation={}

def transformation_SimpleZoom(scopefar):
    zoomrate=sizescopenear.astype('float')/sizescopefar
    zoommat = np.array([
        [zoomrate[1], 0, 0],
        [0, zoomrate[0], 0]
    ])
    scopenear = cv.warpAffine(
        scopefar,
        zoommat,
        np.flip(sizescopenear),
        flags=cv.INTER_NEAREST)
    return scopenear
transformation['zoom']=transformation_SimpleZoom

def transformation_FishEye(scopefar):
    
    COOR=[np.linspace(-1,1,sizescopenear[i]) for i in range(2)]
    COOR=np.meshgrid(COOR[1],COOR[0])
    COOR=np.flip(np.array(COOR),axis=0)
    COOR=np.sign(COOR)*(1-np.sqrt(1-COOR**2))
    COOR+=1
    COOR*=0.5
    COOR*=(sizescopefar-1).reshape([2,1,1])
    COOR=np.round(COOR).astype('int')
    scopenear=scopefar[COOR[0],COOR[1]]
    
    return scopenear
transformation['fisheye']=transformation_FishEye

def gettelescopeview():
    scr = screenshoter(0).shot()
    sizescr = np.array(scr.shape[:2])
    lt = (sizescr*0.5-sizescopefar*0.5).astype('int')
    rd = (sizescr*0.5+sizescopefar*0.5).astype('int')
    scopefar = scr[lt[0]:rd[0], lt[1]:rd[1], :]
    
    return transformation[transformationtype](scopefar)