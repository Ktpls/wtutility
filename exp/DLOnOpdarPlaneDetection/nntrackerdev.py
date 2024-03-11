# neural network tracker
# %% basics

from nntracker import *
from torch.utils.tensorboard import SummaryWriter
import traceback
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
import time

# %%  nn def
modelpath = r"nntracker.pth"
model = getmodel(modelpath)
writer = SummaryWriter(
    f"runs/{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}"
)  # 存放log文件的目录

# %% dataset
from nntracker_common import *


@dataclasses.dataclass
class NnTrackerDataset:
    path: str
    sel: str
    datasettype: str


print("loading dataset")
datasetname = "LE2REnh"
datasetroot = r"C:\file\code\wtutility/exp/DLOnOpdarPlaneDetection/dataset/"
datasets = {
    "LE2REnh": NnTrackerDataset(r"LE2REnh/LE2REnh.zip", r"LE2REnh/all.xlsx", "zip"),
    "SmallAug": NnTrackerDataset(r"SmallAug/SmallAug.zip", r"SmallAug/all.xlsx", "zip"),
    "largeEnoughToRecon": NnTrackerDataset(
        r"largeEnoughToRecon/largeEnoughToRecon.zip",
        r"largeEnoughToRecon/all.xlsx",
        "zip",
    ),
    "origins_nntracker": NnTrackerDataset(
        r"origins_nntracker/origins_nntracker.zip",
        r"origins_nntracker/hardones.xlsx",
        "zip",
    ),
}
train_data = datasets[datasetname]
train_data = labeldataset().init(
    os.path.join(datasetroot, train_data.path),
    os.path.join(datasetroot, train_data.sel),
    8192,
    train_data.datasettype,
    None,
    BaseModule4NNTracker.stdShape,
    rtDataAugOn=True,
)
test_data = datasets["SmallAug"]
test_data = labeldataset().init(
    os.path.join(datasetroot, test_data.path),
    os.path.join(datasetroot, test_data.sel),
    32,
    test_data.datasettype,
    None,
    BaseModule4NNTracker.stdShape,
    rtDataAugOn=False,
)
print("load finished")

# %%  dataloader
# for easier modify batchsize without reloading all samples
batch_size = 2
train_dataloader = DataLoader(train_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=32)


# %% lossFunc


def calclose(pi, pihat):
    (
        isObj,
        meanX,
        meanY,
        wingSpan,
    ) = (
        pi[:, 0],
        pi[:, 1],
        pi[:, 2],
        pi[:, 3],
    )

    isObjCoef = torch.ones_like(pi)
    # dont estimate pos and size when is no object
    isObjCoef[isObj != 1, 1:] = 0

    loss = torch.sum(
        (
            (
                torch.tensor(
                    [
                        [1, 1, 1, 3],
                    ],
                    dtype=torch.float32,
                    device=device,
                    requires_grad=False,
                )
            )
            * (pihat - pi) ** 2
        )
        * isObjCoef
    )
    # loss = torch.log10(loss + 1e-10)
    return loss


# %% train


def trainmainprogress(batch, datatuple):
    model.train()
    src, lbl, pi = datatuple
    src = src.to(device)
    lbl = lbl.to(device)
    pi = pi.to(device)
    pihat = model.forward(src)
    loss = calclose(pi, pihat)
    return loss


def onoutput(batch, aveerr):
    # return
    with torch.no_grad():
        model.eval()
        lossTotal = 0
        for src, lbl, pi in test_dataloader:
            src = src.to(device)
            lbl = lbl.to(device)
            pi = pi.to(device)
            pihat = model.forward(src)
            lossTotal += calclose(pi, pihat).item()
            break
    print(f"testaveerr: {lossTotal/len(test_data)}")
    # writer.add_scalar("aveerr", aveerr, batch)


trainpipe.train(
    train_dataloader,
    torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2),
    trainmainprogress,
    customSubOnOutput=onoutput,
)

# %%
# all the continious running should only be applied on codes above! plz stop here
if __name__ == "__main__":
    exit()


# %% view effect


def viewmodel(datasetusing):
    model.eval()

    plotShape = [4, 2]
    subplotShape = [1, 2]
    samplenum = np.prod(plotShape)
    npp = nestedPyPlot(plotShape, subplotShape, plt.figure(figsize=(20, 20)))
    imshowconfig = {"vmin": 0, "vmax": 1}
    totalinferencetime = 0
    infercount = 0

    def PI2Str(pi):
        return ",".join([f"{i:.2f}" for i in pi])

    with torch.no_grad():
        for i in range(samplenum):
            src, lbl, pi = datasetusing[0]
            src = src.to(device)
            lbl = lbl.to(device)
            pi = pi.to(device)
            batchedsrc = src.reshape((1,) + src.shape)
            tstart = time.perf_counter()
            pihat = model.forward(batchedsrc)
            totalinferencetime += time.perf_counter() - tstart
            infercount += 1
            pihat = np.array(pihat[0].cpu())
            # to ndarray

            datatuple = [src, lbl]
            datatuple = [tensorimg2ndarray(d) for d in datatuple]
            src, lbl = datatuple
            lblhat = planeInfo2Lbl(pihat, BaseModule4NNTracker.stdShape)
            npp.subplot(i, 0)
            plt.title(PI2Str(pi))
            plt.imshow(cv.cvtColor(src, cv.COLOR_BGR2RGB))
            npp.subplot(i, 1)
            lblComparasion = (
                np.array(
                    [
                        lbl,
                        np.zeros_like(lbl),
                        lblhat,
                    ]
                )
                .squeeze(-1)
                .transpose([1, 2, 0])
            )

            plt.title(PI2Str(pihat))
            plt.imshow(lblComparasion, label="lblComparasion", **imshowconfig)
    print(f"average inference time={totalinferencetime / samplenum}")


viewmodel(datasetusing=test_data)

# %% save


def savemodel(path):
    torch.save(model.state_dict(), path)
    print(f"Saved PyTorch Model State to {path}")


savemodel(modelpath)

# %%
writer.close()

# %%
os.system("pause")


# %%
def rmModel():
    os.remove(modelpath)
