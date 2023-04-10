from utilitypack import *
from opdar_config import *

uimask = cv.imread(r"./asset/opdar/UIMASK.png")
uimask = cv.cvtColor(uimask, cv.COLOR_BGR2GRAY)
odc = [
    DataCollector('./output/opdar_plane/spl'),
    DataCollector('./output/opdar_plane/lbl'),
]


def scoring(X, lamb, mu=0):
    return 1 / ((lamb * (X - mu))**2 + 1)


def deltaX(X):
    return X - arrayshift(X, 1)


# sample contribution according to deltaT


class stablizer_continous:

    def __init__(self, lamb, x0=0):
        self.x = x0
        self.lamb = lamb

    def init_from_series(self, X, T):
        COF = self.lamb**(-(T[-1] - T))
        self.x = (self.lamb**(-(T[-1] - T)) * X).sum()

    def sample(self, x, dt):
        self.x = self.x * self.lamb**dt + x * (-self.lamb**dt + 1)
        return self.x

    def val(self):
        return self.x


# treat every sample equally


class stablizer:

    def __init__(self, lamb, x0=0):
        self.x = x0
        self.lamb = lamb

    def init_from_series(self, X):
        # COF=self.lamb**(-(T[-1]-T))
        # self.x=(self.lamb**(-(T[-1]-T))*X).sum()
        pass

    def sample(self, x, acceptableerr=-1):
        # enabled
        if not acceptableerr < 0:
            #not acceptable
            if abs(x - self.x) > acceptableerr:
                return self.x
        self.x = self.x * self.lamb + x * (-self.lamb + 1)
        return self.x

    def val(self):
        return self.x


# assume a remains almost constant


class Estimator:
    #lamb is N/(N+1)
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
    #layout: X==P[:,0], Y==P[:,1]
    delta = (Pcenterized[:, 0]**2 - Pcenterized[:, 1]**2).sum()
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
    dist2 = (A * Pc[:, 0] + B * Pc[:, 1])**2
    dist2max = dist2.max()
    return 2 * np.sqrt(dist2max)


from exp.DLOnOpdarPlaneDetection.nntracker import getmodel

if useNNTracker:
    nntrker = getmodel(
        r'.\exp\DLOnOpdarPlaneDetection\nntracker.pth')
else:
    nntrker = None


def planetracknn(m, posref, mask=None, *paralistelse, **paradictelse):
    mask = mask.astype('float32') * 1 / 255
    size = [m.shape[1], m.shape[0]]
    posref = point_legalize(posref, size)

    # get region
    pul = (posref - searchrange).astype('int32')
    pbr = (posref + searchrange).astype('int32')
    pul = point_legalize(pul, size)
    pbr = point_legalize(pbr, size)
    m = m[pul[1]:pbr[1], pul[0]:pbr[0]]
    mndarray = m
    with torch.no_grad():
        from torchvision.transforms import ToTensor
        m = ToTensor()(m)
        m = m.reshape((1, ) + m.shape)  #add batch
        result = nntrker.forward(m)
        result = result[0, :, :, :]
        m = mndarray
    result = tensorimg2ndarray(result)
    # savemat(result)
    # savemat(mndarray)
    result = cv.threshold(result, 0.5, 1, cv.THRESH_BINARY)[1]

    #clustering
    contours = cv.findContours(result.astype('uint8'), cv.RETR_EXTERNAL,
                               cv.CHAIN_APPROX_NONE)[0]
    contnum = len(contours)
    if contnum == 0:  # found nothing
        return None
    info = np.zeros([contnum, 4])  # x, y, wingspan, averangeAdaptiveThreshErr
    for c in range(contnum):
        mgray = cv.cvtColor(m, cv.COLOR_BGR2GRAY)
        mcontour = np.zeros_like(mgray)
        cv.drawContours(mcontour, contours, c, 1, thickness=cv.FILLED)
        cluster = mcontour * mgray
        clusterbinary = cv.threshold(cluster, 0.1, 1, cv.THRESH_BINARY)[1]

        clusterXdist = clusterbinary.sum(0)
        clusterYdist = clusterbinary.sum(1)
        X = np.arange(pul[0], pbr[0])
        Y = np.arange(pul[1], pbr[1])

        info[c] = [(X * clusterXdist).sum() / (clusterXdist.sum() + 0.001),
                   (Y * clusterYdist).sum() / (clusterYdist.sum() + 0.001),
                   estimateWingSpan(clusterbinary),
                   cluster.sum() / clusterbinary.sum()]

    wingspanref = np.max(info[:, 2], axis=0)
    wingspanerrrelative = (wingspanref - info[:, 2]) / (wingspanref + 0.001)
    scorewingspan = scoring(wingspanerrrelative, wingspanrellamb)
    scorewingspan = (info[:, 2] >= wingspanleast) * scorewingspan

    totalscore = scorewingspan * info[:, 3]
    maxscorecontourid = np.argmax(totalscore, axis=0)
    # not matched satisfyingly
    if totalscore[maxscorecontourid] < scoreleast:
        return None
    mcontourmax = np.zeros_like(mgray)
    cv.drawContours(mcontourmax,
                    contours,
                    maxscorecontourid,
                    1,
                    thickness=cv.FILLED)
    clustermax = mcontourmax * mgray
    # (posx, posy), wingspan, clustermax, pul, its score
    return info[maxscorecontourid,
                0:2], info[maxscorecontourid,
                           2], clustermax, pul, info[maxscorecontourid, 3]


