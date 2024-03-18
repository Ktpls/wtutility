# %%
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All"
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

# %%
# %% utilkaggle
import cv2 as cv
import torch
import numpy as np
import matplotlib.pyplot as plt
import openpyxl as opx
import os
import platform
import typing
import dataclasses
import functools
import itertools


from torch.utils.tensorboard import SummaryWriter
from datetime import datetime


import time


def NormalizeImgToChanneled_CvFormat(m: cv.Mat):
    return m if len(m.shape) == 3 else m.reshape(m.shape + (1,))


def Xls2ListList(path=None, sheetname=None, killNones=True):
    if path is None:
        path = r"eles.in.xlsx"
    xls = opx.load_workbook(path)
    if sheetname is None:
        sheet = xls.active
    else:
        sheet = xls[sheetname]

    ret = [[ele.value for ele in ln] for ln in (sheet.rows)]
    if killNones:
        ret = [l for l in ret if any([e is not None for e in l])]
    return ret


def AllFileIn(path, includeFileInSubDir=True):
    import os

    ret = []
    for dirpath, dir, file in os.walk(path):
        if not includeFileInSubDir and dirpath != path:
            continue
        ret.extend([os.path.join(dirpath, f) for f in file])
    return ret


def batchsizeof(tensor):
    return tensor.shape[0]


def getDeviceInfo():
    # Get CPU info
    cpu_info = platform.processor()
    num_cores = os.cpu_count()
    cpu_frequency = "Not available in Python standard library"

    # Get GPU info
    try:
        gpu_info = torch.cuda.get_device_name()
    except:
        gpu_info = "No GPU detected"

    return (
        f"CPU Info: {cpu_info}, Cores: {num_cores}, Frequency: {cpu_frequency}\n"
        + f"GPU Info: {gpu_info}"
    )


class nestedPyPlot:

    def __init__(self, outtershape, innershape, fig) -> None:
        self.oshape = np.array(outtershape)
        self.ishape = np.array(innershape)
        self.realsize = self.oshape * self.ishape
        self.fig = fig

    def subplot(self, o, i):
        maincoor = np.array((int(o / self.oshape[1]), o % self.oshape[1]))
        subcoor = np.array((int(i / self.ishape[1]), i % self.ishape[1]))
        realcoor = self.ishape * maincoor + subcoor
        # plt.subplot(self.realsize[0], self.realsize[1], realcoor[0]
        #             * self.realsize[1]+realcoor[1]+1)
        ax = self.fig.add_subplot(
            self.realsize[0],
            self.realsize[1],
            realcoor[0] * self.realsize[1] + realcoor[1] + 1,
        )
        return ax


def setModel(model, path=None, device="cpu"):
    import os

    if path is None:
        print(f"Path==None")
        return model
    elif not os.path.exists(path):
        print(f"Warning: Path {path} not exist. Set model default")
        return model
    else:
        print(f"Loading existed nn {path}")
        model.load_state_dict(torch.load(path, map_location=torch.device(device)))
        # torch.load with map_location=torch.device('cpu')
        return model


def tensorimg2ndarray(m):
    m = np.array(m)
    m = np.moveaxis(m, -3, -1)
    return m


def spectrumDecompose(s, psize):
    if type(s) is int:
        s = torch.tensor([s])
    batchsize = s.shape[0]
    s = s.reshape((batchsize, 1))
    return torch.zeros([batchsize, psize], dtype=torch.float).scatter_(
        dim=-1, index=s, src=torch.ones_like(s, dtype=torch.float)
    )


def batchsizeof(tensor):
    return tensor.shape[0]


class nestedPyPlot:
    def __init__(self, outtershape, innershape, fig) -> None:
        self.oshape = np.array(outtershape)
        self.ishape = np.array(innershape)
        self.realsize = self.oshape * self.ishape
        self.fig = fig

    def subplot(self, o, i):
        maincoor = np.array((int(o / self.oshape[1]), o % self.oshape[1]))
        subcoor = np.array((int(i / self.ishape[1]), i % self.ishape[1]))
        realcoor = self.ishape * maincoor + subcoor
        # plt.subplot(self.realsize[0], self.realsize[1], realcoor[0]
        #             * self.realsize[1]+realcoor[1]+1)
        ax = self.fig.add_subplot(
            self.realsize[0],
            self.realsize[1],
            realcoor[0] * self.realsize[1] + realcoor[1] + 1,
        )
        return ax


