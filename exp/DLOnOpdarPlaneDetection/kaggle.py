# neural network tracker
# %%
#basics
import torch
import numpy as np
import matplotlib.pyplot as plt

import cv2 as cv
import os


def spectrumDecompose(s, psize):
    if type(s) is int:
        s = torch.tensor([s])
    batchsize = s.shape[0]
    s = s.reshape((batchsize, 1))
    return torch.zeros([batchsize, psize], dtype=torch.float).scatter_(
        dim=-1, index=s, src=torch.ones_like(s, dtype=torch.float))


def batchsizeof(tensor):
    return tensor.shape[0]


class nestedPyPlot:

    def __init__(self, outtershape, innershape, fig) -> None:
        self.oshape = np.array(outtershape)
        self.ishape = np.array(innershape)
        self.realsize = self.oshape * self.ishape
        self.fig = fig

    def subplot(self, o, i):
        maincoor = np.array((int(o / self.oshape[1]), o % self.oshape[1]))
        subcoor = np.array((int(i / self.ishape[1]), i % self.ishape[1]))
        realcoor = self.ishape * maincoor + subcoor
        # plt.subplot(self.realsize[0], self.realsize[1], realcoor[0]
        #             * self.realsize[1]+realcoor[1]+1)
        ax = self.fig.add_subplot(
            self.realsize[0], self.realsize[1],
            realcoor[0] * self.realsize[1] + realcoor[1] + 1)
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
                 isbn=True,
                 version='v2') -> None:
        super().__init__()
        self.infeat = infeat
        self.outfeat11 = outfeat11
        self.outfeatpool = outfeatpool
        self.outfeat33 = outfeat33
        self.outfeat55 = outfeat55
        self.isbn = isbn
        self.version = version
        if version == 'v2':
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
        elif version == 'v3':
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
                torch.nn.Conv2d(infeat, outfeat33, [1, 3], padding='same'),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat33, outfeat33, [3, 1], padding='same'),
                torch.nn.LeakyReLU(),
            )
            self.path55 = torch.nn.Sequential(
                torch.nn.Conv2d(infeat, infeat, 1, padding='same'),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(infeat, outfeat55, [1, 3], padding='same'),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat55, outfeat55, [3, 1], padding='same'),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat55, outfeat55, [1, 3], padding='same'),
                torch.nn.LeakyReLU(),
                torch.nn.Conv2d(outfeat55, outfeat55, [3, 1], padding='same'),
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

    def __init__(self, *components, combiner=None) -> None:
        super().__init__()
        self.components = components
        for idx, module in enumerate(components):
            self.add_module(str(idx), module)
        if combiner is None:

            def combiner_add(last, current):
                return last + current

            combiner = combiner_add
        self.combiner = combiner

    def forward(self, m):
        o = m
        for i, l in enumerate(self.components):
            ret = l(o)
            o = self.combiner(o, ret)
        return o


import time
from typing import *


class trainpipe:

    @staticmethod
    def train(dataloader,
              optimizer,
              mainprogress,
              epochnum=6,
              outputperbatchnum=100,
              customSubOnOutput=None):
        epochs = epochnum
        start_time = time.time()
        for ep in range(epochs):
            print(f"Epoch {ep+1}")
            print("-------------------------------")

            # train
            for batch, datatuple in enumerate(dataloader):
                loss = mainprogress(batch, datatuple)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                if batch % outputperbatchnum == 0:
                    end_time = time.time()
                    print(f"Batch {batch}/{len(dataloader)}")
                    print(
                        f"Training speed: {outputperbatchnum/(end_time-start_time):>5f} batches per second"
                    )
                    aveloss = loss.item() / batchsizeof(datatuple[0])
                    print(f"Average loss: {aveloss:>7f}")
                    if customSubOnOutput is not None:
                        customSubOnOutput(batch, aveloss)
                    start_time = time.time()

        #win32api.Beep(1000, 1000)
        print("Done!")


from torch import nn
import torch.nn.functional as F
import functools

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

# %%
# nn def

