from utilref import *

import os
print(os.getcwd())
#open dbglog=True in afm_config.py!!!
from autofreshmap_implementation import *
whitelistedmapdetector, stateDetector=loadAssetsNeeded4FreshAMap()
sence=[r"C:\Users\Kita\Desktop\spawnScenseTest.png"]
sence={ss:cv.imread(ss) for ss in sence}

for ssnm,ss in sence.items():
    print('#'*10)
    print(f'{ssnm}')
    print('#'*10)
    print(f'testing map on {ssnm}')
    whitelistedmapdetector['Karelia'].detect(ss)
    for sdnm,sd in stateDetector.items():
        print(f'testing sign {sdnm} on {ssnm}')
        sd.detect(ss)
        
