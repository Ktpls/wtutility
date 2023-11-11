from utilref import *
import wtdistmeaspy
import gameinput

activeWindow(getWTHwnd())
sleep(2)
win32api.Beep(1000, 100)

wtdmp = wtdistmeaspy.wtdistmeaspy()
wtdmp.caliOperator.go(1200)
while True:
    if not wtdmp.caliOperator.getRunning():
        break
    time.sleep(0.33)

win32api.Beep(1000, 100)
