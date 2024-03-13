# %%
# perform dataenh
from utilref import *
from nntracker_common import *
import hashlib


def anySeed(seed):
    seed = hashlib.sha256(str(seed).encode()).digest()
    seed = int.from_bytes(seed)
    return seed


generator = np.random.default_rng(seed=anySeed(42))


def dataEnhance(src, lbl, prog: Progress = None):
    if prog is not None:
        prog.update(prog.cur + 1)
    backcolor = np.mean(src, axis=(0, 1), keepdims=True)

    lbl = NormalizeImgToChanneled_CvFormat(lbl)

    zoom = lambda rate: np.array(
        [[rate, 0, 0], [0, rate, 0], [0, 0, 1]],
        dtype=np.float32,
    )
    shift = lambda x, y: np.array(
        [[1, 0, x], [0, 1, y], [0, 0, 1]],
        dtype=np.float32,
    )
    flip = lambda lr, ud: np.array(
        [[lr, 0, 0], [0, ud, 0], [0, 0, 1]],
        dtype=np.float32,
    )
    rot = lambda the: np.array(
        [[np.cos(the), np.sin(the), 0], [-np.sin(the), np.cos(the), 0], [0, 0, 1]],
        dtype=np.float32,
    )
    identity = lambda: np.array(
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        dtype=np.float32,
    )

    h, w, c = lbl.shape

    X = np.arange(w).reshape(1, w, 1)
    Y = np.arange(h).reshape(h, 1, 1)
    lblTouchingEdge = np.clip(
        ((X == 0) + (X == w - 1) + (Y == 0) + (Y == h - 1)) * lbl, 0, 1
    )

    while True:

        theta = np.random.uniform(-np.pi / 2, np.pi / 2)
        zoomrate = np.random.uniform(0.75, 1.25)
        ifflip = np.random.choice([1, -1], size=2, replace=True)
        movvec = np.random.uniform(-50, 50, size=2)

        src1, lbl1, lte1 = (
            Stream([src, lbl, lblTouchingEdge])
            .map(
                lambda m: cv.warpAffine(
                    m,
                    (
                        shift(0.5 * w, 0.5 * h)
                        @ flip(*ifflip)
                        @ shift(*movvec)
                        @ zoom(zoomrate)
                        @ rot(theta)
                        @ shift(-0.5 * w, -0.5 * h)
                    )[0:2, :],
                    np.flip(m.shape[0:2]),
                    borderMode=cv.BORDER_REPLICATE,
                )
            )
            .map(NormalizeImgToChanneled_CvFormat)
            .collect(Stream.Collector.toList())
        )

        lbl1[lbl1 < 0.5] = 0
        lbl1[lbl1 >= 0.5] = 1  # thresh

        # check
        # expect edge of plane wont be processed with boundary technique
        notTouching = np.sum(lte1) <= 8

        if notTouching:
            src, lbl = src1, lbl1
            break

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

    # # rand spot
    # def randSpot(spl, lbl):
    #     import scipy.interpolate as ipl
    #     planeColor = np.sum(src * lbl, axis=(0, 1), keepdims=True) / np.sum(
    #         lbl, axis=(0, 1), keepdims=True
    #     )

    #     @dataclasses.dataclass
    #     class BaseFunc:
    #         amp: float = 1
    #         freq: float = 1

    #         def __call__(self, x):
    #             pass

    #     @dataclasses.dataclass
    #     class CombinedWave(BaseFunc):
    #         base: list[BaseFunc] = dataclasses.field(default_factory=list)

    #         def __call__(self, x) -> Any:
    #             return self.amp * (
    #                 np.sum([w(self.freq * x) for w in self.base], axis=0)
    #             )

    #     @dataclasses.dataclass
    #     class Interpolated2d(BaseFunc):
    #         """
    #         assert points are in order of x, y, z
    #         freq does not work. it should be done with points provider
    #         """

    #         points: np.ndarray = None

    #         def __call__(self, x: tuple[np.ndarray]):
    #             ret = self.amp * ipl.griddata(
    #                 self.points[:, 0:2],
    #                 self.points[:, 2],
    #                 (x[0], x[1]),
    #                 fill_value=0,
    #                 method="cubic",
    #             )
    #             return ret

    #         @staticmethod
    #         def SuggestedPointNum(freq):
    #             """
    #             discussing with 1 dimentional sin wave, so for freq=1, we will need two sample points
    #             and for higher freq, points adds up linearly
    #             as for 2 dimention, use n^2
    #             """
    #             ret = np.round((freq * 2) ** 2).astype(np.int32)
    #             if ret < 4:
    #                 ret = 4
    #             return ret

    #         @staticmethod
    #         def SuggestedFreqAccordingToPointNum(point_num):
    #             return point_num**0.5 / 2

    #     class makeWaveFunc:
    #         @staticmethod
    #         def make(
    #             amp_base,
    #             amp_lambda,
    #             freq_base,
    #             freq_lambda,
    #             base_num,
    #         ) -> CombinedWave:
    #             return CombinedWave(
    #                 base=[
    #                     Interpolated2d(
    #                         points=np.random.uniform(
    #                             -1,
    #                             1,
    #                             [
    #                                 Interpolated2d.SuggestedPointNum(
    #                                     freq_base * freq_lambda**i
    #                                 ),
    #                                 3,
    #                             ],
    #                         ),
    #                         amp=amp_base * amp_lambda**i,
    #                         freq=None,
    #                     )
    #                     for i in range(base_num)
    #                 ]
    #             )

    #     """
    #     for 1d linear interpolate sampled with 2 points, radius of shape above thresh will be 0.5-thresh/2=0.5*(1-thresh)
    #     for n points, radius = 0.5*(1-thresh)/(n/2)
    #     """
    #     lbl = lbl[:, :, 0]
    #     X, Y = np.meshgrid(
    #         np.linspace(-1, 1, spl.shape[0]), np.linspace(-1, 1, spl.shape[1])
    #     )
    #     planeRadius = (1 - -1) * ((np.sum(lbl) / np.pi) ** 0.5) / spl.shape[0]
    #     if planeRadius < 0.01:
    #         # no plane
    #         return spl
    #     # thresh controls the area ratio of noise
    #     thresh = 0.95
    #     pointNum1d = 2 * 0.5 * (1 - thresh) / planeRadius
    #     sampleBaseFreq = (
    #         Interpolated2d.SuggestedFreqAccordingToPointNum(pointNum1d**2) * 2
    #     )
    #     Noise = (
    #         makeWaveFunc.make(
    #             1,
    #             0.8,
    #             sampleBaseFreq,
    #             np.sqrt(2.2),
    #             5,
    #         )((X, Y))
    #         > thresh
    #     )
    #     aroundLbl = regionave(lbl, (13, 13)) > 0.05
    #     Noise[aroundLbl] = False

    #     spl[Noise] = planeColor
    #     return spl

    # src = randSpot(src, lbl)

    return src, lbl


