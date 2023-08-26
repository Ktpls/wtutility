# warthunder distance measurement plotting scale optical character reconginization

# %%
if __package__ == "":
    from utilref import *
    from defs import *
else:
    from .utilref import *
    from .defs import *

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

# %%
# nn def
"""
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
"""

# 0123456789E
tsize = tsizep1
tsizep1 = tsize + 1
typeElse = tsizep1 - 1


class cbr(torch.nn.Module):
    def __init__(self, infeat, outfeat, convsize, poolsize) -> None:
        super().__init__()
        self.cbr = torch.nn.Sequential(
            torch.nn.Conv2d(infeat, outfeat, convsize, padding="same"),
            torch.nn.BatchNorm2d(outfeat),
            torch.nn.LeakyReLU(),
        )

    def forward(self, m):
        mcbr = self.cbr(m)
        return mcbr 


class chardetector(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        windowWidth = charw | 1
        paddingWidth = charw // 2
        self.comp = torch.nn.Sequential(
            cbr(1, 8, 9, 9),
            res_through(
                inception.even(8, 8),
            ),
            torch.nn.Dropout2d(0.25),
            torch.nn.Conv2d(
                8,
                tsize,
                [charh, windowWidth],
                stride=[charh, 1],
                padding=[0, paddingWidth],
            ),
            torch.nn.LeakyReLU(),
        )

    def forward(self, m):
        if len(m.shape) < 4:
            m = m.unsqueeze(1)
        lblhat = self.comp(m)
        # batch, type, height, width
        lblhat = lblhat.squeeze(2)
        # batch, type, width
        return lblhat

    def lose(self, label, labelhat):
        batchsize = batchsizeof(label)

        coef = 1
        err = torch.sum(coef * (labelhat - label) ** 2)
        return err


def getmodel(modelpath):
    model = setModel(chardetector(), path=modelpath).to(device)
    # print(model)
    return model


# apply model on plotting scale
class RisingEdgeTrigger:
    def __init__(self, state0=False) -> None:
        self.state = state0

    def input(self, state):
        oldstate = self.state
        self.state = state
        return not oldstate and state


def wtdmpsocr(ps, model, resultthresh=0.5):
    assert type(ps) is np.ndarray and len(ps.shape) == 2
    ps = ps.astype(np.float32).reshape((1,) + ps.shape) / 255
    # [batch,channel,h,w]
    ps = torch.tensor(ps)
    model.eval()
    with torch.no_grad():
        lblhat = np.array(model.forward(ps)[0, :, :])
    # [channel,w]
    # set t=argmax of type on this point,
    # if matchness of this type>thresh, else set type as else (tsizep1-1)

    tmax = np.max(lblhat, axis=0)
    targmax = np.argmax(lblhat, axis=0)

    class CharStateChangeDetector:
        def __init__(self, state0=typeElse) -> None:
            self.state = state0

        def input(self, state):
            oldstate = self.state
            self.state = state
            # ret true when detect new char
            # that is, ret true when lastCharType!=charType, and charType!=typeElse
            if state != typeElse and oldstate != state:
                return True
            return False

    cscd = CharStateChangeDetector()
    result = ""
    for x in range(len(targmax)):  # range(w)
        if cscd.input(targmax[x] if tmax[x] > resultthresh else typeElse):
            result += f"{targmax[x]}"
    return result
