from utilitypack.utility import *
from utilitypack.util_app import *

img = np.random.choice(AllFileIn(r"C:\Users\KITA\Pictures\long"))
rect = (0, 0, 15, 15)


def reshapeKeepingRatio(img, wh):
    whimg = img.shape[:2]
    ratio = np.array(wh) / np.array(whimg)
    ratio = np.min(ratio)
    img = cv.resize(
        img, dsize=None, fx=ratio, fy=ratio, interpolation=cv.INTER_LANCZOS4
    )
    return img


img = np.frombuffer(ReadFile(img), dtype=np.uint8)
img = cv.imdecode(img, 1)
img = reshapeKeepingRatio(img, rect[2:])
img = np.maximum(img, 1)
app = BulletinApp(fps=0.2)
region = app.hud.addRegion(fullScrHUD.Region(rect[:2], img))
app.go()
