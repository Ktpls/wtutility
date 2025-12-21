from utilitypack.util_solid import StoppableSomewhat
from utilitypack.cold.util_solid import LongDelay
from utilitypack.util_winkey import *
from shared.globalsys import *
import matplotlib.pyplot as plt
from .config.autofreshmap_configmap_importref import *
from .config.autofreshmap_config import *

MapSize = [648, 648]

dataCollector = DataCollector(mapAutoCollectionPath)


def signName2Path(name):
    return r"statesign/{}.png".format(name)


class StateSign(enum.Enum):
    hanger = "hanger"
    MissionCanceled = "MissionCanceled"
    LoadingMap = "LoadingMap"
    OK = "OK"
    Statistics = "Statistics"
    WarthunderMark = "WarthunderMark"


if resolution == "m1920x1080r1920x1080":
    # res1920x1080,uiscale75%
    standardMapSection = [286, 216, 934, 864]
    RenderResolutionZoomRate = 1.0
elif resolution == "m1920x1080r1280x720":
    # 1280x720,75%
    standardMapSection = [292, 218, 934, 861]
    RenderResolutionZoomRate = 1.5  # 1920/1280
else:
    raise NotImplementedError("unknown resolution")


@dataclasses.dataclass
class SignDetectorParam:
    path: str
    thresh: float = SignDetectorDefaultThresh
    mask: str = None
    zoomRate: float = None
    screenPreproc: typing.Callable[[np.ndarray], np.ndarray] = None