def planetrack(m,
               posref,
               wingspanref=-1,
               mask=None):
    mask = mask.astype('float32') * 1 / 255
    size = [m.shape[1], m.shape[0]]
    posref = point_legalize(posref, size)

    # get region
    pul = (posref - searchrange).astype('int32')
    pbr = (posref + searchrange).astype('int32')
    pul = point_legalize(pul, size)
    pbr = point_legalize(pbr, size)
    m = m[pul[1]:pbr[1], pul[0]:pbr[0]]
    if not mask is None:
        mask = mask[pul[1]:pbr[1], pul[0]:pbr[0]]
        m = m * mask
    if m.size <= 0:
        return None
    imgshape = m.shape
    m = m.astype('float32')*1/255

    # adaptive thresh
    ave = regionave(m, [backgroundrange, backgroundrange], mask)
    madat = ave - m
    madat = cv.threshold(madat, 0, 0, cv.THRESH_TOZERO)[1]
    madat = cv.normalize(madat, madat, 0, 1, cv.NORM_MINMAX)
    # normally filter from background color
    madat = cv.threshold(madat, adptthresh, 0, cv.THRESH_TOZERO)[1]
    
    #abs thresh
    mabst = cv.threshold(m, abslthresh, 1, cv.THRESH_BINARY_INV)[1]
    
    m=madat*mabst

    # clustering
    def density(m, eps=5):
        flter = np.ones([eps, eps])
        flter *= 1 / flter.size
        return cv.filter2D(m, -1, flter)

    d = density(m, regionrange)
    Xc = m * cv.threshold(d, routhresh, 1, cv.THRESH_BINARY)[1]
    Xcspan = regionsum(Xc, [regionrange, regionrange])
    Xbdcrange = cv.threshold(Xcspan, 0, 1, cv.THRESH_BINARY)[1]
    Xbdc = m * Xbdcrange
    contours = cv.findContours(Xbdcrange.astype('uint8'), cv.RETR_EXTERNAL,
                               cv.CHAIN_APPROX_NONE)[0]
    contnum = len(contours)
    if contnum == 0:  # found nothing
        return None
    info = np.zeros([contnum, 4])  # x, y, wingspan, averangeAdaptiveThreshErr
    for c in range(contnum):
        mcontour = np.zeros_like(m)
        cv.drawContours(mcontour, contours, c, 1, thickness=cv.FILLED)
        cluster = mcontour * m
        clusterbinary = cv.threshold(cluster, 0.1, 1, cv.THRESH_BINARY)[1]

        clusterXdist = clusterbinary.sum(0)
        clusterYdist = clusterbinary.sum(1)
        X = np.arange(pul[0], pbr[0])
        Y = np.arange(pul[1], pbr[1])

        info[c] = [(X * clusterXdist).sum() / (clusterXdist.sum()),
                   (Y * clusterYdist).sum() / (clusterYdist.sum()),
                   estimateWingSpan(clusterbinary),
                   cluster.sum() / clusterbinary.sum()]

    sqrdist = (
        ((info[:, 0:1] - np.repeat(posref.reshape([1, 2]), contnum, axis=0)) /
         searchrange)**2).sum(axis=1)
    scorepos = scoring(sqrdist, posrellamb)
    scorepos = np.ones_like(scorepos)

    if wingspanref < 0:
        # no suggusted wingspan
        # use the bigest one as reference, since its often clear in first tracking
        wingspanref = np.max(info[:, 2], axis=0)
    wingspanerrrelative = (wingspanref - info[:, 2]) / wingspanref
    scorewingspan = scoring(wingspanerrrelative, wingspanrellamb)
    scorewingspan = (info[:, 2] >= wingspanleast) * scorewingspan

    totalscore = scorepos * scorewingspan * info[:, 3]
    maxscorecontourid = np.argmax(totalscore, axis=0)

    # not matched satisfyingly
    if totalscore[maxscorecontourid] < scoreleast:
        return None

    mcontourmax = np.zeros_like(m)
    cv.drawContours(mcontourmax,
                    contours,
                    maxscorecontourid,
                    1,
                    thickness=cv.FILLED)
    clustermax = mcontourmax * m

    # (posx, posy), wingspan, clustermax, pul, its score
    return info[maxscorecontourid,
                0:2], info[maxscorecontourid,
                           2], clustermax, pul, info[maxscorecontourid, 3]