def setModule(model, path=None, device=None):
    import os

    if device is None:
        device = "cpu"

    if path is None:
        print(f"Path==None")
    elif not os.path.exists(path):
        print(f"Warning: Path {path} not exist. Set model default")
    else:
        print(f"Loading existed nn {path}")
        model.load_state_dict(torch.load(path, map_location=torch.device(device)))
    return model.to(device)


def tensorimg2ndarray(m):
    m = m.cpu().numpy()
    m = np.moveaxis(m, -3, -1)
    return m


class skiper(torch.nn.Module):
    def __init__(self, component, n_i, n_o) -> None:
        super().__init__()
        self.component = component
        self.combiner = torch.nn.Conv2d(n_i + n_o, n_o, 1)

    def forward(self, m):
        # [b,c,h,w]
        processed = self.component.forward(m)
        c = torch.concat([processed, m], dim=-3)
        result = self.combiner.forward(c)
        return result


class cbr(torch.nn.Module):
    def __init__(self, n_i, n_o, n_c) -> None:
        super().__init__()
        self.component = torch.nn.Sequential(
            torch.nn.Conv2d(n_i, n_o, n_c, padding="same", bias=False),
            torch.nn.BatchNorm2d(n_o),
            torch.nn.LeakyReLU(),
        )

    def forward(self, m):
        # [b,c,h,w]
        return self.component.forward(m)


class cbrps(torch.nn.Module):
    # input chan, output chan, convolve size, pooling size
    # n_o should be like 2*n, cuz maxpool will be concated with former output
    def __init__(self, n_i, n_o, n_c, n_p) -> None:
        super().__init__()
        self.component = torch.nn.Sequential(
            torch.nn.Conv2d(n_i, n_o, n_c, padding="same", bias=False),
            torch.nn.BatchNorm2d(n_o),
            torch.nn.LeakyReLU(),
            skiper(torch.nn.MaxPool2d(n_p, stride=1, padding=int(n_p / 2)), n_o, n_o),
        )

    def forward(self, m):
        # [b,c,h,w]
        return self.component.forward(m)


class inception(torch.nn.Module):
    def __init__(
        self,
        infeat,
        outfeat11,
        outfeatpool,
        outfeat33,
        outfeat55,
        isbn=True,
        version=None,
    ) -> None:
        super().__init__()
        self.infeat = infeat
        self.outfeat11 = outfeat11
        self.outfeatpool = outfeatpool
        self.outfeat33 = outfeat33
        self.outfeat55 = outfeat55
        self.isbn = isbn
        if version is None:
            version = "v2"
        self.version = version
        if version == "v2":
            self.path11 = torch.nn.Sequential(
                torch.nn.Conv2d(infeat, outfeat11, 1, padding="same"),
                torch.nn.LeakyReLU(),
            )
            self.pathpool = torch.nn.Sequential(
                torch.nn.MaxPool2d(3, stride=1, padding=1),
                torch.nn.Conv2d(infeat, outfeatpool, 1, padding="same"),
                torch.nn.LeakyReLU(),
            )
            self.path33 = torch.nn.Sequential(
                torch.nn.Conv2d(infeat, infeat, 1, padding="same"),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(infeat, outfeat33, 3, padding="same"),
                torch.nn.LeakyReLU(),
            )
            self.path55 = torch.nn.Sequential(
                torch.nn.Conv2d(infeat, infeat, 1, padding="same"),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(infeat, outfeat55, 3, padding="same"),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat55, outfeat55, 3, padding="same"),
                torch.nn.LeakyReLU(),
            )
        elif version == "v3":
            self.path11 = torch.nn.Sequential(
                torch.nn.Conv2d(infeat, outfeat11, 1, padding="same"),
                torch.nn.LeakyReLU(),
            )
            self.pathpool = torch.nn.Sequential(
                torch.nn.MaxPool2d(3, stride=1, padding=1),
                torch.nn.Conv2d(infeat, outfeatpool, 1, padding="same"),
                torch.nn.LeakyReLU(),
            )
            self.path33 = torch.nn.Sequential(
                torch.nn.Conv2d(infeat, outfeat55, 1, padding="same"),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat55, outfeat33, [1, 3], padding="same"),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat33, outfeat33, [3, 1], padding="same"),
                torch.nn.LeakyReLU(),
            )
            self.path55 = torch.nn.Sequential(
                torch.nn.Conv2d(infeat, outfeat55, 1, padding="same"),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat55, outfeat55, [1, 3], padding="same"),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat55, outfeat55, [3, 1], padding="same"),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat55, outfeat55, [1, 3], padding="same"),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat55, outfeat55, [3, 1], padding="same"),
                torch.nn.LeakyReLU(),
            )
        else:
            raise ValueError(f"{version} not supported")
        if isbn is not None and isbn:
            self.bn = torch.nn.BatchNorm2d(
                outfeat11 + outfeatpool + outfeat33 + outfeat55
            )
        else:
            self.bn = None

    @staticmethod
    def even(infeat, outfeat, bn=None, version=None):
        assert outfeat % 4 == 0
        outfeatby4 = outfeat // 4
        return inception(
            infeat, outfeatby4, outfeatby4, outfeatby4, outfeatby4, bn, version
        )

    def forward(self, m):
        o = torch.concat(
            [self.path11(m), self.pathpool(m), self.path33(m), self.path55(m)], dim=-3
        )
        if self.bn is not None:
            o = self.bn(o)
        return o  # channel


