from utilref import *
import afm.autofreshmap_implementation as afmi

afmi.loadAssetsNeeded4FreshAMap()


loadingscreen = cv.imread(
    r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-05-08 234924.png"
)
mapImg = afmi.cutmap(loadingscreen).astype(np.float32) / 255
mapImgProced = afmi.MapImgComparer.imagepreprocess(mapImg)
matched = False
# name,detector
for n, d in afmi.mapDetector.items():
    if d.detect(mapImg, mapImgProced):
        print(f"{n}")
        matched = True
print(f"{matched=}")
