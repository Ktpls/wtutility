# %%
# perform dataenh
from utilref import *
from nntracker_common import labeldataset
import hashlib


def anySeed(seed):
    seed = hashlib.sha256(str(seed).encode()).digest()
    seed = int.from_bytes(seed)
    return seed


generator = np.random.default_rng(seed=anySeed(42))


def dataEnhance(src, lbl, prog:Progress=None):
    if prog is not None:
        prog.update(prog.cur+1)
    backcolor = np.mean(src, axis=(0, 1), keepdims=True)

    planeColor = np.sum(src * lbl, axis=(0, 1), keepdims=True) / np.sum(
        lbl, axis=(0, 1), keepdims=True
    )

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
        .collect(Stream.Collector.toList())  # add back channel
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

    # rand spot
    def randSpot(spl, lbl):
        import scipy.interpolate as ipl

        @dataclasses.dataclass
        class BaseFunc:
            amp: float = 1
            freq: float = 1

            def __call__(self, x):
                pass

        @dataclasses.dataclass
        class CombinedWave(BaseFunc):
            base: list[BaseFunc] = dataclasses.field(default_factory=list)

            def __call__(self, x) -> Any:
                return self.amp * (
                    np.sum([w(self.freq * x) for w in self.base], axis=0)
                )

        @dataclasses.dataclass
        class Interpolated2d(BaseFunc):
            """
            assert points are in order of x, y, z
            freq does not work. it should be done with points provider
            """

            points: np.ndarray = None

            def __call__(self, x: tuple[np.ndarray]):
                ret = self.amp * ipl.griddata(
                    self.points[:, 0:2],
                    self.points[:, 2],
                    (x[0], x[1]),
                    fill_value=0,
                    method="cubic",
                )
                return ret

            @staticmethod
            def SuggestedPointNum(freq):
                """
                discussing with 1 dimentional sin wave, so for freq=1, we will need two sample points
                and for higher freq, points adds up linearly
                as for 2 dimention, use n^2
                """
                ret = np.round((freq * 2) ** 2).astype(np.int32)
                if ret < 4:
                    ret = 4
                return ret

            @staticmethod
            def SuggestedFreqAccordingToPointNum(point_num):
                return point_num**0.5 / 2

        class makeWaveFunc:
            @staticmethod
            def make(
                amp_base,
                amp_lambda,
                freq_base,
                freq_lambda,
                base_num,
            ) -> CombinedWave:
                return CombinedWave(
                    base=[
                        Interpolated2d(
                            points=np.random.uniform(
                                -1,
                                1,
                                [
                                    Interpolated2d.SuggestedPointNum(
                                        freq_base * freq_lambda**i
                                    ),
                                    3,
                                ],
                            ),
                            amp=amp_base * amp_lambda**i,
                            freq=None,
                        )
                        for i in range(base_num)
                    ]
                )

        """
        for 1d linear interpolate sampled with 2 points, radius of shape above thresh will be 0.5-thresh/2=0.5*(1-thresh)
        for n points, radius = 0.5*(1-thresh)/(n/2)
        """
        lbl = lbl[:, :, 0]
        X, Y = np.meshgrid(
            np.linspace(-1, 1, spl.shape[0]), np.linspace(-1, 1, spl.shape[1])
        )
        planeRadius = (1 - -1) * ((np.sum(lbl) / np.pi) ** 0.5) / spl.shape[0]
        if planeRadius < 0.01:
            # no plane
            return spl
        # thresh controls the area ratio of noise
        thresh = 0.8
        pointNum1d = 2 * 0.5 * (1 - thresh) / planeRadius
        sampleBaseFreq = (
            Interpolated2d.SuggestedFreqAccordingToPointNum(pointNum1d**2) * 2
        )
        Noise = (
            makeWaveFunc.make(
                1,
                0.8,
                sampleBaseFreq,
                np.sqrt(2.2),
                5,
            )((X, Y))
            > thresh
        )
        aroundLbl = regionave(lbl, (13, 13)) > 0.05
        Noise[aroundLbl] = False

        spl[Noise] = planeColor
        return spl

    src = randSpot(src, lbl)

    lbl[lbl < 0.5] = 0
    lbl[lbl >= 0.5] = 1  # thresh

    return src, lbl


xlsSource = r".\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\all.xlsx"
zipSource = (
    r".\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\largeEnoughToRecon.zip"
)
dest = r".\exp\DLOnOpdarPlaneDetection\dataset\LE2REnh"


@dataclasses.dataclass
class SampleLabelPair:
    sample: np.ndarray
    label: np.ndarray


def performDataEnh():
    nameList = []

    def saveFiles(para):
        name = DataCollector.geneName() + ".png"
        savemat(para.sample * 255, name, rf"{dest}/spl")
        savemat(para.label * 255, name, rf"{dest}/lbl")
        nameList.append(name)

    def afterProc():
        save_list_to_xls(nameList, rf"{dest}/all.xlsx")

    source = Xls2ListList(xlsSource)
    # pick some
    # sampleNum = 10
    # indexStart = int(np.random.random() * (len(source) - sampleNum))
    # source = source[indexStart : indexStart + sampleNum]
    source = (
        Stream(source)
        .filter(lambda l: l is not None and len(l) != 0)
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
        .collect(Stream.Collector.toList())
    )
    sampleNum=8192
    deProg=Progress(sampleNum)
    imgRandomDraws = list((np.random.random(sampleNum) * len(source)).astype(np.int32))
    (
        Stream(imgRandomDraws)
        .map(lambda i: source[i])
        .map(lambda p: SampleLabelPair(*dataEnhance(p.sample, p.label, deProg)))
        .peek(saveFiles)
    )
    afterProc()


performDataEnh()
# %%
