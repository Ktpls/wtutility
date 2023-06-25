# warthunder distance measurement plotting scale optical character reconginization

RunOnWtUtilityEnviroment = True
# %%
#basics
if RunOnWtUtilityEnviroment:
    if __package__ == '':
        from utilref import *
    else:
        from .utilref import *
    pass
else:
    from utilkaggle import *
from torch import nn
import torch.nn.functional as F

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

# %%
# nn def

# %%
# nn def



class nntracker_simple(torch.nn.Module):

    stdShape = np.array([100, 100])

    def __init__(self) -> None:
        super().__init__()
        self.preproc = torch.nn.Sequential(
            cbrps(3, 8, 9, 9),
            inception.even(8, 8),
            inception.even(8, 8),
            inception.even(8, 8),
            torch.nn.Conv2d(8, 1, 1, padding='same'),
            torch.nn.LeakyReLU(),
        )
        self.interferenceAtte = torch.nn.Sequential(
            torch.nn.Flatten(1, -1),
            torch.nn.Linear(np.prod(nntracker_simple.stdShape), 100),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(100, 10),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(10, 10),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(10, 10),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(10, 100),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(100, np.prod(nntracker_simple.stdShape)),
            torch.nn.LeakyReLU(),
        )
        self.deco = torch.nn.Sequential(
            inception.even(1, 8),
            inception.even(8, 8),
            inception.even(8, 8),
            inception.even(8, 8),
            inception.even(8, 8),
            inception.even(8, 8),
            inception.even(8, 4),
            torch.nn.Conv2d(4, 1, 1, padding='same'),
            torch.nn.Sigmoid(),
        )

    def forward(self, m):
        opp = self.preproc(m)
        att = self.interferenceAtte(opp)
        att = att.view(-1, 1, nntracker_simple.stdShape[1],
                       nntracker_simple.stdShape[0])
        attnorm = att / torch.sqrt((att**2 + 0.0001).sum())

        out = self.deco(opp * attnorm)
        return out

    def applyOutAsAtteMaskOnM(self, m, out):
        return m * out + (1 - out)


class SelfAttention(torch.nn.Module):

    def __init__(self, dim, heads=8, dim_head=8, dropout=0.1):
        #dim, the channel depth
        super().__init__()
        self.heads = heads
        self.dim_head = dim_head
        # define linear layers
        self.to_qkv = torch.nn.Linear(dim, 3 * dim_head * heads, bias=False)
        self.to_out = torch.nn.Linear(dim_head * heads, dim)
        self.dropout = torch.nn.Dropout(dropout)
        
        super().register_buffer('scaleFactor', torch.sqrt(torch.FloatTensor([heads*dim_head]))) 

    def forward(self, x):
        #[batch size, sequence length, and feature dimensions]
        B, N, C = x.shape
        qkv = self.to_qkv(x).reshape(B, N, 3, self.heads,
                                     self.dim_head).permute(2, 0, 3, 1, 4)
        # [3, batch size, num_heads, sequence length, feature dimensions per head]
        q, k, v = qkv[0], qkv[1], qkv[2]
        attn = (q @ k.transpose(-2, -1))  / self.get_buffer('scaleFactor')
        attn = attn.softmax(dim=-1)
        attn = self.dropout(attn)
        out = (attn @ v).permute(0, 2, 1,
                                 3).reshape(B, N, self.heads * self.dim_head)
        return self.to_out(out)


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
    depthalf = depth // 2
    y = np.arange(0, shape[0]).reshape([shape[0], 1, 1])
    x = np.arange(0, shape[1]).reshape([1, shape[1], 1])
    d = np.arange(0, depth).reshape([1, 1, depth])
    pe = np.zeros(shape + [depth], np.float32)
    val = np.sin(x / 10000**(d / 128))
    # np.putmask(pe, np.logical_and(d % 2 == 0, d < depthalf),
    #            np.sin(x / 10000**(d / 128)))
    # np.putmask(pe, np.logical_and(d % 2 == 1, d < depthalf),
    #            np.cos(x / 10000**((d - 1) / 128)))
    # np.putmask(pe, np.logical_and((d - depthalf) % 2 == 0, d >= depthalf),
    #            np.sin(y / 10000**((d - depthalf) / 128)))
    # np.putmask(pe, np.logical_and((d - depthalf) % 2 == 1, d >= depthalf),
    #            np.cos(y / 10000**((d - depthalf - 1) / 128)))
    mask = np.logical_and(d % 2 == 0, d < depthalf)[0, 0, :]
    pe[:, :, mask] = np.sin(2*np.pi*x / 10000**(d / shape[1]))[:, :, mask]
    mask = np.logical_and(d % 2 == 1, d < depthalf)[0, 0, :]
    pe[:, :, mask] = np.cos(2*np.pi*x / 10000**((d - 1) / shape[1]))[:, :, mask]
    mask = np.logical_and((d - depthalf) % 2 == 0, d >= depthalf)[0, 0, :]
    pe[:, :, mask] = np.sin(2*np.pi*y / 10000**((d - depthalf) / shape[0]))[:, :, mask]
    mask = np.logical_and((d - depthalf) % 2 == 1, d >= depthalf)[0, 0, :]
    pe[:, :, mask] = np.cos(2*np.pi* y / 10000**((d - depthalf - 1) / shape[0]))[:, :, mask]
    return pe


