from dataclasses import dataclass
from typing import Any, Iterable, Mapping
import matplotlib as mpl
from utilitypack.utility import *
import gameinput
from wtdistmeaspy_config import *
import scipy.interpolate

if ocrimpltype == "tes":
    from wtdistmeaspy_ocrimpl import implTesseract as ocrimpl
elif ocrimpltype == "cnn":
    from wtdistmeaspy_ocrimpl import implCNN as ocrimpl
elif ocrimpltype == "psb":
    from wtdistmeaspy_ocrimpl import implPassby as ocrimpl

ocrimpl.init()


yellowmarkpath = r"./asset/wtdistmeaspy/yellowmarkBinary.png"
kernelyellowmark = (
    cv.cvtColor(cv.imread(yellowmarkpath), cv.COLOR_BGR2GRAY).astype(np.float32) / 255
)
# screen
w = 1920
h = 1080


def kickOutWrongItemInUniformData(l, sqrErrReq):
    l = np.copy(l)
    while True:
        if len(l) < 1:
            # no available interval
            return False
        ave = l.mean()
        errs = (l - ave) ** 2
        err = np.sqrt(errs.sum() / len(errs)) / ave
        if err < sqrErrReq:
            break

        # lower err and try again
        l = np.delete(l, errs.argmax())
    return l, err


@dataclasses.dataclass
class ElementsOfMap:
    playerpos: np.ndarray
    ympos: np.ndarray
    gridave: float
    plottingscale: float
    result: float


@dataclasses.dataclass
class SMException:
    class SolveMapResultType(enum.Enum):
        NO_ERR = "NO_ERR"
        PL_NOT_FOUND = "PL_NOT_FOUND"
        PL_2GREAT_ERR = "PL_2GREAT_ERR"
        YM_2LESS_PROD = "YM_2LESS_PROD"
        GD_BAD_INTE = "GD_BAD_INTE"
        PS_BAD_OCR = "PS_BAD_OCR"
        using_last_playerpos = "using_last_playerpos"
        using_last_grid = "using_last_grid"
        using_last_ps = "using_last_ps"
        SEC_PE = "SEC_PE"
        SEC_YE = "SEC_YE"
        SEC_GE = "SEC_GE"
        SEC_PS = "SEC_PS"
        SEC_PSLOCK = "SEC_PSLOCK"

    smetype: SolveMapResultType
    msg: str = "NOMSG"

    def __repr__(self) -> str:
        return "{}-{}".format(self.smetype.name, self.msg)

    def IsExceptionSafeToPass(self) -> bool:
        return self.smetype in [
            SMException.SolveMapResultType.NO_ERR,
            SMException.SolveMapResultType.PS_BAD_OCR,
            SMException.SolveMapResultType.using_last_playerpos,
            SMException.SolveMapResultType.using_last_grid,
            SMException.SolveMapResultType.using_last_ps,
            SMException.SolveMapResultType.SEC_PE,
            SMException.SolveMapResultType.SEC_YE,
            SMException.SolveMapResultType.SEC_GE,
            SMException.SolveMapResultType.SEC_PS,
            SMException.SolveMapResultType.SEC_PSLOCK,
        ]


@dataclasses.dataclass
class SolveMapResultItem:
    state: SMException
    result: Any
    err: float = 0


@dataclasses.dataclass
class SolveMapResult:
    playerpos: SolveMapResultItem
    ym: SolveMapResultItem
    grid: SolveMapResultItem
    plottingscale: SolveMapResultItem


