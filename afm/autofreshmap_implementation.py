from logging import exception

from utilitypack.utility import *
from keyshortcut.gameinput import *
from .autofreshmap_config import *
from .autofreshmap_configmap_importref import *


def signName2Path(name):
    return r"statesign/{}.png".format(name)


stateDetectorInfo = {
    "hanger": {
        "path": signName2Path("hanger"),
    },
    "MissionCanceled": {
        "path": signName2Path("MissionCanceled"),
    },
    "LoadingMap": {
        "path": signName2Path("LoadingMap"),
    },
    "OK": {"path": signName2Path("OK"), "thresh": 0.195},
    "Statistics": {"path": signName2Path("Statistics")},
}

if resolution == "m1920x1080r1920x1080":
    # res1920x1080,uiscale75%
    standardMapLeftTopPoint = [286, 216]
    pointtemplatezoomrate = 1.0
elif resolution == "m1920x1080r1366x768":
    # 1366x768,75%
    standardMapLeftTopPoint = [294, 221]
    pointtemplatezoomrate = 1.4  # 1920/1366
elif resolution == "m1920x1080r1280x720":
    # 1280x720,75%
    standardMapLeftTopPoint = [292, 218]
    pointtemplatezoomrate = 1.5  # 1920/1280
else:
    raise NotImplementedError("unknown resolution")

if dbglog:
    if log2file:
        logg = logger(
            os.path.join(
                afmassetroot,
                rf'log\{ time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}.log',
            )
        )

        def allchanneloutput(s):
            logg(s)
            print(s)

    else:
        logg = None

        def allchanneloutput(s):
            print(s)

else:

    def allchanneloutput(s):
        pass


def assetpath2realpath(ap):
    return os.path.join(afmassetroot, ap)


zfoo4matcher = ZFunc(10, 0, 20, 1)


class FixedPositionImgMatcher:
    """
    used for map detection.
    cuz i need special algorithm that can not be impled in matchtemplate()
    """

    @staticmethod
    def imagepreprocess(m, mask=None):
        # all preprocess defined in config done here
        if mask is not None:
            m = m * mask
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
            # cvtColor cant process float output by subsampling
            m = m.astype("uint8")
            m = cv.cvtColor(m, cv.COLOR_BGR2GRAY)
            m = m.reshape(m.shape + tuple([1]))  # in accordance to multi channeled
        return m.astype("float")  # for matching

    def __init__(
        self,
        leftTop: typing.List,
        path: str,
        thresh: float | None = None,
        maskpath: str | None = None,
    ):
        # for dbg output
        self.path = path

        path = assetpath2realpath(path)
        m = cv.imread(path)
        if m.size == 0:
            raise Exception("loading matcher failed in {}".format(path))
        self.pointlt = np.array(leftTop)
        self.pointrd = self.pointlt + np.flip(m.shape[:2])
        self.m = FixedPositionImgMatcher.imagepreprocess(m)
        self.thresh = thresh  # optional thresh, for dynamic specified, if needed

        if maskpath is not None:
            m = assetpath2realpath(maskpath)
            m = cv.imread(m)
            self.mask = m
        else:
            self.mask = None

    def cutroi(self, m):
        return m[
            self.pointlt[1] : self.pointrd[1], self.pointlt[0] : self.pointrd[0], :
        ]

    """
    channel can NOT be ignored in mscr.shape, that is like [x,y,c], where c can be 1
    depressing big error in few position
    """

    def matchSign_Z_ABSDIFF_NORMED(self, mscr):
        mscr = FixedPositionImgMatcher.imagepreprocess(mscr)
        return zfoo4matcher(np.sqrt(np.square(self.m - mscr).mean(axis=(2,)))).mean(
            axis=(0, 1)
        )

    def detect(self, mscr, specifiedThresh=None, cutRequired=True):
        if cutRequired:
            mscr = self.cutroi(mscr)
        s = self.matchSign_Z_ABSDIFF_NORMED(mscr)
        if dbglog:
            allchanneloutput(f"{self.path} detecting: s={s}")
        thresh = specifiedThresh if specifiedThresh is not None else self.thresh
        return s < thresh

    def getsignpointlt(self):
        return self.pointlt

    def getsignpointrd(self):
        return self.pointrd

    def getsigncenter(self):
        return 0.5 * (self.pointlt + self.pointrd)


