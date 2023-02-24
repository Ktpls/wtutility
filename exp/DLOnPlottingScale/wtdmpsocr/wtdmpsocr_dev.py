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
from wtdmpsocr import getmodel, tsize, tsizep1, typeElse,device
from defs import *
#torch.set_num_threads(12) 


# %%
# nn def

modelpath = 'wtdmpsocr_new.pth'
model = getmodel(modelpath)
[os.remove(f) for f in AllFileIn('runs')]
writer = SummaryWriter("runs")  # 存放log文件的目录

# %%
# dataset


class labeldataset(Dataset):
    def __init__(self, path):

        # we got dirs 0-10 in root, maybe some not exist cuz no sample under it
        self.piclist = list(range(tsizep1))
        for t in range(tsizep1):
            rootoft = rf'{path}\{t}'
            self.piclist[t] = AllFileIn(
                rootoft) if os.path.exists(rootoft) else []

        # cache this for usage in __getitem__()
        self.endpos = list(itertools.accumulate(
            [len(t) for t in self.piclist]))
        assert(self.endpos[-1]!=0) #that means u got no sample, probabily with totally wrong dataset path

        self.cache = None

    def sampleassetnum(self):
        return self.endpos[-1]

    def __len__(self):
        return 30000

    standardshape = [40, 20]

    @staticmethod
    def dataEnhance(m, t, enh_hairing=True, enh_blocking=True, enh_randmov=False, enh_noisedot=True, enh_noiseline=True, enh_lineblocking=True):

        m = np.copy(m)

        if enh_hairing:
            # grow some hair
            regsum = regionsum(m, [3, 3])
            addups = np.logical_and((m < 0.1), (regsum == 3))
            addups = np.logical_and(addups, (np.random.random(m.shape) < 0.4))
            m += addups

        if enh_blocking:
            # blocking
            hw = np.random.rand(2)*[2, 10]+[1, 2]
            lt = np.random.rand(2)*(m.shape-hw)
            rd = lt+hw
            # for i in range(2):
            #     if rd[i] >= m.shape[i]:
            #         rd[i] = m.shape[i]
            lt, rd = lt.astype('int'), rd.astype('int')
            m[lt[0]:rd[0], lt[1]:rd[1]] = 0

        # standardlize shape and mov char to the center
        # move tmat center to char center
        totalmov = np.zeros(2, dtype='float32')+0.5*np.array([charh, charw])
        mov = np.array(labeldataset.standardshape) / \
            2-0.5*np.array([charh, charw])

        # rand mov
        if enh_randmov:
            # dont think any usefulness in conv net
            mov += np.random.uniform(-1, 1, size=2) * [5, 5]
        totalmov += mov
        matmov = np.array([
            [1, 0, mov[1]],
            [0, 1, mov[0]],
        ])
        m = cv.warpAffine(m, matmov, np.flip(labeldataset.standardshape))

        # set tmat
        tmat = np.zeros(labeldataset.standardshape+[tsize, ], dtype='float32')
        if t != tsizep1-1:  # not t else
            # tmat[:,:,t] indicates answer pos
            totalmov = totalmov.round().astype('int')

            # gaussian answer
            X, Y = np.meshgrid(
                np.arange(labeldataset.standardshape[1])-totalmov[1],
                np.arange(labeldataset.standardshape[0])-totalmov[0])

            # directly set answerchannel = np.exp(-(X**2+Y**2)/(sigma)**2) will lead to underflow
            dist2 = (X**2+Y**2)/(2)**2
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

    def readSample_Realtime(self, t, idx):
        if idx >= len(self.piclist[t]):
            raise IndexError(
                f'index err on type{t}: {idx} of {len(self.piclist[t])}')
        img = cv.imread(
            self.piclist[t][idx])[:, :, 0].astype('float32')/255  # as gray/255

        # shape standardlize included
        img, tmat = labeldataset.dataEnhance(img, t)
        return ToTensor()(img), ToTensor()(tmat), t

    def readSample_WithCaching(self, t, idx):

        if self.cache is None:
            # init cache
            self.cache = [[cv.imread(
                path)[:, :, 0].astype('float32')/255 for path in self.piclist[t]] for t in range(tsizep1)]

        if idx >= len(self.piclist[t]):
            raise IndexError(
                f'index err on type{t}: {idx} of {len(self.piclist[t])}')

        img = self.cache[t][idx]

        # shape standardlize included
        img, tmat = labeldataset.dataEnhance(img, t)
        return ToTensor()(img), ToTensor()(tmat), t

    def readSample(self, t, idx):
        return labeldataset.readSample_WithCaching(self, t, idx)

    def __getitem__(self, idx):
        return self.draw_uniformOnType(np.random.random())

    def drawByFlattenedIdxFrac(self, idxfrac):
        return self.drawByFlattenedIdx(idxfrac*self.sampleassetnum)

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
        idx = idx-self.endpos[t-1] if t != 0 else idx
        return self.readSample(t, idx)

    def draw_uniformOnType(self, idxfrac):
        while (True):
            try:
                # to skip empty
                t = int(np.random.random()*(tsizep1))
                ret = self.drawByType(t, idxfrac)
                break
            except IndexError:
                continue
        return ret

    # idxfrac: 0~1 idx, which will be converted into real idx by timing len(thistype)
    def drawByType(self, t, idxfrac):
        idx = int(idxfrac*len(self.piclist[t]))
        return self.readSample(t, idx)


