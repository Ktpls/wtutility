from utilref import *

import os
print(os.getcwd())
from wtdistmeaspy_implementation import *
scr=cv.imread(r"C:\Users\Kita\Desktop\NWP3.png")
scr=cutBottomRightMap(scr)
SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}_NormalTrace/'.format(
                        time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime()),
                        ))