def SolveMap_BottomRightSmallMap(
    isrc, dbg: bool = False, dbglogpath: str = "", dontGetPlottingScale: bool = False
):
    if dbg:

        def dbglogsavestep(m, name="unnamed", method="savemat"):
            nonlocal dbglogpath
            exec("{}(m,path=dbglogpath,name=name)".format(method))

        logg = logger(os.path.join(dbglogpath, "log.log"))

        def log(s):
            logg(s)

    else:

        def dbglogsavestep(m, name=None, method="savemat"):
            pass

        logg = None

        def log(s):
            pass

    mcolored = isrc
    dbglogsavestep(mcolored)

    mgray = cv.cvtColor(mcolored, cv.COLOR_BGR2GRAY)
    dbglogsavestep(mgray)

    # find player

    mcolorply = cv.cvtColor(mcolored, cv.COLOR_BGR2HSV)
    dbglogsavestep(mcolorply)

    mcolorply = cv.inRange(
        mcolorply, hsv2opencv8bithsv([25, 15, 55]), hsv2opencv8bithsv([65, 60, 256])
    )
    dbglogsavestep(mcolorply)

    mply = cv.adaptiveThreshold(
        mgray, 1, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, -110
    )
    dbglogsavestep(255 * mply)

    mply = mcolorply * mply
    dbglogsavestep(mply)

    def playerfinder_gaussiandensity_method(m):
        b = cv.GaussianBlur(m, [5, 5], None)
        dbglogsavestep(b)

        mply = (m * (b > 255 * 7 / 25)).astype("int")
        dbglogsavestep(mply)

        X = np.arange(mply.shape[1])
        Y = np.arange(mply.shape[0])
        X, Y = np.meshgrid(X, Y)
        mplysum = mply.sum()
        if mplysum < 1:
            return [False, None, None]

        playerpos = [(X * mply).sum() / mplysum, (Y * mply).sum() / mplysum]
        playererr = (
            ((X - playerpos[0]) ** 2 + (Y - playerpos[1]) ** 2) * mply
        ).sum() / mplysum
        log("p=(%3d,%3d),pe=%5.3f" % (playerpos[0], playerpos[1], playererr))
        return True, playerpos, playererr

    afterprocessresult = playerfinder_gaussiandensity_method(mply)
    if not afterprocessresult[0]:
        playerpos = None
        playererr = 0
        playerstate = SMException(SMException.SolveMapResultType.PL_NOT_FOUND)
    else:
        _, playerpos, playererr = afterprocessresult
        if playererr < plerrreq:
            playerstate = SMException(SMException.SolveMapResultType.NO_ERR)
        else:
            playerstate = SMException(
                SMException.SolveMapResultType.PL_2GREAT_ERR, "%5.3f" % playererr
            )
    # try deleting too wrong points like did in grid processing

    # find yellow mark
    mcolorym = cv.cvtColor(mcolored, cv.COLOR_BGR2HSV)
    dbglogsavestep(mcolorym)

    mym = (
        cv.inRange(
            mcolorym,
            hsv2opencv8bithsv([60 - 25, 80, 70]),
            hsv2opencv8bithsv([60 + 25, 100, 100]),
        ).astype(np.float32)
        / 255
    )
    dbglogsavestep(mym * 255)

    mym = cv.filter2D(mym * 2 - 1, -1, kernelyellowmark * 2 - 1) / np.prod(
        kernelyellowmark.shape
    )
    dbglogsavestep(mym, method="savematn")
    ympos = [mym.max(0).argmax(), mym.max(1).argmax()]
    ymerr = mym[ympos[1], ympos[0]]  # not real err. greater is better
    log("y=(%3d,%3d),ye=%5.3f" % (ympos[0], ympos[1], ymerr))

    if ymerr < ymerrreq:
        # should not use last ym
        ymstate = SMException(
            SMException.SolveMapResultType.YM_2LESS_PROD, "%5.3f" % ymerr
        )
    else:
        ymstate = SMException(SMException.SolveMapResultType.NO_ERR)

    # find grid
    mgrd = 255 - mgray
    dbglogsavestep(mgrd)

    mgrd = cv.adaptiveThreshold(
        mgrd, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 5, -5
    )
    dbglogsavestep(mgrd)

    gridlinekernellength = 201
    onepixline = np.ones([gridlinekernellength])
    kernelrow = np.array(
        [-1 * onepixline, 1 * onepixline, 1 * onepixline, -1 * onepixline]
    )
    kernelrow = kernelrow / gridlinekernellength

    mrow = cv.filter2D(mgrd, -1, kernelrow)
    dbglogsavestep(mrow)
    drow = mrow.mean(axis=1) / 255

    mcol = cv.filter2D(mgrd, -1, kernelrow.T)
    dbglogsavestep(mcol)
    dcol = mcol.mean(axis=0) / 255

    dbglogsavestep(
        cv.threshold(
            mcol.astype("float") + mrow.astype("float"), 255, 255, cv.THRESH_TRUNC
        )[1]
    )

    def distribution2interval(d):
        d = d * (d > 0.5)
        # distribution2interval
        linepos = [i for i, l in enumerate(d) if l > 0]
        # trim the last nan out in arrayshift
        interval = (arrayshift(linepos, -1) - linepos)[:-1]
        return interval

    interval = np.concatenate(
        [distribution2interval(dcol), distribution2interval(drow)]
    )

    log("all intervals\n%s" % ("\n".join(["%4d" % i for i in interval])))

    MIN_LINE_INTERVAL = 20
    # filter intervals
    interval = [i for i in interval if i > MIN_LINE_INTERVAL]
    log("degened intervals\n%s" % ("\n".join(["%4d" % i for i in interval])))

    interval = np.array(interval)
    intervaltotalnum = len(interval)

    kickoutresult = kickOutWrongItemInUniformData(interval, griderrreq)
    if type(kickoutresult) is bool and not kickoutresult:
        gridave = 0
        griderr = 0
        gridstate = SMException(SMException.SolveMapResultType.GD_BAD_INTE)
    else:
        interval, err = kickoutresult
        log(
            "grid interval samples used %d out of %d, err=%5f\n"
            % (len(interval), intervaltotalnum, err)
        )

        log("used intervals\n%s" % ("\n".join(["%4d" % i for i in interval])))

        gridave = interval.mean()
        griderr = interval.var()
        gridstate = SMException(SMException.SolveMapResultType.NO_ERR)

    log("g=%3f,ge=%5f.3f" % (gridave, griderr))

    # find plotting scale
    if dontGetPlottingScale:
        # skip this if ps locked
        # cuz implTesseract is really slow
        plottingscalestate, plottingscale = (
            SMException(SMException.SolveMapResultType.NO_ERR),
            0,
        )
    else:
        # standard: all bivalue map must be presented in [0,255] form
        psfindrange = int(2.5 * gridave)
        # cut region and del the "scale"
        # 3 is height of scale, 14 is height of text, 1 is gap between scale and text
        # text is a little bit out of range between two vertical lines,
        # so 2x interval is with slight possibility losing char pixel
        # but 2.5x interval is quite enough
        base = -3 - 1 + plottingscalePosOffset
        mps = np.copy(mcolored[base - 14 : base, -psfindrange:, :])
        dbglogsavestep(mps)
        # consider cut map in the last step, for using as more region info in detection as possible

        # filter absolute color
        mpshsv = cv.cvtColor(mps, cv.COLOR_BGR2HSV)
        darkgraypoints = cv.inRange(
            mpshsv, hsv2opencv8bithsv([0, 0, 0]), hsv2opencv8bithsv([360, 56, 40])
        )
        dbglogsavestep(darkgraypoints)

        # filter adaptive value(lightness)
        mpsgray = mpshsv[:, :, 2]
        mpsgray = mpsgray.astype("float")
        relblack = cv.threshold(
            (mpsgray - regionave(mpsgray, [5, 5])),
            plottingscale_rel_darkness,
            255,
            cv.THRESH_BINARY_INV,
        )[1]
        dbglogsavestep(relblack)

        # be both really black and relatively black
        black = np.logical_and(darkgraypoints, relblack).astype("float")
        # black=np.logical_and(black,relinsat).astype('float')*255
        dbglogsavestep(black * 255)

        charw, charh = 10, 20

        # padding for ease of recongnization by tesseract, at least in the past
        # but our cnn using data collected from tesseract daily use uses the standard 20x10 char pic
        black = cv.copyMakeBorder(black, 3, 3, 3, 3, cv.BORDER_CONSTANT, value=0)
        dbglogsavestep(black * 255)
        plottingscale = ocrimpl.ocr(black, dbglogsavestep, log)
        if (
            plottingscale > plottingscalerequpper
            or plottingscale < plottingscalereqlower
        ):  # bad
            plottingscalestate = SMException(SMException.SolveMapResultType.PS_BAD_OCR)
        else:
            plottingscalestate = SMException(SMException.SolveMapResultType.NO_ERR)

        # im collecting samples on dl prac
        if collectPlottingScale:
            savemat(
                black,
                f"black4CNN_{plottingscale}",
                path="./output/wtdmp_noised_scale_collection_project/",
            )

    return SolveMapResult(
        playerpos=SolveMapResultItem(playerstate, playerpos, playererr),
        ym=SolveMapResultItem(ymstate, ympos, ymerr),
        grid=SolveMapResultItem(gridstate, gridave, griderr),
        plottingscale=SolveMapResultItem(plottingscalestate, plottingscale),
    )


