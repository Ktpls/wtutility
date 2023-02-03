from wtdmpsocr import *

import sys,os

filelist=sys.argv[1:]
[print(f'{f}\n{wtdmpsocr(f)}') for f in filelist]
os.system('pause')