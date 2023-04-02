
from utilitypack.utility import rgb2bgr, hsv2rgb
reflist=[140,180,200,225,275,350,450]
textcolor=255*rgb2bgr(hsv2rgb((0,0,1)))
outputpos=(100,500)

plerrreq=10
ymerrreq=0.45
griderrreq=10
plerrreqstrict=10
ymerrreqstrict=0.5
griderrreqstrict=4
plottingscalestrictlower=100
plottingscalestrictupper=500

shadowthickness=2
shadowcolor=50

measdelay=0.25
retryOnFailure=7
retryDelay=0.25
keepEveryMeasInRecord=False
ocrimpltype='cnn'
tesseractpath = r'D:\Program Files\Tesseract-OCR\tesseract.exe'
modelpath = r'.\exp\DLOnPlottingScale\wtdmpsocr\wtdmpsocr.pth'
cnnresultthresh=0.25

# plottingscalePosOffset, negative for upwards, -2 for 1280x720
plottingscalePosOffset=-2

caliDbg=True
caliP=1
caliD=0
caliControlMul=0.125
delayEveryCali = 0.1