def cutBottomRightMap(m):
    pa = np.array([1548, 729])
    pb = np.array([1871, 1052])
    return cv.getRectSubPix(m, pb - pa, 0.5 * (pa + pb))


uimask = cv.imread(r".\asset\opdar\UIMASK.png")[:, :, 0].astype(np.float32) / 255
uimask = cv.resize(
    uimask, (np.flip(uimask.shape[0:2]) * caliTableDetectionZoomRate).astype(np.int32)
)
uimask[uimask > 0.5] = 1
uimask[uimask <= 0.5] = 0


def SetLineKernel():
    kernelLength = 21
    kernelHalfWidth = 3
    lineHalfWidth = 1.5  # could be float, cuz its soft kernel
    alongWidth = np.linspace(-kernelHalfWidth, kernelHalfWidth, kernelHalfWidth * 2 + 1)
    kerValAlongWidth = np.exp(-((alongWidth / lineHalfWidth) ** 2))
    # transfer to m2 to 1 now
    Transfer0To1ToM1To1 = scipy.interpolate.interp1d(
        [0, 1 / np.e, 1], [-1, 0, 1], assume_sorted=True
    )
    kerValAlongWidth = Transfer0To1ToM1To1(kerValAlongWidth)
    # vertical now
    return (
        np.repeat(
            kerValAlongWidth.reshape((1,) + kerValAlongWidth.shape),
            kernelLength,
            axis=0,
        )
        / kernelLength
    )


