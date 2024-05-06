from utilitypack.util_ocv import *

from .wtdistmeaspy_config import *


class implocr:
    @staticmethod
    def init():
        ...

    @staticmethod
    def ocr(ps, dbglogsavestep, log):
        # ps in float within 0~1
        ...


class implPassby:
    @staticmethod
    def init():
        pass

    @staticmethod
    def ocr(ps, dbglogsavestep, log):
        log("using implPassby.ocr()")
        # a possible value so wont trigger secure check
        return 200


class implTesseract(implocr):
    @staticmethod
    def init():
        pass

    @staticmethod
    def ocr(black, dbglogsavestep, log):
        log("using implTesseract.ocr()")
        import pytesseract.pytesseract as pytesseract

        pytesseract.tesseract_cmd = tesseractpath

        # filter density to remove noise points
        for i in range(2):
            black = densityfilter(black, [5, 5], 3 / 25).astype("float")
            dbglogsavestep(black * 255)

        charw, charh = 10, 20
        # filter density in single char region
        # padding left and right for full convolve
        black = cv.copyMakeBorder(
            black, 0, 0, charw, charw, cv.BORDER_CONSTANT, value=0
        )
        density = black.astype("float").sum(axis=0)
        density = np.correlate(density, np.ones(10))
        density /= charw * charh
        for x in range(len(density)):
            if density[x] < 0.05:
                black[:, int(x + 0.5 * charw + 0.5)] = 0
        dbglogsavestep(getDemonstrationImg())
        dbglogsavestep(black)

        plottingscalestr = pytesseract.image_to_string(
            black.astype("uint8"), lang="eng", config="--psm 7"
        )
        log(f"plottingscalestr={plottingscalestr}")

        plottingscale = Numinstr(plottingscalestr)
        plottingscalestr = str(plottingscale)
        log(f"plottingscaleToNumToStr={plottingscalestr}")
        if len(plottingscalestr) > 3:
            # got extra characters
            # trim and do it again
            # this is for the arrow indicating some players outside the map
            # blocks the 'm' in 'xxx m' and made it tough for ocr
            # but if arrow, or any tank icon blocking the digit chars this would have no way to fix
            plottingscalestr = plottingscalestr[:3]
            plottingscale = Numinstr(plottingscalestr)
        log(f"plottingscaleFinal={plottingscale}")
        return plottingscale


model = None


class implCNN(implocr):
    @staticmethod
    def init():
        from exp.DLOnPlottingScale.wtdmpsocr.wtdmpsocr import getmodel

        global model
        model = getmodel(modelpath)

    @staticmethod
    def ocr(ps, dbglogsavestep, log):
        log("using implCNN.ocr()")
        from exp.DLOnPlottingScale.wtdmpsocr.wtdmpsocr import wtdmpsocr

        assert model is not None
        result = wtdmpsocr(ps, model, cnnresultthresh)
        log(f"resultstr={result}")
        result = Numinstr(result)
        log(f"resultnum={result}")
        return result
