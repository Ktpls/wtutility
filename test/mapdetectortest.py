from utilref import *
import afm.autofreshmap_implementation as afmi

afmi.loadAssetsNeeded4FreshAMap()


def MapLike2ScreenLike(mapshaped):
    # padding for matcher's cutting
    screenshaped = np.zeros([1080, 1920, 3], np.uint8)
    screenshaped[
        afmi.standardMapLeftTopPoint[1] : afmi.standardMapLeftTopPoint[1] + 648,
        afmi.standardMapLeftTopPoint[0] : afmi.standardMapLeftTopPoint[0] + 648,
        :,
    ] = mapshaped
    return screenshaped


loadingscreen = cv.imread(
    r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-04-27 231601.png"
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
