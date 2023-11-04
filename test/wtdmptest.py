from utilref import *

import os

print(os.getcwd())
from wtdistmeaspy_implementation import *

scr = cv.imread(
    r"C:\file\code\wtutility\asset\wtdistmeaspy\log\2023-11-04-21-30-55_NormalTrace\unnamed.png"
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