LineKernel = SetLineKernel()


def SnipScencePreProcess(m, dbg, dbglogsavestep, log):
    # Load input image
    input_image = cv.resize(
        m,
        (np.flip(m.shape[0:2]) * caliTableDetectionZoomRate).astype(np.int32),
        interpolation=cv.INTER_NEAREST,
    )
    dbglogsavestep(input_image)

    # Convert input image to HSV color space
    hsv_image = cv.cvtColor(input_image, cv.COLOR_BGR2HSV).astype(np.float32)

    # Define lower and upper bounds for red color in HSV color space
    # shift hue up by range, move parts over 360 back to hue-360
    # then filter [0,2*range]
    # consider use adaptive hue filter, cuz red is not so clear after zoomed in
    # consider use vertical or horizontal line conv to filter
    huerange = 20
    hsv_image += np.array([[hsv2opencv8bithsv((huerange, 0, 0))]])
    huemax = hsv2opencv8bithsv((360, 0, 0))[0]
    hsv_image[hsv_image[:, :, 0] > huemax, 0] -= huemax
    lower_red = hsv2opencv8bithsv((0, 35, 60))
    upper_red = hsv2opencv8bithsv((2 * huerange, 100, 100))
    red_mask = cv.inRange(hsv_image, lower_red, upper_red) / 255
    dbglogsavestep(red_mask * 255)
    #  apply ui mask here
    red_mask = red_mask * uimask
    dbglogsavestep(red_mask * 255)

    FilterThresh = 0.5
    LineFilteredVer = cv.filter2D(red_mask, -1, LineKernel) > FilterThresh
    LineFilteredHor = cv.filter2D(red_mask, -1, LineKernel.T) > FilterThresh
    LineFiltered = np.logical_or(LineFilteredHor, LineFilteredVer)
    red_mask = np.logical_and(LineFiltered, red_mask > 0.5).astype(np.float32)
    dbglogsavestep(LineFiltered * 255)
    dbglogsavestep(red_mask * 255)
    return red_mask


def AdjustByZoomRate(degenWindow):
    return int(np.round(degenWindow * caliTableDetectionZoomRate))


def GetCrosshair(red_mask):
    # use distribution to find crosshair
    distOnX = red_mask.sum(axis=0)
    distOnY = red_mask.sum(axis=1)
    crosshair = [np.argmax(distOnY), np.argmax(distOnX)]
    crosshairSafeThresh = AdjustByZoomRate(300)
    if (
        distOnX[crosshair[1]] < crosshairSafeThresh
        or distOnY[crosshair[0]] < crosshairSafeThresh
    ):
        raise BadCaliException(
            "AC_BAD_CRHR, maybe go try switch night mode or just not in snipping"
        )
    return crosshair


