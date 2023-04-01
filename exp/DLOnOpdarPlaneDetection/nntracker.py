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

class cbrpsold(torch.nn.Module):
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

class nntracker_simple(torch.nn.Module):

    def __init__(self) -> None:
        super().__init__()
        self.matchtempl = torch.nn.Sequential(
            cbrps(3, 32, 5, 11),
            cbrps(32, 32, 5, 5),
            cbrps(32, 16, 5, 11),
            torch.nn.Conv2d(16, 1, 5, padding='same'),
            torch.nn.LeakyReLU(),
        )

    def forward(self, m):
        return self.matchtempl(1 - m)


class YOLOv1(nn.Module):
    def __init__(self, num_classes=0, num_boxes=1,S=7):
        super(YOLOv1, self).__init__()
        self.num_classes = num_classes
        self.num_boxes = num_boxes
        self.S=S
        self.convs=nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(64, 192, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(192, 128, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(256, 256, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(512, 256, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(512, 256, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(512, 256, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(512, 256, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(512, 512, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(512, 1024, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(1024, 512, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(512, 1024, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(1024, 1024, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(1024, 1024, kernel_size=3, stride=2, padding=1),
            nn.ReLU(True),
            nn.Conv2d(1024, 1024, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(1024, 1024, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
        )
        self.fcs=nn.Sequential(
            nn.Linear(7*7*1024, 4096),
            nn.ReLU(True),
            nn.Linear(4096, S*S*(self.num_classes + self.num_boxes*5)),
            nn.ReLU(True),
            )

    def forward(self, x):
        x=self.convs(x)
        x = x.view(-1, self.S*self.S*1024)
        x=self.fcs(x)
        x = x.view(-1, self.S, self.S, self.num_classes + self.num_boxes*5)
        return x

def getmodel(modelpath):
    model = setModel(YOLOv1(), path=modelpath).to(device)
    #print(model)
    return model



# %%
