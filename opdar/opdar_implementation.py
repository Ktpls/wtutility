from utilref import *
from opdar_config import *
import scipy.interpolate as interpolate

if useNnTracker:
    from utilitypack.util_torch import *

uimask = cv.imread(uimaskPath)
uimask = cv.cvtColor(uimask, cv.COLOR_BGR2GRAY)
uimask = (uimask > 0).astype(np.uint8)
odc = [
    DataCollector(datacoll_samplepath),
    DataCollector(datacoll_labelpath),
]


def scoring(X, lamb, mu=0):  # best score at mu
    return 1 / (lamb * ((X - mu)) ** 2 + 1)


def deltaX(X):
    return X - arrayshift(X, 1)


class stablizer_base:
    def __init__(self, lamb, x0):
        self.x = x0
        self.lamb = lamb

    def sample(self, x):
        pass

    def val(self):
        return self.x


class stablizer_continous(stablizer_base):
    # sample contribution according to deltaT

    def init_from_series(self, X, T):
        self.x = (self.lamb ** (-(T[-1] - T)) * X).sum()

    def sample(self, x, dt):
        self.x = self.x * self.lamb**dt + x * (-self.lamb**dt + 1)
        return self.x


class stablizer(stablizer_base):
    # treat every sample equally

    def init_from_series(self, X):
        pass

    def sample(self, x, acceptableerr=-1):
        # enabled
        if not acceptableerr < 0:
            # not acceptable
            if abs(x - self.x) > acceptableerr:
                return self.x
        self.x = self.x * self.lamb + x * (-self.lamb + 1)
        return self.x


class stablizerNd(stablizer_base):
    def __init__(self, lamb, x0=[0, 0]):
        self.dim = len(x0)
        self.stab = [stablizer(lamb, c) for c in x0]

    def val(self):
        return np.array([s.val() for s in self.stab])

    def sample(self, x, acceptableerr=-1):
        assert len(x) == self.dim
        if isinstance(acceptableerr, (float, int)):
            acceptableerr = [acceptableerr] * self.dim
        assert len(acceptableerr) == self.dim
        [self.stab[i].sample(x[i], acceptableerr[i]) for i in range(self.dim)]
        return self.val()


# assume a remains almost constant


class Estimator:
    # lamb is N/(N+1)
    def __init__(self, lamb, X, T):
        assert len(X) >= 3 and len(T) == len(X)
        DT = deltaX(T)
        DX = deltaX(X)
        V = DX / DT
        DV = deltaX(V)
        A = DV / DT
        Asample = A[2:]
        Tsample = T[2:]
        self.v = V[-1]
        self.x = X[-1]
        self.a = stablizer_continous(lamb)
        self.a.init_from_series(Asample, Tsample)

    def estimate(self, dtfuture):
        return self.x + self.v * dtfuture + self.a.val() / 2 * dtfuture**2

    def update(self, x, dt):
        dx = x - self.x
        self.x = x
        v = dx / dt
        dv = v - self.v
        self.v = v
        a = dv / dt
        self.a.sample(a, dt)


def point_legalize(p, size):
    if p[0] < 0:
        p[0] = 0
    if p[0] >= size[0]:
        p[0] = size[0]
    if p[1] < 0:
        p[1] = 0
    if p[1] >= size[1]:
        p[1] = size[1]
    return p


def fit_errmax(P):
    ave = P.sum(0) / P.shape[0]
    ave = np.repeat(ave.reshape([1, 2]), P.shape[0], axis=0)
    Pcenterized = P - ave
    # layout: X==P[:,0], Y==P[:,1]
    delta = (Pcenterized[:, 0] ** 2 - Pcenterized[:, 1] ** 2).sum()
    gamma = (Pcenterized[:, 0] * Pcenterized[:, 1]).sum()
    base = np.sqrt(delta**2 + 4 * gamma**2)
    if base < 0.1:
        base = 0.1
    cosphi = delta / base
    sinphi = 2 * gamma / base
    cosita = -cosphi
    sinita = -sinphi
    Apsi = np.sqrt((1 - cosita) / 2)
    Bpsi = np.sqrt((cosita + 1) / 2)
    Bpsi = Bpsi if sinita > 0 else -Bpsi
    return -Apsi, Bpsi, Pcenterized


# binary mat


