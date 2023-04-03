#%%
from wtdmpsocr import getmodel,wtdmpsocr,cv
from utilref import *
import sys,os

model=getmodel(r'.\exp\DLOnPlottingScale\wtdmpsocr\wtdmpsocr.pth')
#filelist=sys.argv[1:]
#filelist=[r"C:\file\code\wtutility\exp\DLOnPlottingScale\wtdmp_noised_scale_collection_project.202301112304\locmarked\black4CNN_0.png.png"]
filelist=[row[0] for row in Xls2ListList(r"exp\DLOnPlottingScale\dataset\plottingscaleorgDataset\appendix.xlsx") if row[0] is not None]
[print(f'{f}\n{wtdmpsocr(cv.imread(f)[:,:,0],model,0.3)}') for f in filelist]
os.system('pause')

