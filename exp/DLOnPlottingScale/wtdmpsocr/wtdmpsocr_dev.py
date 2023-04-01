# warthunder distance measurement plotting scale optical character reconginization

# %%
#basics
from utilref import *
from torch.utils.tensorboard import SummaryWriter
import traceback
from torch.utils.data import Dataset
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
from wtdmpsocr import getmodel, tsize, tsizep1, typeElse, device
from defs import *
#torch.set_num_threads(12)

# %%
# nn def

modelpath = 'wtdmpsocr.pth'
model = getmodel(modelpath)
#[os.remove(f) for f in AllFileIn('runs')]
from datetime import datetime

nowtimestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
writer = SummaryWriter(f"runs/{nowtimestamp}")  # 存放log文件的目录

# %%
# dataset


class labeldataset(Dataset):

    def __init__(self, path):

        # we got dirs 0-10 in root, maybe some not exist cuz no sample under it
        self.piclist = list(range(tsizep1))
        for t in range(tsizep1):
            rootoft = rf'{path}\{t}'
            self.piclist[t] = AllFileIn(rootoft) if os.path.exists(
                rootoft) else []

        # cache this for usage in __getitem__()
        self.endpos = list(itertools.accumulate([len(t)
                                                 for t in self.piclist]))
        assert (
            self.endpos[-1] != 0
        )  #that means u got no sample, probabily with totally wrong dataset path

        self.cache = None

    def sampleassetnum(self):
        return self.endpos[-1]

    def __len__(self):
        return 65536

    standardshape = [20, 40]  #h,w

    @staticmethod
    def dataEnhance(m,
                    t,
                    enh_hairing=True,
                    enh_dropout=True,
                    enh_blocking=True,
                    enh_randmov=False,
                    enh_noisedot=True,
                    enh_noiseline=True,
                    enh_lineblocking=True):

        m = np.copy(m)

        if enh_hairing:
            # grow some hair
            regsum = regionsum(m, [3, 3])
            addups = np.logical_and((m < 0.1), (regsum >= 3))
            hairingrate = np.random.random() * 0.6 - 0.2
            addups = np.logical_and(addups,
                                    (np.random.random(m.shape) < hairingrate))
            m += addups

        if enh_dropout:
            # randomly set half of pixels in image m to 0
            m = (np.random.random(m.shape) > 0.2) * m

        if enh_blocking:
            # blocking
            hw = np.random.rand(2) * [2, 10] + [1, 2]
            lt = np.random.rand(2) * (m.shape - hw)
            rd = lt + hw
            # for i in range(2):
            #     if rd[i] >= m.shape[i]:
            #         rd[i] = m.shape[i]
            lt, rd = lt.astype('int'), rd.astype('int')
            m[lt[0]:rd[0], lt[1]:rd[1]] = 0

        # standardlize shape and mov char to the center
        # move tmat center to char center
        totalmov = np.zeros(2,
                            dtype='float32') + 0.5 * np.array([charh, charw])
        mov = np.array(labeldataset.standardshape) / \
            2-0.5*np.array([charh, charw])

        # rand mov
        if enh_randmov:
            # dont think any usefulness in conv net
            mov += np.random.uniform(-1, 1, size=2) * [1, 5]
        totalmov += mov
        matmov = np.array([
            [1, 0, mov[1]],
            [0, 1, mov[0]],
        ])
        m = cv.warpAffine(m, matmov, np.flip(labeldataset.standardshape))

        # set tmat
        tmat = np.zeros(labeldataset.standardshape + [
            tsize,
        ],
                        dtype='float32')
        if t != tsizep1 - 1:  # not t else
            # tmat[:,:,t] indicates answer pos
            totalmov = totalmov.round().astype('int')

            # gaussian answer
            X, Y = np.meshgrid(
                np.arange(labeldataset.standardshape[1]) - totalmov[1],
                np.arange(labeldataset.standardshape[0]) - totalmov[0])

            # directly set answerchannel = np.exp(-(X**2+Y**2)/(sigma)**2) will lead to underflow
            dist2 = (X**2 + Y**2) / (2)**2
            dist2[dist2 > 3] = 3.1
            answerchannel = np.exp(-dist2)
            answerchannel[dist2 > 3] = 0

            # pointly answer
            # answerchannel = np.zeros_like(m)
            # answerchannel[totalmov[1], totalmov[0]] = 1

            tmat[:, :, t] = answerchannel
        else:
            # no non zero point for type else
            pass

        if enh_noiseline:
            # noise line
            for i in range(int(np.random.uniform(-2, 5))):
                p = (np.random.rand(2, 2) *
                     np.flip([labeldataset.standardshape])).astype('int')
                m = cv.line(m, p[0], p[1], color=1, thickness=1)

        if enh_noisedot:
            # noise dot
            for i in range(int(np.random.uniform(10, 50))):
                p = (np.random.rand(2) *
                     labeldataset.standardshape).astype('int')
                m[p[0], p[1]] = 1

        if enh_lineblocking:
            # black line
            for i in range(int(np.random.uniform(-2, 5))):
                p = (np.random.rand(2, 2) *
                     np.flip([labeldataset.standardshape])).astype('int')
                m = cv.line(m, p[0], p[1], color=0, thickness=1)

        return m, tmat

    def readSample_WithCaching(self, t, idx):

        if self.cache is None:
            # init cache
            self.cache = [[
                cv.imread(path)[:, :, 0].astype('float32') / 255
                for path in self.piclist[t]
            ] for t in range(tsizep1)]

        if idx >= len(self.piclist[t]):
            return None

        img = self.cache[t][idx]

        # shape standardlize included

        img, tmat = labeldataset.dataEnhance(
            img,
            t,
            # True,
            # True,
            # False,
            # False,
            # False,
            # False,
            # False
        )
        return ToTensor()(img), ToTensor()(tmat), t

    def readSample(self, t, idx):
        return labeldataset.readSample_WithCaching(self, t, idx)

    def __getitem__(self, idx):
        #return self.draw_uniformOnType(np.random.random())
        return self.drawByFlattenedIdxFrac(np.random.random())

    def drawByFlattenedIdxFrac(self,ifrac):
        return self.drawByFlattenedIdx(int(ifrac * self.sampleassetnum()))

    def drawByFlattenedIdx(self, idx):
        # get the type where idx laies
        # in case of out of range
        idx %= self.endpos[-1]
        lastendpos = 0
        for t in range(tsizep1):
            if idx >= lastendpos and idx < self.endpos[t]:
                tt = t
            lastendpos = self.endpos[t]
        t = tt
        idx = idx - self.endpos[t - 1] if t != 0 else idx
        return self.readSample(t, idx)

    def draw_uniformOnType(self,ifrac):
        while (True):
            # to skip empty
            t = int(np.random.random()* (tsizep1))
            ret = self.drawByType(t, ifrac)
            if ret is not None:
                break
        return ret

    # idxfrac: 0~1 idx, which will be converted into real idx by timing len(thistype)
    def drawByType(self, t,ifrac):
        idx = int(ifrac * len(self.piclist[t]))
        return self.readSample(t, idx)


