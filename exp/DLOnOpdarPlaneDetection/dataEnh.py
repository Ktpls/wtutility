from utilref import *
#%%
# perform dataenh
from nntracker_common import labeldataset


train_data = labeldataset().init(
    r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\all',
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\train.xlsx",
    32768, 'fld')


def dataEnhance(src, lbl):
    dttp = [src, lbl]

    #rot
    def rot(m, the):
        #theta in [-pi/2,pi/2]
        #assert right squared img0 here
        rotmat = np.array([
            [np.cos(the), -np.sin(the)],
            [np.sin(the), np.cos(the)],
        ])

        l0 = m.shape[0]
        Y, X = np.arange(l0, dtype=np.float32), np.arange(l0, dtype=np.float32)
        X, Y = np.meshgrid(X, Y)
        Y -= l0 * 0.5
        X -= l0 * 0.5
        Xp = rotmat[0, 0] * X + rotmat[0, 1] * Y
        Yp = rotmat[1, 0] * X + rotmat[1, 1] * Y
        X = Xp
        Y = Yp
        Y += l0 * 0.5
        X += l0 * 0.5
        m = cv.remap(m, Xp, Yp, cv.INTER_LINEAR)
        return m

    the_u = np.pi / 6
    the_l = -the_u
    the = np.random.rand() * (the_u - the_l) + the_l
    dttp = [rot(m, the) for m in dttp]

    def zoom(m, rate):
        l0 = m.shape[0]
        X = np.arange(l0).reshape([1, l0]).astype(np.float32)
        Y = np.arange(l0).reshape([l0, 1]).astype(np.float32)
        XY = np.array(np.meshgrid(X, Y))
        XY -= l0 / 2
        XY /= rate
        XY += l0 / 2
        return cv.remap(m, *XY, cv.INTER_LINEAR)

    rate = (np.random.rand() * 0.2) + 0.9
    dttp = [zoom(m, rate) for m in dttp]

    #flip
    def flip(m, reallyflip: bool):
        if reallyflip:
            return np.flip(m, axis=1)  # flip lr
        else:
            return m

    reallyflip = (np.random.rand() < 0.5)
    dttp = [flip(m, reallyflip) for m in dttp]
    dttp = [np.ascontiguousarray(m) for m in dttp]

    #give back channel dim
    dttp = [
        m if len(m.shape) == 3 else m.reshape(m.shape + (1, )) for m in dttp
    ]
    src, lbl = dttp
    return src, lbl


def makeSample(cachepair):
    # shape standardlize included
    return dataEnhance(*cachepair[int(len(cachepair) * np.random.random())])


def makeSampleAndPrintProgress(size, cachepair, path):
    percentage = 0
    for i in range(size):
        if i > (percentage + 1) * 0.01 * size:
            percentage = np.floor(i / size * 100)
            print(f'{percentage}%')
        src, lbl = makeSample(cachepair)
        name = DataCollector.geneName()
        savemat(src * 255, name, rf'{path}/spl')
        savemat(lbl * 255, name, rf'{path}/lbl')


outpath = r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed"


def performDataEnh():
    makeSampleAndPrintProgress(8192, train_data.pairs, outpath)


performDataEnh()