class res_through(torch.nn.Module):
    _modules = {}

    def __init__(self, *components, combiner=None) -> None:
        super().__init__()
        self.components = components
        for idx, module in enumerate(components):
            self.add_module(str(idx), module)
        if combiner is None:

            def combiner_add(last, current):
                return last + current

            combiner = combiner_add
        self.combiner = combiner

    def forward(self, m):
        o = m
        for i, l in enumerate(self.components):
            ret = l(o)
            o = self.combiner(o, ret)
        return o


class ModuleFunc(torch.nn.Module):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def forward(self, x):
        return self.func(x)


class trainpipe:
    @staticmethod
    def train(
        dataloader,
        optimizer,
        calcLossFoo,
        epochnum=6,
        outputperbatchnum=100,
        customSubOnOutput=None,
    ):
        epochs = epochnum
        start_time = time.time()
        for ep in range(epochs):
            print(f"Epoch {ep+1}")
            print("-------------------------------")

            # train
            for batch, datatuple in enumerate(dataloader):
                loss = calcLossFoo(batch, datatuple)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                if batch % outputperbatchnum == 0:
                    end_time = time.time()
                    print(f"Batch {batch}/{len(dataloader)}")
                    print(
                        f"Training speed: {outputperbatchnum/(end_time-start_time):>5f} batches per second"
                    )
                    aveloss = loss.item() / batchsizeof(datatuple[0])
                    print(f"Average loss: {aveloss:>7f}")
                    if customSubOnOutput is not None:
                        customSubOnOutput(batch, aveloss)
                    start_time = time.time()

        # win32api.Beep(1000, 1000)
        print("Done!")


EPS = 1e-10
import time


class perf_statistic:
    """
    calculate the time past between start() to now, directly by perf_counter()-starttime
    record all accumulated time before start(), but uncleared after stop()
    so start and stop are also playing roles as resume and pause
    countcycle() will increase the cycle count, helping to calculate average time in a loop-like task
    clear() will clear all accumulated time, stops counting
    """

    def __init__(self, startnow=False):
        self.clear()
        if startnow:
            self.start()

    def clear(self):
        self._starttime = None
        self._stagedtime = 0
        self._cycle = 0
        return self

    def start(self):
        self._starttime = time.perf_counter()
        return self

    def countcycle(self):
        self._cycle += 1
        return self

    def stop(self):
        if self._starttime is None:
            return
        self._stagedtime += self._timeCurrentlyCounting()
        self._starttime = None
        return self

    def time(self):
        return self._stagedtime + self._timeCurrentlyCounting()

    def aveTime(self):
        return self.time() / (self._cycle if self._cycle > 0 else 1)

    def _timeCurrentlyCounting(self):
        return (
            time.perf_counter() - self._starttime if self._starttime is not None else 0
        )