training_data = labeldataset(rf'..\dataset\charDataset\labeled')
test_data = training_data
batch_size =64
train_dataloader = DataLoader(training_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=batch_size)

# %%
# train


def trainAnEpoch():
    optimizer = torch.optim.AdamW(model.parameters(),
                                  lr=1e-4,
                                  weight_decay=1e-4)
    epochs = 6
    outputperbatchnum = 100
    for ep in range(epochs):
        print(f"Epoch {ep+1}")
        print("-------------------------------")

        # train
        model.train()
        start_time = time.time()
        for batch, (m, tmat, t) in enumerate(train_dataloader):

            m, tmat, t = m.to(device), tmat.to(device), t.to(device)
            tmathat = model.forward(m)
            lose = model.lose(tmathat, tmat, t)
            optimizer.zero_grad()
            lose.backward()
            optimizer.step()

            if batch % outputperbatchnum == 0:
                end_time = time.time()
                batch_time = end_time - start_time
                start_time = end_time
                avg_loss = lose.item() / batchsizeof(m)
                print(f"Batch {batch}/{len(train_dataloader)}")
                print(f"Average Loss: {avg_loss}")
                print(f"Training Speed: {outputperbatchnum/batch_time} b/s")
                writer.add_scalar("Training Loss", avg_loss, batch)

    win32api.Beep(1000, 1000)
    print("Done!")


trainAnEpoch()

# %%
# view model tmat


def viewmodel():
    datasetusing = test_data
    model.eval()

    npp = nestedPyPlot([4, 3], [1, 3], plt.figure(figsize=(16, 16)))

    with torch.no_grad():
        for i in range(tsizep1):
            ret = datasetusing.drawByType(i, np.random.rand())
            if ret is None:
                continue
            m, tmat, t = ret
            tmathat = model.forward(m.reshape((1, ) + m.shape))[0, :, :, :]
            m = tensorimg2ndarray(m)[:, :, 0]  # delete channel dim
            tmat = tensorimg2ndarray(tmat)
            tmathat = tensorimg2ndarray(tmathat)

            nestedindex = 0

            def setnppsubplot():
                nonlocal nestedindex
                npp.subplot(i, nestedindex)
                nestedindex += 1

            imshowconfig = {'cmap': 'gray', 'vmin': 0, 'vmax': 1}
            # img
            setnppsubplot()
            plt.imshow(m, **imshowconfig)

            # tmathat right
            setnppsubplot()
            plt.imshow(
                np.repeat(tmathat[:, :, t], 20, axis=0)
                if t != typeElse else np.zeros_like(m), **imshowconfig)

            # tmathat wrong
            setnppsubplot()
            tmathatelse = np.copy(tmathat)
            if t != tsizep1 - 1:
                tmathatelse[:, :, t] = 0
            plt.imshow(np.repeat(np.max(tmathatelse, axis=2), 20, axis=0),
                       **imshowconfig)


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