stateDetectorInfo = {
    StateSign.hanger: SignDetectorParam(
        path="hanger",
    ),
    StateSign.MissionCanceled: SignDetectorParam(
        path="MissionCanceled",
    ),
    StateSign.LoadingMap: SignDetectorParam(
        path="LoadingMap",
        screenPreproc=lambda scr: ccomma(
            h := scr.shape[0], w := scr.shape[1], scr[: h // 2, w // 2 : w * 3 // 4, :]
        ),
    ),
    StateSign.OK: SignDetectorParam(path="OK", thresh=0.195),
    StateSign.Statistics: SignDetectorParam(path="Statistics"),
    StateSign.WarthunderMark: SignDetectorParam(
        path="WarthunderMark",
        zoomRate=RenderResolutionZoomRate,
        screenPreproc=lambda scr: ccomma(
            w := scr.shape[1], scr[:100, w - 200 : w + 200, :]
        ),
    ),
}


def assetpath2realpath(ap):
    return os.path.join(afmassetroot, ap)


zfoo4matcher = ZFunc(zFuncPoint0, 0, zFuncPoint1, 1)


class MapImgComparator:
    """
    used for map detection.
    cuz i need special algorithm that can not be impled in matchtemplate()
    """

    @staticmethod
    def imagepreprocess(m, mask=None):
        # all preprocess defined in config done here
        if mask is not None:
            m = m * mask

        m = delBlueRed(m)

        # remove shadow on loading screen map
        # brightness = np.max(m, axis=2, keepdims=True)
        # m = m / (brightness + EPS)

        if subsampleddetection:
            # this would set [x,y,1] back to [x,y], so do it first
            m = cv.resize(
                m,
                None,
                fx=subsampleddetectionrate,
                fy=subsampleddetectionrate,
                interpolation=cv.INTER_AREA,
            )
        if singlechanneleddetection:
            m = np.average(m, axis=-1, keepdims=True)
        return m

    def __init__(
        self,
        path: str,
        thresh: float | None = None,
        maskpath: str | None = None,
    ):
        # for dbg output
        self.path = path

        path = assetpath2realpath(path)
        m = cv.imread(path)
        m = m.astype(np.float32) / 255
        if m.size == 0:
            raise Exception("loading matcher failed in {}".format(path))
        self.m = MapImgComparator.imagepreprocess(m)
        self.thresh = thresh  # optional thresh, for dynamic specified, if needed

        if maskpath is not None:
            m = assetpath2realpath(maskpath)
            m = cv.imread(m)
            self.mask = (m != 0).astype(np.float32)
        else:
            self.mask = None

    """
    channel can NOT be ignored in mscr.shape, that is like [x,y,c], where c can be 1
    depressing big error in few position
    """

    def matchSign_Z_ABSDIFF_NORMED(self, mscr):
        errAbs = np.sqrt(np.max(np.square(self.m - mscr), axis=(2,)))

        if useNonLightnessedErrorTolerence:

            def toNonLighted(m):
                return m / (np.mean(np.max(m, axis=2)) + EPS)

            mscrNonLighted = toNonLighted(mscr)
            selfMNonLighted = toNonLighted(self.m)
            errNonLighted = np.sqrt(
                np.max(np.square(selfMNonLighted - mscrNonLighted), axis=(2,))
            )
            err = (
                1 - NonLightnessedErrorRatio
            ) * errAbs + NonLightnessedErrorRatio * errNonLighted
        else:
            err = errAbs
        return np.average(
            zfoo4matcher(err),
            axis=(0, 1),
        )

    def detect(self, mscr, specifiedThresh=None):
        s = self.matchSign_Z_ABSDIFF_NORMED(mscr)
        GSBLogger().debug(f"{self.path} detecting: s={s}")
        thresh = Coalesce(specifiedThresh, self.thresh)
        return s < thresh


def threshedmatchtemplate(src, temp, mask, simu):
    matchresult = cv.matchTemplate(src, temp, cv.TM_CCOEFF_NORMED, mask=mask)
    matchresult = np.where(np.isnan(matchresult), 0, matchresult)
    matchresult = np.where(np.isinf(matchresult), 0, matchresult)
    matchresult = 1 - matchresult
    minval, maxval, minloc, maxloc = cv.minMaxLoc(matchresult)
    # print(minval)
    GSBLogger().debug(f"threshedmatchtemplate(): minval={minval}, simuthresh={simu}")
    return minloc if minval <= simu else None


class UnlocatedFullScreenImgMatcher:

    def __init__(
        self,
        path,
        thresh=None,
        mask=None,
        zoomRate=None,
        screenPreproc: typing.Callable[[np.ndarray], np.ndarray] = None,
    ):
        path = assetpath2realpath(path)
        m = cv.imread(path)
        if m.size == 0:
            raise Exception("loading matcher failed in {}".format(path))
        if zoomRate is not None:
            m = cv.resize(m, None, fx=zoomRate, fy=zoomRate)
        self.m = m
        self.thresh = thresh  # optional thresh, for dynamic specified, if needed
        self.screenPreproc = screenPreproc

        # for dbg output
        self.path = path

        if mask is not None:
            m = assetpath2realpath(mask)
            m = cv.imread(m)
            self.mask = m
        else:
            self.mask = None

    def find(self, mscr, specifiedThresh=None):
        thresh = Coalesce(specifiedThresh, self.thresh)
        if self.screenPreproc:
            mscr = self.screenPreproc(mscr)
        ret = threshedmatchtemplate(mscr, self.m, self.mask, thresh)
        GSBLogger().debug(
            f"{self.path} UnlocatedFullScreenImgMatcher detecting, ret={ret}"
        )
        return ret

    def detect(self, mscr, specifiedThresh=None):
        return self.find(mscr, specifiedThresh) is not None


class detector:
    def __init__(self, para):
        pass

    def detect(self, mscr):
        pass


def segmentIconRed(m):
    # m in hsv format
    hueshift = 180
    return cv.inRange(
        m + np.array([hueshift, 0, 0]).reshape([1, 1, -1]),
        np.array([hueshift - 10, 0.70, 0.45], np.float32),
        np.array([hueshift + 10, 1, 1], np.float32),
    )


def segmentIconBlue(m):
    # m in hsv format
    return cv.inRange(
        m,
        np.array([220, 0.70, 0.45], np.float32),
        np.array([230, 1, 1], np.float32),
    )


def delBlueRed(m):
    hsv = cv.cvtColor(m, cv.COLOR_BGR2HSV)
    redPart = np.expand_dims(segmentIconRed(hsv).astype(np.float32), axis=2) / 255
    bluePart = np.expand_dims(segmentIconBlue(hsv).astype(np.float32), axis=2) / 255
    m = m * (1 - bluePart) * (1 - redPart)
    return m


def getMapSpawnCenter(m, spawntype="blue"):
    spawnfilter = {"red": segmentIconRed, "blue": segmentIconBlue}
    hsv = cv.cvtColor(m, cv.COLOR_BGR2HSV)
    m = spawnfilter[spawntype](hsv)
    X = np.reshape(np.arange(m.shape[1]), [1, -1])
    Y = np.reshape(np.arange(m.shape[0]), [-1, 1])
    center = [(C * m).sum() / (m.sum() + EPS) for C in [X, Y]]
    return np.array(center)


def mapname2assetpath(mapname):
    return "map/" + mapname + ".png"


def cutmap(m):
    x1, y1, x2, y2 = standardMapSection
    mm = m[y1:y2, x1:x2]
    mm = cv.resize(mm, MapSize, interpolation=cv.INTER_LINEAR)
    return mm


def zoompointimg(m):
    mattr = np.array(
        [[RenderResolutionZoomRate, 0, 0], [0, RenderResolutionZoomRate, 0]],
        dtype=np.float32,
    )
    return cv.warpAffine(
        m,
        mattr,
        np.round(np.flip(m.shape[:2]) * RenderResolutionZoomRate).astype(np.int32),
    )


Asset4PointDetection_Template = {
    t: zoompointimg(
        cv.imread(assetpath2realpath(signName2Path(t))).astype(np.float32) / 255
    )
    for t in ["A", "B", "C", "redA", "redB", "blueA", "blueB"]
}
Asset4PointDetection_Pointmask = zoompointimg(
    cv.imread(assetpath2realpath(signName2Path("zonemask"))).astype(np.float32) / 255
)[:, :, 0]


class MapDetectorImpled(detector):
    def __init__(self, param: MapDetector):
        """
        the so called path is actually map name, by which mapname2assetpath is needed
        after that assetpath2realpath will be done in matcher
        """
        self.map = param.map
        self.foo = param.foo
        if self.map is not None:
            map = NormalizeIterableOrSingleArgToIterable(self.map)
            map = [mapname2assetpath(mr) for mr in map]
            self.mtc = [
                MapImgComparator(mr, standardMapMatchThreshold, None) for mr in map
            ]
        else:
            self.mtc = []

        self.foo = compile(self.foo, "", "exec")

    def detect(self, mscr, mscrpreproced):

        def detectMapShape(mtcid=0, thresh=None):
            ret = self.mtc[mtcid].detect(mscrpreproced, thresh)
            GSBLogger().debug(f"MapShapeResult={ret}")
            return ret

        def distance(a, b):
            err = np.sqrt(((a - b) ** 2).sum())
            GSBLogger().debug(f"dist={err}")
            return err

        def detectSpawn():
            center = getMapSpawnCenter(mscr)
            GSBLogger().debug(f"spawn={center}")
            return center

        def spawnAround(point, err=None):
            if err is None:
                err = standardSpawnCenterError
            return distance(detectSpawn(), point) < err

        def selectPoint(ptype=None, ppos=None, err=None):
            if ptype is None:
                # fall back to all
                ptype = [k for k in Asset4PointDetection_Template.keys()]
            ptype = NormalizeIterableOrSingleArgToIterable(ptype)
            result = [
                threshedmatchtemplate(
                    mscr,
                    Asset4PointDetection_Template[t],
                    Asset4PointDetection_Pointmask,
                    detectpointsimilarity,
                )
                for t in ptype
            ]
            result = [r for r in result if r is not None]

            if ppos is not None:
                if err is None:
                    err = standardPointSelectorError
                result = [
                    r for r in result if distance(np.array(r), np.array(ppos)) < err
                ]

            return len(result) != 0

        def singlePoint(ppos=None):
            return selectPoint(ptype="A", ppos=ppos) and not selectPoint(ptype="B")

        def selectBattleMode():
            return selectPoint(ptype="redA") or selectPoint(ptype="redB")

        retVal = None

        def ret(val):
            nonlocal retVal
            retVal = val

        try:
            exec(self.foo)
            if retVal is None:
                raise ValueError("nothing returned")
            return retVal
        except Exception as e:
            traceback.print_exc()
            raise e


class AfmAsset:
    def __init__(self, configModuleLike):
        whitelistedmap: list[str] = configModuleLike.whitelistedmap
        blacklistedmap: list[str] = configModuleLike.blacklistedmap
        specialmapdetectors: dict[str, MapDetector] = (
            configModuleLike.specialmapdetectors
        )

        whitelistedmap = Deduplicate(whitelistedmap)
        detectors = {
            **{
                m: MapDetectorImpled(
                    specialmapdetectors[m]
                    if m in specialmapdetectors
                    else MapDetector(map=m, foo="ret(detectMapShape())")
                )
                for m in whitelistedmap
            }
        }
        if len(blacklistedmap) != 0:
            detectAllMaps = " and ".join(
                [f"(not detectMapShape(mtcid={i}))" for i in range(len(blacklistedmap))]
            )
            detectors["blacklisted"] = MapDetectorImpled(
                MapDetector(map=blacklistedmap, foo=f"ret({detectAllMaps})")
            )
        self.mapDetector = detectors
        self.stateDetector = {
            k: UnlocatedFullScreenImgMatcher(
                path=signName2Path(v.path),
                thresh=v.thresh,
                mask=v.mask,
                zoomRate=v.zoomRate,
                screenPreproc=v.screenPreproc,
            )
            for k, v in stateDetectorInfo.items()
        }


def leaveButton():
    time.sleep(1)
    # move after click for not blocking next time detection
    moveto([0, 0])


class freshAMap(MessagedThread):
    @ExtendEnum(MessagedThread.MessageType)
    class MessageType(aenum.Enum):
        acceptMap = 1

    class AFMAborted(BaseException): ...

    @GSBLogger.ExceptionLogged()
    def run(self):
        class KeepDetectingScreen:

            class NextStepAction(enum.Enum):
                finish = 0
                continuee = 1
                abort = 2

            @staticmethod
            def do(
                successCond: typing.Callable[[np.ndarray], bool],
                sleeptime=0.5,
            ) -> bool:
                """
                successCond: bool(*foo)(Mat& screen), with return of if detected
                cancelCond: same but return true if cancel detection
                ret: true if successCond else false on cancelCond
                """
                while True:
                    scr = shot()
                    match successCond(scr):
                        case KeepDetectingScreen.NextStepAction.finish:
                            return True
                        case KeepDetectingScreen.NextStepAction.continuee:
                            pass
                        case KeepDetectingScreen.NextStepAction.abort:
                            return False
                    time.sleep(sleeptime)

        # init
        aa = AfmAsset(autofreshmap_configmap)
        stateDetector, mapDetector = aa.stateDetector, aa.mapDetector
        assert stateDetector is not None and mapDetector is not None
        ss = screenshoter(0)
        wifi = WifiRefresher()

        def shot():
            shot = ss.shotbgr()
            if saveScreenShot:
                if random.uniform(0, 1) < saveRate:
                    savemat(shot, name=GetTimeString(), path=logscreenpath)
            return ss.shotbgr()

        while True:
            GSBLogger().debug("try matching")

            # detect loading map
            loadingscreen = None

            GSBLogger().debug(str("detecting loading map"))

            Rhythms.Notify.play()

            enteredMatchButNotShowingMap = False
            embnsmPersistTimer = perf_statistic(False)

            def detectLoadingMap(scr):
                """
                if detect loading map, go on
                else if detect WarthunderMark but not showing loading map, keep observing
                if loading map still undetected after enteredMatchButNotShowingMap_persistedTime, abandon this pass
                """
                assert stateDetector is not None
                while not self.mq.empty():
                    match self.mq.get().type:
                        case freshAMap.MessageType.stop:
                            # canceled
                            # press asap
                            scr = shot()
                            if not any(
                                [
                                    stateDetector[d].detect(scr)
                                    for d in [
                                        StateSign.hanger,
                                        StateSign.MissionCanceled,
                                    ]
                                ]
                            ):
                                # clear matching state
                                Keyboard.KeyPress(win32con.VK_ESCAPE)
                            Rhythms.Cancel.play()
                            raise freshAMap.AFMAborted()
                if stateDetector[StateSign.LoadingMap].detect(scr):
                    nonlocal loadingscreen
                    loadingscreen = scr
                    return KeepDetectingScreen.NextStepAction.finish
                if stateDetector[StateSign.WarthunderMark].detect(scr):
                    if not embnsmPersistTimer.isRunning():
                        embnsmPersistTimer.start()
                    GSBLogger().debug(
                        f"only WarthunderMark found, persisted {embnsmPersistTimer.time()}"
                    )
                else:
                    embnsmPersistTimer.stop().clear()
                if (
                    embnsmPersistTimer.time()
                    >= enteredMatchButNotShowingMap_persistedTime
                ):
                    nonlocal enteredMatchButNotShowingMap
                    enteredMatchButNotShowingMap = True
                    return KeepDetectingScreen.NextStepAction.finish
                if any(
                    [
                        stateDetector[d].detect(scr)
                        for d in [
                            StateSign.hanger,  # for click not succeed
                            StateSign.MissionCanceled,
                            StateSign.OK,
                        ]
                    ]
                ):
                    Keyboard.KeyPress(win32con.VK_RETURN)
                    time.sleep(DelayAfterClickEnter)
                    return KeepDetectingScreen.NextStepAction.continuee
                return KeepDetectingScreen.NextStepAction.continuee

            KeepDetectingScreen.do(
                successCond=detectLoadingMap,
                sleeptime=LoadingMapDetectionInterval,
            )

            if enteredMatchButNotShowingMap:
                Rhythms.BadNotify.asyncPlay()
                GSBLogger().debug("enteredMatchButNotShowingMap")
            else:
                Rhythms.Notify.asyncPlay()
                GSBLogger().debug("loading map")
                loadingscreen_u8 = cutmap(loadingscreen)
                loadingscreen = loadingscreen_u8.astype(np.float32) / 255
                loadingscreenProced = MapImgComparator.imagepreprocess(loadingscreen)
                # name,detector

                sortedMapDetectorKeys = list(mapDetector.keys())
                sortedMapDetectorKeys.sort()
                found = False
                for n in sortedMapDetectorKeys:
                    d = mapDetector.get(n)
                    # done this by hand to get 2 times faster
                    if d.detect(loadingscreen, loadingscreenProced):
                        found = True
                        break
                if mapAutoCollection:
                    dataCollector.save(loadingscreen)
                if found:
                    GSBLogger().debug(f"{n}")
                    Rhythms.Success.play()
                    GSBLogger().debug("good map")
                    return True

            # detected banned map
            wifi.setOff()
            Rhythms.Notify.play()
            GSBLogger().debug("bad map")

            # detect game canceled, which is if in hanger
            gameCanceledPerfStat = perf_statistic(True)
            shouldStopAfterGameCanceld = False

            def detectGameCanceled(scr):
                while not self.mq.empty():
                    match self.mq.get().type:
                        case freshAMap.MessageType.stop:
                            """
                            task canceld, do the cleanning
                            set on wifi after fully exit the game match
                            """
                            Rhythms.Cancel.play()
                            nonlocal shouldStopAfterGameCanceld
                            shouldStopAfterGameCanceld = True
                            GSBLogger().debug("stop recieved")
                        case freshAMap.MessageType.acceptMap:
                            wifi.setOn()
                            Rhythms.Success.play()
                            GSBLogger().debug("accepted as good map")
                            raise freshAMap.AFMAborted()
                # sleep at least some time
                if gameCanceledPerfStat.time() < minDelayAfterDisconnected:
                    return KeepDetectingScreen.NextStepAction.continuee
                assert stateDetector is not None
                if not stateDetector[StateSign.WarthunderMark].detect(scr):
                    return KeepDetectingScreen.NextStepAction.finish
                return KeepDetectingScreen.NextStepAction.continuee

            KeepDetectingScreen.do(
                successCond=detectGameCanceled,
                sleeptime=2,
            )
            if shouldStopAfterGameCanceld:
                GSBLogger().debug("stopped afm")
                wifi.setOn()
                raise freshAMap.AFMAborted()

            wifi.setOn()
            Rhythms.Notify.play()
            GSBLogger().debug("canceled")
            # for not enter game too soon after wifi on
            wifonitime = time.time()
            SleepUntil(lambda: time.time() - wifonitime > setonwifirecoverthresh, 1)


class ApproximateStandardizationGuide:
    @dataclasses.dataclass
    class GuideItem:
        pattern: str | re.Pattern
        replacement: str

        def do(self, s: str) -> str:
            """
            Perform the replacement operation on the given string.

            Args:
                s (str): The input string to be modified.

            Returns:
                str: The modified string after performing the replacement.
            """
            return re.sub(self.pattern, self.replacement, s)

    def __init__(self, guideSourceCode: str):
        """
        Initialize the ApproximateStandardizationGuide with the given guide source code.

        Args:
            guideSourceCode (str): The source code of the guide.
        """
        self.guideSourceCode = guideSourceCode
        guideitem: list[ApproximateStandardizationGuide.GuideItem] = []
        for g in guideSourceCode.split("\n"):
            if len(g) == 0:
                continue
            if g.startswith("//"):
                continue
            spliter = "->"
            splitpos = g.find(spliter)
            if splitpos < 0:
                continue

            guideitem.append(
                ApproximateStandardizationGuide.GuideItem(
                    re.compile(g[:splitpos], re.MULTILINE), g[splitpos + len(spliter) :]
                )
            )
        self.guideitem = guideitem

    def do(self, s: str) -> str:
        """
        Perform the standardization process on the given string.

        Args:
            s (str): The input string to be standardized.

        Returns:
            str: The standardized string.
        """
        for g in self.guideitem:
            s = g.do(s)
        return s.strip()


@dataclasses.dataclass
class VehicleInfo:
    name: str
    pattern: re.Pattern

    @staticmethod
    def compile(
        sourceCode: str, asg: ApproximateStandardizationGuide
    ) -> list["VehicleInfo"]:
        ret = []
        for t in sourceCode.split("\n"):
            if len(t) == 0:
                continue
            if t.startswith("//"):
                continue
            ret.append(VehicleInfo(t, re.compile(asg.do(t))))
        return ret

    @dataclasses.dataclass
    class MatchResult:
        line: int
        playerVehicle: str
        vehicleInfo: str

    @staticmethod
    def matchPlayerVehicleListAndVehicleInfoList(
        players: list[str], vi: list["VehicleInfo"]
    ):
        ret: list[VehicleInfo.MatchResult] = []
        for l, p in enumerate(players):
            for v in vi:
                if re.match(v.pattern, p) is not None:
                    ret.append(VehicleInfo.MatchResult(l, p, v.name))
        return ret

    @staticmethod
    def detectAnyInOutputOfTesseract(
        players: str,
        vi: list["VehicleInfo"],
        asg: ApproximateStandardizationGuide,
    ):
        playerlist = [asg.do(t) for t in players.split("\n")]
        ret = VehicleInfo.matchPlayerVehicleListAndVehicleInfoList(playerlist, vi)
        if len(ret) == 0:
            print("nothing matched")
        else:
            print(
                "\n".join(
                    [f"line {r.line}\t{r.playerVehicle}\t{r.vehicleInfo}" for r in ret]
                )
            )
        return len(ret) != 0


def FreshBr(BannedVehicleInfoSourceCode, WantedVehicleInfoSourceCode):
    # cant distinguish MiG-17 AS with MiG-17 mentioned in source code
    # and wanted vehicles may be brought by some players as squad
    # init
    import pytesseract.pytesseract as pytesseract

    pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def shot():
        return ss.shotbgr()

    # wait until true
    def keepdetecting(foo: typing.Callable[[np.ndarray], bool], sleeptime=0.5) -> bool:
        while True:
            scr = shot()
            if foo(scr):
                return True
            time.sleep(sleeptime)

    def moveMouseAway():
        moveto((0, 0))
        mouse.click(0)

    aa = AfmAsset(autofreshmap_configmap)
    stateDetector, mapDetector = aa.stateDetector, aa.mapDetector

    ss = screenshoter(0)
    asg = ApproximateStandardizationGuide(
        r"""
//confusing
[A4]->A
[Ss5]->S
[0Oo]->O
[Cc]->C
[Ili1Jj7T]->I
[Kk]->K
[Mm]->M
[Pp]->P
[UuVv]->U
[Ww]->W
[Xx]->X
[Zz]->Z
//nation marks
^O->
^#->
//unexpected
[^A-Za-z0-9\(\)\n]->
"""[
            1:-1
        ],
    )

    IDontWannaSeeThem = VehicleInfo.compile(BannedVehicleInfoSourceCode, asg)
    IWannaSeeThem = VehicleInfo.compile(WantedVehicleInfoSourceCode, asg)

    while True:
        """
        try start matching
        may found crew locked
        """

        def detectStartMatch(scr):
            assert stateDetector is not None
            sp = stateDetector[StateSign.Statistics].find(scr)
            if sp is not None:
                moveto(sp)
                time.sleep(1)
                mouse.movr(*(10, 10))
                time.sleep(1)
                mouse.click(0)
                time.sleep(1)
                return True
            if stateDetector[StateSign.hanger].detect(scr) or stateDetector[
                StateSign.MissionCanceled
            ].detect(scr):
                # piority lower than statistics, so the to battle button on spawn scence wont confuse
                Keyboard.KeyPress(win32con.VK_RETURN)
                return False
            if stateDetector[StateSign.OK].detect(scr):
                Keyboard.KeyPress(win32con.VK_ESCAPE)
                LongDelay(15)
                return False
            return False

        moveMouseAway()
        keepdetecting(detectStartMatch, sleeptime=10)

        class DetectPlayerVehicleResult(enum.Enum):
            unset = 0
            good = 1
            bad = 2
            timeout = 3

        detectPlayerVehicleResult = DetectPlayerVehicleResult.unset
        timer = perf_statistic(startnow=True)

        def detectPlayerVehicleList(scr):
            nonlocal detectPlayerVehicleResult, timer
            # 400,330 -> 600,700
            playerlistLeftTop = [400, 330]
            playerlistRightDown = [600, 700]
            # actually player vehicles
            players = scr[
                playerlistLeftTop[1] : playerlistRightDown[1],
                playerlistLeftTop[0] : playerlistRightDown[0],
            ]
            players = pytesseract.image_to_string(players)
            print(players)
            print("bads")
            bads = VehicleInfo.detectAnyInOutputOfTesseract(
                players, IDontWannaSeeThem, asg
            )
            print("goods")
            goods = VehicleInfo.detectAnyInOutputOfTesseract(
                players, IWannaSeeThem, asg
            )
            # bads priored
            if bads:
                detectPlayerVehicleResult = DetectPlayerVehicleResult.bad
                return True
            if goods:
                detectPlayerVehicleResult = DetectPlayerVehicleResult.good
                return True
            if timer.time() >= AFM_FRESHBR_VEHICLE_LIST_TIMEOUT:
                detectPlayerVehicleResult = DetectPlayerVehicleResult.timeout
                return True

            return False

        moveMouseAway()
        keepdetecting(detectPlayerVehicleList, sleeptime=5)

        if detectPlayerVehicleResult == DetectPlayerVehicleResult.good:
            # good
            Rhythms.Success.play()
            import subprocess

            files = AllFileIn(musicPath)
            files = [
                f
                for f in files
                if (
                    (extpos := str.rfind(f, ".")) != -1
                    and f[extpos + 1 :] in ["mp3", "flac"]
                )
            ]
            f = files[np.random.choice(len(files))]
            print(f)
            subprocess.call([player, f])
            break
        elif (
            detectPlayerVehicleResult == DetectPlayerVehicleResult.bad
            or detectPlayerVehicleResult == DetectPlayerVehicleResult.timeout
        ):
            # bad
            Rhythms.BadNotify.play()
        elif detectPlayerVehicleResult == DetectPlayerVehicleResult.unset:
            raise Exception("detectPlayerVehicleResult is unset")

        KEY_OP_INTERVAL = 0.3
        # bad
        # exit statistics
        Keyboard.KeyPress(win32con.VK_ESCAPE)
        time.sleep(KEY_OP_INTERVAL)

        # to menu
        Keyboard.KeyPress(win32con.VK_ESCAPE)
        time.sleep(KEY_OP_INTERVAL)

        moveto((0, 0))

        # select return to hanger
        for i in range(5):
            Keyboard.KeyPress(win32con.VK_DOWN)
            time.sleep(KEY_OP_INTERVAL)

        # click it
        Keyboard.KeyPress(win32con.VK_RETURN)
        time.sleep(KEY_OP_INTERVAL)

        # select yes
        Keyboard.KeyPress(win32con.VK_LEFT)
        time.sleep(KEY_OP_INTERVAL)

        # click
        Keyboard.KeyPress(win32con.VK_RETURN)
        time.sleep(KEY_OP_INTERVAL)

        moveMouseAway()
        mouse.click(0)

        # exit settlement screen
        def detectMissionCanceled(scr):
            assert stateDetector is not None
            if stateDetector[StateSign.MissionCanceled].detect(scr):
                Keyboard.KeyPress(win32con.VK_ESCAPE)
                return True
            return False

        keepdetecting(detectMissionCanceled)

        LongDelay(5 * 60)