def mat2pointset(m):
    idx = np.array(np.where(m > 0))
    X = idx[0].reshape([idx.shape[1], 1])
    Y = idx[1].reshape([idx.shape[1], 1])
    P = np.concatenate((X, Y), axis=1)
    return P


def estimateWingSpan(m):
    ps = mat2pointset(m)
    # at least 2 points
    if len(ps) < 2:
        return 0
    A, B, Pc = fit_errmax(ps)
    dist2 = (A * Pc[:, 0] + B * Pc[:, 1]) ** 2
    dist2max = dist2.max()
    return 2 * np.sqrt(dist2max)


if useNnTracker:
    from exp.DLOnOpdarPlaneDetection.nntracker import getmodel

    nntrker = getmodel(r".\exp\DLOnOpdarPlaneDetection\nntracker.pth")
else:
    nntrker = None


def ObjectFilterNn(m: np.ndarray):
    assert np.sqrt(np.sum((np.array(m.shape) - [128, 128]) ** 2)) < 1
    mndarray = m
    with torch.no_grad():
        from torchvision.transforms import ToTensor

        m = ToTensor()(m)
        m = m.reshape((1,) + m.shape)  # add batch
        result = nntrker.forward(m)
        result = result[0, :, :, :]
        m = mndarray
    result = tensorimg2ndarray(result)
    result = cv.threshold(result, 0.5, 1, cv.THRESH_BINARY)[1]
    return result


def ObjectFilterTrad(m: np.ndarray):
    # adaptive thresh
    ave = regionave(m, [backgroundrange, backgroundrange])
    madat = m - ave
    madat = (madat >= adptthresh).astype(np.uint8)

    # abs thresh
    mabst = np.copy(m)
    mabst = (mabst >= abslthresh).astype(np.uint8)

    # denoise
    def density(m, range=5):
        flter = np.ones([range, range])
        flter *= 1 / flter.size
        return cv.filter2D(m, -1, flter)

    rho = density(m, regionrange)
    m_rhoThreshed = (rho >= rhothresh).astype(np.uint8)

    m = (madat * mabst * m_rhoThreshed).astype(np.float32)
    return m


def SplitObject(m: cv.Mat):
    contours = cv.findContours(
        m.astype("uint8"), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE
    )[0]
    ret: list[cv.Mat] = []
    for c in range(len(contours)):
        mcontour = np.zeros_like(m)
        cv.drawContours(mcontour, contours, c, 1, thickness=cv.FILLED)
        ret.append(mcontour)
    return ret


@dataclasses.dataclass
class ObjectInfo:
    r: np.ndarray
    wingspan: float
    shape: cv.Mat
    aabb: np.ndarray

    @staticmethod
    def fromObjectSignal(m: cv.Mat):
        clusterXdist = m.sum(0)
        clusterYdist = m.sum(1)
        X = np.arange(0, m.shape[1])
        Y = np.arange(0, m.shape[0])

        return ObjectInfo(
            r=np.array(
                [
                    (X * clusterXdist).sum() / (clusterXdist.sum() + epsilon),
                    (Y * clusterYdist).sum() / (clusterYdist.sum() + epsilon),
                ]
            ),
            wingspan=estimateWingSpan(m),
            shape=m,
            aabb=np.array(get_AABB(m)),
        )


