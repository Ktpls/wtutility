from utilref import *
import wtdmp.wtdistmeaspy

activeWindow(GetWtHwnd())
time.sleep(2)
Rhythms.Notify.play()

wtdmpv = wtdmp.wtdistmeaspy.wtdistmeaspy()
wtdmpv.caliOperator.go(1200)
while True:
    if not wtdmpv.caliOperator.isRunning():
        break
    time.sleep(0.33)

Rhythms.Notify.play()
