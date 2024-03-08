RunOnWtUtilityEnviroment = True
if RunOnWtUtilityEnviroment:
    from utilref import *

    pass
else:
    # from utilkaggle import *
    pass
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
    return (meanX, meanY, wingSpan)


def planeInfo2Lbl(tup, lblShape):
    h, w = lblShape
    meanX, meanY, wingSpan = tup
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
        item=copy.deepcopy(item)
        noise=np.random.normal(0,0.2,item.spl.shape)
        item.spl+=noise
        item.spl=np.clip(item.spl,0,1)
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