# %%
# nn def


class BaseModule4NNTracker:
    stdShape = [128, 128]


class SelfAttention(torch.nn.Module):

    def __init__(self, dim, heads=8, dim_head=64, dropout=0):
        #dim, the channel depth
        super().__init__()
        assert dim_head // heads == 0  # ill split out dim into several heads
        self.heads = heads
        self.dim_head = dim_head
        # define linear layers
        self.to_qkv = torch.nn.Linear(dim, 3 * dim_head, bias=False)
        self.to_out = torch.nn.Linear(dim_head, dim)
        # self.dropout = torch.nn.Dropout(dropout)

        super().register_buffer('scaleFactor',
                                torch.sqrt(torch.FloatTensor([dim_head])))

    def forward(self, x):
        # [batch size, sequence length, and feature dimensions]
        B, N, C = x.shape
        qkv = self.to_qkv(x).reshape(B, N, 3, self.heads,
                                     self.dim_head // self.heads).permute(
                                         2, 0, 3, 1, 4)
        # [batch size, sequence length, 3 * dim_head]
        # [batch size, sequence length, 3, num_heads, feature dimensions per head]
        # [3, batch size, num_heads, sequence length, feature dimensions per head]
        q, k, v = qkv[0], qkv[1], qkv[2]
        attn = (q @ k.transpose(-2, -1)) / self.get_buffer('scaleFactor')
        # [batch size, num_heads, sequence length, sequence length]
        attn = attn.softmax(dim=-1)
        attn = self.dropout(attn)
        out = (attn @ v).permute(0, 2, 1, 3).reshape(B, N, self.dim_head)
        # [batch size, num_heads, sequence length, feature dimensions per head]
        # [batch size, sequence length, num_heads, feature dimensions per head]
        # [batch size, sequence length, dim_head]
        out = self.to_out(out)
        # [batch size, sequence length, dim]
        # out = self.dropout(out)
        return out


class ReshapeModule(nn.Module):

    def __init__(self, *shape):
        super().__init__()
        self.shape = shape

    def forward(self, x):
        return x.view(*self.shape)


class PermuteModule(nn.Module):

    def __init__(self, *arglist):
        super().__init__()
        self.arglist = arglist

    def forward(self, x):
        return x.permute(*self.arglist)


def PositionalEmbedding2D(shape, depth):
    assert depth % 2 == 0
    depth_half = depth // 2
    y = np.arange(0, shape[0]).reshape([shape[0], 1, 1])
    x = np.arange(0, shape[1]).reshape([1, shape[1], 1])
    d = np.arange(0, depth).reshape([1, 1, depth])
    pe = np.zeros(shape + [depth], np.float32)

    mask_even = np.logical_and(d % 2 == 0, d < depth_half)[0, 0, :]
    mask_odd = np.logical_and(d % 2 == 1, d < depth_half)[0, 0, :]
    mask_even_half = np.logical_and((d - depth_half) % 2 == 0,
                                    d >= depth_half)[0, 0, :]
    mask_odd_half = np.logical_and((d - depth_half) % 2 == 1,
                                   d >= depth_half)[0, 0, :]

    pe[:, :, mask_even] = np.sin(
        2 * np.pi * x / 10000**((d + 1) / depth_half))[:, :, mask_even]
    pe[:, :, mask_odd] = np.cos(
        2 * np.pi * x / 10000**((d - 1 + 1) / depth_half))[:, :, mask_odd]
    pe[:, :, mask_even_half] = np.sin(
        2 * np.pi * y /
        10000**(((d + 1) - depth_half) / depth_half))[:, :, mask_even_half]
    pe[:, :, mask_odd_half] = np.cos(
        2 * np.pi * y /
        10000**((d - depth_half - 1 + 1) / depth_half))[:, :, mask_odd_half]

    return pe


