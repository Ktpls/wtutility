from utilref import *

import os
print(os.getcwd())
from wtdistmeaspy_implementation import *
scr=cv.imread(r"D:\File\code\prog\wtutility\asset\wtdistmeaspy\log\2023-03-24-18-49-12_OnSEC_PE\unnamed.png")
SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}_NormalTrace/'.format(
                        time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime()),
                        ))