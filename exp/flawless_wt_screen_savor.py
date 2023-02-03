
import sys
sys.path.append('.')
from utility import *

#setadmin(__file__)

h=getWTHwnd()
print(h)

for t in range(1,5+1):
    for b in range(t):
        win32api.Beep(500,100)
    time.sleep(1)

ss=screenshoter(h)
I=0
while(True):
    win32api.Beep(1000,1000)
    m=ss.shot()
    m=cv.cvtColor(m,cv.COLOR_BGRA2BGR)
    cv.imwrite(r"C:\output\pycammot\flawless_wt_screen_savor{}.png".format(I),m)
    I+=1
    time.sleep(1)
    if I>10:
        break
win32api.Beep(500,1000)