# %%
# perform dataenh
from utilref import *
from utilitypack.util_torch import *
from utilitypack.util_windows import *
from nntracker_common import labeldataset

# train_data = labeldataset().init(
#     r".\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\largeEnoughToRecon.zip",
#     r".\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\all.xlsx",
#     8192,
#     "zip",
#     stdShape=[128, 128],
# )


def dataEnhance(src, lbl):
    backcolor = np.mean(src, axis=(0, 1), keepdims=True)

    # rot
    def rot(m, the):
        # theta in [-pi/2,pi/2]
        # assert right squared img0 here
        rotmat = np.array(
            [
                [np.cos(the), -np.sin(the)],
                [np.sin(the), np.cos(the)],
            ]
        )

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

    # zoom
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

    # flip
    def flip(m, reallyflip: bool):
        if reallyflip:
            return np.flip(m, axis=1)  # flip lr
        else:
            return m

    reallyflip = np.random.rand() < 0.5

    # mov
    def mov(m, vec):
        mattr = np.array([[1, 0, vec[0]], [0, 1, vec[1]]]).astype("float")
        m = cv.warpAffine(m, mattr, np.flip(m.shape[0:2]))
        return m

    vec = np.random.uniform(-50, 50, size=2)

    src, lbl = (
        Stream([src, lbl])
        .map(lambda m: rot(m, the))
        .map(lambda m: zoom(m, rate))
        .map(lambda m: flip(m, reallyflip))
        .map(lambda m: np.ascontiguousarray(m))
        .map(lambda m: mov(m, vec))
        .map(lambda m: m if len(m.shape) == 3 else m.reshape(m.shape + (1,)))
        .collect(Stream.Collector.toList())
    )

    black_pixels = np.where(np.sum(src, axis=2) < 0.1)
    src[black_pixels] = backcolor

    # rand line
    def draw_random_line(image, n):
        height, width, _ = image.shape
        color = (0, 0, 0)  # Black color
        for l in range(n):
            start_point = (np.random.randint(0, width), np.random.randint(0, height))
            end_point = (np.random.randint(0, width), np.random.randint(0, height))
            cv.line(image, start_point, end_point, color, 1)
        return image

    src = draw_random_line(src, 5)

    lbl[lbl < 0.5] = 0
    lbl[lbl >= 0.5] = 1  # thresh

    return src, lbl


xlsSource = r".\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\all.xlsx"
zipSource = (
    r".\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\largeEnoughToRecon.zip"
)
dest = r".\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\enhanced"


@dataclasses.dataclass
class SampleLabelPair:
    sample: np.ndarray
    label: np.ndarray


def performDataEnh():

    def saveFiles(para):
        name = DataCollector.geneName() + ".png"
        savemat(para.sample * 255, name, rf"{dest}/spl")
        savemat(para.label * 255, name, rf"{dest}/lbl")

    source = Xls2ListList(xlsSource)
    # pick one
    source = [source[int(np.random.random() * len(source))]]
    (
        Stream(source)
        .map(lambda l: l[0])
        .map(
            lambda f: SampleLabelPair(
                *(
                    Stream(
                        [
                            ReadFileInZip(zipSource, f"spl/{f}"),
                            ReadFileInZip(zipSource, f"lbl/{f}"),
                        ]
                    )
                    .map(lambda i: np.frombuffer(i, dtype=np.uint8))
                    .map(lambda i: cv.imdecode(i, cv.IMREAD_COLOR))
                    .map(lambda i: i.astype(np.float32) / 255)
                    .collect(Stream.Collector.toList())
                )
            )
        )
        .map(lambda p: SampleLabelPair(*dataEnhance(p.sample, p.label)))
        .peek(saveFiles)
    )


performDataEnh()
# %%
