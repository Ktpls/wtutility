from utilref import *
import wtdistmeaspy
activeWindow(getWTHwnd())
win32api.Beep(1000,100)
sleep(2)
wtdmp=wtdistmeaspy.wtdistmeaspy()
wtdmp.caliOperator.start(1200)
while(True):
    if wtdmp.caliOperator.stopped:
        break
    time.sleep(0.33)
win32api.Beep(1000,100)