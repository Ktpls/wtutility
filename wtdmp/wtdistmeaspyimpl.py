from shared.globalsys import *
from utilitypack.util_wt import *
from utilitypack.cold.util_solid import *
from utilitypack.util_winkey import *
from .wtdistmeaspy_config import *
import scipy.interpolate

if ocrimpltype == "tes":
    from .wtdistmeaspy_ocrimpl import implTesseract as ocrimpl
elif ocrimpltype == "cnn":
    from .wtdistmeaspy_ocrimpl import implCNN as ocrimpl
elif ocrimpltype == "psb":
    from .wtdistmeaspy_ocrimpl import implPassby as ocrimpl

ocrimpl.init()


kernelyellowmark = (
    cv.cvtColor(cv.imread(yellowmarkpath), cv.COLOR_BGR2GRAY).astype(np.float32) / 255
)
# screen
w = 1920
h = 1080


@dataclasses.dataclass
class SmallReportLogger:
    path: str
    enable: bool = True
    logg: Logger = dataclasses.field(init=False)

    def __post_init__(self):
        if self.enable:
            filePath = os.path.join(self.path, "log.log")
            self.logg = Logger(filePath)
        else:
            self.logg = None

    def __call__(self, msg=None, img: np.ndarray = None):
        if self.enable:
            if isinstance(msg, np.ndarray) and img is None:
                # actually calling like: self(some image without msg)
                img = msg
                msg = None
            if img is not None:
                if img.dtype in (
                    np.dtype("float32"),
                    np.dtype("float64"),
                    np.dtype("bool"),
                ):
                    img = (img * 255).astype(np.uint8)
                savemat(
                    img,
                    name=make_filename_safe(
                        f"[{datetime.now().strftime('%Y-%m-%d,%H,%M,%S,%f')}]{msg}"
                    ),
                    path=self.path,
                )
            else:
                self.logg(msg)


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
    result: typing.Any
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
    logg = SmallReportLogger(dbglogpath, enable=dbg)

    mcolored = isrc
    logg(mcolored)

    mgray = cv.cvtColor(mcolored, cv.COLOR_BGR2GRAY)
    logg(mgray)

    # find player

    mcolorply = cv.cvtColor(mcolored, cv.COLOR_BGR2HSV)
    logg(mcolorply)

    mcolorply = cv.inRange(
        mcolorply, hsv2opencv8bithsv([25, 15, 55]), hsv2opencv8bithsv([65, 60, 256])
    )
    logg(mcolorply)

    mply = cv.adaptiveThreshold(
        mgray, 1, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, -110
    )
    logg(255 * mply)

    mply = mcolorply * mply
    logg(mply)

    def playerfinder_gaussiandensity_method(m):
        b = cv.GaussianBlur(m, [5, 5], None)
        logg(b)

        mply = (m * (b > 255 * 7 / 25)).astype("int")
        logg(mply)

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
        logg("p=(%3d,%3d),pe=%5.3f" % (playerpos[0], playerpos[1], playererr))
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
    logg(mcolorym)

    mym = (
        cv.inRange(
            mcolorym,
            hsv2opencv8bithsv([60 - 25, 80, 70]),
            hsv2opencv8bithsv([60 + 25, 100, 100]),
        ).astype(np.float32)
        / 255
    )
    logg(mym)

    mym = cv.filter2D(mym * 2 - 1, -1, kernelyellowmark * 2 - 1) / np.prod(
        kernelyellowmark.shape
    )
    logg(CvNormalize_Copy(mym, 0, 255, cv.NORM_MINMAX))
    ympos = [mym.max(0).argmax(), mym.max(1).argmax()]
    ymerr = mym[ympos[1], ympos[0]]  # not real err. greater is better
    logg("y=(%3d,%3d),ye=%5.3f" % (ympos[0], ympos[1], ymerr))

    if ymerr < ymerrreq:
        # should not use last ym
        ymstate = SMException(
            SMException.SolveMapResultType.YM_2LESS_PROD, "%5.3f" % ymerr
        )
    else:
        ymstate = SMException(SMException.SolveMapResultType.NO_ERR)

    # find grid
    mgrd = 255 - mgray
    logg(mgrd)

    mgrd = cv.adaptiveThreshold(
        mgrd, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 5, -2
    )
    # mgrd=(mgrd-regionave(mgrd,[5,5])>2).astype(np.uint8)*255
    logg(mgrd)

    gridlinekernellength = 201
    onepixline = np.ones([gridlinekernellength])
    kernelrow = np.array(
        [-1 * onepixline, 1 * onepixline, 1 * onepixline, -1 * onepixline]
    )
    kernelrow = kernelrow / gridlinekernellength

    mrow = cv.filter2D(mgrd, -1, kernelrow)
    logg(mrow)
    drow = mrow.mean(axis=1) / 255

    mcol = cv.filter2D(mgrd, -1, kernelrow.T)
    logg(mcol)
    dcol = mcol.mean(axis=0) / 255

    logg(
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

    logg("all intervals\n%s" % ("\n".join(["%4d" % i for i in interval])))

    MIN_LINE_INTERVAL = 20
    # filter intervals
    interval = [i for i in interval if i > MIN_LINE_INTERVAL]
    logg("degened intervals\n%s" % ("\n".join(["%4d" % i for i in interval])))

    interval = np.array(interval)
    intervaltotalnum = len(interval)

    kickoutresult = kickOutWrongItemInUniformData(interval, griderrreq)
    if type(kickoutresult) is bool and not kickoutresult:
        gridave = 0
        griderr = 0
        gridstate = SMException(SMException.SolveMapResultType.GD_BAD_INTE)
    else:
        interval, err = kickoutresult
        logg(
            "grid interval samples used %d out of %d, err=%5f\n"
            % (len(interval), intervaltotalnum, err)
        )

        logg("used intervals\n%s" % ("\n".join(["%4d" % i for i in interval])))

        gridave = interval.mean()
        griderr = interval.var()
        gridstate = SMException(SMException.SolveMapResultType.NO_ERR)

    logg("g=%3f,ge=%5f.3f" % (gridave, griderr))

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
        logg(mps)
        # consider cut map in the last step, for using as more region info in detection as possible

        # filter absolute color
        mpshsv = cv.cvtColor(mps, cv.COLOR_BGR2HSV)
        darkgraypoints = cv.inRange(
            mpshsv, hsv2opencv8bithsv([0, 0, 0]), hsv2opencv8bithsv([360, 56, 40])
        )
        logg(darkgraypoints)

        # filter adaptive value(lightness)
        mpsgray = mpshsv[:, :, 2]
        mpsgray = mpsgray.astype("float")
        relblack = cv.threshold(
            (mpsgray - regionave(mpsgray, [5, 5])),
            plottingscale_rel_darkness,
            255,
            cv.THRESH_BINARY_INV,
        )[1]
        logg(relblack)

        # be both really black and relatively black
        black = np.logical_and(darkgraypoints, relblack).astype("float")
        # black=np.logical_and(black,relinsat).astype('float')*255
        logg(black)

        charw, charh = 10, 20

        # padding for ease of recongnization by tesseract, at least in the past
        # but our cnn using data collected from tesseract daily use uses the standard 20x10 char pic
        black = cv.copyMakeBorder(black, 3, 3, 3, 3, cv.BORDER_CONSTANT, value=0)
        logg(black)
        plottingscale = ocrimpl.ocr(black, logg)
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
    alongWidth = np.linspace(
        -LineDetectorKernelHalfWidth,
        LineDetectorKernelHalfWidth,
        LineDetectorKernelHalfWidth * 2 + 1,
    )

    # the initial shape, which requires magnitude adjustment for positive and negative parts perspectively
    kerValAlongWidth = np.clip(
        1 - np.abs(alongWidth / LineDetectorLineHalfWidth), -1, 1
    )
    # do experiment to get pos and neg surface
    posPart = np.sum(np.where(kerValAlongWidth >= 0, 1, 0) * kerValAlongWidth)
    negPart = np.sum(np.where(kerValAlongWidth < 0, 1, 0) * kerValAlongWidth)

    kerValAlongWidth = scipy.interpolate.interp1d(
        [-1, 0, 1], [3 / negPart, 0, 1 / posPart], assume_sorted=True
    )(kerValAlongWidth)

    # stack the kernel along length direction
    # vertical now
    kerValAlongWidth = (
        np.repeat(
            kerValAlongWidth.reshape((1,) + kerValAlongWidth.shape),
            LineDetectorKernelLength,
            axis=0,
        )
        / LineDetectorKernelLength
    )
    return kerValAlongWidth


LineKernel = SetLineKernel()


def DetectHorAndVerLine(m, logg):
    # Load input image
    input_image = cv.resize(
        m,
        (np.flip(m.shape[0:2]) * caliTableDetectionZoomRate).astype(np.int32),
        interpolation=cv.INTER_NEAREST,
    )
    logg("input_image", input_image)

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
    redpart = cv.inRange(hsv_image, lower_red, upper_red) / 255
    logg("redpart", redpart)
    #  apply ui mask here
    redpart = redpart * uimask
    logg("ui masked", redpart)

    LineFilteredVer = cv.filter2D(redpart, -1, LineKernel) > lineFilterThresh
    logg("LineFilteredVer", LineFilteredVer)
    LineFilteredHor = cv.filter2D(redpart, -1, LineKernel.T) > lineFilterThresh
    logg("LineFilteredHor", LineFilteredHor)

    # do it again to eliminate noise from each other
    LineFilteredVer_InterinferenceRm = (
        cv.filter2D(
            np.logical_and(redpart, np.logical_not(LineFilteredHor)).astype(np.float32),
            -1,
            LineKernel,
        )
        > lineFilterThresh
    )
    logg("LineFilteredVer_InterinferenceRm", LineFilteredVer_InterinferenceRm)
    LineFilteredHor_InterinferenceRm = (
        cv.filter2D(
            np.logical_and(redpart, np.logical_not(LineFilteredVer)).astype(np.float32),
            -1,
            LineKernel.T,
        )
        > lineFilterThresh
    )
    logg("LineFilteredHor_InterinferenceRm", LineFilteredHor_InterinferenceRm)
    LineFilteredVer, LineFilteredHor = (
        LineFilteredVer_InterinferenceRm,
        LineFilteredHor_InterinferenceRm,
    )
    return LineFilteredVer, LineFilteredHor


def AdjustByZoomRate(degenWindow):
    return int(np.round(degenWindow * caliTableDetectionZoomRate))


def GetCrosshair(LineFilteredVer, LineFilteredHor):
    # use distribution to find crosshair
    distOnX = LineFilteredVer.sum(axis=0)
    distOnY = LineFilteredHor.sum(axis=1)
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


def getMilInterval(red_mask, crosshair, gridSearchWidth, logg):
    gridlineHor, rangeHor = findGridAroundLine(
        red_mask, crosshair[0], 0, gridSearchWidth
    )
    gridlineHorPos = np.where(gridlineHor)[0]
    gridlineHorInterval = (arrayshift(gridlineHorPos, -1) - gridlineHorPos)[:-1]
    logg("gridlineHorInterval")
    logg(np.ndarray.__repr__(gridlineHorInterval))

    gridlineHorInterval = np.array(
        [i for i in gridlineHorInterval if i > milGridIntervalMin]
    )
    logg("gridlineHorInterval, filtered")
    logg(np.ndarray.__repr__(gridlineHorInterval))
    kickResult = kickOutWrongItemInUniformData(
        gridlineHorInterval, milDataErrorReq
    )  # uniform kicking method here with the line compensation method of calibration table lines, cuz they are facing the same problem that wants line positions but there could be interference that may be detected as false positive split, that breaks one section into several sections, or false negative split, that merges several sections into one section
    if type(kickResult) is bool and not kickResult:
        # not too bad, just more time on calibrating
        logg(
            "warning, gridlineHorInterval may be too bad to pass milDataErrorReq, check go it"
        )
        raise BadCaliException("BadCaliTableException")
    else:
        gridlineHorInterval, _ = kickResult
        logg("gridlineHorInterval, kicked out")
        logg(np.ndarray.__repr__(gridlineHorInterval))

    # that should be evenly distributed
    mil = gridlineHorInterval.mean()
    return gridlineHor, rangeHor, mil


gridSearchWidth_unzoom = 8


class BadCaliException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def RegionAve1D(interval, windowHalfWidth, dontCountPointItself=True):
    regionAveKernel = np.ones(windowHalfWidth * 2 + 1)
    if dontCountPointItself:
        regionAveKernel[windowHalfWidth] = 0
    regionNeiborNum = np.correlate(np.ones_like(interval), regionAveKernel, "same")
    regionAve = np.correlate(interval, regionAveKernel, "same") / regionNeiborNum
    return regionAve


def CompensateCalibrationTableMissedLine(tableLines):
    interval = np.diff(tableLines)
    """
    对于interval，
    使用np的卷积函数，计算出一个数据周围的数据的平均值
        这里，使用卷积核ones(CompensateCalibrationTableMissedLine_IntervalEstimationRange)
        先和ones_like(interval)卷积，padding=0，得出周围数据点数量
        再和interval卷积，padding=0，结果再除以周围数据点数量，得到周围数据的平均值
    当interval某处的值大于此处周围平均值*1.75倍，将此处的值平分为两个interval
    """

    regionAve = RegionAve1D(
        interval,
        CompensateCalibrationTableMissedLine_IntervalEstimationRangeHalfWidth,
        True,
    )
    ret = list()
    for i in range(len(interval)):
        if interval[i] > regionAve[i] * 1.75:
            ret.extend([interval[i] / 2] * 2)
        else:
            ret.append(interval[i])
    interval = np.array(ret)

    # rebuild tableLines from interval
    tableLine0Pos = tableLines[0]
    newTableLines = tableLine0Pos + np.concatenate([[0], np.cumsum(interval)])
    return newTableLines


def getNowCalibration(m, targetcali, logg: SmallReportLogger):
    LineFilteredVer, LineFilteredHor = DetectHorAndVerLine(m, logg)

    crosshair = GetCrosshair(LineFilteredVer, LineFilteredHor)
    crosshairY, crosshairX = crosshair
    # get calibration table
    gridSearchWidth = AdjustByZoomRate(gridSearchWidth_unzoom)

    gridlineVer, rangeVer = findGridAroundLine(
        LineFilteredHor, crosshairX, 1, gridSearchWidth
    )
    gridlineVerPos = np.where(gridlineVer)[0]
    logg("gridlineVerPos")
    logg(np.ndarray.__repr__(gridlineVerPos))

    if len(gridlineVerPos) == 0:
        # so we are in snip scence, but no cali table found, maybe blocked by gui due to scope shaking
        logg("bad gridlineVerPos")
        raise BadCaliException()

    gridlineVerPos = CompensateCalibrationTableMissedLine(gridlineVerPos)
    targetDistance = np.arange(len(gridlineVerPos)) * 200
    logg("gridlineVerPos, compensated")
    logg(np.ndarray.__repr__(gridlineVerPos))

    f = scipy.interpolate.interp1d(
        targetDistance,
        gridlineVerPos,
        bounds_error=False,
        fill_value="extrapolate",
        assume_sorted=True,
    )
    targetpos = f(targetcali)
    posnow = crosshairY
    logg(f"targetpos{targetpos}, posnow{posnow}")

    # get mil interval
    gridlineHor, rangeHor, mil = getMilInterval(
        LineFilteredVer, crosshair, gridSearchWidth, logg
    )

    if logg.enable:
        rebuildMap = np.zeros_like(LineFilteredVer)
        rebuildMap[crosshair[0], :] = 1
        rebuildMap[:, crosshair[1]] = 1

        # calibration grid
        rebuildMap[gridlineVerPos.astype(np.int32), rangeVer[0] : rangeVer[1]] = 1

        # mil
        rebuildMap[rangeHor[0] : rangeHor[1], gridlineHor] = 1
        logg("rebuildMap", rebuildMap)

    ret = np.array((targetpos, posnow, mil))
    ret /= caliTableDetectionZoomRate
    return ret


def switchNightMode():
    Keyboard.KeyPress(win32con.VK_F6)


def adjustCaliberation(pidoutput):
    keycode2press = win32con.VK_PRIOR if pidoutput > 0 else win32con.VK_NEXT

    control = np.abs(pidoutput)
    if control < nonlinearCaliStart:
        control = 1 / nonlinearCaliStart * control**2  # make it more precise

    # # try if get improvement in the case of no response
    # for k in [win32con.VK_PRIOR, win32con.VK_NEXT]:
    #     Keyboard.KeyPress(k)

    Keyboard.KeyDown(keycode2press)
    PreciseSleep(control)
    Keyboard.KeyUp(keycode2press)
    return control


class LoadCalibrationOperator(StoppableThread):
    @GSBLogger.ExceptionLogged()
    def foo(self, targetcali):
        pid = PIDController(caliP, 0, caliD)
        ss = screenshoter()

        logg = SmallReportLogger(
            wtdmplogpath.format(
                time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()), "GetCali"
            ),
            enable=caliDbg,
        )

        iterNum = 0
        while True:
            if self.stopsignal:
                # forced stop
                logg(self.result)
                return
            logg(f"iter {iterNum}")
            try:
                # cali err in pixel
                caliresult = getNowCalibration(ss.shotbgr(), targetcali, logg)
            except BadCaliException:
                self.result = "BadCaliException"
                self.stopped = True
                logg(self.result)
                return

            targetpix, nowpix, mil = caliresult
            logg(f"targetpix{targetpix}, nowpix{nowpix}, mil{mil}")
            # print(targetpix,nowpix)
            if np.abs(targetpix - nowpix) <= autoCaliErr:
                self.result = "Great"
                self.stopped = True
                logg(self.result)
                return
            control = pid.update(targetpix - nowpix) * caliControlMul / mil
            logg(f"control {control}")
            # get the real control, but without direction
            control = adjustCaliberation(control)
            time.sleep(delayEveryCali)
            iterNum += 1