def GetObjectOnSignal(
    m: np.ndarray,
    posref: np.ndarray,
    wingspanref=None,
    shaperef=None,
    mask: np.ndarray = None,
):
    if useNnTracker:
        m = ObjectFilterNn(m)
    else:
        m = ObjectFilterTrad(m)
    obj = SplitObject(m)
    if len(obj) == 0:
        return None
    obj = [ObjectInfo.fromObjectSignal(o) for o in obj]

    # position score
    # searchrange is the center of cutted roi
    sqrdist = ((([i.r for i in obj] - posref) / posref) ** 2).sum(axis=1)
    scorepos = scoring(sqrdist, posrellamb)
    scorepos = np.ones_like(scorepos)

    # wingspan score
    if wingspanref is None:
        # no suggusted wingspan
        scorewingspan = 1
    else:
        wingspanerrrelative = (wingspanref - np.array([i.wingspan for i in obj])) / (
            wingspanref + epsilon
        )
        scorewingspan = scoring(wingspanerrrelative, wingspanrellamb)
        scorewingspan = (
            np.array([i.wingspan for i in obj]) >= wingspanleast
        ) * scorewingspan

    # shape score
    if shaperef is None:
        # no suggusted shape
        shapescore = 1
    else:
        objinfoShaperef = ObjectInfo.fromObjectSignal(shaperef)
        allObj = obj + [objinfoShaperef]
        # [obj, [minx, miny, maxx, maxy]]
        aabb_uncentred = np.array([i.aabb for i in allObj])
        center = np.array([i.r for i in allObj])
        aabbmin = aabb_uncentred[:, :2] - center
        aabbmax = aabb_uncentred[:, 2:] - center
        aabbminOfAll = np.min(aabbmin, axis=0)
        aabbmaxOfAll = np.max(aabbmax, axis=0)
        newShape = np.ceil(aabbmaxOfAll - aabbminOfAll).astype(
            np.uint32
        )  # dont need a flip
        newCenter = np.flip(-aabbminOfAll)

        relocateds = [
            cv.warpAffine(
                o.shape,
                np.array(
                    [[1, 0, newCenter[0] - o.r[0]], [0, 1, newCenter[1] - o.r[1]]],
                    dtype=np.float32,
                ),
                newShape,
            )
            for o in allObj
        ]
        # relocateds[-1] is the shaperef
        shapescore = np.array(
            [
                scoring(
                    np.sum((o - relocateds[-1]) ** 2)
                    / (np.sum(relocateds[-1]) + epsilon),
                    shapereallamb,
                )
                for o in relocateds
            ]
        )[
            :-1
        ]  # remove the shaperef

    # total score
    totalscore = scorepos * scorewingspan * shapescore
    # totalscore = np.ones(len(obj))
    maxscorecontourid = np.argmax(totalscore, axis=0)

    # not matched satisfyingly
    if totalscore[maxscorecontourid] < scoreleast:
        return None

    savemat(m * 255)
    savemat(obj[maxscorecontourid].shape * 255)
    return obj[maxscorecontourid]


def cameramotion(m0, m1, mask, subsamplerate=0.2):
    m0small = cv.resize(
        m0, None, fx=subsamplerate, fy=subsamplerate, interpolation=cv.INTER_AREA
    )
    masksmall = cv.resize(
        mask, None, fx=subsamplerate, fy=subsamplerate, interpolation=cv.INTER_AREA
    )
    prev_pts = cv.goodFeaturesToTrack(
        m0small,
        maxCorners=100,
        qualityLevel=0.001,
        minDistance=3,
        blockSize=3,
        mask=masksmall,
    )
    if prev_pts is None:
        raise Exception("No point to track")
    # sky=m0small[:int(0.5*m0small.shape[0]),:]
    # sky_pts = cv.goodFeaturesToTrack(sky,
    #                                   maxCorners=200,
    #                                   qualityLevel=0.001,
    #                                   minDistance=3,
    #                                   blockSize=3,
    #                                   mask=masksmall[:int(0.5*masksmall.shape[0]),:])
    # prev_pts=np.concatenate((prev_pts,sky_pts))

    m1small = cv.resize(
        m1, None, fx=subsamplerate, fy=subsamplerate, interpolation=cv.INTER_AREA
    )

    # Calculate optical flow (i.e. track feature points)
    curr_pts, status, err = cv.calcOpticalFlowPyrLK(m0small, m1small, prev_pts, None)

    # Sanity check
    assert prev_pts.shape == curr_pts.shape

    # Filter only valid points
    idx = np.where(status == 1)[0]
    if idx.size == 0:
        return curr_pts, [[1, 0, 0], [0, 1, 0]]
    prev_pts = prev_pts[idx]
    curr_pts = curr_pts[idx]
    prev_pts = prev_pts / subsamplerate
    curr_pts = curr_pts / subsamplerate

    # Find transformation matrix
    # m = cv.estimateRigidTransform(prev_pts, curr_pts, fullAffine=False)
    # will only work with OpenCV-3 or less
    m = cv.estimateAffinePartial2D(prev_pts, curr_pts, False)[0]

    # Extract traslation

    return curr_pts, m


from wtdmp.wtdistmeaspy_implementation import (
    SnipScencePreProcess,
    GetCrosshair,
    getMilInterval,
    AdjustByZoomRate,
    gridSearchWidth_unzoom,
    BadCaliException,
)


