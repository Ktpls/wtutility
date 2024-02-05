
from utilitypack import *

resolution = np.array([1080, 1920])
concernedRegionLT = (resolution*0.4).astype(np.int32)
concernedRegionRD = (resolution*0.6).astype(np.int32)


class doShotCache:
    def __init__(self, t, m):
        self.t = t
        self.m = m


eedc = DataCollector(r'./output/eagleeye/')
cacheMaxNum = 10
cacheRate = 2
lastCacheTime = None
cachedShots: typing.List[doShotCache] = []
timeReverse=0.3
lastSaveTime=None
timeSaveInterval=3
timer = perf_statistic(startnow=True)
ss = screenshoter()


def onClick():
    global lastSaveTime
    nowtime=timer.time()
    i=len(cachedShots)-1
    while(i>=0):
        if (nowtime-cachedShots[i].t)>timeReverse:
            break
        i-=1
    if i<0:
        # no shot satisfied
        return
    if lastSaveTime is not None and nowtime-lastSaveTime<timeSaveInterval:
        # too short
        return
    eedc.save(cachedShots[i].m)
    lastSaveTime=nowtime
    RythmNotify.play()


def onFrame():
    global lastCacheTime,cachedShots
    if lastCacheTime is not None and timer.time()-lastCacheTime <= 1/cacheRate:
        # too short
        return

    cachedShots.append(doShotCache(timer.time(), ss.shotbgr()[
                       concernedRegionLT[0]:concernedRegionRD[0],
                       concernedRegionLT[1]:concernedRegionRD[1],
                       :]))
    if len(cachedShots) > cacheMaxNum:
        cachedShots = cachedShots[len(cachedShots)-cacheMaxNum:]

    lastCacheTime = timer.time()