class SelfAttentionOfConv(torch.nn.Module):
    #inshape:[C,H,W]
    def __init__(self,
                 dim,
                 inshape,
                 subshape=[10, 10],
                 nhead=4,
                 dim_feedforward=64):
        super().__init__()
        self.inshape = inshape
        self.subshape = subshape
        super().register_buffer(
            'positionalEmbedding',
            torch.tensor(PositionalEmbedding2D(self.subshape, dim),
                         dtype=torch.float32).permute(
                             2, 0, 1).reshape([1, dim] + self.subshape))
        self.dim = dim
        self.sa = torch.nn.TransformerEncoderLayer(dim, nhead, dim_feedforward)

    def forward(self, x):
        x = F.interpolate(x, self.subshape, mode='bilinear')
        x = x + self.positionalEmbedding
        x = x.view(-1, self.dim, np.prod(self.subshape)).permute(0, 2, 1)
        x = self.sa(x)
        x = x.view(-1, self.dim, *self.subshape)
        x = F.interpolate(x, size=self.inshape, mode='bilinear')
        return x


class SelfAttentionOfConvCustomResampler(torch.nn.Module):
    #inshape:[C,H,W]
    def __init__(self,
                 dim,
                 inshape,
                 subshape,
                 downsampler,
                 upsampler,
                 nhead=4,
                 dim_feedforward=64):
        super().__init__()
        self.inshape = inshape
        self.subshape = subshape
        super().register_buffer(
            'positionalEmbedding',
            torch.tensor(PositionalEmbedding2D(self.subshape, dim),
                         dtype=torch.float32).permute(
                             2, 0, 1).reshape([1, dim] + self.subshape))
        self.dim = dim
        self.sa = torch.nn.TransformerEncoderLayer(dim, nhead, dim_feedforward)
        self.downsampler = downsampler
        self.upsampler = upsampler

    def forward(self, x):
        x = self.downsampler(x)
        x = x + self.positionalEmbedding
        x = x.view(-1, self.dim, np.prod(self.subshape)).permute(0, 2, 1)
        x = self.sa(x)
        x = x.view(-1, self.dim, *self.subshape)
        x = self.upsampler(x)
        return x


class SemanticInjectionModule(torch.nn.Module):

    def __init__(self, localdim, globaldim=None, outdim=None):
        if globaldim is None:
            globaldim = localdim
        if outdim is None:
            outdim = localdim
        self.localdim = localdim
        self.globaldim = globaldim
        self.outdim = outdim
        super().__init__()
        self.local = nn.Sequential(nn.Conv2d(localdim, outdim, 1), )
        self.global1 = nn.Sequential(
            nn.Conv2d(globaldim, outdim, 1),
            nn.Sigmoid(),
        )
        self.global2 = nn.Sequential(nn.Conv2d(globaldim, outdim, 1), )
        self.bn = nn.BatchNorm2d(outdim)

    def forward(self, local, globalsemantic):
        x = self.local(local) * self.global1(globalsemantic) + self.global2(
            globalsemantic)
        return self.bn(x)


class VGGNet(nn.Module):

    def __init__(self):
        super().__init__()
        self.comp = nn.Sequential(  #100
            inception.even(3, 64),
            nn.MaxPool2d(3, 1, 1),  #100
            inception.even(64, 124),
            nn.MaxPool2d(3, 1, 1),  #100
            inception.even(124, 256),
            inception.even(256, 256),
            nn.MaxPool2d(2),  #50
            inception.even(256, 512),
            inception.even(512, 512),
            nn.MaxPool2d(2),  #25
            inception.even(512, 512),
            nn.ReLU(),
            inception.even(512, 512),
            nn.ReLU(),
            nn.MaxPool2d(5),  #5
            nn.Flatten(1, -1),
            nn.Linear(512 * 5**2, 4096),
            nn.ReLU(),
            nn.Linear(4096, 4096),
            nn.ReLU(),
            nn.Linear(4096, 100),
            nn.ReLU(),
        )

        # original one
        # self.comp = nn.Sequential(  #100
        #     nn.Conv2d(3, 64, 3, padding=1),
        #     nn.ReLU(),
        #     nn.MaxPool2d(3,1, 1),  #100
        #     nn.Conv2d(64, 124, 3, padding=1),
        #     nn.ReLU(),
        #     nn.MaxPool2d(3,1, 1),  #100
        #     nn.Conv2d(124, 256, 3, padding=1),
        #     nn.ReLU(),
        #     nn.Conv2d(256, 256, 3, padding=1),
        #     nn.ReLU(),
        #     nn.MaxPool2d(2),  #50
        #     nn.Conv2d(256, 512, 3, padding=1),
        #     nn.ReLU(),
        #     nn.Conv2d(512, 512, 3, padding=1),
        #     nn.ReLU(),
        #     nn.MaxPool2d(2),  #25
        #     nn.Conv2d(512, 512, 3, padding=1),
        #     nn.ReLU(),
        #     nn.Conv2d(512, 512, 3, padding=1),
        #     nn.ReLU(),
        #     nn.MaxPool2d(5),  #5
        #     nn.Flatten(1, -1),
        #     nn.Linear(512 * 5**2, 4096),
        #     nn.ReLU(),
        #     nn.Linear(4096, 4096),
        #     nn.ReLU(),
        #     nn.Linear(4096, 100),
        #     nn.ReLU(),
        # )

    def forward(self, x):
        return self.comp(x)