def findGridAroundLine(red_mask, pos, axis, gridSearchWidth):
    # search grid line around vertical crosshair line, again use distribution

    gridSearchRange = np.array([pos - gridSearchWidth, pos + gridSearchWidth])

    # [AllowedRange[0],AllowedRange[1]), left closed right open
    def validateCoor(AllowedRange, coor):
        if coor < AllowedRange[0]:
            coor = AllowedRange[0]
        if coor >= AllowedRange[1]:
            coor = AllowedRange[1] - 1
        return coor

    for i in range(len(gridSearchRange)):
        gridSearchRange[i] = validateCoor([0, red_mask.shape[axis]], gridSearchRange[i])
    distOnAxis_Grid = (
        red_mask[:, gridSearchRange[0] : gridSearchRange[1]]
        if axis == 1
        else red_mask[gridSearchRange[0] : gridSearchRange[1], :]
    ).sum(axis=axis)

    line = distOnAxis_Grid > np.min(
        [0.75 * gridSearchWidth * 2, AdjustByZoomRate(10)]
    )  # cuz gridline length is limited

    # degenerate wide line occupying multiple rows into one
    line = line.astype(np.float32)
    degenWindow = AdjustByZoomRate(3)
    i = 0
    while i < len(line) - degenWindow:
        windowSum = line[i : i + degenWindow].sum()
        if windowSum > 1:
            center = (
                np.arange(i, i + degenWindow) * line[i : i + degenWindow]
            ).sum() / windowSum
            line[i : i + degenWindow] = 0
            line[int(center)] = 1
        i += 1
    line = line > 0.5
    return line, gridSearchRange  # range just for rebuilding


def getMilInterval(red_mask, crosshair, gridSearchWidth, log):
    gridlineHor, rangeHor = findGridAroundLine(
        red_mask, crosshair[0], 0, gridSearchWidth
    )
    gridlineHorPos = np.where(gridlineHor)[0]
    gridlineHorInterval = (arrayshift(gridlineHorPos, -1) - gridlineHorPos)[:-1]
    log("gridlineHorInterval")
    log(np.ndarray.__repr__(gridlineHorInterval))

    gridlineHorInterval = np.array(
        [i for i in gridlineHorInterval if i > milGridIntervalMin]
    )
    log("gridlineHorInterval, filtered")
    log(np.ndarray.__repr__(gridlineHorInterval))
    kickResult = kickOutWrongItemInUniformData(gridlineHorInterval, milDataErrorReq)
    if type(kickResult) is bool and not kickResult:
        # not too bad, just more time on calibrating
        log(
            "warning, gridlineHorInterval may be too bad to pass milDataErrorReq, check go it"
        )
        raise BadCaliException("BadCaliTableException")
    else:
        gridlineHorInterval, _ = kickResult
        log("gridlineHorInterval, kicked out")
        log(np.ndarray.__repr__(gridlineHorInterval))

    # that should be evenly distributed
    mil = gridlineHorInterval.mean()
    return gridlineHor, rangeHor, mil


gridSearchWidth_unzoom = 8


class BadCaliException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def getNowCalibration(m, targetcali, dbg, dbglogsavestep, log):
    red_mask = SnipScencePreProcess(m, dbg, dbglogsavestep, log)

    crosshair = GetCrosshair(red_mask)
    # get calibration table
    gridSearchWidth = AdjustByZoomRate(gridSearchWidth_unzoom)
    gridlineVer, rangeVer = findGridAroundLine(
        red_mask, crosshair[1], 1, gridSearchWidth
    )
    gridlineVerPos = np.where(gridlineVer)[0]
    log("gridlineVerPos")
    log(np.ndarray.__repr__(gridlineVerPos))
    if len(gridlineVerPos) == 0:
        # so we are in snip scence, but no cali table found, maybe blocked by gui due to scope shaking
        log("bad gridlineVerPos")
        raise BadCaliException()
    targetDistance = np.arange(len(gridlineVerPos)) * 200
    f = scipy.interpolate.interp1d(
        targetDistance,
        gridlineVerPos,
        bounds_error=False,
        fill_value="extrapolate",
        assume_sorted=True,
    )
    targetpos = f(targetcali)
    posnow = crosshair[0]
    log(f"targetpos{targetpos}, posnow{posnow}")

    # get mil interval
    gridlineHor, rangeHor, mil = getMilInterval(
        red_mask, crosshair, gridSearchWidth, log
    )

    if dbg:
        rebuildMap = np.zeros_like(red_mask)
        rebuildMap[crosshair[0], :] = 1
        rebuildMap[:, crosshair[1]] = 1

        # calibration grid
        rebuildMap[gridlineVer, rangeVer[0] : rangeVer[1]] = 1

        # mil
        rebuildMap[rangeHor[0] : rangeHor[1], gridlineHor] = 1
        dbglogsavestep(rebuildMap * 255)

    ret = np.array((targetpos, posnow, mil))
    ret /= caliTableDetectionZoomRate
    return ret


