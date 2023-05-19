from utilref import *
import autofreshmap_implementation as afmi
afmi.loadAssetsNeeded4FreshAMap()


def MapShaped2ScreenShaped(mapshaped):
    # padding for matcher's cutting
    screenshaped=np.zeros([1080,1920,3],np.uint8)
    screenshaped[afmi.standardMapLeftTopPoint[1]:afmi.standardMapLeftTopPoint[1]+648,
                afmi.standardMapLeftTopPoint[0]:afmi.standardMapLeftTopPoint[0]+648,:]=mapshaped
    return screenshaped
loadingscreen=cv.imread(r"C:\Users\Kita\Desktop\nwp.png")
ret = False
# name,detector
for n, d in afmi.whitelistedmapdetector.items():
    # done this by hand to get 2 times faster
    if d.detect(loadingscreen):
        afmi.allchanneloutput(f'{n}')
        ret = True
        break

print(ret)