class nntracker_yolo(torch.nn.Module, BaseModule4NNTracker):

    def __init__(self) -> None:
        super().__init__()
        picsurface = np.prod(nntracker_yolo.stdShape)
        self.comp = torch.nn.Sequential(
            cbrps(3, 8, 9, 9),
            # res_through(
            SelfAttentionOfConv(8, nntracker_yolo.stdShape),
            SelfAttentionOfConv(8, nntracker_yolo.stdShape),
            SelfAttentionOfConv(8, nntracker_yolo.stdShape),
            SelfAttentionOfConv(8, nntracker_yolo.stdShape),
            SelfAttentionOfConv(8, nntracker_yolo.stdShape),
            SelfAttentionOfConv(8, nntracker_yolo.stdShape),
            # ),
            torch.nn.Conv2d(8, 1, 1, padding='same'),
            torch.nn.LeakyReLU(),
            torch.nn.Flatten(1, -1),
            torch.nn.Linear(np.prod(np.array(nntracker_yolo.stdShape)), 100),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(100, 10),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(10, 5),
        )
        self.comp.modules

    def forward(self, m):
        normalizeCoef = (nntracker_yolo.stdShape[1],
                         nntracker_yolo.stdShape[0],
                         nntracker_yolo.stdShape[1],
                         nntracker_yolo.stdShape[0], 1)
        out = self.comp(m) \
            * torch.tensor(normalizeCoef)\
                .view(1, 5).to(device)
        return out


class nntracker_simple(torch.nn.Module, BaseModule4NNTracker):

    def __init__(self) -> None:
        super().__init__()
        self.preproc = torch.nn.Sequential(
            cbr(3, 8, 9),
            res_through(
                inception.even(8, 8),
                inception.even(8, 8),
            ),
        )
        #downsampling 16x
        self.contentway = torch.nn.Sequential(
            inception.even(8, 8),
            res_through(
                nn.Sequential(
                    nn.MaxPool2d(4),
                    #32
                    inception.even(8, 16),
                    res_through(
                        nn.Sequential(
                            nn.MaxPool2d(4),
                            inception.even(16, 64),
                            #8
                            res_through(
                                inception.even(64, 64),
                                inception.even(64, 64),
                            ),
                            nn.ConvTranspose2d(64, 16, 4, stride=4),
                        ),
                        combiner=SemanticInjectionModule(16)),
                    nn.ConvTranspose2d(16, 8, 4, stride=4),
                ),
                combiner=SemanticInjectionModule(8)),
            torch.nn.LeakyReLU(),
        )
        self.positionway = torch.nn.Sequential(
            res_through(
                inception.even(8, 8),
                inception.even(8, 8),
                inception.even(8, 8),
            ), )
        self.deco = torch.nn.Sequential(
            inception.even(2 * 8 + 3, 8),
            res_through(
                inception.even(8, 8),
                inception.even(8, 8),
            ),
            torch.nn.Conv2d(8, 1, 1, padding='same'),
            torch.nn.LeakyReLU(),
        )

    def forward(self, m):
        pp = self.preproc(m)
        cont = self.contentway(pp)
        pos = self.positionway(pp)
        out = self.deco(torch.concat([cont, pos, m], dim=1))
        return out