@dataclasses.dataclass
class WtdmpMainLogicResult:
    prompt: str
    succeed: bool


class wtdistmeaspy:
    """
    TODO
    reconstruct logic to make it of specificity
    """

    caliOperator = LoadCalibrationOperator(
        strategy_runonrunning=StoppableThread.StrategyRunOnRunning.stop_and_rerun
    )

    lastDistMeasResultStaged = ElementsOfMap(None, None, None, None, None)

    psLocked = False

    smallMapCollector = DataCollector(datacoll_smallmappath)

    def solveMapMainLogic(self):
        time.sleep(measdelay)  # for network delay

        # solve as successfully as possible
        for i in range(retryOnFailure):
            scr = screenshoter().shotbgr()
            scr = cutBottomRightMap(scr)

            # keep collecting
            if keepEveryMeasInRecord:
                ret = SolveMap_BottomRightSmallMap(
                    scr,
                    dbg=True,
                    dbglogpath=wtdmplogpath.format(
                        GetTimeString(),
                        "NormalTrace",
                    ),
                    dontGetPlottingScale=self.psLocked,
                )
            else:
                ret = SolveMap_BottomRightSmallMap(
                    scr,
                    dontGetPlottingScale=self.psLocked,
                )
            # not found
            if ret.ym.state.smetype == SMException.SolveMapResultType.NO_ERR:
                break
            time.sleep(retryDelay)

        def exceptionlist2str(el, spliter=None):
            if spliter is None:
                spliter = "\n"
            return spliter.join([e.__repr__() for e in el])

        exception: list[SMException] = []
        prompt = ""

        # check if fall back to last result
        def CheckAndReplaceIfNeeded(
            resultitem: SolveMapResultItem,
            val2replace: typing.Any,
            exceptionOnReplace: SMException,
        ):
            if resultitem.state.smetype != SMException.SolveMapResultType.NO_ERR:
                if val2replace is not None:
                    resultitem.result = val2replace
                    resultitem.err = 0
                    exception.append(exceptionOnReplace)
                else:
                    exception.append(resultitem.state)

        # ym is special, dont use staged one
        if ret.ym.state.smetype != SMException.SolveMapResultType.NO_ERR:
            exception.append(ret.ym.state)
        CheckAndReplaceIfNeeded(
            ret.playerpos,
            self.lastDistMeasResultStaged.playerpos,
            SMException(SMException.SolveMapResultType.using_last_playerpos),
        )
        CheckAndReplaceIfNeeded(
            ret.grid,
            self.lastDistMeasResultStaged.gridave,
            SMException(SMException.SolveMapResultType.using_last_grid),
        )
        # lock is priored than normally check and replace
        if self.psLocked:
            if self.lastDistMeasResultStaged.plottingscale is not None:
                ret.plottingscale.result = self.lastDistMeasResultStaged.plottingscale
                ret.plottingscale.err = 0
                # hint in exception will be done in secure check
            else:
                raise Exception("ps locked but no last ps")
        else:
            CheckAndReplaceIfNeeded(
                ret.plottingscale,
                self.lastDistMeasResultStaged.plottingscale,
                SMException(SMException.SolveMapResultType.using_last_ps),
            )

        if all([e.IsExceptionSafeToPass() for e in exception]):
            # able to go on

            # u wont need to strictly check if anything fatal, will u?
            def strictErrCheck():
                err = []

                if ret.playerpos.err > plerrreqstrict:
                    err.append(SMException(SMException.SolveMapResultType.SEC_PE))
                else:
                    self.lastDistMeasResultStaged.playerpos = ret.playerpos.result

                if ret.ym.err < ymerrreqstrict:
                    err.append(SMException(SMException.SolveMapResultType.SEC_YE))
                else:
                    self.lastDistMeasResultStaged.ympos = ret.ym.result

                if ret.grid.err > griderrreqstrict:
                    err.append(SMException(SMException.SolveMapResultType.SEC_GE))
                else:
                    self.lastDistMeasResultStaged.gridave = ret.grid.result

                if self.psLocked:
                    err.append(SMException(SMException.SolveMapResultType.SEC_PSLOCK))
                else:
                    if (
                        ret.plottingscale.result < plottingscalestrictlower
                        or ret.plottingscale.result > plottingscalestrictupper
                    ):
                        # something going wrong, either not found or digits lost,
                        # if less than 100 or more than 500
                        err.append(SMException(SMException.SolveMapResultType.SEC_PS))
                    else:
                        self.lastDistMeasResultStaged.plottingscale = (
                            ret.plottingscale.result
                        )

                return err  # keep dbglog unneeded

            exception += strictErrCheck()

            # calc
            ympos = np.array(ret.ym.result)
            playerpos = np.array(ret.playerpos.result)
            gridave = ret.grid.result
            plottingscale = ret.plottingscale.result
            distingrid = (
                np.sqrt(((ympos - playerpos) ** 2).sum()) / gridave
            )  # using unit in grid
            dist = distingrid * plottingscale

            refresult = ["%3d: %5d" % (r, int(distingrid * r + 0.5)) for r in reflist]

            prompt += "OK, dist=%.2f\n" % (dist)
            if len(exception) != 0:
                prompt += exceptionlist2str(exception, ",") + "\n"

            # got here anyway avoiding all the fatal ones
            # commit result
            self.lastDistMeasResultStaged.result = dist

            # todo: considering if i should automaticly calibrate

            i = 0
            while i < len(refresult):
                for j in range(3):
                    prompt += refresult[i] + ", "
                    i += 1
                    if i >= len(refresult):
                        break
                prompt += "\n"
            prompt += "dg=%.2f,ps=%d,pe=%.2f,ye=%.2f,ge=%.2f" % (
                distingrid,
                plottingscale,
                ret.playerpos.err,
                ret.ym.err,
                ret.grid.err,
            )
            solveSummary = True
        else:
            # fatal happended
            prompt += "Failed\n"
            prompt += exceptionlist2str(exception) + "\n"

            if collectFailDebugOutput:
                # resolve with debug config
                ret = SolveMap_BottomRightSmallMap(
                    scr,
                    dbg=True,
                    dbglogpath=wtdmplogpath.format(
                        GetTimeString(),
                        exceptionlist2str(exception, ", "),
                    ),
                )
            solveSummary = False

        if collectingSmallMap:
            self.smallMapCollector.save(scr)
        return WtdmpMainLogicResult(prompt, solveSummary)

    def freshPlottingScale(self):
        def SetPs(val):
            self.lastDistMeasResultStaged.plottingscale = val
            self.psLocked = True
            return "OK, ps=%d" % self.lastDistMeasResultStaged.plottingscale

        # try 8111
        try:
            ret = Port8111Cache().get(Port8111.QueryType.map_info)
            if ret is not None and ret.expectValid().valid:
                return SetPs(ret.grid_steps[0])
        except Port8111.FetchFailure:
            ...

        # try solve map
        # ret = SolveMap_BottomRightSmallMap(
        #     cutBottomRightMap(screenshoter().shotbgr()),
        #     dontGetPlottingScale=False,
        # )
        # if ret.plottingscale.state.smetype == SMException.SolveMapResultType.NO_ERR:
        #     return SetPs(ret.plottingscale.result)

        # bad
        return "bad fresh"