class SelfAttentionOfConv(torch.nn.Module):
    #inshape:[C,H,W]
    def __init__(self, dim, inshape, subshape=[10,10]):
        super().__init__()
        self.inshape = inshape
        self.sashape = subshape
        super().register_buffer('positionalEmbedding', torch.tensor(PositionalEmbedding2D(self.sashape, dim),dtype=torch.float32).permute(
            2, 0, 1).reshape([1, dim] + self.sashape))
        self.dim = dim
        self.sa = SelfAttention(dim)

    def forward(self, x):
        x = F.interpolate(x, self.sashape, mode='bilinear')
        x = x + self.get_buffer('positionalEmbedding')
        x = x.view(-1, self.dim, np.prod(self.sashape)).permute(0, 2, 1)
        x = self.sa(x)
        x = x.view(-1, self.dim, *self.sashape)
        x = F.interpolate(x, size=self.inshape, mode='bilinear')
        return x


class nntracker_yolo(torch.nn.Module):

    stdShape = [100, 100]

    def __init__(self) -> None:
        super().__init__()
        picsurface = np.prod(nntracker_yolo.stdShape)
        subshape1=nntracker_yolo.stdShape
        subshape2=torch.tensor(nntracker_yolo.stdShape)//2
        self.comp = torch.nn.Sequential(
            cbrps(3, 4, 9, 9),
            res_through(
                inception.even(4, 4),
                SelfAttentionOfConv(4, nntracker_yolo.stdShape),
                inception.even(4, 4),
                SelfAttentionOfConv(4, nntracker_yolo.stdShape),
                inception.even(4, 4),
                SelfAttentionOfConv(4, nntracker_yolo.stdShape),
                inception.even(4, 4),
                SelfAttentionOfConv(4, nntracker_yolo.stdShape),),
            torch.nn.Conv2d(4, 1, 1, padding='same'),
            torch.nn.LeakyReLU(),
            torch.nn.Flatten(1, -1),
            torch.nn.Linear(np.prod(np.array(nntracker_yolo.stdShape)), 100),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(100, 10),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(10, 10),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(10, 10),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(10, 5),
        )

    def forward(self, m):
        normalizeCoef = (nntracker_yolo.stdShape[1],
                         nntracker_yolo.stdShape[0],
                         nntracker_yolo.stdShape[1],
                         nntracker_yolo.stdShape[0], 1)
        out = self.comp(m) * torch.tensor(normalizeCoef).view(1, 5).to(device)
        return out


def getmodel(modelpath):
    model = setModel(nntracker_yolo(), device=device,
                     path=modelpath).to(device=device)
    #print(model)
    return model


# %%
