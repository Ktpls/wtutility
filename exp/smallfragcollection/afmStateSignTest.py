from utilref import *

import os
print(os.getcwd())
#open dbglog=True in afm_config.py!!!
from afm.autofreshmap_implementation import *
aa = AfmAsset(autofreshmap_configmap)
stateDetector, mapDetector = aa.stateDetector, aa.mapDetector
sence=[r"C:\file\code\wtutility\asset\autofreshmap\log\screen\2023-11-05-15-49-02.png"]
sence={ss:cv.imread(ss) for ss in sence}

for ssnm,ss in sence.items():
    print('#'*10)
    print(f'{ssnm}')
    print('#'*10)
    print(f'testing map on {ssnm}')
    mapDetector['Karelia'].detect(ss)
    for sdnm,sd in stateDetector.items():
        print(f'testing sign {sdnm} on {ssnm}')
        print(f'result={sd.detect(ss)}')
        
