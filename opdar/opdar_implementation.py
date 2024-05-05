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


class BayesEstimator:
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
    # deambient
    ambient = np.mean(m)
    m = np.clip(m - ambient, 0, 1)

    # adaptive thresh
    ave = regionave(m, [backgroundrange, backgroundrange])
    mAdat = (m - ave) / (ave + EPS)
    mAdat = (mAdat >= adptthresh).astype(np.uint8)

    # abs thresh
    mAbst = np.copy(m)
    mAbst = (mAbst >= abslthresh).astype(np.uint8)

    m = (mAdat).astype(np.float32)

    # # density thresh
    # rho = regionave(m, [backgroundrange, backgroundrange])
    # mRhoThreshed = (rho >= rhothresh).astype(np.uint8)

    # m = (m * mRhoThreshed).astype(np.float32)
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

    # savemat(obj[maxscorecontourid].shape * 255)
    return obj[maxscorecontourid]


from wtdmp.wtdistmeaspyimpl import (
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
        self.motionEstimator = MotionEstimator(uimask, camerestablizersubsamplerate)
        self.motionEstimator.update(curr[:, :, 2])

        self.trackbuildinguptimer = 2 * fps

        self.lazyplanetrackerfpsmanager = FpsManager(fps=trackFps)

        self.mtif = MtiFilter(mtiQueueSize)
        self.mtif.update(curr, None)

    def collectScreenInSearchRange(self):
        if collectingPlaneSample and np.random.random() < collectingPlaneSampleRate:
            curr = self.ss.shotbgr().astype("uint8")
            ponshot = lockpoint_default
            m4coll = curr[
                int(ponshot[1]) - searchrange : int(ponshot[1]) + searchrange,
                int(ponshot[0]) - searchrange : int(ponshot[0]) + searchrange,
                :,
            ]
            name = DataCollector.geneName()
            odc[0].save(m4coll, datacoll_sampleFormat.format(name))

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
                    np.array([searchrange, searchrange]),  # at the center of cutted img
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
                        odc[0].save(m4coll, datacoll_sampleFormat.format(name))
                        odc[1].save(planemap * 255, datacoll_labelFormat.format(name))

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
