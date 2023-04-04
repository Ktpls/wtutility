# warthunder distance measurement plotting scale optical character reconginization

# %%
from torch.utils.data import Dataset
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
from utilref import *
from defs import *
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

devmode = True

# %%
'''
use cnn to find where plotting scale starts
'''


class locator(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.locer = torch.nn.Sequential(
            torch.nn.Conv2d(1, 32, [19,25], padding='same'), # quite large, but in good vision
            torch.nn.BatchNorm2d(32),
            torch.nn.LeakyReLU(),
            torch.nn.MaxPool2d(3,1,1),
            
            torch.nn.Conv2d(32, 32, 3, padding='same'),
            torch.nn.BatchNorm2d(32),
            torch.nn.LeakyReLU(),
            torch.nn.MaxPool2d(3,1,1),
            
            torch.nn.Conv2d(32, 32, 3, padding='same'),
            torch.nn.BatchNorm2d(32),
            torch.nn.LeakyReLU(),
            torch.nn.MaxPool2d(3,1,1),
            
            torch.nn.Conv2d(32, 32, 3, padding='same'),
            torch.nn.BatchNorm2d(32),
            torch.nn.LeakyReLU(),
            torch.nn.MaxPool2d(3,1,1),
            
            torch.nn.Conv2d(32, 1, [charh-1, charw-1], padding='same'),
            torch.nn.MaxPool2d([20, 1])
        )

    def forward(self, m):
        l = self.locer(m)

        # only keep batch and width
        l = torch.reshape(l, [l.shape[0], l.shape[-1]])
        l = torch.softmax(l, dim=-1)
        return l  # lhat

    def lose(self, lhat, l):
        lpos = torch.argmax(l)
        tmp = torch.arange(lhat.shape[-1])
        tmp = torch.reshape(tmp, (1,)+tmp.shape)
        tmp = torch.repeat_interleave(tmp, batchsizeof(lhat), dim=0)
        weight = torch.exp(-((tmp-lpos)/5)**2)
        gain = (lhat*weight).sum()
        return -gain
        # return torch.nn.CrossEntropyLoss()(lhat, l)+torch.mean(torch.mean(punishweight*lhat,dim=-1))

    @staticmethod
    def standardlizeImgShape(m):
        standardshape = [20, 150]
        mattr = np.array([
            [1, 0, 0],
            [0, 1, 0]
        ]).astype('float')
        m = cv.warpAffine(m, mattr, np.flip(standardshape))
        return m


modelpath = 'locator.pth'
model = setModel(locator(), path=modelpath).to(device)
print(model)


# %%
class labeldataset(Dataset):
    def __init__(self, train, size):
        Dataroot =\
            rf'D:\File\code\prog\wtutility\exp\DLOnPlottingScale\dataset\locatorDataset\{"trains" if train else "tests"}'
        self.piclist = AllFileIn(Dataroot)
        self.size=size

    def __len__(self):
        return self.size

    @staticmethod
    def dataenhancement(m, l):

        # blocking
        lt = np.random.rand(2)*m.shape
        hw = np.random.rand(2)*[20, 4]
        rd = lt+hw
        for i in range(2):
            if rd[i] >= m.shape[i]:
                rd[i] = m.shape[i]
        lt, rd = lt.astype('int'), rd.astype('int')
        m[lt[0]:rd[0], lt[1]:rd[1]] = 0

        # move
        mov = np.random.uniform(-1, 1, size=2)*[20, 0]
        matmov = np.array([
            [1, 0, mov[0]],
            [0, 1, mov[1]],
        ])
        m = cv.warpAffine(m, matmov, np.flip(m.shape))
        l = arrayshift(l, int(mov[0]+0.5)-2, fill=0)

        # noise line
        for i in range(int(np.random.uniform(-5, 10))):
            p = (np.random.rand(2, 2) *
                 np.flip([m.shape])).astype('int')
            m = cv.line(m, p[0], p[1], color=1, thickness=1)

        # noise dot
        for i in range(int(np.random.uniform(50, 200))):
            p = (np.random.rand(2) *
                 m.shape).astype('int')
            m[p[0], p[1]] = 1

        return m, l

    def readsample(self, idx):
        img = cv.imread(
            self.piclist[idx]).astype('float32')/255
        img = model.standardlizeImgShape(img)
        l = img[0, :, -1]  # red channel as location
        img = img[:, :, 0]  # as gray
        img, l = labeldataset.dataenhancement(img, l)
        return ToTensor()(img), torch.tensor(l),

    def __getitem__(self, idx):
        idx=int(np.random.random()*len(self.piclist))
        return self.readsample(idx)


if devmode:
    training_data = labeldataset(train=True,size=8192)
    test_data = labeldataset(train=False,size=128)
    batch_size = 16
    train_dataloader = DataLoader(training_data, batch_size=batch_size)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)
    for X, y in test_dataloader:
        print(f"Shape of X [N, C, H, W]: {X.shape}")
        print(f"Shape of y: {y.shape} {y.dtype}")
        break


