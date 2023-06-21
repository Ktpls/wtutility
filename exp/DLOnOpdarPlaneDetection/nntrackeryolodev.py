# neural network tracker
# %%
#basics

from torch.utils.tensorboard import SummaryWriter
import traceback
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
import time
from nntracker_common import *
from nntracker import *
# %%
# nn def
modelpath = r'nntrackeryolo.pth'
model = getmodel(modelpath)
writer = SummaryWriter(
    f"runs/{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}"
)  # 存放log文件的目录

# %%\
# dataset

print('loading dataset')
datasetname = 'largeEnoughToRecon'
datasetroot = 'C:/file/code/wtutility/exp/DLOnOpdarPlaneDetection/dataset/'
if datasetname == 'LE2REnh':
    path = r"LE2REnh/LE2REnh.zip"
    sel = r"LE2REnh/all.xlsx"
    datasettype = 'zip'
elif datasetname == 'largeEnoughToRecon':
    path = r"largeEnoughToRecon/largeEnoughToRecon.zip"
    sel = r"largeEnoughToRecon/all.xlsx"
    datasettype = 'zip'
elif datasetname == 'origins_nntracker':
    path = r"origins_nntracker/origins_nntracker.zip"
    sel = r"origins_nntracker/hardones.xlsx"
    datasettype = 'zip'

train_data = labeldataset().init(datasetroot + path, datasetroot + sel, 8192,
                                 datasettype, None, model.stdShape)
test_data = labeldataset().init(datasetroot + path, datasetroot + sel, 16,
                                datasettype, None, model.stdShape)
print('load finished')

#%%
# dataloader
# for easier modify batchsize without reloading all samples
batch_size = 4
train_dataloader = DataLoader(train_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=batch_size)

# %%
# train


def calclose(lbl, aabbhat):
    aabb = []
    for i in range(len(lbl)):
        aabb.append(AABBOf(lbl[i, 0, :, :].cpu().numpy()))
    aabb = torch.tensor(np.array(aabb), dtype=torch.float32).to(device)
    #[b,d,h,w]

    confidence = aabb[:, 4:]
    coef = torch.repeat_interleave(confidence, 5, -1)
    coef[:, 4] = 1
    loss = (coef * (aabbhat - aabb)**2).sum()

    return (loss)


def viewLossOnTest(testbatch=1):

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
    loss2show = losstotal / samplenum
    print(f" [testloss={loss2show}]")
    writer.add_scalar('testloss', (loss2show), 0)


def trainAnEpoch(epochnum=6, outputperbatchnum=100):

    optimizer = torch.optim.AdamW(model.parameters(),
                                  lr=1e-4,
                                  weight_decay=1e-1)
    epochs = epochnum
    start_time = time.time()
    for ep in range(epochs):
        print(f"Epoch {ep+1}")
        print("-------------------------------")

        # train
        for batch, datatuple in enumerate(train_dataloader):

            model.train()
            datatuple = [d.to(device) for d in datatuple]
            src, lbl = datatuple
            aabbhat = model.forward(src)
            loss = calclose(lbl, aabbhat)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if batch % outputperbatchnum == 0:
                end_time = time.time()
                print(f"Batch {batch}/{len(train_dataloader)}")
                print(
                    f"Training speed: {outputperbatchnum/(end_time-start_time):>5f} batches per second"
                )
                aveloss = loss.item() / batchsizeof(src)
                print(f"Average loss: {aveloss:>7f}")
                writer.add_scalar('trainloss', aveloss, batch)
                start_time = time.time()
                # viewLossOnTest()

    #win32api.Beep(1000, 1000)
    print("Done!")


trainAnEpoch()

#%%
# all the continious running should only be applied on codes above! plz stop here
if __name__ == '__main__':
    exit()

# %%
# view effect


def drawAABB(img, aabb):
    img = np.copy(img)
    img = cv.rectangle(img, [aabb[0], aabb[1]], [aabb[2], aabb[3]],
                       color=(1, 0, 0),
                       thickness=1)
    return img


def regulate(x, a, b):
    if x < a:
        return a
    elif x > b:
        return b
    else:
        return x


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

            tsrc = src.reshape((1, ) + src.shape).to(device)
            aabbhat = model.forward(tsrc).cpu()
            aabbhat = np.array(aabbhat[0, :])
            #to ndarray
            datatuple = [src, lbl]
            datatuple = [tensorimg2ndarray(d) for d in datatuple]
            src, lbl = datatuple
            src = cv.cvtColor(src, cv.COLOR_BGR2RGB)

            npp.subplot(i, 0)
            plt.imshow(src)
            npp.subplot(i, 1)
            plt.imshow(lbl, **imshowconfig)

            npp.subplot(i, 2)
            plt.imshow(drawAABB(src, AABBOf(lbl[:, :, 0])[0:4]))

            aabbhatreg = np.array([
                regulate(aabbhat[0], 0, src.shape[1]),
                regulate(aabbhat[1], 0, src.shape[0]),
                regulate(aabbhat[2], 0, src.shape[1]),
                regulate(aabbhat[3], 0, src.shape[0]),
            ]).astype(np.int32)

            npp.subplot(i, 3)
            plt.imshow(drawAABB(src, aabbhatreg[0:4]))
            plt.title(f'{aabbhat[4]:>.2f}')


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
