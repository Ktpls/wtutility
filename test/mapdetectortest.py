from utilref import *
import afm.autofreshmap_implementation as afmi

afmi.loadAssetsNeeded4FreshAMap()


loadingscreen = cv.imread(
    r"C:\prog\wtutility\output\autofreshmap\mapAutoCollection\6YEFYW8Y4X.png"
)
# mapImg = afmi.cutmap(loadingscreen)
mapImg = loadingscreen
mapImg = mapImg.astype(np.float32) / 255
mapImgProced = afmi.MapImgComparer.imagepreprocess(mapImg)
matched = False
# name,detector
for n, d in afmi.mapDetector.items():
    if d.detect(mapImg, mapImgProced):
        print(f"{n}")
        matched = True
print(f"{matched=}")