# %%
def trainAnEpoch():
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=1e-3)
    epochs = 1
    for ep in range(epochs):
        print(f"Epoch {ep+1}")
        print("-------------------------------")

        # train
        model.train()
        size = len(train_dataloader.dataset)
        for batch, (m, ep) in enumerate(train_dataloader):

            m, ep = m.to(device), ep.to(device)
            lhat = model.forward(m)
            lose = model.lose(lhat, ep)
            optimizer.zero_grad()
            lose.backward()
            optimizer.step()

            if batch % 20 == 0:
                current = batch * batch_size
                print(f" [{current:>5d}/{size:>5d}]")
                print(f"{lose.item()}/{lhat.shape[0]}")

        # test
        model.eval()
        with torch.no_grad():
            test_loss, correct = 0, 0
            for batch, (m, ep) in enumerate(test_dataloader):
                m, ep = m.to(device), ep.to(device)
                lhat = model.forward(m)
                test_loss += model.lose(lhat, ep).item()
                correct += (lhat.argmax(dim=1) == ep.argmax(dim=1)
                            ).type(torch.float).sum()
            test_loss /= len(test_dataloader.dataset)
            correct /= len(test_dataloader.dataset)
            print(f"Test Error:")
            print(f"Avg loss: {test_loss:>8f}")
            print(f"correct rate: {correct:>8f}")

    print("Done!")


if devmode:
    trainAnEpoch()


# %%
def viewmodel():
    datasetusing = test_data
    model.eval()

    samplenum = 10
    npp = nestedPyPlot([samplenum, 1], [1, 1], plt.figure(figsize=(16, 16)))
    with torch.no_grad():
        sampleidx = np.random.choice(
            range(len(datasetusing)), samplenum, False)
        for i in range(samplenum):
            m, l = datasetusing[sampleidx[i]]

            lhat = model.forward(m.reshape((1,)+m.shape))[0]

            npp.subplot(i, 0)
            # m=m[0,:,:]
            m = np.array(m)
            m = np.moveaxis(m, 0, 2)
            m = np.repeat(m, 3, axis=2)
            m[:, np.argmax(l), 1] = 1
            m[-1, :, 0] = lhat
            m[:, np.argmax(lhat), 0] = 1
            plt.imshow(m, cmap='gray', vmin=0, vmax=1)
    # plt.show()


if devmode:
    viewmodel()

# %%
# save


def savemodel(path):
    torch.save(model.state_dict(), path)
    print(f"Saved PyTorch Model State to {path}")


if devmode:
    savemodel(modelpath)


# %%
# cut char using model
# ###caution###
def cut():
    with torch.no_grad():
        piclist = AllFileIn(
            r"D:\File\code\prog\wtutility\exp\DLOnPlottingScale\dataset\plottingscaleorgDataset\appendix")
        for p in piclist:
            m = cv.imread(p)[:, :, 0]
            m = model.standardlizeImgShape(m)
            mt = torch.tensor(m).type(torch.float)/255
            mt = mt.reshape((1,1)+mt.shape)
            start = model.forward(mt).argmax()
            start = int(start)

            def savecharshaped(x):
                savemat(m[:, x:x+charw])

            # cut real digital chars
            for c in range(3):
                savecharshaped(start+charw*c)

            # cut typeElse texture
            typeElseSampleNumMax=10
            textureDensity = np.average(m.astype(np.float32)/255, axis=0)
            textureDensity = np.correlate(
                textureDensity, np.ones(charw, np.float32)/charw, 'valid')
            densityValid = textureDensity > 0.01
            densityValid[start-charw:start+3*charw] = False
            probdist = textureDensity*densityValid
            
            for teti in range(typeElseSampleNumMax):
                if np.sum(probdist)<0.001:
                    # no where to cut
                    break
                #norm
                probdist *= 1/np.sum(probdist)
                pos = np.random.choice(len(probdist), replace=False, p=probdist)
                savecharshaped(pos)
                delstart,delend=pos-charw,pos+charw
                if delstart<0:
                    delstart=0
                if delend>=len(probdist):
                    delend=len(probdist)-1
                probdist[delstart:delend]=0


cut()
# %%
