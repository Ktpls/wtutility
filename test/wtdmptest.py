from utilref import *

import os

print(os.getcwd())
from wtdistmeaspy_implementation import *

scr = cv.imread(
    r"C:\prog\wtutility\asset\wtdistmeaspy\log\2023-08-29-23-18-54_Onusing last ps\unnamed.png"
)
# scr = cutBottomRightMap(scr)
ret = SolveMap_BottomRightSmallMap(
    scr,
    dbg=True,
    dbglogpath=r"./asset/wtdistmeaspy/log/{}_WtdmptestTrace/".format(
        time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()),
    ),
)
print(ret)
