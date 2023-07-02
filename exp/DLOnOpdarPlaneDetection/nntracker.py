# warthunder distance measurement plotting scale optical character reconginization

RunOnWtUtilityEnviroment = True
# %%
#basics
if __package__ == '':
    from utilref import *
else:
    from .utilref import *
pass
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


# %%
