
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


def setModel(model, path=None, device='cpu'):
    import os

    if path is None:
        print(f'Path==None')
        return model
    elif not os.path.exists(path):
        print(f'Warning: Path {path} not exist. Set model default')
        return model
    else:
        print(f'Loading existed nn {path}')
        model.load_state_dict(
            torch.load(path, map_location=torch.device(device)))
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

class cbr(torch.nn.Module):
    def __init__(self, n_i, n_o, n_c) -> None:
        super().__init__()
        self.component = \
            torch.nn.Sequential(
                torch.nn.Conv2d(n_i, n_o, n_c, padding='same', bias=False),
                torch.nn.BatchNorm2d(n_o),
                torch.nn.LeakyReLU(),
            )

    def forward(self, m):
        #[b,c,h,w]
        return self.component.forward(m)
class cbrps(torch.nn.Module):
    #input chan, output chan, convolve size, pooling size
    #n_o should be like 2*n, cuz maxpool will be concated with former output
    def __init__(self, n_i, n_o, n_c, n_p) -> None:
        super().__init__()
        self.component = \
            torch.nn.Sequential(
                torch.nn.Conv2d(n_i, n_o, n_c, padding='same', bias=False),
                torch.nn.BatchNorm2d(n_o),
                torch.nn.LeakyReLU(),
                skiper(
                    torch.nn.MaxPool2d(n_p, stride=1, padding=int(n_p / 2)),
                    n_o, n_o)
            )

    def forward(self, m):
        #[b,c,h,w]
        return self.component.forward(m)

class inception(torch.nn.Module):

    def __init__(self,
                 infeat,
                 outfeat11,
                 outfeatpool,
                 outfeat33,
                 outfeat55,
                 isbn=True) -> None:
        super().__init__()
        self.infeat=infeat
        self.outfeat11=outfeat11
        self.outfeatpool=outfeatpool
        self.outfeat33=outfeat33
        self.outfeat55=outfeat55
        self.isbn=isbn
        self.path11 = torch.nn.Sequential(
            torch.nn.Conv2d(infeat, outfeat11, 1, padding='same'),
            torch.nn.LeakyReLU(),
        )
        self.pathpool = torch.nn.Sequential(
            torch.nn.MaxPool2d(3, stride=1, padding=1),
            torch.nn.Conv2d(infeat, outfeatpool, 1, padding='same'),
            torch.nn.LeakyReLU(),
        )
        self.path33 = torch.nn.Sequential(
            torch.nn.Conv2d(infeat, infeat, 1, padding='same'),
            torch.nn.LeakyReLU(),
            torch.nn.Conv2d(infeat, outfeat33, 3, padding='same'),
            torch.nn.LeakyReLU(),
        )
        self.path55 = torch.nn.Sequential(
            torch.nn.Conv2d(infeat, infeat, 1, padding='same'),
            torch.nn.LeakyReLU(),
            torch.nn.Conv2d(infeat, outfeat55, 3, padding='same'),
            torch.nn.LeakyReLU(),
            torch.nn.Conv2d(outfeat55, outfeat55, 3, padding='same'),
            torch.nn.LeakyReLU(),
        )
        if isbn is not None and isbn:
            self.bn = torch.nn.BatchNorm2d(outfeat11 + outfeatpool +
                                           outfeat33 + outfeat55)
        else:
            self.bn = None

    @staticmethod
    def even(infeat, outfeat, bn=None):
        assert outfeat % 4 == 0
        outfeatby4 = outfeat // 4
        return inception(infeat, outfeatby4, outfeatby4, outfeatby4,
                         outfeatby4, bn)

    def forward(self, m):
        o = torch.concat(
            [self.path11(m),
             self.pathpool(m),
             self.path33(m),
             self.path55(m)],
            dim=-3)
        if self.bn is not None:
            o = self.bn(o)
        return o  #channel



class res_through(torch.nn.Module):

    _modules = {}

    def __init__(self, *components) -> None:
        super().__init__()
        self.components = components
        for idx, module in enumerate(components):
            self.add_module(str(idx), module)

    def forward(self, m):
        o = m
        for i,l in enumerate(self.components):
            ret=l(o)
            o = ret + o
        return o