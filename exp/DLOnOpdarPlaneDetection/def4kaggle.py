
import cv2 as cv
import torch
import numpy as np
import matplotlib.pyplot as plt
import openpyxl as opx
import os

def Xls2ListList(path):
    return [[ele.value for ele in row] for row in (opx.load_workbook(path).active.rows)]


def AllFileIn(path, includeFileInSubDir=True):
    import os
    ret = []
    for dirpath, dir, file in os.walk(path):
        if not includeFileInSubDir and dirpath != path:
            continue
        ret.extend([os.path.join(dirpath, f)for f in file])
    return ret
def batchsizeof(tensor):
    return tensor.shape[0]
class nestedPyPlot:
    def __init__(self, outtershape, innershape, fig) -> None:
        self.oshape = np.array(outtershape)
        self.ishape = np.array(innershape)
        self.realsize = self.oshape*self.ishape
        self.fig = fig

    def subplot(self, o, i):
        maincoor = np.array((int(o/self.oshape[1]), o % self.oshape[1]))
        subcoor = np.array((int(i/self.ishape[1]), i % self.ishape[1]))
        realcoor = self.ishape*maincoor+subcoor
        # plt.subplot(self.realsize[0], self.realsize[1], realcoor[0]
        #             * self.realsize[1]+realcoor[1]+1)
        ax = self.fig.add_subplot(self.realsize[0], self.realsize[1], realcoor[0]
                                  * self.realsize[1]+realcoor[1]+1)
        return ax

def setModel(model, path=None):
    import os

    if path is None:
        print(f'Path==None')
        return model
    elif not os.path.exists(path):
        print(f'Warning: Path {path} not exist. Set model default')
        return model
    else:
        print(f'{path} not existed, Loading existed nn')
        model.load_state_dict(torch.load(path))
        return model


def tensorimg2ndarray(m):
    m = np.array(m)
    m = np.moveaxis(m, -3, -1)
    return m

# warthunder distance measurement plotting s

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

# %%
# nn def


class skiper(torch.nn.Module):

    def __init__(self, component, n_i, n_o) -> None:
        super().__init__()
        self.component = component
        self.combiner = torch.nn.Conv2d(n_i + n_o, n_o, 1)

    def forward(self, m):
        #[b,c,h,w]
        processed = self.component.forward(m)
        c = torch.concat([processed, m], dim=-3)
        result = self.combiner.forward(c)
        return result


class cbrps(torch.nn.Module):
    #input chan, output chan, convolve size, pooling size
    #n_o should be like 2*n, cuz maxpool will be concated with former output
    def __init__(self, n_i, n_o, n_c, n_p) -> None:
        super().__init__()
        self.component = \
        skiper(
            torch.nn.Sequential(
                torch.nn.Conv2d(n_i, n_o, n_c, padding='same', bias=False),
                #torch.nn.BatchNorm2d(n_o),
                torch.nn.LeakyReLU(),
                skiper(
                    torch.nn.MaxPool2d(n_p, stride=1, padding=int(n_p / 2)),
                       n_o, n_o)
                ), n_i, n_o)

    def forward(self, m):
        #[b,c,h,w]
        return self.component.forward(m)


class nntracker(torch.nn.Module):

    def __init__(self) -> None:
        super().__init__()
        self.matchtempl = torch.nn.Sequential(
            skiper(
                torch.nn.Sequential(
                    cbrps(3, 32, 5, 5),
                    cbrps(32, 16, 5, 5),
                ),3,16),
            torch.nn.Conv2d(16, 1, 5, padding='same'),
            torch.nn.LeakyReLU(),
        )

    def forward(self, m):
        return self.matchtempl(1 - m)


class nntracker_small(torch.nn.Module):

    def __init__(self) -> None:
        super().__init__()
        self.matchtempl = torch.nn.Sequential(
            cbrps(3, 32, 5, 5),
            torch.nn.Conv2d(32, 1, 5, padding='same'),
            torch.nn.LeakyReLU(),
        )

    def forward(self, m):
        return self.matchtempl(1 - m)


def getmodel(modelpath):
    model = setModel(nntracker(), path=modelpath).to(device)
    #print(model)
    return model


def getmodelsmall(modelpath):
    model = setModel(nntracker_small(), path=modelpath).to(device)
    #print(model)
    return model


# %%
