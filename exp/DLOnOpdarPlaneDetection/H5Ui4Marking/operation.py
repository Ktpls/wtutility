import base64
from utilref import *
'''
init using source img path
mark plane pos by markpos()
it will calc initial thresh
then adjust thresh by add/minthresh()
and view the result
finally use finish() to save result
'''


class OperatorOnSample:
    TmpPath = r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\H5Ui4Marking\m2shot_tmp.png'
    SrcPath = r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\H5Ui4Marking\dataset\proc\src'
    LabeledPath = r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\H5Ui4Marking\dataset\proc\labeled'
    ThreshModifyStep=5
    InitialThresh=30
    def __init__(self, path) -> None:

        self.path = path
        self.mcolor=cv.imread(path)
        self.mgray = cv.cvtColor(self.mcolor, cv.COLOR_BGR2GRAY)

    @staticmethod
    def readPngData(path):
        with open(path, mode='rb') as f:
            data = f.read()
        return base64.b64encode(data).decode(encoding='ascii')
    
    @staticmethod
    def blendAndToPng(m1, m2):
        ms=[m1,m2]
        ms=[m.reshape(m.shape+(1,)) if len(m.shape)==2 else m for m in ms]
        assert(all([len(m.shape)==3 for m in ms]))
        m1,m2=ms
        m2show = m1 * 0.5 + m2 * 0.5
        #m2show = mtarget
        cv.imwrite(OperatorOnSample.TmpPath, m2show)
        data = OperatorOnSample.readPngData(OperatorOnSample.TmpPath)
        return data

    def applythresh(self):
        planemarkcolor = 0
        selfmcopy = np.copy(self.mgray)
        cv.floodFill(selfmcopy, None, np.flip(self.pos), planemarkcolor, 255,
                     int(self.thresh),8|cv.FLOODFILL_FIXED_RANGE )[1]
        selfmcopy[selfmcopy != 0] = 255
        selfmcopy = 255 - selfmcopy
        return selfmcopy

    def showLabelEffect(self, mtarget):
        return OperatorOnSample.blendAndToPng(self.mcolor,mtarget)


    def markpos(self, pos):
        pos = np.array(pos).astype(np.int32)
        self.pos = pos
        self.thresh = OperatorOnSample.InitialThresh #called thresh, but actually delta
        return self.showLabelEffect(self.applythresh())

    def addthresh(self):
        self.thresh += OperatorOnSample.ThreshModifyStep
        return self.showLabelEffect(self.applythresh())

    def minthresh(self):
        self.thresh -= OperatorOnSample.ThreshModifyStep
        if self.thresh<0:
            self.thresh=0
        return self.showLabelEffect(self.applythresh())

    def finish(self):
        os.system(f'copy "{self.path}" "{OperatorOnSample.SrcPath}"')
        cv.imwrite(
            os.path.join(OperatorOnSample.LabeledPath,
                         os.path.basename(self.path)), self.applythresh())


class OperatorOnSample4Viewing(OperatorOnSample):
    def __init__(self, path) -> None:
        self.name=os.path.basename(path)
        self.mcolor=cv.imread(os.path.join(OperatorOnSample.SrcPath,self.name))
        self.m2=cv.imread(os.path.join(OperatorOnSample.LabeledPath,self.name))
    
    def show(self):
        return self.showLabelEffect(self.m2)
    
    def getname(self):
        return self.name
    
    def finish(self):
        pass #no modification