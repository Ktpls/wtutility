# neural network tracker

# %%
#basics
from utilkaggle import *
from torch.utils.tensorboard import SummaryWriter
import traceback
from torch.utils.data import Dataset
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
from nntracker import getmodel, device
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

    def __init__(self, path):

        # we got dirs 0-10 in root, maybe some not exist cuz no sample under it
        piclist = list(AllFileIn(os.path.join(path, 'spl')))
        piclist = [os.path.basename(p) for p in piclist]
        self.cacheSrc = [
            cv.imread(os.path.join(path, f'spl/{p}')).astype(np.float32) / 255
            for p in piclist
        ]
        self.cacheLbl = [
            cv.imread(os.path.join(
                path, f'lbl/{p}'))[:, :, 0:1].astype(np.float32) / 255
            for p in piclist
        ]

    def __len__(self):
        return 10000

    @staticmethod
    def dataEnhance(src, lbl):
        
        # dttp = [src, lbl]
        # src, lbl = dttp
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
    r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\old\dataset\all')
batch_size = 32
train_dataloader = DataLoader(training_data, batch_size=batch_size)

# %%
# train


def trainAnEpoch():

    def calclose(lbl, lblhat):
        #[b,c,h,w]
        return (((lbl - lblhat)**2).sum(dim=[-1, -2, -3])**2).sum()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    epochs = 2*6
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
                writer.add_scalar('loss',
                                  lose.item() / batchsizeof(datatuple[0]),
                                  current)

    #win32api.Beep(1000, 1000)
    print("Done!")


trainAnEpoch()

# %%
# view effect

def viewmaxpool():
    datasetusing = training_data
    polkersz=11
    mdl=torch.nn.MaxPool2d(polkersz,1,int(polkersz/2))
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
            plt.imshow(cv.cvtColor(src,cv.COLOR_BGR2RGB))
            npp.subplot(i, 1)
            plt.imshow(cv.cvtColor(srchat,cv.COLOR_BGR2RGB))

def viewmodel():
    datasetusing = training_data
    model.eval()

    samplenum = 3 * 4
    npp = nestedPyPlot([3, 4], [2, 1], plt.figure(figsize=(16, 16)))
    imshowconfig = {'cmap': 'gray', 'vmin': 0, 'vmax': 1}
    with torch.no_grad():
        for i in range(samplenum):
            src, lbl = datasetusing[0]
            srcbatched=src.reshape((1,)+src.shape)
            lblhat = model.forward(srcbatched)[0,:,:,:]

            #to ndarray
            datatuple = [src, lbl, lblhat]
            datatuple = [np.array(d) for d in datatuple]
            datatuple = [np.moveaxis(d, 0, 2) for d in datatuple]
            src, lbl, lblhat = datatuple

            npp.subplot(i, 0)
            plt.imshow(cv.cvtColor(src,cv.COLOR_BGR2RGB))
            npp.subplot(i, 1)
            plt.imshow(lblhat, **imshowconfig)


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