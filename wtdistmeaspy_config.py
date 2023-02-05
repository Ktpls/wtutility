
from utilitypack.utility import rgb2bgr, hsv2rgb
reflist=[140,180,200,225,275,350,450]
textcolor=255*rgb2bgr(hsv2rgb((0,0,1)))
outputpos=(100,500)

plerrreq=10
ymerrreq=0.5
griderrreq=10
plerrreqstrict=4
ymerrreqstrict=0.55
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
