# warthunder distance measurement plotting scale optical character reconginization

# %%
if __package__ == '':
    from utilref import setModel,torch,batchsizeof,cv,np
    from defs import *
else:
    from .utilref import setModel,torch,batchsizeof,cv,np
    from .defs import *
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

# 0123456789E
tsize = 10
tsizep1 = tsize+1
typeElse = tsizep1-1

class cbrp(torch.nn.Module):
    def __init__(self,infeat,outfeat,convsize,poolsize) -> None:
        super().__init__()
        self.cbr = torch.nn.Sequential(
            torch.nn.Conv2d(infeat, outfeat, convsize, padding='same'),
            torch.nn.BatchNorm2d(outfeat),
            torch.nn.LeakyReLU(),
        )
        #self.pool= torch.nn.AvgPool2d(poolsize,padding=int(poolsize/2),stride=1)

    def forward(self, m):
        mcbr=self.cbr(m)
        return mcbr#+self.pool(mcbr)

class inception(torch.nn.Module):
    def __init__(self,infeat,outfeat11,outfeatpool,outfeat33,outfeat55) -> None:
        super().__init__()
        self.path11 = torch.nn.Sequential(
            torch.nn.Conv2d(infeat, outfeat11, 1, padding='same'),
            torch.nn.LeakyReLU(),
        )
        self.pathpool = torch.nn.Sequential(
            torch.nn.MaxPool2d(3,stride=1,padding=1),
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
    def forward(self, m):
        return torch.concat([
            self.path11(m),
            self.pathpool(m),
            self.path33(m),
            self.path55(m)
        ],dim=-3) #channel

class chardetector(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.comp = torch.nn.Sequential(
            cbrp(1,8,7,7),
            inception(8,4,4,4,4),
            torch.nn.BatchNorm2d(16),
            inception(16,8,8,8,8),
            torch.nn.BatchNorm2d(32),
            inception(32,4,4,4,4),
            torch.nn.BatchNorm2d(16),
            torch.nn.Conv2d(16, tsize, [charh, charw-1], padding=[0,int((charw-1-1)/2)]),
            torch.nn.LeakyReLU(),
            
        )

    def forward(self, m):
        tmat = self.comp(m)
        return tmat  # that

    def lose(self, tmathat, tmat, t):
        batchsize = batchsizeof(tmat)
        
        tmat=torch.max(tmat,dim=-2) # do max along height to squeeze it with height=1

        # type right = 0, wrong =1
        coef = torch.scatter(
            torch.ones((batchsize, tsizep1), dtype=torch.float32),
            -1,
            t.reshape((batchsize, 1)),
            torch.zeros((batchsize, 1))
        )[:, :tsize].reshape((batchsize, tsize, 1, 1))

        # and fine adjust
        coef = coef*3+1
        # [batch,channel,h,w]
        tmat=tmat.max(dim=-2)[0]
        tmat=tmat.unsqueeze(2) #give height dim back
        err = torch.sum(coef*(tmathat-tmat)**2)
        return err




def getmodel(modelpath):
    model = setModel(chardetector(), path=modelpath).to(device)
    #print(model)
    return model


# apply model on plotting scale
class RisingEdgeTrigger:
    def __init__(self, state0=False) -> None:
        self.state = state0

    def input(self, state):
        oldstate = self.state
        self.state = state
        return not oldstate and state


def wtdmpsocr(ps,model,resultthresh=0.5):
    assert(type(ps) is np.ndarray and len(ps.shape)==2)
    ps = ps.astype(np.float32).reshape((1, 1)+ps.shape)/255
    # [batch,channel,h,w]
    ps = torch.tensor(ps)
    with torch.no_grad():
        tmathat = model.forward(ps)[0, :, :, :]
    tmathat = np.array(tmathat)
    # [channel,h,w]
    t = np.max(tmathat, axis=-2)
    # [channel,w]
    # set t=argmax of type on this point,
    # if matchness of this type>thresh, else set type as else (tsizep1-1)

    tmax = np.max(t, axis=-2)
    targmax = np.argmax(t, axis=-2)



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
    result = ''
    for x in range(len(targmax)):  # range(w)
        if cscd.input(targmax[x] if tmax[x] > resultthresh else typeElse):
            result += f'{targmax[x]}'
    return result
