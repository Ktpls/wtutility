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
        self.component = skiper(
            torch.nn.Sequential(
                torch.nn.Conv2d(n_i, n_o, n_c, padding='same', bias=False),
                torch.nn.BatchNorm2d(n_o),
                torch.nn.LeakyReLU(),
                skiper(torch.nn.MaxPool2d(n_p, stride=1, padding=int(n_p / 2)),
                       n_o, n_o)), n_i, n_o)

    def forward(self, m):
        #[b,c,h,w]
        return self.component.forward(m)


class nntracker(torch.nn.Module):

    def __init__(self) -> None:
        super().__init__()
        self.matchtempl = torch.nn.Sequential(
            cbrps(3, 32, 5, 5),
            cbrps(32, 16, 5, 5),
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
