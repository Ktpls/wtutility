from utilitypack import *
from .telescope_config import *
import shared.globalsys as globalsys

sizelen = np.array(sizelen)
availtransformation = {}

sizezoom = np.array(sizezoom)


def transformation_zoom(view):
    zoomrate = sizezoom.astype("float") / view.shape[:2]
    zoommat = np.array([[zoomrate[1], 0, 0], [0, zoomrate[0], 0]])
    view = cv.warpAffine(view, zoommat, np.flip(sizezoom), flags=cv.INTER_NEAREST)
    return view


availtransformation["zoom"] = transformation_zoom


def transformation_fisheye(view):

    COOR = [np.linspace(-1, 1, view.shape[i]) for i in range(2)]
    COOR = np.meshgrid(COOR[1], COOR[0])
    COOR = np.flip(np.array(COOR), axis=0)
    COOR = np.sign(COOR) * (1 - np.sqrt(1 - COOR**2))
    COOR += 1
    COOR *= 0.5
    COOR *= (np.array(view.shape[:2]) - 1).reshape([2, 1, 1])
    COOR = np.round(COOR).astype("int")
    view = view[COOR[0], COOR[1]]

    return view


availtransformation["fisheye"] = transformation_fisheye


def transformation_detailenh(view):

    def modval(x):
        # return np.arctan(x)*15*2/np.pi
        return x * detailenh_coef

    regave = regionave(view, [11, 11])
    view += modval(view - regave)
    view[view > 255] = 255
    view[view < 0] = 0
    return view


availtransformation["detail"] = transformation_detailenh


def gettelescopeview():
    # view of len
    scr = screenshoter(0).shotbgr().astype("float")
    sizescr = np.array(scr.shape[:2])
    lt = (sizescr * 0.5 - sizelen * 0.5).astype("int")
    rd = (sizescr * 0.5 + sizelen * 0.5).astype("int")
    view = scr[lt[0] : rd[0], lt[1] : rd[1], :]

    for t in transformationapplied:
        view = availtransformation[t](view)
    view = view.astype("int")
    # in case of totally black place in view
    # although im doing this by channel so pix like [0,0,1], which is not really black will be [1,1,1]
    view[view < 1] = 1
    return view


class MTI:
    def __init__(self):
        mtiSize = 5
        # uimask = cv.imread(r"asset\opdar\UIMASK.png", cv.IMREAD_GRAYSCALE)
        uimask = None
        self.mtif = MtiFilter(
            mtiSize,
            filter=interpolate.interp1d(
                [0, 0.4, 0.6, 1],
                [0, 0, 1, 1],
                kind="linear",
                assume_sorted=True,
            ),
        )
        self.me = MotionEstimator(uimask, subsamplerate=0.1)

    def reset(self):
        self.mtif.mtiQueue.clear()
        self.me.lastScreen = None

    def update(self):
        view = screenshoter(0).shotbgr()
        viewgray = view[:, :, 2].astype(np.uint8)
        ret = self.me.update(viewgray)
        if ret is None:
            mo = None
        else:
            _, mo = ret
        view = np.clip(view.astype(np.float32) / 255, 0, 1)
        result = self.mtif.update(view, mo)
        if result is None:
            return np.ones_like(viewgray)
        else:
            return (result * 255).astype(np.uint8)