class Progress:
    """
    irreversable!
    """

    def __init__(self, total: float, cur=0, printPercentageStep: float = 0.1) -> None:
        self.total = total
        self.nowStage = 0
        self.printPercentageStep = printPercentageStep
        self.cur = cur
        self.ps = perf_statistic()

    def update(self, current: float) -> None:
        self.cur = current
        while True:
            if current / self.total > self.nowStage * self.printPercentageStep:
                self.nowStage += 1
                self.ps.stop()
                if current > 1:
                    # not the first time
                    instantSpeed = (self.printPercentageStep * self.total) / (
                        self.ps.time() + EPS
                    )
                else:
                    instantSpeed = 1
                self.ps.clear().start()
                print(
                    f"{100 * current / self.total:>3.2f}% of {self.total}, {instantSpeed:.2f}it/s",
                    end="\n",
                )
            else:
                break

    def setFinish(self):
        self.update(self.total)


def Deduplicate(l: list):
    return list(set(l))


class Stream:
    content: list
    actions: list

    def __init__(self, iter: list | tuple | dict) -> None:
        if isinstance(iter, (list, tuple)):
            self.content = iter
        elif isinstance(iter, dict):
            self.content = iter.items()
        else:
            raise TypeError("iter must be list|tuple|dict")

    def sort(self, pred: typing.Callable[[typing.Any, typing.Any], int]):
        self.content.sort(key=functools.cmp_to_key(pred))
        return self

    def peek(self, pred: typing.Callable[[typing.Any], None]):
        for i in self.content:
            pred(i)
        return self

    def filter(self, pred: typing.Callable[[typing.Any], bool]):
        self.content = list(filter(pred, self.content))
        return self

    def map(self, pred: typing.Callable[[typing.Any], typing.Any]):
        self.content = list(map(pred, self.content))
        return self

    def flatMap(self, pred: "typing.Callable[[typing.Any],Stream]"):
        self.content = list(
            itertools.chain.from_iterable([s.content for s in map(pred, self.content)])
        )
        return self

    def distinct(self):
        self.content = Deduplicate(self.content)
        return self

    class Collector:
        def __init__(self, collectImpl):
            self.collectImpl = collectImpl

        def do(self, stream):
            return self.collectImpl(stream)

        @staticmethod
        def toList():
            return Stream.Collector(lambda stream: list(stream.content))

        @staticmethod
        def toDict(keyPred, valuePred):
            return Stream.Collector(
                lambda stream: {keyPred(i): valuePred(i) for i in stream.content}
            )

        @staticmethod
        def groupBy(keyPred):
            return Stream.Collector(
                lambda stream: {
                    key: list(group)
                    for key, group in itertools.groupby(
                        sorted(stream.content, key=keyPred), key=keyPred
                    )
                }
            )

    def collect(self, collector: "Stream.Collector"):
        return collector.do(self)


# %%
# %% nntracker_common
from torchvision.transforms import ToTensor

from torch.utils.data import Dataset
import numpy as np


class ImgReader:
    def read(self, path): ...


class ImgReaderFolder(ImgReader):
    def __init__(self, folder):
        self.folder = folder

    def read(self, path):
        m = os.path.join(self.folder, path)
        m = cv.imread(m, 1)
        m = m.astype(np.float32) / 255
        return m


class ImgReaderZip(ImgReader):
    def __init__(self, zipf):
        from zipfile import ZipFile

        self.zipf = ZipFile(zipf)

    def read(self, path):
        m = self.zipf.read(path)
        m = np.frombuffer(m, dtype=np.uint8)
        m = cv.imdecode(m, 1)
        m = m.astype(np.float32) / 255
        return m


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


def lbl2PlaneInfo(lbl: np.ndarray):
    h, w = lbl.shape
    X = np.arange(w).reshape(1, 1, w)
    Y = np.arange(h).reshape(1, h, 1)
    lblsurface = lbl.sum(axis=(-1, -2), keepdims=True) + 1
    meanX = (lbl * X).sum(axis=(-1, -2), keepdims=True) / lblsurface
    meanY = (lbl * Y).sum(axis=(-1, -2), keepdims=True) / lblsurface
    meanX = meanX[0, 0, 0] / w
    meanY = meanY[0, 0, 0] / h
    wingSpan = estimateWingSpan(lbl) / w
    isObj = 1 if lbl.sum() > 10 else 0
    return (
        isObj,
        meanX,
        meanY,
        wingSpan,
    )


