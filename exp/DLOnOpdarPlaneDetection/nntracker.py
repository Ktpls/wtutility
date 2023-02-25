# warthunder distance measurement plotting scale optical character reconginization

# %%
if __package__ == '':
    from utilref import setModel, torch, batchsizeof, cv, np
else:
    from .utilref import setModel, torch, batchsizeof, cv, np

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

# %%
# nn def
'''
idea is,
given charh x charw img,
use conv to find features
conv to combine features to tell char prob dist at this point
its like 10 channeled matchtemplate()
in final usage,
find max along height
find max along type(channel)
if maxtype>thresh, type is max type
else type is nothing here
content on that scan line along x axis can be told
we got classification along x axis
use rising edge trigger to tell where should type be output
'''


class cbrp(torch.nn.Module):
    #input chan, output chan, convolve size, pooling size
    def __init__(self, n_i, n_o, n_c, n_p) -> None:
        super().__init__()
        self.component = torch.nn.Sequential(
            torch.nn.Conv2d(n_i, n_o, n_c, padding='same', bias=False),
            torch.nn.BatchNorm2d(n_o),
            torch.nn.LeakyReLU(),
            torch.nn.MaxPool2d(n_p, stride=1, padding=int(n_p / 2)),
        )

    def forward(self, m):
        return self.component.forward(m)


class cbrp_skip(torch.nn.Module):
    #input chan, output chan, convolve size, pooling size
    #n_o should be like 2*n, cuz maxpool will be concated with former output
    def __init__(self, n_i, n_o, n_c, n_p) -> None:
        assert (n_o % 2 == 0)
        n_o_real = int(n_o / 2)
        super().__init__()
        self.component = torch.nn.Sequential(
            torch.nn.Conv2d(n_i, n_o_real, n_c, padding='same', bias=False),
            torch.nn.BatchNorm2d(n_o_real),
            torch.nn.LeakyReLU(),
        )
        self.pool = torch.nn.MaxPool2d(n_p, stride=1, padding=int(n_p / 2))

    def forward(self, m):
        #[b,c,h,w]
        a = self.component.forward(m)
        b = self.pool.forward(a)
        c = torch.concat([a, b], dim=-3)
        return c


class nntracker(torch.nn.Module):

    def __init__(self) -> None:
        super().__init__()
        self.matchtempl = torch.nn.Sequential(
            cbrp_skip(3, 32, 5, 5),
            cbrp_skip(32, 64, 5, 5),
            cbrp_skip(64, 16, 5, 5),
            torch.nn.Conv2d(16, 1, 5, padding='same'),
            torch.nn.LeakyReLU(),
        )

    def forward(self, m):
        return self.matchtempl(1 - m)

class nntracker_small(torch.nn.Module):

    def __init__(self) -> None:
        super().__init__()
        self.matchtempl = torch.nn.Sequential(
            cbrp_skip(3, 32, 5, 5),
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
