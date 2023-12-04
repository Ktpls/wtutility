from utilref import *
import wtdmp.wtdistmeaspy

activeWindow(getWTHwnd())
sleep(2)
win32api.Beep(1000, 100)

wtdmpv = wtdmp.wtdistmeaspy.wtdistmeaspy()
wtdmpv.caliOperator.go(1200)
while True:
    if not wtdmpv.caliOperator.getRunning():
        break
    time.sleep(0.33)

win32api.Beep(1000, 100)