class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.last_error = 0
        self.integral = 0

    def update(self, targetval, nowval, dt=1):
        error = targetval - nowval
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.last_error = error
        return output


def switchNightMode():
    gameinput.press(gameinput.keycode.key_F6)


# to stop oscilation in autoCali due to sleep() precise
def PreciseSleep(t):
    if t > 0.1:
        # too rough
        sleep(t)
    else:
        endtime = time.perf_counter() + t
        while True:
            if time.perf_counter() >= endtime:
                break


def adjustCaliberation(pidoutput):
    keycode2press = (
        gameinput.keycode.key_PageUp
        if pidoutput > 0
        else gameinput.keycode.key_PageDown
    )

    control = np.abs(pidoutput)
    # if control<0.5:
    #     control=2*control**2 # make it more precise

    # try if get improvement in the case of no response
    gameinput.keyup(keycode2press)

    gameinput.keydown(keycode2press)
    PreciseSleep(control)
    gameinput.keyup(keycode2press)
    return control


class loadCalibrationOperator:
    def __init__(self) -> None:
        self.stopsignal = True
        self.stopped = True
        self.result = ""

    def start(self, targetcali, dbglogpath=None):
        if not self.stopped:
            # no running again
            return
        self.stopsignal = False
        self.stopped = False
        self.result = ""

        def loadCalibration(targetcali, errAllowed):
            nonlocal dbglogpath
            pid = PIDController(caliP, 0, caliD)
            ss = screenshoter()
            if caliDbg:
                if dbglogpath is None:
                    # same as in solve
                    dbglogpath = r"./asset/wtdistmeaspy/log/{}_GetCali/".format(
                        time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                    )

                def dbglogsavestep(m, name="unnamed", method="savemat"):
                    nonlocal dbglogpath
                    exec("{}(m,path=dbglogpath,name=name)".format(method))

                logg = logger(os.path.join(dbglogpath, "log.log"))

                def log(s):
                    logg(s)

            else:

                def dbglogsavestep(m, name=None, method="savemat"):
                    pass

                logg = None

                def log(s):
                    pass

            while True:
                if self.stopsignal:
                    # forced stop
                    self.result = "Stoped"
                    self.stopped = True
                    log(self.result)
                    return
                try:
                    # cali err in pixel
                    caliresult = getNowCalibration(
                        ss.shotbgr(), targetcali, caliDbg, dbglogsavestep, log
                    )
                except BadCaliException:
                    self.result = "BadCaliException"
                    self.stopped = True
                    log(self.result)
                    return

                targetpix, nowpix, mil = caliresult
                log(f"targetpix{targetpix}, nowpix{nowpix}, mil{mil}")
                # print(targetpix,nowpix)
                if np.abs(targetpix - nowpix) <= errAllowed:
                    self.result = "Great"
                    self.stopped = True
                    log(self.result)
                    return
                control = pid.update(targetpix, nowpix) * caliControlMul / mil
                log(f"control {control}")
                # get the real control, but without direction
                control = adjustCaliberation(control)
                sleep(delayEveryCali)

        threading.Thread(target=loadCalibration, args=(targetcali, autoCaliErr)).start()

    def stop(self):
        if self.stopped:
            return
        self.stopsignal = True
        while True:
            if self.stopped:
                break
            sleep(0.5)
        return self.result
