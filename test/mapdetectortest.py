from utilref import *
import afm.autofreshmap_implementation as afmi

afmi.loadAssetsNeeded4FreshAMap()


loadingscreen = cv.imread(
    r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]BattleForBastogne.Png"
)
# mapImg = afmi.cutmap(loadingscreen)
mapImg = loadingscreen
mapImg = mapImg.astype(np.float32) / 255
mapImgProced = afmi.MapImgComparator.imagepreprocess(mapImg)
matched = False
# name,detector
ps=perf_statistic().start()
for n, d in afmi.mapDetector.items():
    if d.detect(mapImg, mapImgProced):
        print(f"{n}")
        matched = True
    ps.countcycle()
ps.stop()
print(ps.aveTime())
print(f"{matched=}")