class unet(nn.Module, BaseModule4NNTracker):

    def __init__(self):
        super().__init__()
        self.comp = nn.Sequential(
            #100
            inception.even(3, 64),
            inception.even(64, 64),
            res_through(
                nn.Sequential(
                    nn.MaxPool2d(2),
                    #50
                    inception.even(64, 128),
                    inception.even(128, 128),
                    res_through(
                        nn.Sequential(
                            nn.MaxPool2d(2),
                            #25
                            inception.even(128, 256),
                            inception.even(256, 256),
                            res_through(
                                nn.Sequential(
                                    nn.MaxPool2d(5),
                                    #5
                                    inception.even(256, 512),
                                    inception.even(512, 512),
                                    res_through(
                                        nn.Sequential(
                                            nn.MaxPool2d(5),
                                            #1
                                            inception.even(512, 1024),
                                            inception.even(1024, 1024),
                                            nn.ConvTranspose2d(1024,
                                                               512,
                                                               5,
                                                               stride=5),
                                        )),
                                    nn.ConvTranspose2d(512, 256, 5, stride=5),
                                )),
                            nn.ConvTranspose2d(256, 128, 2, stride=2),
                        )),
                    nn.ConvTranspose2d(128, 64, 2, stride=2),
                )),
            nn.Conv2d(64, 1, kernel_size=3, padding='same'),
        )

    def forward(self, x):
        return self.comp(x)


def getmodel(modelpath):
    model = setModel(nntracker_simple(), device=device,
                     path=modelpath).to(device=device)
    #print(model)
    return model


from torch.utils.tensorboard import SummaryWriter
import traceback
import itertools
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
import time
# %%
# nn def
modelpath = r'nntracker.pth'
model = getmodel(modelpath)
writer = SummaryWriter(
    f"runs/{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}"
)  # 存放log文件的目录

# %%\
# dataset

import openpyxl as opx
def Xls2ListList(path=None, sheetname=None, killNones=True):
    if path is None:
        path = r'eles.in.xlsx'
    xls = opx.load_workbook(path)
    if sheetname is None:
        sheet = xls.active
    else:
        sheet = xls[sheetname]

    ret = [[ele.value for ele in ln] for ln in (sheet.rows)]
    if killNones:
        ret = [l for l in ret if any([e is not None for e in l])]
    return ret

from torchvision.transforms import ToTensor

from torch.utils.data import Dataset

def readImgInFolder(folder, pathlist):
    mlist = [os.path.join(folder, m) for m in pathlist]
    mlist = [cv.imread(m, 1) for m in mlist]
    mlist = [m.astype(np.float32) / 255 for m in mlist]
    return mlist


def readImgInZip(zipf, pathlist):
    from zipfile import ZipFile
    zipf = ZipFile(zipf)
    mlist = [zipf.read(imgf) for imgf in pathlist]
    mlist = [np.frombuffer(m, dtype=np.uint8) for m in mlist]
    mlist = [cv.imdecode(m, 1) for m in mlist]
    mlist = [m.astype(np.float32) / 255 for m in mlist]
    return mlist


