from exp.DLOnPlottingScale.wtdmpsocr.wtdmpsocr import getmodel, wtdmpsocr
import pytesseract.pytesseract as ptact
from utilitypack import *

tesseractpath = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class implocr:
    @staticmethod
    def init():
        ...

    @staticmethod
    def ocr(ps):
        ...


class implTesseract(implocr):
    @staticmethod
    def init():
        ptact.tesseract_cmd = tesseractpath

    @staticmethod
    def ocr(black):

        # filter density to remove noise points
        for i in range(2):
            black = densityfilter(black/255, [5, 5], 3/25).astype('float')*255
            # dbglogsavestep(black)

        charw, charh = 10, 20
        # filter density in single char region
        # padding left and right for full convolve
        black = cv.copyMakeBorder(
            black, 0, 0, charw, charw, cv.BORDER_CONSTANT, value=0)
        density = black.astype('float').sum(axis=0)/255
        density = np.correlate(density, np.ones(10))
        density /= (charw*charh)
        for x in range(len(density)):
            if density[x] < 0.05:
                black[:, int(x+0.5*charw+0.5)] = 0
        # dbglogsavestep(black)

        plottingscalestr = ptact.image_to_string(
            black.astype('uint8'), lang='eng', config='--psm 7')

        plottingscale = numinstr(plottingscalestr)
        plottingscalestr = str(plottingscale)
        if len(plottingscalestr) > 3:
            # got extra characters
            # trim and do it again
            # this is for the arrow indicating some players outside the map
            # blocks the 'm' in 'xxx m' and made it tough for ocr
            # but if arrow, or any tank icon blocking the digit chars this would have no way to fix
            plottingscalestr = plottingscalestr[:3]
            plottingscale = numinstr(plottingscalestr)
        return plottingscale


modelpath = r'.\exp\DLOnPlottingScale\wtdmpsocr\wtdmpsocr.pth'
model = None


class implCNN(implocr):
    @staticmethod
    def init():
        global model
        model = getmodel(modelpath)

    @staticmethod
    def ocr(ps):
        assert (model is not None)
        return numinstr(wtdmpsocr(ps, model))
