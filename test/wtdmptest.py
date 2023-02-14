from utilref import *

import os
os.chdir('..')

from wtdistmeaspy_implementation import *
scr=cv.imread(r"C:\file\code\wtutility\asset\wtdistmeaspy\log\2023-02-05-01-06-59_OnSEC_DN\unnamed.png")
SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}_NormalTrace/'.format(
                        time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime()),
                        ))