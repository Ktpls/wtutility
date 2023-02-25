from utilref import *
os.chdir(r'C:\file\code\wtutility')
from autofreshmap_implementation import *
whitelistedmapdetector, stateDetector=loadAssetsNeeded4FreshAMap()
loadingscreen=cv.imread(r"C:\file\code\wtutility\asset\autofreshmap\map\Berlin.png")

ret = False
# name,detector
for n, d in whitelistedmapdetector.items():
    # done this by hand to get 2 times faster
    if d.detect(loadingscreen):
        allchanneloutput(f'{n}')
        ret = True
        break

print(ret)
