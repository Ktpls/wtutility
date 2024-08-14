from utilref import *
import afm.autofreshmap_implementation as afmi


class SingleMapConfigMimic:
    def __init__(self, mapp: list[str]):
        self.whitelistedmap = mapp


# mapconfig = afmi.autofreshmap_configmap
mapconfig = SingleMapConfigMimic(
    [r"air\[Operation]ConsolidationOfPositionsOnSicily(LightVehicles)"]
)
aa = afmi.AfmAsset(mapconfig)
stateDetector, mapDetector = aa.stateDetector, aa.mapDetector


def TestOnePicWithAllMapDetectors():
    mapImg = cv.imread(r"C:\file\code\wtutility\output\Unknown_018.png")
    # mapImg = afmi.cutmap(mapImg)
    mapImg = mapImg.astype(np.float32) / 255
    mapImgProced = afmi.MapImgComparator.imagepreprocess(mapImg)
    matched = False
    ps = perf_statistic().start()
    # name, detector
    for n, d in mapDetector.items():
        if d.detect(mapImg, mapImgProced):
            print(f"{n}")
            matched = True
        ps.countcycle()
    ps.stop()
    print(f"{ps.aveTime()=}")
    print(f"{matched=}")


def TestOnePicWithStateDetectors():
    loadingscreen = cv.imread(
        r"C:\Users\KITA\Pictures\Screenshots\Screenshot 2024-07-03 130919.png"
    )
    mapImg = loadingscreen
    # mapImg = mapImg.astype(np.float32) / 255
    ps = perf_statistic().start()
    # name, detector
    for n, d in stateDetector.items():
        if d.detect(mapImg):
            print(f"{n}")
            matched = True
        ps.countcycle()
    ps.stop()
    print(f"{ps.aveTime()=}")
    print(f"{matched=}")


TestOnePicWithAllMapDetectors()