class labeldataset(Dataset):

    def __init__(self) -> None:
        super().__init__()

    def init(self,
             path,
             selection,
             size,
             pathtype='fld',
             sheetname=None,
             stdShape=None):
        self.size = size
        selection = Xls2ListList(selection, sheetname)
        selection = [s[0] for s in selection]
        selection = [s for s in selection if s is not None]
        self.names = selection

        if pathtype == 'fld':
            reader = readImgInFolder
        elif pathtype == 'zip':
            reader = readImgInZip
        else:
            raise TypeError(f'inproper path type {pathtype}')

        spl = reader(path, [rf'spl/{p}' for p in selection])
        lbl = reader(path, [rf'lbl/{p}' for p in selection])
        if stdShape is not None:
            spl = [cv.resize(m, stdShape) for m in spl]
            lbl = [cv.resize(m, stdShape) for m in lbl]
        lbl = [
            cv.threshold(p[:, :, 0:1], 0.5, 1, cv.THRESH_BINARY)[1]
            for p in lbl
        ]
        self.pairs = list(zip(spl, lbl))

        return self

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        index = int(len(self.pairs) * np.random.random())
        return [
            ToTensor()(i)
            for i in self.pairs[index]
        ]

    def rawlength(self):
        return len(self.pairs)

    def rawgetitem(self, rawidx):
        return self.pairs[rawidx]

    def getname(self, rawidx):
        return self.names[rawidx]


class yoloformdatafset(Dataset):

    def __init__(self) -> None:
        super().__init__()

    # #grid ,#bondingbox, width,widthofsourcepic
    def init(self,
             path,
             selection,
             size,
             S=7,
             B=1,
             W=448,
             W0=100,
             pathtype='fld',
             sheetname=None):
        self.size = size
        selection = Xls2ListList(selection, sheetname)
        selection = selection[1:]
        if len(selection) > 512:
            selection = selection[:512]
        names = [s[0] for s in selection]
        self.S, self.B, self.W, self.W0 = S, B, W, W0

        if pathtype == 'fld':
            reader = readImgInFolder
        elif pathtype == 'zip':
            reader = readImgInZip
        else:
            raise TypeError(f'inproper path type {pathtype}')

        pic = reader(path, [f'spl/{p}' for p in names])

        pairs = list(zip(pic, selection))

        def W0ToW(pair):
            img, (Name, MinX, MinY, MaxX, MaxY, CenterX, CenterY) = pair

            coors = [MinX, MinY, MaxX, MaxY, CenterX, CenterY]
            coors = map(lambda x: self.W / self.W0 * float(x), coors)
            MinX, MinY, MaxX, MaxY, CenterX, CenterY = coors

            img = cv.resize(img, (self.W, self.W))
            img = ToTensor()(img)

            grids = np.zeros([self.S, self.S, self.B * 5], np.float32)
            center = (CenterY, CenterX)
            centergrid = [int(self.S * c / self.W) for c in center]
            grids[centergrid[0], centergrid[1]] = [1, MinX, MinY, MaxX, MaxY]
            lbl = torch.tensor(grids)
            return img, lbl

        self.pairs = [W0ToW(p) for p in pairs]

        return self

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return self.pairs[int(len(self.pairs) * np.random.random())]

    def rawlength(self):
        return len(self.pairs)

    def rawgetitem(self, rawidx):
        return self.pairs[rawidx]

    def getname(self, rawidx):
        return self.names[rawidx]


def XYWH2XYXY(X, Y, W, H):
    return (X - W / 2, Y - H / 2, X + W / 2, Y + H / 2)


