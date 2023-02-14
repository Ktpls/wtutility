from utilitypack import *


def scoring(X, lamb, mu=0):
    return 1 / ((lamb * (X - mu))**2 + 1)


def getlambfromtarget(how, where):
    return np.sqrt((1 / how - 1)) / where


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
    #X==P[:,0], Y==P[:,1]
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


def planetrack(m,
               posref,
               wingspanref=-1,
               searchrange=100,
               backgroundrange=31,
               adptthresh=0.4,
               regionrange=10,
               routhresh=0.2,
               posrellamb=0,
               wingspanrellamb=0,
               wingspanleast=0,
               scoreleast=0.1,
               mask=None):
    mask = mask.astype('float32') * 1 / 255
    size = [m.shape[1], m.shape[0]]
    posref = point_legalize(posref, size)

    # get region
    pul = (posref - searchrange).astype('int32')
    pbr = (posref + searchrange).astype('int32')
    pul = point_legalize(pul, size)
    pbr = point_legalize(pbr, size)

    # adaptive thresh
    m = m[pul[1]:pbr[1], pul[0]:pbr[0]]
    if not mask is None:
        mask = mask[pul[1]:pbr[1], pul[0]:pbr[0]]
        m = m * mask
    if m.size <= 0:
        return None
    imgshape = m.shape
    m = m.astype('float32')
    ave = regionave(m, [backgroundrange, backgroundrange], mask)
    m = ave - m
    m = cv.threshold(m, 0, 0, cv.THRESH_TOZERO)[1]
    m = cv.normalize(m, m, 0, 1, cv.NORM_MINMAX)
    # normally filter from background color
    m = cv.threshold(m, adptthresh, 0, cv.THRESH_TOZERO)[1]

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