def cameramotion(m0, m1, mask, subsamplerate=0.2):
    m0small = cv.resize(m0,
                        None,
                        fx=subsamplerate,
                        fy=subsamplerate,
                        interpolation=cv.INTER_AREA)
    masksmall = cv.resize(mask,
                          None,
                          fx=subsamplerate,
                          fy=subsamplerate,
                          interpolation=cv.INTER_AREA)
    prev_pts = cv.goodFeaturesToTrack(m0small,
                                      maxCorners=100,
                                      qualityLevel=0.001,
                                      minDistance=3,
                                      blockSize=3,
                                      mask=masksmall)
    if prev_pts is None:
        raise Exception('No point to track')
    # sky=m0small[:int(0.5*m0small.shape[0]),:]
    # sky_pts = cv.goodFeaturesToTrack(sky,
    #                                   maxCorners=200,
    #                                   qualityLevel=0.001,
    #                                   minDistance=3,
    #                                   blockSize=3,
    #                                   mask=masksmall[:int(0.5*masksmall.shape[0]),:])
    # prev_pts=np.concatenate((prev_pts,sky_pts))

    m1small = cv.resize(m1,
                        None,
                        fx=subsamplerate,
                        fy=subsamplerate,
                        interpolation=cv.INTER_AREA)

    # Calculate optical flow (i.e. track feature points)
    curr_pts, status, err = cv.calcOpticalFlowPyrLK(m0small, m1small, prev_pts,
                                                    None)

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
    #m = cv.estimateRigidTransform(prev_pts, curr_pts, fullAffine=False)
    # will only work with OpenCV-3 or less
    m = cv.estimateAffinePartial2D(prev_pts, curr_pts, False)[0]

    # Extract traslation

    return curr_pts, m


class tracker:

    def setup(self, p0):
        self.omegastab = [stablizer(stablamb, 0), stablizer(stablamb, 0)]
        self.lastpos = p0
        self.lastwingspan = -1
        self.ss = screenshoter()
        # no longer able to shot wt individually, but setwindowcaptureaffinity solved hud in another way

        curr = self.ss.shot().astype('uint8')
        self.lastshottime = time.perf_counter()
        self.prev_red = curr[:, :, 2]

        self.trackbuildinguptimer = 2 * fps

        self.lazyplanetrackerfpsmanager = fpsmanager(fps=trackFps)

    def track(self):
        curr = self.ss.shotbgr().astype('uint8')
        shottime = time.perf_counter()
        tdelta = shottime - self.lastshottime

        curr_red = curr[:, :, 2]
        trackingpoints, cm = cameramotion(self.prev_red, curr_red, uimask,
                                          camerestablizersubsamplerate)

        curr_gray = None
        # blue channel
        if planetrackerchannel == 'B':
            curr_gray = curr[:, :, 0]
        # gray channel
        elif planetrackerchannel == 'G':
            curr_gray = cv.cvtColor(curr, cv.COLOR_BGRA2GRAY)
        # value channel
        elif planetrackerchannel == 'V':
            curr_gray = np.max(curr, axis=2)
        else:  # fallback to blue
            curr_gray = curr[:, :, 0]

        pomega = np.zeros([2])
        for c in range(len(pomega)):
            pomega[c] = self.omegastab[c].val()
        pestimated = self.lastpos+tdelta*pomega if self.trackbuildinguptimer == 0 else \
            self.lastpos
        preference = cm @ np.concatenate((pestimated, [1]))
        plastinthisframe = cm @ np.concatenate((self.lastpos, [1]))

        useEstimation = True
        if self.lazyplanetrackerfpsmanager.CheckIfTimeToDoNextFrame():
            if useNNTracker:
                ret = planetracknn(curr, preference, mask=uimask.copy())
            else:
                ret = planetrack(curr_gray,
                                 preference,
                                 wingspanref=self.lastwingspan,
                                 mask=uimask.copy())
            if ret != None:
                ponshot, wingspan, planemap, pul, maxscore = ret
                useEstimation = False
                # collecing for dl project
                # ponshot is in x,y format
                collectingPlaneSample
                if collectingPlaneSample and np.random.random(
                ) < collectingPlaneSampleRate:
                    name = DataCollector.geneName()
                    m4coll = curr[int(ponshot[1]) -
                                  searchrange:int(ponshot[1]) + searchrange,
                                  int(ponshot[0]) -
                                  searchrange:int(ponshot[0]) + searchrange, :]
                    odc[0].save(m4coll, name)


#                    odc[1].save(planemap * 255, name)

        if useEstimation:
            # no found to update, or canceled by fps, keep estimation
            ponshot, wingspan, planemap, pul, maxscore = [
                preference, self.lastwingspan,
                np.zeros([1, 1]), [0, 0], 0
            ]

        pomega = (ponshot - plastinthisframe) / tdelta

        self.prev_red = curr_red
        self.lastshottime = shottime
        for c in range(len(self.omegastab)):
            acceptableerr = -1 if self.trackbuildinguptimer > 0 \
                else self.omegastab[c].val()*stabaccepterrrelthr+stabaccepterrabsthr
            pomega[c] = self.omegastab[c].sample(pomega[c], acceptableerr)
        self.lastpos = ponshot
        self.lastwingspan = wingspan
        if self.trackbuildinguptimer > 0:
            self.trackbuildinguptimer -= 1
        return ponshot, pomega, plastinthisframe, wingspan, cm, trackingpoints, planemap, pul, maxscore