def threshedmatchtemplate(src, temp, mask, simu):
    matchresult = 1 - cv.matchTemplate(src, temp, cv.TM_CCOEFF_NORMED, mask=mask)
    minval, maxval, minloc, maxloc = cv.minMaxLoc(matchresult)
    # print(minval)
    if dbglog:
        allchanneloutput(f"threshedmatchtemplate(): minval={minval}, simuthresh={simu}")
    return minloc if minval <= simu else None


class UnlocatedFullScreenImgMatcher:
    def __init__(self, path, thresh=None, mask=None):
        path = assetpath2realpath(path)
        m = cv.imread(path)
        if m.size == 0:
            raise Exception("loading matcher failed in {}".format(path))
        self.m = m
        self.thresh = thresh  # optional thresh, for dynamic specified, if needed

        # for dbg output
        self.path = path

        if mask is not None:
            m = assetpath2realpath(mask)
            m = cv.imread(m)
            self.mask = m
        else:
            self.mask = None

    def find(self, mscr, specifiedThresh=None):
        thresh = specifiedThresh if specifiedThresh is not None else self.thresh
        ret = threshedmatchtemplate(mscr, self.m, self.mask, thresh)
        if dbglog:
            allchanneloutput(
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


class signdetector(UnlocatedFullScreenImgMatcher):
    def __init__(self, path, thresh=0.27, mask=None):
        super().__init__(path, thresh, mask)


def getMapSpawnCenter(m, spawntype="blue"):
    def spawnfilter_red(m):
        return cv.inRange(
            m, hsv2opencv8bithsv([0, 70, 40]), hsv2opencv8bithsv([10, 100, 100])
        )

    def spawnfilter_blue(m):
        return cv.inRange(
            m, hsv2opencv8bithsv([220, 70, 40]), hsv2opencv8bithsv([230, 100, 100])
        )

    spawnfilter = {"red": spawnfilter_red, "blue": spawnfilter_blue}
    m = cv.cvtColor(m, cv.COLOR_BGR2HSV)
    m = spawnfilter[spawntype](m)
    X = np.arange(m.shape[1])
    Y = np.arange(m.shape[0])
    XY = np.meshgrid(X, Y)
    center = [(C * m).sum() / (m.sum() + 0.01) for C in XY]
    return np.array(center)


def mapname2assetpath(mapname):
    return "map/" + mapname + ".png"


def cutmap(m):
    pointlt = np.array(standardMapLeftTopPoint)
    pointrd = pointlt + np.array([648, 648])
    mm = m[pointlt[1] : pointrd[1], pointlt[0] : pointrd[0]]
    return mm


def zoompointimg(m):
    mattr = np.array(
        [[pointtemplatezoomrate, 0, 0], [0, pointtemplatezoomrate, 0]], dtype=np.float32
    )
    return cv.warpAffine(
        m,
        mattr,
        np.round(np.flip(m.shape[:2]) * pointtemplatezoomrate).astype(np.int32),
    )


Asset4PointDetection_Template = {
    t: zoompointimg(cv.imread(assetpath2realpath(signName2Path(t))))
    for t in ["A", "B", "C", "redA", "redB", "blueA", "blueB"]
}
Asset4PointDetection_Pointmask = zoompointimg(
    cv.imread(assetpath2realpath(signName2Path("zonemask")))
)[:, :, 0]


class MapDetectorImpled(detector, MapDetector):
    def __init__(self, para: MapDetector):
        super().__init__(para)
        """
        the so called path is actually map name, by which mapname2assetpath is needed
        after that assetpath2realpath will be done in matcher
        """
        if para.map is not None:
            map = NormalizeIterableOrSingleArgToIterable(para.map)
            map = [mapname2assetpath(mr) for mr in map]
            self.mtc = [
                FixedPositionImgMatcher(
                    standardMapLeftTopPoint, mr, standardMapMatchThreshold, None
                )
                for mr in map
            ]
        else:
            self.mtc = []

        self.foo = para.foo

    def detect(self, mscr):
        mapcut = cutmap(mscr)

        def detectMapShape(mtcid=0, thresh=None):
            ret = self.mtc[mtcid].detect(mscr, thresh)
            allchanneloutput(f"MapShapeResult={ret}")
            return ret

        def distance(a, b):
            err = np.sqrt(((a - b) ** 2).sum())
            allchanneloutput(f"dist={err}")
            return err

        def detectSpawn():
            center = getMapSpawnCenter(mapcut)
            allchanneloutput(f"spawn={center}")
            return center

        def spawnAround(point, err=None):
            if err is None:
                err = standardSpawnCenterError
            return distance(detectSpawn(), point) < err

        def selectPoint(ptype=None, ppos=None, err=None):
            if ptype is None:
                # fall back to all
                ptype = [k for k in Asset4PointDetection_Template.keys()]
            ptype=NormalizeIterableOrSingleArgToIterable(ptype)
            result = [
                threshedmatchtemplate(
                    mapcut,
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
            if ret is None:
                raise ValueError("nothing returned")
            return retVal
        except Exception as e:
            traceback.print_exc()
            raise e


def maplist2detectorlist(ml):
    ml = deduplicate(ml)
    dl = {
        m: MapDetectorImpled(
            specialmapdetectors[m]
            if m in specialmapdetectors
            else MapDetector(map=m, foo="ret(detectMapShape())")
        )
        for m in ml
    }
    return dl


whitelistedmapdetector = None
stateDetector = None


def loadAssetsNeeded4FreshAMap():
    global whitelistedmapdetector, stateDetector
    whitelistedmapdetector = maplist2detectorlist(whitelistedmap)
    stateDetector = {k: signdetector(**v) for k, v in stateDetectorInfo.items()}
    return whitelistedmapdetector, stateDetector


def leaveButton():
    sleep(1)
    # move after click for not blocking next time detection
    moveto([0, 0])


class freshAMap(StoppableThread):
    def foo(self):
        """
        successCond: bool(*foo)(Mat& screen), with return of if detected
        cancelCond: same but return true if cancel detection
        ret: true if successCond else false on cancelCond
        """

        def KeepDetecting(
            successCond: typing.Callable[[np.ndarray], bool],
            cancelCond: typing.Callable[[np.ndarray], bool] | None = None,
            sleeptime=0.5,
        ) -> bool:
            while True:
                scr = shot()
                # respond cancel first
                if cancelCond and cancelCond(scr):
                    return False
                if successCond(scr):
                    return True
                sleep(sleeptime)

        # init
        loadAssetsNeeded4FreshAMap()
        assert stateDetector is not None and whitelistedmapdetector is not None
        ss = screenshoter(0)
        wifi = WifiRefresher()

        def shot():
            shot = ss.shotbgr()
            if saveScreenShot:
                if random.uniform(0, 1) < saveRate:
                    savemat(shot, name=GetTimeString(), path=logscreenpath)
            return ss.shotbgr()

        while True:
            allchanneloutput("try matching")

            # detect loading map
            loadingscreen = None

            allchanneloutput(str("detecting loading map"))

            Rhythms.Notify.play()

            def detectLoadingMap(scr):
                assert stateDetector is not None
                if stateDetector["LoadingMap"].detect(scr):
                    nonlocal loadingscreen
                    loadingscreen = scr
                    return True
                if any(
                    [
                        stateDetector[d].detect(scr)
                        for d in [
                            "hanger",  # for click not succeed
                            "MissionCanceled",
                            "OK",
                        ]
                    ]
                ):
                    press(win32con.VK_RETURN)
                    return False
                return False

            if not KeepDetecting(
                successCond=detectLoadingMap,
                cancelCond=lambda src: self.timeToStop(),
                sleeptime=1,
            ):
                # canceled
                # press asap
                scr = shot()
                if not any(
                    [
                        stateDetector[d].detect(scr)
                        for d in [
                            "hanger",
                            "MissionCanceled",
                        ]
                    ]
                ):
                    # clear matching state
                    press(win32con.VK_ESCAPE)
                Rhythms.Cancel.play()
                return False

            Rhythms.Notify.play()
            allchanneloutput("loading map")

            # determine if map desired
            ret = False
            # name,detector
            for n, d in whitelistedmapdetector.items():
                # done this by hand to get 2 times faster
                if d.detect(loadingscreen):
                    allchanneloutput(f"{n}")
                    ret = True
                    break

            allchanneloutput(str(ret))
            if ret:
                # enter game
                Rhythms.Success.play()
                allchanneloutput("good map")
                return True

            # detected banned map
            wifi.setOff()
            Rhythms.Notify.play()
            allchanneloutput("bad map")

            # detect game canceled, which is not in loading map scence
            def detectGameCanceled(scr):
                assert stateDetector is not None
                if not stateDetector["LoadingMap"].detect(scr):
                    return True
                return False

            # sleep at least some time
            sleep(minDelayAfterDisconnected)
            if not KeepDetecting(
                successCond=detectGameCanceled,
                cancelCond=lambda scr: self.timeToStop(),
                sleeptime=2,
            ):
                """
                task canceld, do the cleanning
                set on wifi after fully exit the game match
                """
                Rhythms.Cancel.play()
                KeepDetecting(
                    successCond=detectGameCanceled,
                    sleeptime=2,
                )
                wifi.setOn()
                return False

            wifi.setOn()
            Rhythms.Notify.play()
            allchanneloutput("canceled")
            # for not enter game too soon after wifi on
            wifonitime = time.time()
            sleepuntil(lambda: time.time() - wifonitime > setonwifirecoverthresh, 1)


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
        guideitem: typing.List[ApproximateStandardizationGuide.GuideItem] = []
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
    ) -> typing.List["VehicleInfo"]:
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
        players: typing.List[str], vi: typing.List["VehicleInfo"]
    ):
        ret: typing.List[VehicleInfo.MatchResult] = []
        for l, p in enumerate(players):
            for v in vi:
                if re.match(v.pattern, p) is not None:
                    ret.append(VehicleInfo.MatchResult(l, p, v.name))
        return ret

    @staticmethod
    def detectAnyInOutputOfTesseract(
        players: str,
        vi: typing.List["VehicleInfo"],
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
            sleep(sleeptime)

    def moveMouseAway():
        moveto((0, 0))
        mouse.click(0)

    loadAssetsNeeded4FreshAMap()

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
            sp = stateDetector["Statistics"].find(scr)
            if sp is not None:
                moveto(sp)
                time.sleep(1)
                mouse.movr(*(10, 10))
                time.sleep(1)
                mouse.click(0)
                time.sleep(1)
                return True
            if stateDetector["hanger"].detect(scr) or stateDetector[
                "MissionCanceled"
            ].detect(scr):
                # piority lower than statistics, so the to battle button on spawn scence wont confuse
                press(win32con.VK_RETURN)
                return False
            if stateDetector["OK"].detect(scr):
                press(win32con.VK_ESCAPE)
                longDelay(15)
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
        press(win32con.VK_ESCAPE)
        time.sleep(KEY_OP_INTERVAL)

        # to menu
        press(win32con.VK_ESCAPE)
        time.sleep(KEY_OP_INTERVAL)

        moveto((0, 0))

        # select return to hanger
        for i in range(5):
            press(win32con.VK_DOWN)
            time.sleep(KEY_OP_INTERVAL)

        # click it
        press(win32con.VK_RETURN)
        time.sleep(KEY_OP_INTERVAL)

        # select yes
        press(win32con.VK_LEFT)
        time.sleep(KEY_OP_INTERVAL)

        # click
        press(win32con.VK_RETURN)
        time.sleep(KEY_OP_INTERVAL)

        moveMouseAway()
        mouse.click(0)

        # exit settlement screen
        def detectMissionCanceled(scr):
            assert stateDetector is not None
            if stateDetector["MissionCanceled"].detect(scr):
                press(win32con.VK_ESCAPE)
                return True
            return False

        keepdetecting(detectMissionCanceled)

        longDelay(5 * 60)