training_data = labeldataset(rf'..\dataset\charDataset\labeled')
test_data = training_data
batch_size =64
train_dataloader = DataLoader(training_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=batch_size)


# %%
# train


def trainAnEpoch():
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=1e-4)
    epochs = 3
    for ep in range(epochs):
        print(f"Epoch {ep+1}")
        print("-------------------------------")

        # train
        model.train()
        size = len(train_dataloader.dataset)
        for batch, (m, tmat, t) in enumerate(train_dataloader):

            m, tmat, t = m.to(device), tmat.to(device), t.to(device)
            tmathat = model.forward(m)
            lose = model.lose(tmathat, tmat, t)
            optimizer.zero_grad()
            lose.backward()
            optimizer.step()
            
            current = batch * batchsizeof(m)
            if current % 100 == 0:
                print(f" [{current:>5d}/{size:>5d}]")
                writer.add_scalar('loss', lose.item()/batchsizeof(m), current)

        # # test
        # model.eval()
        # with torch.no_grad():
        #     test_loss = 0
        #     for batch, (m, tmat, t) in enumerate(test_dataloader):
        #         m, tmat, t = m.to(device), tmat.to(device), t.to(device)
        #         tmathat = model.forward(m)
        #         test_loss += model.lose(tmathat, tmat,
        #                                 t).item() / batchsizeof(m)
        #         break
        #     #test_loss /= len(test_dataloader.dataset)
        #     print(f"Test Error:")
        #     print(f"Av
        # g loss: {test_loss:>8f}")

    win32api.Beep(1000, 1000)
    print("Done!")


trainAnEpoch()


# %%
# view model tmat


def viewmodel():
    viewindetachedimg = True
    datasetusing = test_data
    model.eval()

    if viewindetachedimg:
        npp = nestedPyPlot([4, 3], [1, 3], plt.figure(figsize=(16, 16)))
    else:
        npp = nestedPyPlot([3, 4], [1, 1], plt.figure(figsize=(16, 16)))

    with torch.no_grad():
        for i in range(tsizep1):
            try:
                m, tmat, t = datasetusing.drawByType(i, np.random.rand())
            except IndexError as e:
                print(e)
                continue

            tmathat = model.forward(m.reshape((1,)+m.shape))[0, :, :, :]
            m = tensorimg2ndarray(m)[:, :, 0]  # delete channel dim
            tmat = tensorimg2ndarray(tmat)
            tmathat = tensorimg2ndarray(tmathat)

            if viewindetachedimg:
                nestedindex = 0

                def setnppsubplot():
                    nonlocal nestedindex
                    npp.subplot(i, nestedindex)
                    nestedindex += 1
                imshowconfig = {
                    'cmap': 'gray',
                    'vmin': 0,
                    'vmax': 1
                }
                # img
                setnppsubplot()
                plt.imshow(m, **imshowconfig)

                # tmathat right
                setnppsubplot()
                plt.imshow(tmathat[:, :, t] if t !=
                           typeElse else np.zeros_like(m), **imshowconfig)

                # tmathat wrong
                setnppsubplot()
                tmathatelse = np.copy(tmathat)
                if t != tsizep1-1:
                    tmathatelse[:, :, t] = 0
                channelelse = np.max(tmathatelse, axis=2)
                plt.imshow(np.max(tmathatelse, axis=2), **imshowconfig)

            else:

                m2show = np.zeros(m.shape[0:2] + (3,))

                # show sample
                m3channeld = np.repeat(
                    m.reshape(m.shape[0:2] + (1,)), 3, axis=2)
                np.putmask(m2show, m3channeld > 0.1, m3channeld*0.5)

                # tmathat type right
                if t != tsizep1-1:
                    channelright = tmathat[:, :, t]
                    channelright[channelright > 1] = 1
                    np.putmask(m2show[:, :, 1], channelright
                               > 0.1, channelright)

                # tmathat type wrong
                tmathatelse = np.copy(tmathat)
                if t != tsizep1-1:
                    tmathatelse[:, :, t] = 0
                channelelse = np.max(tmathatelse, axis=2)
                np.putmask(m2show[:, :, 0], channelelse > 0.1, channelelse)

                # # show tmat type right
                # if t!=tsizep1-1:
                #     np.putmask(m2show[:, :, 1], tmat[:, :, t] > 0.1, tmat[:, :, t])

                npp.subplot(i, 0)
                plt.imshow(m2show)


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