xlsSource = r".\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\all.xlsx"
zipSource = (
    r".\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\largeEnoughToRecon.zip"
)
dest = r".\exp\DLOnOpdarPlaneDetection\dataset\LE2REnh"


def performDataEnh():
    dataset = labeldataset().init(
        zipSource,
        xlsSource,
        1,
        "zip",
        stdShape=[128] * 2,
    )
    nameList = []

    def saveFiles(para: SampleItem):
        name = DataCollector.geneName() + ".png"
        savemat(para.spl * 255, name, rf"{dest}/spl")
        savemat(para.lbl * 255, name, rf"{dest}/lbl")
        nameList.append(name)

    def saveXls():
        save_list_to_xls(nameList, rf"{dest}/all.xlsx")

    # pltshape = (9, 9)
    # fig = plt.figure(figsize=(20, 20))
    # i = 0

    # def showLbl(si: SampleItem):
    #     nonlocal i
    #     i += 1
    #     ax = fig.add_subplot(pltshape[0], pltshape[1], i)
    #     ax.imshow(si.lbl)

    sampleNum = 10000
    deProg = Progress(sampleNum)
    idxsrc = list([dataset.rndIndex() for i in range(sampleNum)])
    for i, idx in enumerate(idxsrc):
        p = dataset.rawgetitem(idx)
        p = dataEnhance(p.spl, p.lbl, deProg)
        p = SampleItem(name="", spl=p[0], lbl=p[1], pi=None)
        saveFiles(p)
        deProg.update(i)
    saveXls()


performDataEnh()
# %%
