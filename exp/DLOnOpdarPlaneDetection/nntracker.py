# %%
# basics
from utilref import *
from utilitypack.util_torch import *
from torch import nn
import torch.nn.functional as F
import functools
from nntracker_common import *

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

# %%
# nn def

# %%
# nn def


class BaseModule4NNTracker:
    stdShape = [128, 128]


def PositionalEmbedding2D(shape, depth, len_max=None):
    if len_max is None:
        len_max = 10000
    h, w = shape
    y = np.arange(0, h).reshape([-1, 1, 1])
    x = np.arange(0, w).reshape([1, -1, 1])
    d = np.arange(0, depth).reshape([1, 1, -1])
    pe = np.zeros(list(shape) + [depth], np.float32)

    def BroadCastToBeLikePe(vec):
        return np.zeros_like(pe) + vec

    d_like_pe = BroadCastToBeLikePe(d)

    sinx = np.sin(x / (len_max ** (d / depth)))
    cosx = np.cos(x / (len_max ** ((d - 1) / depth)))
    siny = np.sin(y / (len_max ** (d / depth)))
    cosy = np.cos(y / (len_max ** ((d - 1) / depth)))
    evens = BroadCastToBeLikePe(sinx) + BroadCastToBeLikePe(siny)
    odds = BroadCastToBeLikePe(cosx) + BroadCastToBeLikePe(cosy)
    pe[d_like_pe % 2 == 0] = evens[d_like_pe % 2 == 0]
    pe[d_like_pe % 2 == 1] = odds[d_like_pe % 2 == 1]

    return pe.reshape([1, -1, depth])


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
        self.local = nn.Sequential(
            nn.Conv2d(localdim, outdim, 1),
        )
        self.global1 = nn.Sequential(
            nn.Conv2d(globaldim, outdim, 1),
            nn.Sigmoid(),
        )
        self.global2 = nn.Sequential(
            nn.Conv2d(globaldim, outdim, 1),
        )
        self.bn = nn.BatchNorm2d(outdim)

    def forward(self, local, globalsemantic):
        x = self.local(local) * self.global1(globalsemantic) + self.global2(
            globalsemantic
        )
        return self.bn(x)


class AddPositionalEmbedding(nn.Module):
    def __init__(self, shape, depth, len_max=None):
        super().__init__()
        self.pe = nn.Parameter(
            torch.tensor(
                PositionalEmbedding2D(shape, depth, len_max),
                dtype=torch.float32,
                requires_grad=False,
            )
        )

    def forward(self, x):
        return x + self.pe


class PermuteModule(nn.Module):
    def __init__(self, dims):
        super().__init__()
        self.dims = dims

    def forward(self, x):
        return torch.permute(x, self.dims)


class nntracker_pi(torch.nn.Module):
    def __init__(self):
        super().__init__()
        useBn = True
        incver = "v3"
        self.mod = nn.Sequential(
            # 128
            inception.even(3, 8, bn=useBn, version=incver),
            res_through(
                inception.even(8, 8, bn=useBn, version=incver),
                inception.even(8, 8, bn=useBn, version=incver),
            ),
            nn.MaxPool2d(2),  # 64
            res_through(
                inception.even(8, 8, bn=useBn, version=incver),
                inception.even(8, 8, bn=useBn, version=incver),
            ),
            nn.MaxPool2d(2),  # 32
            res_through(
                inception.even(8, 8, bn=useBn, version=incver),
                inception.even(8, 8, bn=useBn, version=incver),
            ),
            PermuteModule((0, 2, 3, 1)),
            nn.Flatten(1, 2),  # keep depth unflattened
            AddPositionalEmbedding((32, 32), 8, 32),
            nn.TransformerEncoderLayer(8, 4, 32),
            nn.TransformerEncoderLayer(8, 4, 32),
            nn.Flatten(1, -1),
            nn.Linear(8 * 32**2, 100),
            nn.LeakyReLU(),
            nn.Linear(100, 20),
            nn.LeakyReLU(),
            nn.Linear(20, 3),
            nn.LeakyReLU(),
        )

    def forward(self, m):
        out = self.mod(m)
        return out


def getmodel(modelpath):
    model = setModule(nntracker_pi(), path=modelpath, device=device)
    # print(model)
    return model


# %%
