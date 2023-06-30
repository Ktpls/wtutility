#%%
# perform dataenh
from utilref import *
from nntracker_common import labeldataset

train_data = labeldataset().init(
    r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\largeEnoughToRecon.zip',
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\all.xlsx",
    8192, 'zip')


def dataEnhance(src, lbl):
    dttp = [src, lbl]
    backcolor = np.mean(src, axis=(0, 1), keepdims=True)

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

    the = np.random.uniform(-np.pi / 3, np.pi / 3)
    dttp = [rot(m, the) for m in dttp]

    #zoom
    def zoom(m, rate):
        l0 = m.shape[0]
        X = np.arange(l0).reshape([1, l0]).astype(np.float32)
        Y = np.arange(l0).reshape([l0, 1]).astype(np.float32)
        XY = np.array(np.meshgrid(X, Y))
        XY -= l0 / 2
        XY /= rate
        XY += l0 / 2
        return cv.remap(m, *XY, cv.INTER_LINEAR)

    rate = np.random.uniform(0.8, 1.2)
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

    #mov
    def mov(m, vec):
        mattr = np.array([[1, 0, vec[0]], [0, 1, vec[1]]]).astype('float')
        m = cv.warpAffine(m, mattr, np.flip(m.shape[0:2]))
        return m

    vec = np.random.uniform(-50, 50, size=2)
    dttp = [mov(m, vec) for m in dttp]

    #give back channel dim
    dttp = [
        m if len(m.shape) == 3 else m.reshape(m.shape + (1, )) for m in dttp
    ]
    src, lbl = dttp

    lbl[lbl < 0.5] = 0
    lbl[lbl >= 0.5] = 1  #thresh

    black_pixels = np.where(np.sum(src, axis=2) < 0.1)
    src[black_pixels] = backcolor

    #rand line
    def draw_random_line(image, n):
        height, width, _ = image.shape
        color = (0, 0, 0)  # Black color
        for l in range(n):
            start_point = (np.random.randint(0, width),
                           np.random.randint(0, height))
            end_point = (np.random.randint(0, width),
                         np.random.randint(0, height))
            cv.line(image, start_point, end_point, color, 1)
        return image

    src = draw_random_line(src, 5)

    return src, lbl


def makeSampleAndPrintProgress(size, cachepair, path):
    percentage = 0
    namelist = []
    for i in range(size):
        if i > (percentage + 1) * 0.01 * size:
            percentage = np.floor(i / size * 100)
            print(f'{percentage}%')
        src, lbl = dataEnhance(
            *cachepair[int(len(cachepair) * np.random.random())])
        name = DataCollector.geneName()
        savemat(src * 255, name, rf'{path}/spl')
        savemat(lbl * 255, name, rf'{path}/lbl')
        namelist.append(name + ".png")
    save_list_to_xls(namelist, rf'{path}/all.xlsx')
    print('Done')


outpath = r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\LE2REnh"


def performDataEnh():
    makeSampleAndPrintProgress(2048, train_data.pairs, outpath)


performDataEnh()