def GetMilIntervalFromScrShot(m):
    dbglogsavestep = lambda m, name=None, method="savemat": None
    log = lambda s: None
    dbg = False
    red_mask = SnipScencePreProcess(m, dbg, dbglogsavestep, log)
    crosshair = GetCrosshair(red_mask)
    gridlineHor, rangeHor, mil = getMilInterval(
        red_mask, crosshair, AdjustByZoomRate(gridSearchWidth_unzoom), log
    )
    return mil


class MtiFilter:
    @dataclasses.dataclass
    class MtiStorage:
        img: np.ndarray

        # compared with prev frame
        cammotion: np.ndarray

    def __init__(self, mtiQueueSize) -> None:
        """
        consider storage only the transformed and meaned pic
        like the dynamic window way. kick the oldest one in queue out, and take its effect out of meaned pic
        """
        self.filter = interpolate.interp1d([0, 0.3, 0.75, 1], [1, 1, 0, 0])
        # fake type notation in order to scam ide type analysis
        self.mtiQueue: typing.List[
            MtiFilter.MtiStorage
        ] | AccessibleQueue = AccessibleQueue(mtiQueueSize)

        # try convienient type annotation but wont work
        # self.mtiQueue: AccessibleQueue.Annotation(
        #     MtiFilter.MtiStorage
        # ) = AccessibleQueue(5)

    def update(self, img: np.ndarray, cammotion: np.ndarray):
        if self.mtiQueue.isEmpty():
            ret = np.ones_like(img)
        else:
            # mit proc
            def cammotionmat2x3to3x3(cammot: np.ndarray):
                return np.concatenate(
                    [
                        cammot,
                        [[0, 0, 1]],
                    ]
                )

            def cammotionmat3x3to2x3(cammot: np.ndarray):
                return cammot[:2, :]

            motionSum = cammotionmat2x3to3x3(cammotion)
            scrsize = img.shape
            prevScreenAtNowView = []
            for i in range(len(self.mtiQueue)):
                # iter from the newest to oldest
                prevScreenAtNowView.append(
                    cv.warpAffine(
                        self.mtiQueue[-i].img,
                        cammotionmat3x3to2x3(motionSum),  # only x, y, no w
                        np.flip(scrsize),
                        borderMode=cv.BORDER_CONSTANT,
                        borderValue=0,
                    )
                )
                motionSum = (
                    cammotionmat2x3to3x3(self.mtiQueue[-i].cammotion) @ motionSum
                )
            self.mtiQueue.push__pop_if_full(MtiFilter.MtiStorage(img, cammotion))
            prevsignal = np.array(prevScreenAtNowView)
            prevsignal = np.average(prevsignal, axis=0)
            """
            in case that input is not binary, like a gray dot
            and it doesnt hurt in this case, that:
                for the head part of trajectory of moving dot, img_now is 1-ish, so prevsignal is 0-ish
                for the tail part, img_now is 0-ish, so prevsignal is 1-ish
                it fits the filter logic
            """
            prevsignal = prevsignal / (img + epsilon)

            ret = self.filter(prevsignal)
        return ret


class MotionEstimator:
    def __init__(self) -> None:
        self.lastScreen = None

    def update(self, newScreen):
        newScreen = newScreen[:, :, 2]
        if self.lastScreen is None:
            self.lastScreen = newScreen
            return None
        return cameramotion(
            self.lastScreen, newScreen, uimask, camerestablizersubsamplerate
        )


@dataclasses.dataclass
class trackerRet:
    ponshot: np.ndarray
    pomega: np.ndarray
    plastinthisframe: np.ndarray
    wingspan: float
    cm: np.ndarray
    trackingpoints: typing.Any
    planemap: cv.Mat
    pul: np.ndarray
    thetabypix: float


