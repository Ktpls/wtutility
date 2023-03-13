
import torch
import numpy as np
import matplotlib.pyplot as plt


def spectrumDecompose(s, psize):
    if type(s) is int:
        s = torch.tensor([s])
    batchsize = s.shape[0]
    s = s.reshape((batchsize, 1))
    return torch.zeros([batchsize, psize], dtype=torch.float).scatter_(dim=-1, index=s, src=torch.ones_like(s, dtype=torch.float))


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
        print(f'Loading existed nn {path}')
        model.load_state_dict(torch.load(path))
        return model



def tensorimg2ndarray(m):
    m = np.array(m)
    m = np.moveaxis(m, -3, -1)
    return m

class kineticEnergyAccelerator:

    def __init__(self,threshpow=0) -> None:
        self.mul = 1
        self.threshpow=threshpow
    
    def getmul(self):
        return self.mul
    
    def __call__(self, loss):
        loss=self.mul*loss
        mag = torch.log10(loss.detach())
        if mag < self.threshpow:
            self.mul *= 10
        return loss