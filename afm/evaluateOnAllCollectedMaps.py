from utilref import *
import afm.autofreshmap_implementation as afmi


aa = afmi.AfmAsset(afmi.autofreshmap_configmap)
stateDetector, mapDetector = aa.stateDetector, aa.mapDetector


def TryClassifyOneMap(filepath):
    mapImg = cv.imread(filepath).astype(np.float32) / 255
    mapImgProced = afmi.MapImgComparator.imagepreprocess(mapImg)
    matched = False
    # name,detector
    ps = perf_statistic().start()
    for n, d in mapDetector.items():
        if d.detect(mapImg, mapImgProced):
            print(f"{n}")
            matched = True
        ps.countcycle()
    ps.stop()
    print(f"{ps.aveTime()=}")
    print(f"{matched=}")