class tracker:
    def setup(self, p0):
        self.omegastab = stablizerNd(stablamb, [0, 0])
        self.lastpos = p0
        self.lastwingspan = None
        self.lastshape = None
        self.ss = screenshoter()
        # no longer able to shot wt individually, but setwindowcaptureaffinity solved hud in another way

        curr = self.ss.shot().astype("uint8")
        self.lastshottime = time.perf_counter()
        self.motionEstimator = MotionEstimator()
        self.motionEstimator.update(curr)

        self.trackbuildinguptimer = 2 * fps

        self.lazyplanetrackerfpsmanager = fpsmanager(fps=trackFps)

        self.mtif = MtiFilter(mtiQueueSize)
        self.mtif.update(curr, None)

    def track(self):
        curr = self.ss.shotbgr().astype("uint8")
        shottime = time.perf_counter()
        tdelta = shottime - self.lastshottime

        # i expect cm has no zoom and rotation, so only with translation
        trackingpoints, cm = self.motionEstimator.update(curr)

        signal_fullscreen = None
        # blue channel
        if planetrackerchannel == "B":
            signal_fullscreen = curr[:, :, 0]
        # gray channel
        elif planetrackerchannel == "G":
            signal_fullscreen = cv.cvtColor(curr, cv.COLOR_BGRA2GRAY)
        # value channel
        elif planetrackerchannel == "V":
            signal_fullscreen = np.max(curr, axis=2)
        else:  # fallback to blue
            signal_fullscreen = curr[:, :, 0]

        # neg to get dark signal
        signal_fullscreen = 1 - signal_fullscreen.astype(np.float32) / 255

        if mtiOn:
            mtiresult = self.mtif.update(signal_fullscreen, cm)
            signal_fullscreen = mtiresult * signal_fullscreen

        pomega = self.omegastab.val()
        pestimated = (
            self.lastpos + tdelta * pomega
            if self.trackbuildinguptimer == 0
            else self.lastpos
        )

        preference = cm @ np.concatenate((pestimated, [1]))
        plastinthisframe = cm @ np.concatenate((self.lastpos, [1]))

        thetabypix = c_thetabypix
        size = [signal_fullscreen.shape[1], signal_fullscreen.shape[0]]
        posref = point_legalize(preference, size)

        # get region
        pul = (posref - searchrange).astype("int32")
        pbr = (posref + searchrange).astype("int32")
        pul = point_legalize(pul, size)
        pbr = point_legalize(pbr, size)

        # close eye, set default in case of tracking failed
        ponshot, wingspan, planemap = [
            preference,
            self.lastwingspan,
            np.zeros([1, 1]),
        ]
        if self.lazyplanetrackerfpsmanager.CheckIfTimeToDoNextFrame():
            self.lazyplanetrackerfpsmanager.SetToNextFrame()

            if useThetaByPixCalcFromMil:
                try:
                    thetabypix = (2 * 3.1415926 / 6000) / GetMilIntervalFromScrShot(
                        curr
                    )
                except BadCaliException:
                    pass

            if not uimask is None:
                signal_fullscreen = signal_fullscreen * uimask
            signal = signal_fullscreen[pul[1] : pbr[1], pul[0] : pbr[0]]

            if signal.size > 0:
                # not bad cut
                ret = GetObjectOnSignal(
                    signal,
                    preference,
                    wingspanref=self.lastwingspan,
                    shaperef=self.lastshape,
                    mask=uimask.copy(),
                )

                if ret is not None:
                    # back to global coordinate
                    ponshot, wingspan, planemap = ret.r + pul, ret.wingspan, ret.shape
                    # collecing for dl project
                    # ponshot is in x,y format
                    if (
                        collectingPlaneSample
                        and np.random.random() < collectingPlaneSampleRate
                    ):
                        name = DataCollector.geneName()
                        m4coll = curr[
                            int(ponshot[1])
                            - searchrange : int(ponshot[1])
                            + searchrange,
                            int(ponshot[0])
                            - searchrange : int(ponshot[0])
                            + searchrange,
                            :,
                        ]
                        odc[0].save(m4coll, name)
                        odc[1].save(planemap * 255, name)

        pomega = (ponshot - plastinthisframe) / tdelta

        self.lastshottime = shottime

        if self.trackbuildinguptimer > 0:
            acceptableerr = -1
        else:
            acceptableerr = (
                self.omegastab.val() * stabaccepterrrelthr + stabaccepterrabsthr
            )
        pomega = self.omegastab.sample(pomega, acceptableerr)

        self.lastpos = ponshot
        self.lastwingspan = wingspan
        self.lastshape = planemap
        if self.trackbuildinguptimer > 0:
            self.trackbuildinguptimer -= 1
        return trackerRet(
            ponshot=ponshot,
            pomega=pomega,
            plastinthisframe=plastinthisframe,
            wingspan=wingspan if wingspan is not None else 1,
            cm=cm,
            trackingpoints=trackingpoints,
            planemap=planemap if planemap is not None else np.zeros([1, 1]),
            pul=pul,
            thetabypix=thetabypix,
        )
