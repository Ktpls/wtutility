# neural network tracker

# %%
#basics
from utilref import *
from torch.utils.tensorboard import SummaryWriter
import traceback
from torch.utils.data import Dataset
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
from nntracker import getmodel, getmodelsmall, device
#torch.set_num_threads(12)

# %%
# nn def
modelpath = 'nntracker.pth'
model = getmodel(modelpath)
[os.remove(f) for f in AllFileIn('runs')]
writer = SummaryWriter("runs")  # 存放log文件的目录

# %%
# dataset


class labeldataset(Dataset):

    def __init__(self, path, selection):
        selection = Xls2ListList(selection)
        selection = [s[0] for s in selection]
        selection = [s for s in selection if s is not None]

        self.cacheSrc = [
            cv.imread(os.path.join(path, f'spl/{p}')).astype(np.float32) / 255
            for p in selection
        ]
        self.cacheLbl = [
            cv.threshold(
                cv.imread(os.path.join(path, f'lbl/{p}'))[:, :, 0:1].astype(
                    np.float32) / 255, 0.5, 1, cv.THRESH_BINARY)[1]
            for p in selection
        ]

    def __len__(self):
        return 30000

    @staticmethod
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
            Y, X = np.arange(l0, dtype=np.float32), np.arange(l0,
                                                              dtype=np.float32)
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

            # #cut so no black part
            # l1 = int(l0 / ((np.tan(np.abs(the)) + 1) * np.cos(np.abs(the))))
            # offset = int((l0 - l1) * 0.5)
            # matcut = np.array([
            #     [1, 0, -offset],
            #     [0, 1, -offset],
            # ],
            #                   dtype=np.float32)
            # m = cv.warpAffine(m, matcut, [l1, l1])
            # #zoom back
            # matzoomback = np.array([
            #     [l0 / l1, 0, 0],
            #     [0, l0 / l1, 0],
            # ],dtype=np.float32)
            # m = cv.warpAffine(m, matzoomback, [l0, l0])
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
            m if len(m.shape) == 3 else m.reshape(m.shape + (1, ))
            for m in dttp
        ]
        src, lbl = dttp
        return src, lbl

    #idx in [0,1)

    def readSample(self, idx):
        idx = int(len(self.cacheSrc) * idx)

        src = self.cacheSrc[idx]
        lbl = self.cacheLbl[idx]

        # shape standardlize included
        src, lbl = labeldataset.dataEnhance(src, lbl)

        return ToTensor()(src), ToTensor()(lbl)

    def __getitem__(self, idx):
        return self.readSample(np.random.random())


training_data = labeldataset(
    r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\all',
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selection.xlsx"
)
batch_size = 64
train_dataloader = DataLoader(training_data, batch_size=batch_size)


# %%
# trainx

def calclose(lbl, lblhat):
    #[b,c,h,w]
    loss= \
    (
        (
            ((lbl - lblhat)**2).sum(dim=[-1, -2, -3])
            #     /
            # (lbl.sum(dim=[-1, -2, -3]) + 1)
        )**2
    ).sum()
    
    return (loss)

def trainAnEpoch():

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    epochs = 9
    for ep in range(epochs):
        print(f"Epoch {ep+1}")
        print("-------------------------------")

        # train
        model.train()
        size = len(train_dataloader.dataset)
        for batch, datatuple in enumerate(train_dataloader):

            datatuple = [d.to(device) for d in datatuple]
            src, lbl = datatuple
            lblhat = model.forward(src)
            lose = calclose(lbl, lblhat)
            optimizer.zero_grad()
            lose.backward()
            optimizer.step()

            current = batch * batchsizeof(datatuple[0])
            if current % 100 == 0:
                print(f" [{current:>5d}/{size:>5d}]")
                loss2show=lose.item() / batchsizeof(datatuple[0])
                print(f" [loss={loss2show}]")
                writer.add_scalar('loss',
                                  (loss2show),
                                  current)

    win32api.Beep(1000, 1000)
    print("Done!")


trainAnEpoch()

#%%
# all the continious running should only be applied on codes above!
# plz stop here
exit()

# %%
# view effect


def viewmaxpool():
    datasetusing = training_data
    polkersz = 11
    mdl = torch.nn.MaxPool2d(polkersz, 1, int(polkersz / 2))
    mdl.eval()

    samplenum = 3 * 4
    npp = nestedPyPlot([3, 4], [2, 1], plt.figure(figsize=(16, 16)))
    imshowconfig = {'cmap': 'gray', 'vmin': 0, 'vmax': 1}
    with torch.no_grad():
        for i in range(samplenum):
            src, lbl = datasetusing[0]
            srchat = mdl.forward(src)

            #to ndarray
            datatuple = [src, lbl, srchat]
            datatuple = [np.array(d) for d in datatuple]
            datatuple = [tensorimg2ndarray(d) for d in datatuple]
            src, lbl, srchat = datatuple

            npp.subplot(i, 0)
            plt.imshow(cv.cvtColor(src, cv.COLOR_BGR2RGB))
            npp.subplot(i, 1)
            plt.imshow(cv.cvtColor(srchat, cv.COLOR_BGR2RGB))


def testloss():
    model.train()
    with torch.no_grad():
        batchnum = 10
        samplenum = 0
        lose = 0
        for batch, datatuple in enumerate(train_dataloader):

            datatuple = [d.to(device) for d in datatuple]
            src, lbl = datatuple
            lblhat = model.forward(src)
            lose += calclose(lbl, lblhat).item()
            samplenum += batchsizeof(datatuple[0])
            if batch >= batchnum:
                break
        print(f" [{(lose/samplenum)}]")


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
    datasetusing = training_data
    model.eval()

    samplenum = 3 * 4
    npp = nestedPyPlot([3, 4], [2, 2], plt.figure(figsize=(16, 16)))
    imshowconfig = {'cmap': 'gray', 'vmin': 0, 'vmax': 1}
    with torch.no_grad():
        for i in range(samplenum):
            src, lbl = datasetusing[0]
            srcbatched = src.reshape((1, ) + src.shape)
            lblhat = model.forward(srcbatched)[0, :, :, :]

            #to ndarray
            datatuple = [src, lbl, lblhat]
            datatuple = [np.array(d) for d in datatuple]
            datatuple = [np.moveaxis(d, 0, 2) for d in datatuple]
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