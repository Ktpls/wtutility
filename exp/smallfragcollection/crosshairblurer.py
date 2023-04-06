from utilref import *
def deleteCrossHair(path):
    m=cv.imread(path).astype(np.float32)
    hsv=cv.cvtColor(m,cv.COLOR_BGR2HSV)
    absBlack=cv.inRange(hsv,hsv2opencv8bithsv([0,0,0]),hsv2opencv8bithsv([360,15,40]))/255
    savematflt(absBlack)
    
    value=hsv[:,:,2] # in ocv, value in [0,255]
    regave=regionave(value,[7,7])
    relBlack=((value-regave)<-20).astype(np.float32)
    savematflt(relBlack)
    
    crosshair=relBlack*absBlack
    crosshair=regionsum(crosshair,[3,3])
    crosshair[crosshair>0]=1
    savematflt(crosshair)
    filler=regionave(m,[5,5],1-crosshair,False)
    crosshair=crosshair.reshape(crosshair.shape+(1,))
    blured=m*(crosshair<0.5)+filler*(crosshair>=0.5)
    savemat(blured)
    return blured

filelistlist=Xls2ListList(r"C:\file\code\wtutility\exp\output\src\src.xlsx")

[deleteCrossHair(f[0]) for f in filelistlist]
#deleteCrossHair(filelistlist[0][0])