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
    def ocr(m):
        # padding for ease of recongnization by tesseract
        black = cv.copyMakeBorder(m, 3, 3, 3, 3, cv.BORDER_CONSTANT, value=0)

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
        assert(model is not None)
        return wtdmpsocr(ps, model)
