src=r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\LE2REnh'
dst=r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\HardEnh'
import nntracker_common
import os
import numpy as np
import cv2 as cv
dataset=nntracker_common.labeldataset().init(src,os.path.join(src,'all.xlsx'),0)
def det(spl,lbl): #find hards
    spl=cv.cvtColor(spl,cv.COLOR_BGR2HSV)
    value=spl[:,:,2]
    regsize=31
    valuenear=cv.filter2D(value,-1,np.ones([regsize,regsize],np.float32)/(regsize*regsize))
    err=((valuenear-value)*lbl).sum()/(lbl.sum()+0.001)
    return err<0.15
for i in range(dataset.rawlength()):
    spl,lbl=dataset.rawgetitem(i)
    if det(spl,lbl):
        name=dataset.getname(i)
        print(name)
        a=os.path.join(src,f"spl\\{name}")
        b=os.path.join(dst,f"spl\\{name}")
        os.system(f'copy {a},{b}')
        a=os.path.join(src,f"lbl\\{name}")
        b=os.path.join(dst,f"lbl\\{name}")
        os.system(f'copy {a},{b}')
    if i%1000==0:
        print(f'now progress {i} / {dataset.rawlength()}')