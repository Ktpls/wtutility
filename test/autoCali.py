from shared.globalsys import *
from utilitypack.util_wt import *
import wtdmp.wtdistmeaspyimpl

activeWindow(GetWtHwnd())
time.sleep(2)
Rhythms.Notify.play()

wtdmpv = wtdmp.wtdistmeaspyimpl.wtdistmeaspy()
wtdmpv.caliOperator.go(1200)
while True:
    if not wtdmpv.caliOperator.isRunning():
        break
    time.sleep(0.33)

Rhythms.Notify.play()
