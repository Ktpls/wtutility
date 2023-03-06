# neural network tracker
# %%
#basics

from nntracker import *
from torch.utils.tensorboard import SummaryWriter
import traceback
from torch.utils.data import Dataset
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
import time
from nntracker import getmodel, device
# %%
# nn def
modelpath = r'nntracker.pth'
model = getmodel(modelpath)
#[os.remove(f) for f in AllFileIn('runs')]
writer = SummaryWriter(
    f"runs/{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}"
)  # 存放log文件的目录

# %%
# dataset


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
    
    def init(self, path, selection, size, pathtype='fld'):
        self.size = size
        selection = Xls2ListList(selection)
        selection = [s[0] for s in selection]
        selection = [s for s in selection if s is not None]

        if pathtype == 'fld':
            reader = labeldataset.__readFileInterface_Folder
        elif pathtype == 'zip':
            reader = labeldataset.__readFileInterface_Zip
        else:
            raise TypeError(f'inproper path type {pathtype}')

        self.pairs = [
            (cv.imread(os.path.join(path, f'spl/{p}')).astype(np.float32) /
             255,
             cv.threshold(
                 cv.imread(os.path.join(path, f'lbl/{p}'))[:, :, 0:1].astype(
                     np.float32) / 255, 0.5, 1, cv.THRESH_BINARY)[1])
            for p in selection
        ]

        return self

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return [
            ToTensor()(i)
            for i in self.pairs[int(len(self.pairs) * np.random.random())]
        ]


batch_size = 32
train_data = labeldataset().init(
    r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\all',
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\train.xlsx",
    32768, 'fld')
train_dataloader = DataLoader(train_data, batch_size=batch_size)
test_data = labeldataset().init(
    r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\all',
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\test.xlsx",
    256, 'fld')
test_dataloader = DataLoader(test_data, batch_size=batch_size)

# %%
# train


def calclose(lbl, lblhat):
    #[b,c,h,w]
    loss= \
    10000*(
        (
            ((lbl - lblhat)**2).sum(dim=[-1, -2, -3])**2
            #     /
            # (lbl.sum(dim=[-1, -2, -3]) + 1)
        )#**2
    ).sum()

    return (loss)


def viewLossOnTest(testbatch=3):

    #    model.eval()
    losstotal = 0
    samplenum = 0
    with torch.no_grad():
        for batch, datatuple in enumerate(test_dataloader):

            datatuple = [d.to(device) for d in datatuple]
            src, lbl = datatuple
            lblhat = model.forward(src)
            losstotal += calclose(lbl, lblhat).item()
            samplenum += batchsizeof(src)
            if batch >= testbatch:
                break
    print(f" [testloss]")
    loss2show = losstotal / samplenum
    print(f" [loss={loss2show}]")
    writer.add_scalar('testloss', (loss2show), 0)


def trainAnEpoch(epochnum=6):

    optimizer = torch.optim.AdamW(model.parameters(),
                                  lr=1e-4,
                                  weight_decay=1e-2)
    epochs = epochnum
    for ep in range(epochs):
        print(f"Epoch {ep+1}")
        print("-------------------------------")

        # train
        size = len(train_dataloader.dataset)
        for batch, datatuple in enumerate(train_dataloader):

            model.train()
            datatuple = [d.to(device) for d in datatuple]
            src, lbl = datatuple
            lblhat = model.forward(src)
            lose = calclose(lbl, lblhat)
            optimizer.zero_grad()
            lose.backward()
            optimizer.step()

            current = batch * batchsizeof(src)
            if current % 2**10 == 0:
                print(f" [{current:>5d}/{size:>5d}]")
                loss2show = lose.item() / batchsizeof(src)
                print(f" [loss={loss2show}]")
                writer.add_scalar('loss', (loss2show), current)
            if current % 2**13 == 0:
                viewLossOnTest()

    #win32api.Beep(1000, 1000)
    print("Done!")


trainAnEpoch()

#%%
# all the continious running should only be applied on codes above!
# plz stop here
exit()

# %%
# view effect


def viewModelOnPic():

    def viewModelOnAPic(m):
        if type(m) is np.ndarray or type(m) is cv.Mat:
            m = ToTensor()(m)
        m = m.reshape((1, ) + m.shape)  #add batch
        with torch.no_grad():
            result = model.forward(m)
        result = result[0, :, :, :]  #debatch
        result = tensorimg2ndarray(result)
        result = cv.threshold(result, 0.5, 1, cv.THRESH_BINARY)[1]
        return result

    filelist = [
        row[0] for row in Xls2ListList(
            r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\sampleNotIncluded.xlsx"
        ) if row[0] is not None
    ]

    singleMapWidthHeightRatio = 2
    pltwidth = np.ceil(np.sqrt(len(filelist) /
                               singleMapWidthHeightRatio)).astype(np.int32)
    pltheight = np.ceil(singleMapWidthHeightRatio * pltwidth).astype(np.int32)
    npp = nestedPyPlot([pltheight, pltwidth], [1, 2],
                       plt.figure(figsize=(16, 16)))
    for i, p in enumerate(filelist):
        m = cv.imread(p)
        npp.subplot(i, 0)
        plt.imshow(cv.cvtColor(m, cv.COLOR_BGR2RGB))
        npp.subplot(i, 1)
        result = viewModelOnAPic(m)
        plt.imshow(result, **{'cmap': 'gray', 'vmin': 0, 'vmax': 1})


def viewmodel():
    datasetusing = train_data
    model.eval()

    samplenum = 3 * 4
    npp = nestedPyPlot([3, 4], [2, 2], plt.figure(figsize=(16, 16)))
    imshowconfig = {'cmap': 'gray', 'vmin': 0, 'vmax': 1}
    imshowconfignonnorm = {'cmap': 'gray'}
    with torch.no_grad():
        for i in range(samplenum):
            src, lbl = datasetusing[0]

            lblhat = model.forward(src.reshape((1, ) + src.shape).to(device))
            lblhat = np.array(lblhat[0, :, :, :].cpu())
            #to ndarray

            datatuple = [src, lbl, lblhat]
            datatuple = [tensorimg2ndarray(d) for d in datatuple]
            src, lbl, lblhat = datatuple

            npp.subplot(i, 0)
            plt.imshow(cv.cvtColor(src, cv.COLOR_BGR2RGB))
            npp.subplot(i, 1)
            lblhat = cv.threshold(lblhat, 0.5, 1, cv.THRESH_BINARY)[1]
            plt.imshow(lblhat, **imshowconfig)
            npp.subplot(i, 2)
            plt.imshow(lbl, **imshowconfig)


viewmodel()

# %%
# save


def savemodel(path):
    torch.save(model.state_dict(), path)
    print(f"Saved PyTorch Model State to {path}")


savemodel(modelpath)

# %%
writer.close()

# %%
os.system("pause")
