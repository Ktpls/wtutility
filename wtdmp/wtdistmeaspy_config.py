from utilitypack.utility import rgb2bgr, hsv2rgb
from .wtdistmeaspy_config_dell import *

reflist = [140, 180, 200, 225, 275, 350, 450]
textcolor = 255 * rgb2bgr(hsv2rgb((0, 0, 1)))
outputpos = (100, 500)

plerrreq = 10
ymerrreq = 0.33
griderrreq = 0.1
plottingscalereqlower = 100
plottingscalerequpper = 600

plerrreqstrict = 10
ymerrreqstrict = 0.33
griderrreqstrict = 4
plottingscalestrictlower = 130
plottingscalestrictupper = 550

shadowthickness = 2
shadowcolor = 50

measdelay = 0.4  # nencessary for covering last yellow mark with new one
retryOnFailure = 7
retryDelay = 0.1
keepEveryMeasInRecord = False
collectFailDebugOutput = True
collectPlottingScale = True
ocrimpltype = "tes"
tesseractpath = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
modelpath = r".\asset\wtdistmeaspy\wtdmpsocr.pth"
cnnresultthresh = 0.3
plottingscale_rel_darkness = -2.5


caliDbg = True
caliP = 1
caliD = 0
caliControlMul = 0.125  # for 30%
# caliControlMul=0.27 #for 20%
delayEveryCali = 0.05
caliTableDetectionZoomRate = 1.0
milDataErrorReq = 0.1
milGridIntervalMin = 5
autoCaliErr = 1

collectingSmallMap = True

yellowmarkpath = r"./asset/wtdistmeaspy/yellowmarkBinary.png"
datacoll_smallmappath = r"./asset/wtdistmeaspy/smallMapCollection"
wtdmplogpath = r"./asset/wtdistmeaspy/log/{}_{}/"
