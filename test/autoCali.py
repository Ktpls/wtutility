from utilref import *
import wtdistmeaspy
activeWindow(getWTHwnd())
win32api.Beep(1000,100)
sleep(2)
wtdistmeaspy.caliOperator.start(1200)