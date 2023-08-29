# warthunder distance measurement plotting scale optical character reconginization

# generating sample and training as in real task

# %%
# basics
from utilref import *
from torch.utils.tensorboard import SummaryWriter
import traceback
from torch.utils.data import Dataset
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
from wtdmpsocr import getmodel, tsize, tsizep1, typeElse, device
from defs import *

# torch.set_num_threads(12)

# %%
# nn def

modelpath = "wtdmpsocr.pth"
model = getmodel(modelpath)
# [os.remove(f) for f in AllFileIn('runs')]
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
            rootoft = rf"{path}\{t}"
            self.piclist[t] = AllFileIn(rootoft) if os.path.exists(rootoft) else []

        self.cache = [
            [
                cv.imread(path)[:, :, 0].astype("float32") / 255
                for path in self.piclist[t]
            ]
            for t in range(tsizep1)
        ]

        self.charsamplerate = {
            0: 1,
            1: 1,
            2: 1,
            3: 1,
            4: 1,
            5: 1,
            6: 1,
            7: 1,
            8: 1,
            9: 1,
            10: 1,
        }
        csrsum = sum(self.charsamplerate.values())
        self.charsamplerate = {k: v / csrsum for k, v in self.charsamplerate.items()}

    def __len__(self):
        return 2**31

    standardshape = [charh, 100]  # h,w

    @staticmethod
    def dataEnhance(
        m,
        enh_hairing=True,
        enh_blocking=False,
        enh_whitedot=True,
        enh_whiteline=True,
        enh_blackdot=True,
        enh_blackline=False,
    ):
        m = np.copy(m)

        if enh_hairing:
            # grow some hair
            hairdepth = int(np.random.uniform(-2, 2))
            for i in range(hairdepth):
                regsum = regionsum(m, [3, 3])
                addups = np.logical_and((m < 0.1), (regsum == 2))
                hairingrate = np.random.uniform(-1, 0.5)
                addups = np.logical_and(
                    addups, (np.random.random(m.shape) < hairingrate)
                )
                m += addups
                m[m > 1] = 1

        if enh_blocking:
            # blocking
            hw = np.random.rand(2) * [4, 10] + [-2, 2]
            lt = np.random.rand(2) * (m.shape - hw)
            rd = lt + hw
            # for i in range(2):
            #     if rd[i] >= m.shape[i]:
            #         rd[i] = m.shape[i]
            lt, rd = lt.astype("int"), rd.astype("int")
            m[lt[0] : rd[0], lt[1] : rd[1]] = 0

        if enh_whiteline:
            # noise line
            for i in range(int(np.random.uniform(-2, 3))):
                p = (
                    np.random.rand(2, 2) * np.flip([labeldataset.standardshape])
                ).astype("int")
                m = cv.line(m, p[0], p[1], color=1, thickness=1)

        if enh_whitedot:
            # noise dot
            noiseDotRate = np.random.uniform(-0.025, 0.05)
            noiseDotMask = (np.random.random(m.shape) < noiseDotRate).astype(np.float32)
            m += noiseDotMask
            m[m > 1] = 1

        if enh_blackline:
            # black line
            for i in range(int(np.random.uniform(-2, 3))):
                p = (
                    np.random.rand(2, 2) * np.flip([labeldataset.standardshape])
                ).astype("int")
                m = cv.line(m, p[0], p[1], color=0, thickness=1)

        if enh_blackdot:
            # randomly set half of pixels in image m to 0
            dropoutrate = np.random.uniform(-0.025, 0.05)
            m = (np.random.random(m.shape) > dropoutrate) * m

        return m

    def readSample(self):
        plottingscale = np.zeros(labeldataset.standardshape, np.float32)
        label = np.zeros([tsize, labeldataset.standardshape[1]], np.float32)
        occupied = np.zeros([labeldataset.standardshape[1]], np.float32)
        bellWidth = 5
        bellLabel = np.exp(-((np.linspace(-2, 2, bellWidth)) ** 2))
        charnum = np.random.choice(np.arange(3, 6))
        i = 0
        while True:
            if i >= charnum:
                break
            chartype = int(
                np.random.choice(
                    a=np.arange(tsizep1), p=[self.charsamplerate[t] for t in range(tsizep1)]
                )
            )
            if len(self.cache[chartype]) == 0:
                continue
            xpos = np.random.randint(0, labeldataset.standardshape[1] - charw + 1)
            if np.sum(occupied[xpos : xpos + charw]) > 0:
                continue
            i += 1

            char = np.copy(
                self.cache[chartype][np.random.choice(len(self.cache[chartype]))]
            )

            # vertical shake
            # vshake = np.random.uniform(-1.5, 0.5)
            # matmov = np.array(
            #     [
            #         [1, 0, 0],
            #         [0, 1, vshake],
            #     ],
            #     dtype=np.float32,
            # )
            # char = cv.warpAffine(char, matmov, [charw, charh])
            # char = (char > 0.5).astype(np.float32)
            plottingscale[:, xpos : xpos + charw] += char
            if chartype != tsize:
                # if is char
                bellstart = xpos + (charw - bellWidth) // 2
                label[chartype, bellstart : bellstart + bellWidth] += bellLabel
            charstart = xpos
            occupied[charstart : charstart + charw] = 1
        plottingscale = (plottingscale > 0).astype(np.float32)
        label[label > 1] = 1
        plottingscale = self.dataEnhance(plottingscale)
        return torch.from_numpy(plottingscale), torch.from_numpy(label)

    def __getitem__(self, idx):
        return self.readSample()


training_data = labeldataset(
    rf"C:\prog\wtutility\exp\DLOnPlottingScale\dataset\charDataset\labeled"
)
test_data = training_data
batch_size = 8
train_dataloader = DataLoader(training_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=batch_size)

# %%
# train


def trainAnEpoch():
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    epochs = 6
    outputperbatchnum = 100
    for ep in range(epochs):
        print(f"Epoch {ep+1}")
        print("-------------------------------")

        # train
        model.train()
        start_time = time.time()
        for batch, (m, label) in enumerate(train_dataloader):
            m, label = m.to(device), label.to(device)
            labelhat = model.forward(m)
            lose = model.lose(labelhat, label)
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

    outershape = [5, 3]

    npp = nestedPyPlot(outershape, [3, 1], plt.figure(figsize=(16, 16)))

    model.eval()
    with torch.no_grad():
        for i in range(np.prod(outershape)):
            m, label = datasetusing[0]
            labelhat = np.array(model.forward(m.reshape((1,) + m.shape))[0, :, :])
            label = np.array(label)

            labelerr = np.abs(labelhat - label)
            # labelerr = label

            def viewLabel(l):
                l = np.max(l, axis=0)
                l = l.reshape((1, labeldataset.standardshape[1]))
                return np.repeat(l, charh, axis=0)

            nestedindex = 0

            def setnppsubplot():
                nonlocal nestedindex
                npp.subplot(i, nestedindex)
                nestedindex += 1

            imshowconfig = {"cmap": "gray", "vmin": 0, "vmax": 1}

            # generated plotting scale
            setnppsubplot()
            plt.imshow(m, **imshowconfig)

            # lblhat
            setnppsubplot()
            plt.imshow(viewLabel(labelhat), **imshowconfig)

            # err
            setnppsubplot()
            plt.imshow(viewLabel(labelerr), **imshowconfig)
    plt.show()


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
