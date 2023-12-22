from utilref import *
import wtdmp.wtdistmeaspy

activeWindow(GetWtHwnd())
sleep(2)
RythmNotify.play()

wtdmpv = wtdmp.wtdistmeaspy.wtdistmeaspy()
wtdmpv.caliOperator.go(1200)
while True:
    if not wtdmpv.caliOperator.getRunning():
        break
    time.sleep(0.33)

RythmNotify.play()
