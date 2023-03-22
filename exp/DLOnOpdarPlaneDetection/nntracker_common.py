

from torch.utils.data import Dataset
RunOnWtUtilityEnviroment = True
if RunOnWtUtilityEnviroment:
    if __package__ == '':
        from utilref import *
    else:
        from .utilref import *
    pass
else:
    from utilkaggle import *
from torchvision.transforms import ToTensor

class labeldataset(Dataset):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def __readFileInterface_Folder(folder, pathlist):
        mlist = [os.path.join(folder, m) for m in pathlist]
        mlist = [cv.imread(m, 1) for m in mlist]
        mlist = [m.astype(np.float32) / 255 for m in mlist]
        return mlist

    @staticmethod
    def __readFileInterface_Zip(zipf, pathlist):
        from zipfile import ZipFile
        zipf = ZipFile(zipf)
        mlist = [zipf.read(imgf) for imgf in pathlist]
        mlist = [np.frombuffer(m, dtype=np.uint8) for m in mlist]
        mlist = [cv.imdecode(m, 1) for m in mlist]
        mlist = [m.astype(np.float32) / 255 for m in mlist]
        return mlist

    def init(self, path, selection, size, pathtype='fld', sheet=None):
        self.size = size
        selection = Xls2ListList(selection, sheet)
        selection = [s[0] for s in selection]
        selection = [s for s in selection if s is not None]
        self.names=selection

        if pathtype == 'fld':
            reader = labeldataset.__readFileInterface_Folder
        elif pathtype == 'zip':
            reader = labeldataset.__readFileInterface_Zip
        else:
            raise TypeError(f'inproper path type {pathtype}')

        self.pairs = list(
            zip(reader(path, [f'spl/{p}' for p in selection]), [
                cv.threshold(p[:, :, 0:1], 0.5, 1, cv.THRESH_BINARY)[1]
                for p in reader(path, [f'lbl/{p}' for p in selection])
            ]))

        return self

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return [
            ToTensor()(i)
            for i in self.pairs[int(len(self.pairs) * np.random.random())]
        ]
    
    def rawlength(self):
        return len(self.pairs)
    
    def rawgetitem(self,rawidx):
        return self.pairs[rawidx]
    
    def getname(self,rawidx):
        return self.names[rawidx]