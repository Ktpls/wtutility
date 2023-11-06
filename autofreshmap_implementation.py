from logging import exception

from utilitypack import *
from gameinput import *
from autofreshmap_config import *

assetroot = "./asset/autofreshmap/"


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
    "OK": {"path": signName2Path("OK"), "thresh": 0.2},
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
    pointtemplatezoomrate = 1.5  # 1920/1366

if dbglog:
    if log2file:
        logg = logger(
            os.path.join(
                assetroot,
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


class networkOperationImplementationSuite:
    @staticmethod
    def setoffwifi():
        pass

    @staticmethod
    def setonwifi():
        pass


class networkOperationImplementation_ipconfigrelease(
    networkOperationImplementationSuite
):
    @staticmethod
    def setoffwifi():
        os.system('ipconfig /release "WLAN"')

    @staticmethod
    def setonwifi():
        os.system('ipconfig /renew "WLAN"')


class networkOperationImplementation_netshinterfacesetinterfacedisable(
    networkOperationImplementationSuite
):
    @staticmethod
    def setoffwifi():
        os.system(
            f'netsh interface set interface name="{wlanname4netshinterface}" admin=disable'
        )

    @staticmethod
    def setonwifi():
        os.system(
            f'netsh interface set interface name="{wlanname4netshinterface}" admin=enable'
        )


class networkOperationImplementation_netshwlandisconnect(
    networkOperationImplementationSuite
):
    @staticmethod
    def setoffwifi():
        os.system(f"netsh wlan disconnect")

    @staticmethod
    def setonwifi():
        os.system(f'netsh wlan connect name="{wlanname4netshwlan}"')
        os.system(
            f'netsh wlan set profileparameter name="{wlanname4netshwlan}" connectionMode=auto'
        )
        # set auto so it will be auto connected the next time u boot


networkOperationImplementationAvailableList = [
    "ipconfigrelease",
    "netshinterfacesetinterfacedisable",
    "netshwlandisconnect",
]

networkOperationImplementationName = networkOperationImplementationAvailableList[2]


def setoffwifi():
    exec(
        "networkOperationImplementation_{}.setoffwifi()".format(
            networkOperationImplementationName
        )
    )


def setonwifi():
    exec(
        "networkOperationImplementation_{}.setonwifi()".format(
            networkOperationImplementationName
        )
    )


# singleChanneled
def picNorm(m):
    return np.sqrt((m.astype("float") ** 2).sum()) + 0.01


"""
info like:{
    "path":path
    "mask":mask,
    "lt":[x,y],
    "thresh":123
}
"""


def assetpath2realpath(ap):
    return os.path.join(assetroot, ap)


zfoo4matcher = ZFunc(10, 0, 20, 1)


class matcher:
    # deprecated
    # removed lt property in info, wont work and dont use this any more
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

    def __init__(self, info: Dict):
        path = assetpath2realpath(info["path"])
        m = cv.imread(path)
        if m.size == 0:
            raise BaseException("loading matcher failed in {}".format(path))
        self.pointlt = np.array(info["lt"])
        self.pointrd = self.pointlt + np.flip(m.shape[:2])
        self.m = matcher.imagepreprocess(m)
        self.thresh = info.get(
            "thresh", None
        )  # optional thresh, for dynamic specified, if needed

        # for dbg output
        self.path = info["path"]

        if info["mask"] is not None:
            m = assetpath2realpath(info["mask"])
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
        mscr = matcher.imagepreprocess(mscr)
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


class matchTemplateClassWrapper:
    def __init__(self, info: Dict):
        path = assetpath2realpath(info["path"])
        m = cv.imread(path)
        if m.size == 0:
            raise BaseException("loading matcher failed in {}".format(path))
        self.m = m
        self.thresh = info.get(
            "thresh", None
        )  # optional thresh, for dynamic specified, if needed

        # for dbg output
        self.path = info["path"]

        if info["mask"] is not None:
            m = assetpath2realpath(info["mask"])
            m = cv.imread(m)
            self.mask = m
        else:
            self.mask = None

    def find(self, mscr, specifiedThresh=None):
        thresh = specifiedThresh if specifiedThresh is not None else self.thresh
        ret = threshedmatchtemplate(mscr, self.m, self.mask, thresh)
        if dbglog:
            allchanneloutput(
                f"{self.path} matchTemplateClassWrapper detecting, ret={ret}"
            )
        return ret

    def detect(self, mscr, specifiedThresh=None):
        return self.find(mscr, specifiedThresh) is not None


class detector:
    def __init__(self, para):
        pass

    def detect(self, mscr):
        pass


class defaultdetector(detector):
    # para is matcherinfo
    def __init__(self, para):
        self.mtc = matcher(para)

    def detect(self, mscr):
        return self.mtc.detect(mscr)


class signdetector(detector):
    # para: {"path":path,"lt":lt}
    def __init__(self, para: dict):
        para = deepcopy(para)
        para.setdefault("thresh", 0.27)
        para.setdefault("mask", None)
        para.setdefault("type", "matchtemplate")

        if para.get("type") == "matcher":
            self.mtc = matcher(para)
        elif para.get("type") == "matchtemplate":
            self.mtc = matchTemplateClassWrapper(para)

    def detect(self, mscr: np.ndarray):
        return self.mtc.detect(mscr)

    def getsigncenter(self):
        return self.mtc.getsigncenter()

    def getsignpointrd(self):
        return self.mtc.getsignpointrd()


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
    pointrd = pointlt + [648, 648]
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


class mapdetector(detector):
    """
    para: {
        "mapreq":path,
        "foo":str
    }
    the so called path is actually map name, by which mapname2assetpath is needed
    after that assetpath2realpath will be done in matcher
    """

    def __init__(self, para: dict):
        para = deepcopy(para)

        if "mapreq" in para:
            mapreq = para["mapreq"]
            # formalize to list
            if type(mapreq) is str:
                mapreq = [mapreq]
            mapreq = [mapname2assetpath(mr) for mr in mapreq]
            bean4mtc = [
                {
                    "mask": None,
                    "lt": standardMapLeftTopPoint,
                    "thresh": standardMapMatchThreshold,
                    "path": mr,
                }
                for mr in mapreq
            ]
            self.mtc = [matcher(bm) for bm in bean4mtc]
        else:
            self.mtc = []

        self.foo = para["foo"]

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
            if type(ptype) is str:
                ptype = [ptype]
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
            return retVal
        except BaseException as e:
            traceback.print_exc()
            raise e


def maplist2detectorlist(ml):
    ml = deduplicate(ml)
    dl = {
        m: mapdetector(
            specialmapdetectors[m]
            if m in specialmapdetectors
            else {"mapreq": m, "foo": "ret(detectMapShape())"}
        )
        for m in ml
    }
    return dl


whitelistedmapdetector = None
stateDetector = None


def loadAssetsNeeded4FreshAMap():
    global whitelistedmapdetector, stateDetector
    whitelistedmapdetector = maplist2detectorlist(whitelistedmap)
    stateDetector = {k: signdetector(v) for k, v in stateDetectorInfo.items()}
    return whitelistedmapdetector, stateDetector


def leaveButton():
    sleep(1)
    # move after click for not blocking next time detection
    moveto([0, 0])


def freshAMap():
    # foo: bool(*foo)(Mat& screen), with return of if detected
    # ret: if matched and continue to next freshmap process step
    def keepdetecting(foo: Callable[[np.ndarray], bool], sleeptime=0.5) -> bool:
        while True:
            scr = shot()
            if foo(scr):
                return True
            sleep(sleeptime)

    # init
    loadAssetsNeeded4FreshAMap()

    ss = screenshoter(0)

    def shot():
        shot = ss.shotbgr()
        if saveScreenShot:
            if random.uniform(0, 1) < saveRate:
                savemat(
                    shot, name=GetTimeString(), path="./asset/autofreshmap/log/screen/"
                )
        return ss.shotbgr()

    while True:
        allchanneloutput(str("detecting to battle"))

        def detectToBattle(scr):
            # ret in each path so no interference between them
            if stateDetector["OK"].detect(scr):
                press(keycode.key_Enter)
                return False
            if stateDetector["hanger"].detect(scr):
                press(keycode.key_Enter)
                return True
            if stateDetector["MissionCanceled"].detect(scr):
                press(keycode.key_Enter)
                return True
            return False

        if not keepdetecting(detectToBattle):
            return
        win32api.Beep(500, 100)
        allchanneloutput("matching")

        # detect loading map
        loadingscreen = None

        allchanneloutput(str("detecting loading map"))

        def detectLoadingMap(scr):
            if stateDetector["LoadingMap"].detect(scr):
                nonlocal loadingscreen
                loadingscreen = scr
                return True
            if stateDetector["hanger"].detect(scr):  # for click not succeed
                press(keycode.key_Enter)
                return False
            if stateDetector["OK"].detect(scr):
                press(keycode.key_Enter)
                return False
            if stateDetector["MissionCanceled"].detect(scr):
                press(keycode.key_Enter)
                return False
            return False

        if not keepdetecting(detectLoadingMap, 1):
            return

        win32api.Beep(500, 100)
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
            win32api.Beep(1000, 100)
            win32api.Beep(500, 100)
            win32api.Beep(1000, 100)
            allchanneloutput("good map")
            break

        # detected banned map
        setoffwifi()
        win32api.Beep(500, 100)
        allchanneloutput("bad map")

        # detect game canceled, which is not in loading map scence
        def detectGameCanceled(scr):
            if not stateDetector["LoadingMap"].detect(scr):
                return True
            # setoffwifi()
            return False

        # detect able to enter again
        def detectGameRematchable(scr):
            if stateDetector["hanger"].detect(scr):
                return True
            if stateDetector["MissionCanceled"].detect(scr):
                return True
            return False

        # sleep at least some time
        sleep(minDelayAfterDisconnected)
        if not keepdetecting(detectGameCanceled, sleeptime=2):
            return

        setonwifi()
        win32api.Beep(500, 100)
        allchanneloutput("canceled")
        # for not enter game too soon after wifi on
        wifonitime = time.time()
        sleepuntil(lambda: time.time() - wifonitime > setonwifirecoverthresh, 1)


def longDelay(t, interval=0.5):
    round = math.ceil(t / interval)
    for i in range(round):
        time.sleep(interval)


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
        guideitem = []
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
        return s


@dataclasses.dataclass
class VehicleInfo:
    name: str
    pattern: re.Pattern

    @staticmethod
    def compile(
        sourceCode: str, asg: ApproximateStandardizationGuide
    ) -> List["VehicleInfo"]:
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
    def matchPlayerVehicleListAndVehicleInfoList(players: str, vi: List["VehicleInfo"]):
        ret: List[VehicleInfo.MatchResult] = []
        for l, p in enumerate(players):
            for v in vi:
                if re.match(v.pattern, p) is not None:
                    ret.append(VehicleInfo.MatchResult(l, p, v.name))
        return ret

    @staticmethod
    def detectAnyInOutputOfTesseract(
        players: str, vi: List["VehicleInfo"], asg: ApproximateStandardizationGuide
    ):
        players = [asg.do(t) for t in players.split("\n")]
        ret = VehicleInfo.matchPlayerVehicleListAndVehicleInfoList(players, vi)
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
    def keepdetecting(foo: Callable[[np.ndarray], bool], sleeptime=0.5) -> bool:
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
            sp = stateDetector["Statistics"].mtc.find(scr)
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
                press(keycode.key_Enter)
                return False
            if stateDetector["OK"].detect(scr):
                press(keycode.key_Esc)
                longDelay(15)
                return False
            return False

        moveMouseAway()
        keepdetecting(detectStartMatch, sleeptime=10)

        class DetectPlayerVehicleResult(Enum):
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
            win32api.Beep(1000, 100)
            win32api.Beep(500, 100)
            win32api.Beep(1000, 100)
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
            win32api.Beep(500, 100)
            win32api.Beep(500, 100)
            win32api.Beep(500, 100)
        elif detectPlayerVehicleResult == DetectPlayerVehicleResult.unset:
            raise Exception("detectPlayerVehicleResult is unset")

        KEY_OP_INTERVAL = 0.3
        # bad
        # exit statistics
        press(keycode.key_Esc)
        time.sleep(KEY_OP_INTERVAL)

        # to menu
        press(keycode.key_Esc)
        time.sleep(KEY_OP_INTERVAL)

        moveto((0, 0))

        # select return to hanger
        for i in range(5):
            press(keycode.key_Down)
            time.sleep(KEY_OP_INTERVAL)

        # click it
        press(keycode.key_Enter)
        time.sleep(KEY_OP_INTERVAL)

        # select yes
        press(keycode.key_Left)
        time.sleep(KEY_OP_INTERVAL)

        # click
        press(keycode.key_Enter)
        time.sleep(KEY_OP_INTERVAL)

        moveMouseAway()
        mouse.click(0)

        # exit settlement screen
        def detectStartMatch(scr):
            if stateDetector["MissionCanceled"].detect(scr):
                press(keycode.key_Esc)
                return True
            return False

        keepdetecting(detectStartMatch)

        longDelay(5 * 60)