def planeInfo2Lbl(tup, lblShape):
    h, w = lblShape
    isObj, meanX, meanY, wingSpan = tup
    meanX = meanX * w
    meanY = meanY * h
    wingSpan = wingSpan * w
    lbl = np.zeros(lblShape + [1], dtype=np.float32)
    X = np.arange(w).reshape(1, w, 1)
    Y = np.arange(h).reshape(h, 1, 1)
    dist = np.sqrt((X - meanX) ** 2 + (Y - meanY) ** 2)
    lbl[dist < wingSpan / 2] = 1
    return lbl


@dataclasses.dataclass
class SampleItem:
    name: str
    spl: np.ndarray
    lbl: np.ndarray
    pi: tuple


import copy


def dataAug(src, lbl):
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

    def gaussianNoise(src):
        noise = np.random.normal(0, 0.2, src.shape)
        src = np.clip(src + noise, 0, 1, dtype=np.float32)
        return src

    src = gaussianNoise(src)

    return src, lbl


class labeldataset(Dataset):

    def __init__(self) -> None:
        super().__init__()

    def init(
        self,
        path,
        selection,
        size,
        pathtype="fld",
        sheetname=None,
        stdShape=None,
        rtDataAugOn=None,
    ):
        self.size = size
        if rtDataAugOn is None:
            rtDataAugOn = False
        self.rtDataAugOn = rtDataAugOn
        selection = Xls2ListList(selection, sheetname)
        selection = [s[0] for s in selection]
        selection = [s for s in selection if s is not None]
        self.names = selection
        reader: ImgReader = None
        if pathtype == "fld":
            reader = ImgReaderFolder(path)
        elif pathtype == "zip":
            reader = ImgReaderZip(path)
        else:
            raise TypeError(f"inproper path type {pathtype}")

        items = []
        prog = Progress(len(selection))
        for i, p in enumerate(selection):
            spl = reader.read(f"spl/{p}")
            lbl = reader.read(f"lbl/{p}")

            if stdShape is not None:
                spl = cv.resize(spl, stdShape)
                lbl = cv.resize(lbl, stdShape)
                lbl = cv.threshold(lbl[:, :, 0:1], 0.5, 1, cv.THRESH_BINARY)[1]
            pi = lbl2PlaneInfo(lbl)
            items.append(SampleItem(p, spl, lbl, pi))
            prog.update(i)
        self.items = items
        prog.setFinish()

        return self

    def __len__(self):
        return self.size

    def rtDataAug(self, item: SampleItem):
        item = copy.deepcopy(item)
        item.spl, item.lbl = dataAug(item.spl, item.lbl)
        item.lbl = item.lbl[:, :, 0]
        item.pi = lbl2PlaneInfo(item.lbl)
        return item

    @staticmethod
    def procItemToTensor(item):
        return (
            ToTensor()(item.spl),
            ToTensor()(item.lbl),
            torch.tensor(item.pi, dtype=torch.float32),
        )

    def __getitem__(self, idx):
        index = self.rndIndex()
        item = self.items[index]
        if self.rtDataAugOn:
            item = self.rtDataAug(item)
        return labeldataset.procItemToTensor(item)

    def rndIndex(self):
        return int(len(self.items) * np.random.random())

    def rawlength(self):
        return len(self.items)

    def rawgetitem(self, rawidx):
        return self.items[rawidx]

    def getname(self, rawidx):
        return self.names[rawidx]


def XYWH2XYXY(X, Y, W, H):
    return (X - W / 2, Y - H / 2, X + W / 2, Y + H / 2)


