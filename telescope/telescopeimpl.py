from utilitypack.utility import *
from .telescope_config import *
import shared.globalsys as globalsys

sizeScope = np.array(sizeScope)
availtransformation = {}

sizezoom = np.array(sizezoom)


def transformation_zoom(view):
    zoomrate = sizezoom.astype(np.float32) / view.shape[:2]
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
    COOR = np.round(COOR).astype(np.int32)
    # consider using cv.remap()
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


class Telescope(StoppableThread):

    def __init__(self, pool: ThreadPoolExecutor = None):
        super().__init__(pool=pool)
        self.buf = None

    def foo(self):
        fpsm = FpsManager(telescopeFps)
        while True:
            fpsm.WaitUntilNextFrame()
            if self.timeToStop():
                break
            self.update()

    def update(self):
        # view of len
        scr = screenshoter(0).shotbgr().astype(np.float32)
        sizescr = np.array(scr.shape[:2])
        lt = (sizescr * 0.5 - sizeScope * 0.5).astype(np.int32)
        rd = (sizescr * 0.5 + sizeScope * 0.5).astype(np.int32)
        view = scr[lt[0] : rd[0], lt[1] : rd[1], :]

        for t in transformationapplied:
            view = availtransformation[t](view)
        view = view.astype(np.uint8)
        # in case of totally black place in view
        # although im doing this by channel so pix like [0,0,1], which is not really black will be [1,1,1]
        view = np.maximum(1, view)
        self.buf = view

    def get(self):
        if self.buf is None:
            self.update()
        return self.buf

    def getBlankScope(self):
        view = np.zeros([sizeScope[1], sizeScope[0], 3], np.float32)
        for t in transformationapplied:
            view = availtransformation[t](view)
        view = np.zeros_like(view, np.uint8)
        return view

    def clearBuf(self):
        self.buf = self.getBlankScope()


class MTI(StoppableThread):

    def __init__(self, pool: ThreadPoolExecutor = None):
        # uimask = cv.imread(r"asset\opdar\UIMASK.png", cv.IMREAD_GRAYSCALE)
        uimask = None
        filterInterpolate = interpolate.interp1d(
            [0, 0.2, 0.8, 1],
            [0, 0, 1, 1],
            kind="linear",
            assume_sorted=True,
        )

        def filter(x):
            ret = filterInterpolate(x)
            return ret

        self.mtif = MtiFilter(
            mtiSize,
            filter=filter,
            camstablize=True,
        )
        self.me = MotionEstimator(uimask, subsamplerate=0.1)
        self.ss = screenshoter()
        self.ones = np.ones(
            np.flip(np.array(mtiRect[2:]) - np.array(mtiRect[:2])), np.uint8
        )
        self.buf = None
        super().__init__(
            StoppableSomewhat.StrategyRunOnRunning.stop_and_rerun,
            StoppableSomewhat.StrategyError.print_error,
            pool,
        )

    def reset(self):
        self.mtif.mtiQueue.clear()
        self.me.lastScreen = None

    def getResult(self):
        ret = self.ones if self.buf is None else self.buf
        ret = np.repeat(np.expand_dims(ret, axis=2), 3, axis=2)
        return ret

    def update(self):
        view = self.ss.shotbgr()
        viewgray = view[:, :, 2].astype(np.uint8)
        ret = self.me.update(viewgray)
        if ret is None:
            mo = None
        else:
            _, mo = ret
        view = np.clip(view.astype(np.float32) / 255, 0, 1)
        result = self.mtif.update(view, mtiRect, mo)
        if result is None:
            return None
        else:
            return (result * 255).astype(np.uint8)

    def foo(self):
        self.reset()
        fpsm = FpsManager(mtiFps)
        while True:
            fpsm.WaitUntilNextFrame()
            if self.timeToStop():
                break
            self.buf = self.update()
