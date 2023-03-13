from utilref import *

import os
print(os.getcwd())
#open dbglog=True in afm_config.py!!!
from autofreshmap_implementation import *
whitelistedmapdetector, stateDetector=loadAssetsNeeded4FreshAMap()
sence=[r"./test/emuoftest/1280x720/{}.png".format(i) for i in [1,2,3,4]]
sence={ss:cv.imread(ss) for ss in sence}

for ssnm,ss in sence.items():
    print(f'map on {ssnm}')
    whitelistedmapdetector['Karelia'].detect(ss)
    for sdnm,sd in stateDetector.items():
        print(f'{sdnm} on {ssnm}')
        sd.detect(ss)