def XYXY2XYWH(x1, y1, x2, y2):
    return (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1


def AABBOf(lbl, noobjthresh=5):
    assert len(lbl.shape) == 2
    y, x = np.where(lbl > 0)
    if len(y) < noobjthresh:
        return (0, 0, 0, 0, 0)
    x1, x2 = np.min(x), np.max(x)
    y1, y2 = np.min(y), np.max(y)
    # (x1, x2, y1, y2, c)

    return XYXY2XYWH(x1, y1, x2, y2) + (1,)


# %%
# %% nntracker

from torch import nn
import torch.nn.functional as F
import functools
import torchvision

print(getDeviceInfo())

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

# %%
# nn def


class BaseModule4NNTracker:
    stdShape = [128, 128]


def PositionalEmbedding2D(shape, depth, len_max=None):
    if len_max is None:
        len_max = 10000
    h, w = shape
    y = np.arange(0, h).reshape([-1, 1, 1])
    x = np.arange(0, w).reshape([1, -1, 1])
    d = np.arange(0, depth).reshape([1, 1, -1])
    pe = np.zeros(list(shape) + [depth], np.float32)

    def BroadCastToBeLikePe(vec):
        return np.zeros_like(pe) + vec

    d_like_pe = BroadCastToBeLikePe(d)

    sinx = np.sin(x / (len_max ** (d / depth)))
    cosx = np.cos(x / (len_max ** ((d - 1) / depth)))
    siny = np.sin(y / (len_max ** (d / depth)))
    cosy = np.cos(y / (len_max ** ((d - 1) / depth)))
    evens = BroadCastToBeLikePe(sinx) + BroadCastToBeLikePe(siny)
    odds = BroadCastToBeLikePe(cosx) + BroadCastToBeLikePe(cosy)
    pe[d_like_pe % 2 == 0] = evens[d_like_pe % 2 == 0]
    pe[d_like_pe % 2 == 1] = odds[d_like_pe % 2 == 1]

    return pe.reshape([1, -1, depth])


class SemanticInjectionModule(torch.nn.Module):
    def __init__(self, localdim, globaldim=None, outdim=None):
        if globaldim is None:
            globaldim = localdim
        if outdim is None:
            outdim = localdim
        self.localdim = localdim
        self.globaldim = globaldim
        self.outdim = outdim
        super().__init__()
        self.local = nn.Sequential(
            nn.Conv2d(localdim, outdim, 1),
        )
        self.global1 = nn.Sequential(
            nn.Conv2d(globaldim, outdim, 1),
            nn.Sigmoid(),
        )
        self.global2 = nn.Sequential(
            nn.Conv2d(globaldim, outdim, 1),
        )
        self.bn = nn.BatchNorm2d(outdim)

    def forward(self, local, globalsemantic):
        x = self.local(local) * self.global1(globalsemantic) + self.global2(
            globalsemantic
        )
        return self.bn(x)


class AddPositionalEmbedding(nn.Module):
    def __init__(self, shape, depth, len_max=None):
        super().__init__()
        self.pe = nn.Parameter(
            torch.tensor(
                PositionalEmbedding2D(shape, depth, len_max),
                dtype=torch.float32,
                requires_grad=False,
            )
        )

    def forward(self, x):
        return x + self.pe


class PermuteModule(nn.Module):
    def __init__(self, dims):
        super().__init__()
        self.dims = dims

    def forward(self, x):
        return torch.permute(x, self.dims)


class nntracker_pi(torch.nn.Module):
    def __init__(self):
        super().__init__()
        useBn = True
        incver = "v3"
        self.mod = nn.Sequential(
            # 128
            inception.even(3, 8, bn=useBn, version=incver),
            res_through(
                inception.even(8, 8, bn=useBn, version=incver),
                inception.even(8, 8, bn=useBn, version=incver),
            ),
            nn.MaxPool2d(2),  # 64
            inception.even(8, 16, bn=useBn, version=incver),
            res_through(
                inception.even(16, 16, bn=useBn, version=incver),
                inception.even(16, 16, bn=useBn, version=incver),
            ),
            nn.MaxPool2d(2),  # 32
            inception.even(16, 32, bn=useBn, version=incver),
            res_through(
                inception.even(32, 32, bn=useBn, version=incver),
                inception.even(32, 32, bn=useBn, version=incver),
            ),
            nn.MaxPool2d(2),  # 16
            inception.even(32, 64, bn=useBn, version=incver),
            res_through(
                inception.even(64, 64, bn=useBn, version=incver),
                inception.even(64, 64, bn=useBn, version=incver),
            ),
            PermuteModule((0, 2, 3, 1)),
            nn.Flatten(1, 2),  # keep depth unflattened
            AddPositionalEmbedding((16, 16), 64, None),
            nn.TransformerEncoderLayer(64, 8, 16),
            nn.TransformerEncoderLayer(64, 8, 16),
            nn.TransformerEncoderLayer(64, 8, 16),
            nn.TransformerEncoderLayer(64, 8, 16),
            nn.Flatten(1, -1),
            nn.Linear(64 * 16**2, 4096),
            nn.LeakyReLU(),
            nn.Linear(4096, 1000),
            nn.LeakyReLU(),
            nn.Linear(1000, 4),
            nn.LeakyReLU(),
        )

    def forward(self, m):
        out = self.mod(m)
        return out


class nntracker_respi(torch.nn.Module):
    def __init__(
        self,
        frozenLayers=(
            "conv1",
            "bn1",
            "relu",
            "maxpool",
            "layer1",
            "layer2",
            "layer3",
            "layer4",
        ),
    ):
        super().__init__()
        weights = torchvision.models.ResNet18_Weights.DEFAULT
        backbone = torchvision.models.resnet18(weights=weights)
        backboneOutShape = 512
        for name, param in backbone.named_parameters():
            matched = False
            for fl in frozenLayers:
                if name.startswith(fl):
                    param.requires_grad = False
                    matched = True
                    break
            if not matched:
                param.requires_grad = True
        self.backbone = backbone
        self.backbonepreproc = weights.transforms()

        self.mod = nn.Sequential(
            res_through(
                nn.Linear(backboneOutShape, backboneOutShape),
                nn.LeakyReLU(),
                nn.Linear(backboneOutShape, backboneOutShape),
                nn.LeakyReLU(),
            ),
            nn.Linear(backboneOutShape, 4),
            nn.LeakyReLU(),
        )

    def forward(self, m):
        m = self.backbonepreproc(m)
        m = self.backbone.conv1(m)
        m = self.backbone.bn1(m)
        m = self.backbone.relu(m)
        m = self.backbone.maxpool(m)
        m = self.backbone.layer1(m)
        m = self.backbone.layer2(m)
        m = self.backbone.layer3(m)
        m = self.backbone.layer4(m)
        m = self.backbone.avgpool(m)
        m = torch.flatten(m, 1)
        out = self.mod(m)
        return out


def getmodel(modelpath, **kwargs):
    model = setModule(nntracker_respi(**kwargs), path=modelpath, device=device)
    # print(model)
    return model


# %%

# %%  basics

from torch.utils.tensorboard import SummaryWriter
import traceback
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
import time

# %%
# %%  nn def
modelpath = r"nntracker.pth"
model = getmodel(
    modelpath,
    frozenLayers=(
        "conv1",
        "bn1",
        "relu",
        "maxpool",
        "layer1",
        "layer2",
        "layer3",
        # "layer4",
    ),
)
writer = SummaryWriter(f"runs/{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}")


# %%
# %% dataset
@dataclasses.dataclass
class NnTrackerDataset:
    path: str
    sel: str
    datasettype: str


print("loading dataset")
datasetname = "largeEnoughToRecon"
datasetroot = r"/kaggle/input/nntrackerle2renh"
datasets = {
    "LE2REnh": NnTrackerDataset(r"LE2REnh/LE2REnh", r"LE2REnh/all.xlsx", "fld"),
    "SmallAug": NnTrackerDataset(r"SmallAug/SmallAug", r"SmallAug/all.xlsx", "fld"),
    "largeEnoughToRecon": NnTrackerDataset(
        r"largeEnoughToRecon/largeEnoughToRecon",
        r"largeEnoughToRecon/all.xlsx",
        "fld",
    ),
    "origins_nntracker": NnTrackerDataset(
        r"origins_nntracker/origins_nntracker",
        r"origins_nntracker/hardones.xlsx",
        "fld",
    ),
    "withaimingring": NnTrackerDataset(
        r"withaimingring/withaimingring", r"withaimingring/xls.xlsx", "fld"
    ),
}
train_data = datasets[datasetname]
train_data = labeldataset().init(
    os.path.join(datasetroot, train_data.path),
    os.path.join(datasetroot, train_data.sel),
    8192,
    train_data.datasettype,
    None,
    BaseModule4NNTracker.stdShape,
    rtDataAugOn=True,
)
test_data = datasets["largeEnoughToRecon"]
test_data = labeldataset().init(
    os.path.join(datasetroot, test_data.path),
    os.path.join(datasetroot, test_data.sel),
    32,
    test_data.datasettype,
    None,
    BaseModule4NNTracker.stdShape,
    rtDataAugOn=True,
)
print("load finished")


# %%

# %%  dataloader
# for easier modify batchsize without reloading all samples
batch_size = 2
train_dataloader = DataLoader(train_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=32)


# %%

# %% lossFunc


def calclose(pi, pihat):
    (
        isObj,
        meanX,
        meanY,
        wingSpan,
    ) = (
        pi[:, 0],
        pi[:, 1],
        pi[:, 2],
        pi[:, 3],
    )

    coef = torch.ones_like(
        pi,
        dtype=torch.float32,
        device=device,
        requires_grad=False,
    )
    # enphasize wing span
    coef[:, 3] = 3
    # dont estimate pos and size when is no object
    coef[isObj != 1, 1:] = 0
    coef[isObj != 1, 0] = 6

    loss = torch.sum(((pihat - pi) ** 2) * coef)
    # loss = torch.log10(loss + 1e-10)
    return loss


# %%

# %% train


def trainmainprogress(batch, datatuple):
    model.train()
    src, lbl, pi = datatuple
    src = src.to(device)
    lbl = lbl.to(device)
    pi = pi.to(device)
    pihat = model.forward(src)
    loss = calclose(pi, pihat)
    return loss


def onoutput(batch, aveerr):
    # return
    with torch.no_grad():
        model.eval()
        lossTotal = 0
        numTotal = 0
        for src, lbl, pi in test_dataloader:
            src = src.to(device)
            lbl = lbl.to(device)
            pi = pi.to(device)
            pihat = model.forward(src)
            lossTotal += calclose(pi, pihat).item()
            numTotal += batchsizeof(src)
            break
    print(f"testaveerr: {lossTotal/numTotal}")
    # writer.add_scalar("aveerr", aveerr, batch)


trainpipe.train(
    train_dataloader,
    torch.optim.AdamW(
        filter(lambda x: x.requires_grad is not False, model.parameters()),
        lr=1e-4,
        weight_decay=1e-2,
    ),
    trainmainprogress,
    customSubOnOutput=onoutput,
    epochnum=100 * 2,
)

# %%

# %% save


def savemodel(path):
    torch.save(model.state_dict(), path)
    print(f"Saved PyTorch Model State to {path}")


savemodel(modelpath)


# %%
# %%
# all the continious running should only be applied on codes above! plz stop here
if __name__ == "__main__":
    exit()

# %%
# %% view effect


def viewmodel(datasetusing):
    model.eval()

    plotShape = [7, 4]
    subplotShape = [1, 2]
    samplenum = np.prod(plotShape)
    npp = nestedPyPlot(plotShape, subplotShape, plt.figure(figsize=(20, 20)))
    imshowconfig = {"vmin": 0, "vmax": 1}
    totalinferencetime = 0
    infercount = 0

    def PI2Str(pi):
        return ",".join([f"{i:.2f}" for i in pi])

    with torch.no_grad():
        for i in range(samplenum):
            src, lbl, pi = datasetusing[0]
            tstart = time.perf_counter()
            pihat = model.forward(src.reshape((1,) + src.shape).to(device))
            totalinferencetime += time.perf_counter() - tstart
            infercount += 1
            pihat = pihat[0].cpu().numpy()

            pi = pi.numpy()
            src, lbl = [tensorimg2ndarray(d) for d in [src, lbl]]

            # lblFromPi = planeInfo2Lbl(pi, BaseModule4NNTracker.stdShape)
            lblhat = planeInfo2Lbl(pihat, BaseModule4NNTracker.stdShape)
            npp.subplot(i, 0)
            plt.title(PI2Str(pi))
            plt.imshow(cv.cvtColor(src, cv.COLOR_BGR2RGB))
            npp.subplot(i, 1)
            lblComparasion = (
                np.array(
                    [
                        lbl,
                        # lblFromPi,
                        np.zeros_like(lbl),
                        lblhat,
                    ]
                )
                .squeeze(-1)
                .transpose([1, 2, 0])
            )

            plt.title(PI2Str(pihat))
            plt.imshow(lblComparasion, label="lblComparasion", **imshowconfig)
    print(f"average inference time={totalinferencetime / samplenum}")


viewmodel(datasetusing=test_data)


# %%
# %%
import os


def rmModel():
    os.remove(modelpath)


rmModel()
