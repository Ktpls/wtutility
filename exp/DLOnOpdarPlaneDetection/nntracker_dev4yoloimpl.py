# neural network tracker
# %%
#basics

from nntracker import *
from torch.utils.tensorboard import SummaryWriter
import traceback
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
import time
from nntracker import getmodel, device
import torch.nn.functional as F
# %%
# nn def
modelpath = r'yolotracker.pth'
model = getmodel(modelpath)
writer = SummaryWriter(
    f"runs/{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}"
)  # 存放log文件的目录

# %%
# dataset
from nntracker_common import labeldataset

train_data = labeldataset().init(
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed\selallenhed.zip",
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed\sel.xlsx",
    32768, 'zip')
test_data = labeldataset().init(
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed\selallenhed.zip",
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed\sel.xlsx",
    64, 'zip')

#%%
# for easier modify batchsize without reload all samples
batch_size = 32
train_dataloader = DataLoader(train_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=batch_size)

# %%
# train


def yolo_loss(pred, target, S, B, C, lambda_coord, lambda_noobj):
    """
    pred: (batch_size, S, S, Bx5+C)
    target: (batch_size, S, S, Bx5+C)
    S: int, grid size
    B: int, number of boxes per grid cell
    C: int, number of classes
    lambda_coord: float, weight for coordinate loss
    lambda_noobj: float, weight for no-object loss
    """
    # separate predictions for objectness, box coordinates, and class probabilities
    pred_obj = pred[..., :B]
    pred_box = pred[..., B:B*5]
    pred_class = pred[..., B*5:]

    # separate targets for objectness, box coordinates, and class probabilities
    target_obj = target[..., :B]
    target_box = target[..., B:B*5]
    target_class = target[..., B*5:]

    # calculate binary cross-entropy loss for objectness
    obj_loss = F.binary_cross_entropy_with_logits(pred_obj, target_obj, reduction='none')

    # calculate MSE loss for box coordinates
    box_loss = F.mse_loss(pred_box, target_box, reduction='none')

    # create mask for cells with object
    obj_mask = target_obj > 0.5

    # calculate coordinate loss only for cells with object
    coord_loss = lambda_coord * torch.sum(box_loss[obj_mask])

    # calculate no-object loss only for cells without object
    noobj_mask = target_obj <= 0.5
    noobj_loss = lambda_noobj * torch.sum(obj_loss[noobj_mask])

    # calculate class loss
    class_loss = F.binary_cross_entropy_with_logits(pred_class, target_class, reduction='none')

    # sum up all losses
    total_loss = torch.sum(coord_loss + noobj_loss + class_loss)

    return total_loss


def viewLossOnTest(testbatch=3):

    #    model.eval()
    losstotal = 0
    samplenum = 0
    with torch.no_grad():
        for batch, datatuple in enumerate(test_dataloader):

            (images, targets) =datatuple
            outputs = model(images)
            losstotal += yolo_loss(outputs, targets, S=7, B=2, C=1, lambda_coord=5, lambda_noobj=0.5).item()
            samplenum += batchsizeof(images)
            if batch >= testbatch:
                break
    print(f" [testloss]")
    loss2show = losstotal / samplenum
    print(f" [loss={loss2show}]")
    writer.add_scalar('testloss', (loss2show), 0)


def trainAnEpoch(epochnum=6, outputperbatchnum=100):

    optimizer = torch.optim.AdamW(model.parameters(),
                                  lr=1e-4,
                                  weight_decay=1e-2)
    epochs = epochnum
    start_time = time.time()
    for ep in range(epochs):
        print(f"Epoch {ep+1}")
        print("-------------------------------")

        # train
        for batch, datatuple in enumerate(train_dataloader):

            model.train()
            datatuple = [d.to(device) for d in datatuple]
            (images, targets) =datatuple
            optimizer.zero_grad()
            outputs = model(images)
            loss = yolo_loss(outputs, targets, S=7, B=2, C=1, lambda_coord=5, lambda_noobj=0.5)
            loss.backward()
            if batch % outputperbatchnum == 0:
                end_time = time.time()
                print(f"Batch {batch}/{len(train_dataloader)}")
                print(
                    f"Training speed: {outputperbatchnum/(end_time-start_time):>5f} batches per second"
                )
                aveloss = loss.item()/batchsizeof(images)
                print(f"Average loss: {aveloss:>7f}")
                writer.add_scalar('trainloss',
                                  aveloss, batch)
                start_time = time.time()

        viewLossOnTest()
    #win32api.Beep(1000, 1000)
    print("Done!")

trainAnEpoch()

#%%
# all the continious running should only be applied on codes above! plz stop here
if __name__ == '__main__':
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
