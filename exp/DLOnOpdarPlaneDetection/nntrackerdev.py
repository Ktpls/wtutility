# neural network tracker
# %%
# basics

from nntracker import *
from torch.utils.tensorboard import SummaryWriter
import traceback
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
import time

# %%
# nn def
modelpath = r"nntracker.pth"
model = getmodel(modelpath)
writer = SummaryWriter(
    f"runs/{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}"
)  # 存放log文件的目录

# %%\
# dataset
from nntracker_common import labeldataset

print("loading dataset")
datasetname = "LE2REnh"
datasetroot = r"C:\file\code\wtutility/exp/DLOnOpdarPlaneDetection/dataset/"
if datasetname == "LE2REnh":
    path = r"LE2REnh/"
    sel = r"LE2REnh/all.xlsx"
    datasettype = "fld"
if datasetname == "LE2RAREnh":
    path = r"LE2RAREnh/LE2RAREnh.zip"
    sel = r"LE2RAREnh/all.xlsx"
    datasettype = "zip"
elif datasetname == "largeEnoughToRecon":
    path = r"largeEnoughToRecon/largeEnoughToRecon.zip"
    sel = r"largeEnoughToRecon/all.xlsx"
    datasettype = "zip"
elif datasetname == "origins_nntracker":
    path = r"origins_nntracker\origins_nntracker.zip"
    sel = r"origins_nntracker/hardones.xlsx"
    datasettype = "zip"
elif datasetname == "withaimingring":
    path = r"withaimingring/withaimingring.zip"
    sel = r"withaimingring/xls.xlsx"
    datasettype = "zip"

train_data = labeldataset().init(
    datasetroot + path, datasetroot + sel, 2048, datasettype, None, [96] * 2
)
test_data = train_data
print("load finished")

# %%
# dataloader
# for easier modify batchsize without reloading all samples
batch_size = 2
train_dataloader = DataLoader(train_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=batch_size)

# %%
# train


def calclose(lbl, lblhat):
    X = torch.arange(lbl.shape[-1]).view(-1, 1, 1, lbl.shape[-1]).to(device)
    Y = torch.arange(lbl.shape[-2]).view(-1, 1, lbl.shape[-2], 1).to(device)
    lblsurface = lbl.sum(dim=[-1, -2, -3], keepdim=True) + 1
    meanX = (lbl * X).sum(dim=(-1, -2), keepdim=True)
    meanY = (lbl * Y).sum(dim=(-1, -2), keepdim=True)
    radius = torch.sqrt(lblsurface / torch.pi)
    dist2 = torch.sqrt((X - meanX) ** 2 + (Y - meanY) ** 2) / radius
    coef = 1 + 0.5 * (dist2 > 1)  # /(radius)
    # coef[lblsurface[:, 0, 0, 0] < 3, :, :, :] = 3  # clear sky
    # [b,d,h,w]
    loss = (
        1
        * (
            (
                (coef * (lbl - lblhat) ** 2).sum(dim=[-1, -2, -3])
                #     /
                # (np.sqrt(lblsurface[:,0,0,0]) + 0.01) #emphasize large ons more
            )  # **2
        ).sum()
    )
    return loss


def trainmainprogress(batch, datatuple):
    model.train()
    datatuple = [d.to(device) for d in datatuple]
    src, lbl = datatuple
    lblhat = model.forward(src)
    loss = calclose(lbl, lblhat)
    return loss


def onoutput(batch, aveerr):
    writer.add_scalar("aveerr", aveerr, batch)


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


# %%
# view effect


def evalOnAll(updateSampleList=False):
    rawlength = train_data.rawlength()
    nowpercentage = 0
    totaltime = 0
    model.eval()
    loss = []
    with torch.no_grad():
        for pi in range(rawlength):
            spl, lbl = train_data.rawgetitem(pi)

            def dataPreperation(d):
                return ToTensor()(d).to(device).unsqueeze(0)

            spl = dataPreperation(spl)
            lbl = dataPreperation(lbl)
            starttime = time.time()
            lblhat = model.forward(spl)
            totaltime += time.time() - starttime
            curloss = calclose(lbl, lblhat).item()
            loss.append(curloss)
            if nowpercentage <= pi / rawlength * 100:
                nowpercentage += 1
                print(f"{nowpercentage}%")
        aveloss = np.average(loss)
    print(f"average loss{aveloss}")
    print(f"inference time{totaltime/rawlength}")
    if updateSampleList:
        train_data.pairs = [
            train_data.pairs[i] for i, l in enumerate(loss) if l >= aveloss
        ]
        print(f"samplelist update done,wrong samples:{len(train_data.pairs)}")


def viewmodel():
    datasetusing = train_data
    model.eval()

    samplenum = 3 * 4
    npp = nestedPyPlot([3, 4], [2, 2], plt.figure(figsize=(16, 16)))
    imshowconfig = {"cmap": "gray", "vmin": 0, "vmax": 1}
    imshowconfignonnorm = {"cmap": "gray"}
    totalinferencetime = 0
    infecount = 0
    with torch.no_grad():
        for i in range(samplenum):
            src, lbl = datasetusing[0]

            tsrc = src.reshape((1,) + src.shape).to(device)
            tstart = time.perf_counter()
            lblhat = model.forward(tsrc)
            totalinferencetime += time.perf_counter() - tstart
            infecount += 1
            lblhat = np.array(lblhat[0, :, :, :].cpu())
            srcatte = np.zeros_like(src)
            # to ndarray

            datatuple = [src, lbl, lblhat, srcatte]
            datatuple = [tensorimg2ndarray(d) for d in datatuple]
            src, lbl, lblhat, srcatte = datatuple

            npp.subplot(i, 0)
            plt.imshow(cv.cvtColor(src, cv.COLOR_BGR2RGB))
            npp.subplot(i, 1)
            lblhat = cv.threshold(lblhat, 0.5, 1, cv.THRESH_BINARY)[1]
            plt.imshow(lblhat, **imshowconfig)
            npp.subplot(i, 2)
            plt.imshow(lbl, **imshowconfig)
            # npp.subplot(i, 3)
            # plt.imshow(cv.cvtColor(srcatte, cv.COLOR_BGR2RGB))
    print(f"average inference time={totalinferencetime / samplenum}")


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
