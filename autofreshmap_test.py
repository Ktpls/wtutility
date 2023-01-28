
#%%
# basic
from autofreshmap_implementation import *

whitelistedmapdetector,stateDetector=loadAssetsNeeded4FreshAMap()
def tryCutROIOnScrShot(ss):
    scr=cv.imread(ss)
    roi=stateDetector['hanger'].mtc.cutroi(scr)
    savemat(roi)

def tryDetectOnScrShot(ss,detector):
    scr=cv.imread(ss)
    result=detector.mtc.matchSign_Z_ABSDIFF_NORMED(scr)
    print(f'{detector.mtc.path}: {result}')

def keepShotingAndCall(foo):
    ss=screenshoter()
    while(True):
        foo(ss.shotbgr())
        sleep(1)

#%%
#tryDetectOnScrShot(r"D:\File\code\prog\wtutility\asset\autofreshmap\statesign\test.png",stateDetector['OK'])

#%%
def foo(scr):
    dttlist=[
        'hanger',
    ]
    [print(f'{d}:{stateDetector[d].mtc.matchSign_Z_ABSDIFF_NORMED(scr)}') for d in dttlist]
    [savemat(stateDetector[d].mtc.cutroi(scr)) for d in dttlist]
keepShotingAndCall(foo)
# %%
