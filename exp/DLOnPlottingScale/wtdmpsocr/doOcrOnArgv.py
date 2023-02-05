from wtdmpsocr import getmodel,wtdmpsocr,cv

import sys,os

model=getmodel('wtdmpsocr.pth')
filelist=sys.argv[1:]
#filelist=[r"C:\file\code\wtutility\exp\DLOnPlottingScale\wtdmp_noised_scale_collection_project.202301112304\locmarked\black4CNN_0.png.png"]
[print(f'{f}\n{wtdmpsocr(cv.imread(f)[:,:,0],model)}') for f in filelist]
os.system('pause')

