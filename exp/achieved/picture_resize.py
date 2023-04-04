
import sys
sys.path.append('.')
from utility import *

m=cv.imread(r"D:\output\pycammot\anypainting.png")
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
rate=0.25
msmall=cv.resize(m,None,fx=rate,fy=rate,interpolation=cv.INTER_AREA)
cv.imwrite(r"D:\output\pycammot\anypainting_smallgray.png",msmall)