def XYXY2XYWH(x1, y1, x2, y2):
    return (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1


def AABBOf(lbl, noobjthresh=5):
    assert (len(lbl.shape) == 2)
    y, x = np.where(lbl > 0)
    if len(y) < noobjthresh:
        return (0, 0, 0, 0, 0)
    x1, x2 = np.min(x), np.max(x)
    y1, y2 = np.min(y), np.max(y)
    #(x1, x2, y1, y2, c)

    return XYXY2XYWH(x1, y1, x2, y2) + (1, )


print('loading dataset')
datasetname = 'LE2REnh'
datasetroot = '/kaggle/input/nntrackerdataset/'
if datasetname == 'LE2REnh':
    path = r"LE2REnh/LE2REnh"
    sel = r"LE2REnh/all.xlsx"
    datasettype = 'fld'
if datasetname == 'LE2RAREnh':
    path = r"LE2RAREnh/LE2RAREnh"
    sel = r"LE2RAREnh/all.xlsx"
    datasettype = 'fld'
elif datasetname == 'largeEnoughToRecon':
    path = r"largeEnoughToRecon/largeEnoughToRecon"
    sel = r"largeEnoughToRecon/all.xlsx"
    datasettype = 'fld'
elif datasetname == 'origins_nntracker':
    path = r"origins_nntracker\origins_nntracker"
    sel = r"origins_nntracker/hardones.xlsx"
    datasettype = 'fld'
elif datasetname == 'withaimingring':
    path = r"withaimingring/withaimingring"
    sel = r"withaimingring/xls.xlsx"
    datasettype = 'fld'

train_data = labeldataset().init(datasetroot + path, datasetroot + sel, 2048,
                                 datasettype, None, [96] * 2)
test_data = train_data
print('load finished')

#%%
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
    lblsurface = (lbl.sum(dim=[-1, -2, -3], keepdim=True) + 1)
    meanX = (lbl * X).sum(dim=(-1, -2), keepdim=True)
    meanY = (lbl * Y).sum(dim=(-1, -2), keepdim=True)
    dist2 = ((X - meanX)**2 + (Y - meanY)**2) / (lblsurface / torch.pi)
    coef = (1 + 0.5 * (dist2 > 1))
    coef[lblsurface[:, 0, 0, 0] < 3, :, :, :] = 3  # clear sky
    #[b,d,h,w]
    loss= \
    1*(
        (
            (coef*(lbl - lblhat)**2).sum(dim=[-1, -2, -3])
            #     /
            # (np.sqrt(lblsurface[:,0,0,0]) + 0.01) #emphasize large ons more
        )#**2
    ).sum()

    return (loss)


def trainmainprogress(batch, datatuple):
    model.train()
    datatuple = [d.to(device) for d in datatuple]
    src, lbl = datatuple
    lblhat = model.forward(src)
    loss = calclose(lbl, lblhat)
    return loss


def onoutput(batch, aveerr):
    writer.add_scalar('aveerr', aveerr, batch)


trainpipe.train(train_dataloader,
                torch.optim.AdamW(model.parameters(),
                                  lr=1e-4,
                                  weight_decay=1e-2),
                trainmainprogress,
                customSubOnOutput=onoutput)

#%%
# all the continious running should only be applied on codes above! plz stop here
if __name__ == '__main__':
    exit()

# %%
# view effect


def evalOnAll(updateSampleList=False, errcriterion=200):
    loss = 0
    rawlength = train_data.rawlength()
    nowpercentage = 0
    totaltime = 0
    model.eval()
    wronglist = [] if updateSampleList else None
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
            loss += curloss
            if updateSampleList and curloss > errcriterion:
                wronglist.append(pi)
            if nowpercentage <= pi / rawlength * 100:
                nowpercentage += 1
                print(f'{nowpercentage}%')
    print(f'average loss{loss/rawlength}')
    print(f'inference time{totaltime/rawlength}')
    if updateSampleList:
        train_data.pairs = [train_data.pairs[i] for i in wronglist]
        print(f'samplelist update done,wrong samples:{len(wronglist)}')


def viewmodel():
    datasetusing = train_data
    model.eval()

    samplenum = 3 * 4
    npp = nestedPyPlot([3, 4], [2, 2], plt.figure(figsize=(16, 16)))
    imshowconfig = {'cmap': 'gray', 'vmin': 0, 'vmax': 1}
    imshowconfignonnorm = {'cmap': 'gray'}
    totalinferencetime = 0
    infecount = 0
    with torch.no_grad():
        for i in range(samplenum):
            src, lbl = datasetusing[0]

            tsrc = src.reshape((1, ) + src.shape).to(device)
            tstart = time.perf_counter()
            lblhat = model.forward(tsrc)
            totalinferencetime += time.perf_counter() - tstart
            infecount += 1
            lblhat = np.array(lblhat[0, :, :, :].cpu())
            srcatte = np.zeros_like(src)
            #to ndarray

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
    print(f"average inferencetime={totalinferencetime / samplenum}")


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
