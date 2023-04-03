from utilref import *

import os
print(os.getcwd())
from wtdistmeaspy_implementation import *
scr=cv.imread(r"D:\File\code\prog\wtutility\asset\wtdistmeaspy\log\2023-04-02-20-49-41_OnSEC_PS\unnamed.png")
SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}_NormalTrace/'.format(
                        time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime()),
                        ))