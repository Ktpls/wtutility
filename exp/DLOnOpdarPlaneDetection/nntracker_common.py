RunOnWtUtilityEnviroment = True
if RunOnWtUtilityEnviroment:
    from utilref import *
else:
    # from utilkaggle import *
    pass
from torchvision.transforms import ToTensor

from torch.utils.data import Dataset


def readImgInFolder(folder, pathlist):
    mlist = [os.path.join(folder, m) for m in pathlist]
    mlist = [cv.imread(m, 1) for m in mlist]
    mlist = [m.astype(np.float32) / 255 for m in mlist]
    return mlist


def readImgInZip(zipf, pathlist):
    from zipfile import ZipFile
    zipf = ZipFile(zipf)
    mlist = [zipf.read(imgf) for imgf in pathlist]
    mlist = [np.frombuffer(m, dtype=np.uint8) for m in mlist]
    mlist = [cv.imdecode(m, 1) for m in mlist]
    mlist = [m.astype(np.float32) / 255 for m in mlist]
    return mlist


class labeldataset(Dataset):

    def __init__(self) -> None:
        super().__init__()

    def init(self,
             path,
             selection,
             size,
             pathtype='fld',
             sheetname=None,
             stdShape=None):
        self.size = size
        selection = Xls2ListList(selection, sheetname)
        selection = [s[0] for s in selection]
        selection = [s for s in selection if s is not None]
        self.names = selection

        if pathtype == 'fld':
            reader = readImgInFolder
        elif pathtype == 'zip':
            reader = readImgInZip
        else:
            raise TypeError(f'inproper path type {pathtype}')

        spl = reader(path, [rf'spl/{p}' for p in selection])
        lbl = reader(path, [rf'lbl/{p}' for p in selection])
        if stdShape is not None:
            spl = [cv.resize(m, stdShape) for m in spl]
            lbl = [cv.resize(m, stdShape) for m in lbl]
        lbl = [
            cv.threshold(p[:, :, 0:1], 0.5, 1, cv.THRESH_BINARY)[1]
            for p in lbl
        ]
        self.pairs = list(zip(spl, lbl))

        return self

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        index = int(len(self.pairs) * np.random.random())
        return [
            ToTensor()(i)
            for i in self.pairs[index]
        ]

    def rawlength(self):
        return len(self.pairs)

    def rawgetitem(self, rawidx):
        return self.pairs[rawidx]

    def getname(self, rawidx):
        return self.names[rawidx]


class yoloformdatafset(Dataset):

    def __init__(self) -> None:
        super().__init__()

    # #grid ,#bondingbox, width,widthofsourcepic
    def init(self,
             path,
             selection,
             size,
             S=7,
             B=1,
             W=448,
             W0=100,
             pathtype='fld',
             sheetname=None):
        self.size = size
        selection = Xls2ListList(selection, sheetname)
        selection = selection[1:]
        if len(selection) > 512:
            selection = selection[:512]
        names = [s[0] for s in selection]
        self.S, self.B, self.W, self.W0 = S, B, W, W0

        if pathtype == 'fld':
            reader = readImgInFolder
        elif pathtype == 'zip':
            reader = readImgInZip
        else:
            raise TypeError(f'inproper path type {pathtype}')

        pic = reader(path, [f'spl/{p}' for p in names])

        pairs = list(zip(pic, selection))

        def W0ToW(pair):
            img, (Name, MinX, MinY, MaxX, MaxY, CenterX, CenterY) = pair

            coors = [MinX, MinY, MaxX, MaxY, CenterX, CenterY]
            coors = map(lambda x: self.W / self.W0 * float(x), coors)
            MinX, MinY, MaxX, MaxY, CenterX, CenterY = coors

            img = cv.resize(img, (self.W, self.W))
            img = ToTensor()(img)

            grids = np.zeros([self.S, self.S, self.B * 5], np.float32)
            center = (CenterY, CenterX)
            centergrid = [int(self.S * c / self.W) for c in center]
            grids[centergrid[0], centergrid[1]] = [1, MinX, MinY, MaxX, MaxY]
            lbl = torch.tensor(grids)
            return img, lbl

        self.pairs = [W0ToW(p) for p in pairs]

        return self

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return self.pairs[int(len(self.pairs) * np.random.random())]

    def rawlength(self):
        return len(self.pairs)

    def rawgetitem(self, rawidx):
        return self.pairs[rawidx]

    def getname(self, rawidx):
        return self.names[rawidx]


def XYWH2XYXY(X, Y, W, H):
    return (X - W / 2, Y - H / 2, X + W / 2, Y + H / 2)


def XYXY2XYWH(x1, y1, x2, y2):
    return (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1


def AABBOf(lbl, noobjthresh=5):
    assert (len(lbl.shape) == 2)
    y, x = np.where(lbl > 0)
    if len(y) < noobjthresh:
        return (0, 0, 0, 0, 0)
    x1, x2 = np.min(x), np.max(x)
    y1, y2 = np.min(y), np.max(y)
    #(x1, x2, y1, y2, c)

    return XYXY2XYWH(x1, y1, x2, y2) + (1, )
