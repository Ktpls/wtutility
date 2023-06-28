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
                 bn=True) -> None:
        super().__init__()
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
        if bn is not None and bn:
            self.bn = torch.nn.BatchNorm2d(outfeat11 + outfeatpool +
                                           outfeat33 + outfeat55)
        else:
            self.bn = None

    @staticmethod
    def even(infeat, outfeat, bn=None):
        assert outfeat % 4 == 0
        outfeatby4 = int(outfeat / 4)
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
        for l in self.components:
            o = l(o) + o
        return o




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
        #self.scale = torch.sqrt(torch.FloatTensor([dim_head]))

    def forward(self, x):
        #[batch size, sequence length, and feature dimensions]
        B, N, C = x.shape
        qkv = self.to_qkv(x).reshape(B, N, 3, self.heads,
                                     self.dim_head).permute(2, 0, 3, 1, 4)
        # [3, batch size, num_heads, sequence length, feature dimensions per head]
        q, k, v = qkv[0], qkv[1], qkv[2]
        attn = (q @ k.transpose(-2, -1)) #/ self.scale
        attn = attn.softmax(dim=-1)
        attn = self.dropout(attn)
        out = (attn @ v).transpose(1, 2).permute(0, 2, 1, 3).reshape(
            B, N, self.heads * self.dim_head)
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


class SelfAttentionOfConv(torch.nn.Module):
    #inshape:[C,H,W]
    def __init__(self, dim, inshape):
        super().__init__()
        self.inshape = inshape
        self.sashape = [10, 10]
        self.dim = dim
        # self.sa = SelfAttention(dim)
        self.sa = torch.nn.TransformerEncoderLayer(dim,2,64,0)

    def forward(self, x):
        x = F.interpolate(x, self.sashape, mode='bilinear')
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
                SelfAttentionOfConv(4, nntracker_yolo.stdShape),
                inception.even(4, 4),
                SelfAttentionOfConv(4, nntracker_yolo.stdShape),
                inception.even(4, 4),
                SelfAttentionOfConv(4, nntracker_yolo.stdShape),
                inception.even(4, 4),
                SelfAttentionOfConv(4, nntracker_yolo.stdShape),
                inception.even(4, 4),
                SelfAttentionOfConv(4, nntracker_yolo.stdShape),
            ),
            torch.nn.Conv2d(4, 1, 1, padding='same'),
            torch.nn.LeakyReLU(),
            torch.nn.Flatten(1, -1),
            torch.nn.Linear(picsurface, 100),
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
        normalizeCoef = (nntracker_yolo.stdShape[0],
                         nntracker_yolo.stdShape[0],
                         nntracker_yolo.stdShape[1],
                         nntracker_yolo.stdShape[1], 1)
        out = self.comp(m) * torch.tensor(normalizeCoef).view(1, 5).to(device)
        return out


class nntracker_simple(torch.nn.Module):

    stdShape = [100, 100]

    def __init__(self) -> None:
        super().__init__()
        self.preproc = torch.nn.Sequential(
            cbrps(3, 8, 9, 9),
            # res_through(
                inception.even(8, 8),
                inception.even(8, 8),
                inception.even(8, 8),
            # ),
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
            # res_through(
                inception.even(8, 8),
                inception.even(8, 8),
                inception.even(8, 8),
                inception.even(8, 8),
                inception.even(8, 8),
            # ),
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


def getmodel(modelpath):
    model = setModel(nntracker_yolo(), device=device, path=modelpath).to(device=device)
    #print(model)
    return model


# %%
