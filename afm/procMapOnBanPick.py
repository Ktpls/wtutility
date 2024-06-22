# %%
from utilref import *
from utilitypack.util_pyplot import *
import dataclasses
import pytesseract.pytesseract as pytesseract
import itertools

pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

"""
不利于处理陆战ABC3点,由于图标被wt缩放处理过
"""


class AfterEffectOnLoadingScreen:

    shadow = r"asset\autofreshmap\statesign\avg_minn,maxx=[0.38048921403451735,1.2050963220176332].png"
    minn, maxx = [0.38048921403451735, 1.2050963220176332]

    @staticmethod
    def GetAfterEffectOnLoadingScreen():
        highQuality = []
        unshadowedReconstructed = []

        def ReadBrightness(m):
            m = cv.imread(m).astype(np.float32) / 255
            # m = cv.resize(m, None, fx=0.25, fy=0.25, interpolation=cv.INTER_AREA)
            # m = cv.cvtColor(m, cv.COLOR_BGR2RGB)
            v = np.max(m, axis=2)
            return v

        highQuality = [ReadBrightness(f) for f in highQuality]
        unshadowedReconstructed = [ReadBrightness(f) for f in unshadowedReconstructed]

        V = list()
        AveV = np.zeros(highQuality[0].shape[0:2] + (1,))
        i = 0
        deltaNum = len(highQuality) * len(unshadowedReconstructed)
        prog = Progress(deltaNum)
        for h in range(len(highQuality)):
            for r in range(len(unshadowedReconstructed)):
                V.append((highQuality[h] - unshadowedReconstructed[r]))
                i += 1
                prog.update(i)
        prog.setFinish()
        V = np.array(V)

        def delOverErroredByImg(V):
            valid = np.full_like(V, True, dtype=np.bool_)
            pltshape = [10, 10]
            mpp = MassivePicturePlot(pltshape)
            prog = Progress(np.prod(pltshape))
            for i in range(np.prod(pltshape) - 1):
                avg = np.mean(V, where=valid, axis=0, keepdims=True)
                std = np.std(V, where=valid, axis=0, keepdims=True)
                validNew = np.abs(V - avg) < 2 * std
                if (valid == validNew).all():
                    break
                valid = validNew
                mpp.toNextPlot()
                plt.imshow(avg[0])
                prog.update(i)
            prog.setFinish()
            avg = np.mean(V, where=valid, axis=0, keepdims=True)
            mpp.toNextPlot()
            plt.imshow(avg[0])

        def ignoreOverErroredPixel(V):
            avg = np.mean(V, axis=0)
            std = np.std(V, axis=0)
            window = [81, 81]
            stdReg = regionave(std, window)
            stdExceeds = (std - stdReg) / (stdReg + EPS)
            stdMask = stdExceeds < 0.1
            avg = regionave(avg, window, mask=stdMask)
            NewPyPlotAxis()
            plt.imshow(avg)
            # delta brightness to relative brightness
            base = np.mean(unshadowedReconstructed, axis=0)
            avg = (base + avg) / (base + EPS)
            NewPyPlotAxis()
            plt.imshow(avg)
            minn = np.min(avg)
            maxx = np.max(avg)
            print(f"minn,maxx=[{minn},{maxx}]")
            avgNorm = (avg - minn) / (maxx - minn) * 255
            cv.imwrite("avg.png", avgNorm)

        def fourierTransform(V):
            m = np.mean(V, axis=0)
            h, w = m.shape
            msize = np.prod(m.shape)
            flags = cv.DFT_COMPLEX_OUTPUT
            dft = np.fft.fftshift(cv.dft(m, flags=flags))
            X = np.arange(w).reshape(1, -1) - w // 2
            Y = np.arange(h).reshape(-1, 1) - h // 2
            dist = w // 10
            dft[np.logical_and(np.abs(X) > dist, np.abs(Y) > dist)] = 0
            magnitude_spectrum = (cv.magnitude(dft[:, :, 0], dft[:, :, 1])) / msize
            NewPyPlotAxis(), plt.imshow(magnitude_spectrum)
            imgback = cv.idft(np.fft.fftshift(dft), flags=flags) / msize
            NewPyPlotAxis(), plt.imshow(imgback[:, :, 0])

        ignoreOverErroredPixel(V)

    @staticmethod
    def loadShadow():

        minn, maxx = [AfterEffectOnLoadingScreen.minn, AfterEffectOnLoadingScreen.maxx]
        shadow = (cv.imread(AfterEffectOnLoadingScreen.shadow)[:, :, 0:1] / 255) * (
            maxx - minn
        ) + minn
        return shadow

    @staticmethod
    def applyShadow(m, shadow):
        return m * shadow


class BanPickScreenShot2MapAsset:

    mapRect = [1253, 160, 1630, 537]
    lineNameRect = [1230, 542, 1655, 560]
    lineBrRect = [1365, 561, 1540, 585]
    stdMapSize = [648, 648]
    pathScreenShot = r"output\mapsOrg"
    pathOutput = r"output\proced"

    @dataclasses.dataclass
    class ImgInfo:
        map: np.ndarray
        name: str
        br: str

        @staticmethod
        def fromBanPickScreenShot(img: np.ndarray):

            def cutRoi(m, rect):
                return m[rect[1] : rect[3], rect[0] : rect[2]]

            def StringProc(s):
                return re.sub("[\r\n\t]", "_", s)

            map = cutRoi(img, BanPickScreenShot2MapAsset.mapRect)
            map = cv.resize(
                map,
                BanPickScreenShot2MapAsset.stdMapSize,
                interpolation=cv.INTER_LANCZOS4,
            )

            iname = cutRoi(img, BanPickScreenShot2MapAsset.lineNameRect)
            name = pytesseract.image_to_string(iname)
            name = StringProc(name)

            def procFileName(s: str):
                s = regex.sub(r"\W\w", lambda x: str.upper(x.group()), s)
                s = (
                    s.replace("{", "[")
                    .replace("}", "]")
                    .replace("_", "")
                    .replace(" ", "")
                )
                return s

            name = procFileName(name)

            ibr = cutRoi(img, BanPickScreenShot2MapAsset.lineBrRect)
            br = pytesseract.image_to_string(ibr)
            br = StringProc(br)

            def procBr(s: str):
                s = s.replace("BR:", "").replace("_", "").replace(" ", "")
                if s.find("+") >= 0:
                    plusPos = s.find("+")
                    s = f"[{s[: plusPos]},None]"
                elif s.find("-") >= 0:
                    minusPos = s.find("-")
                    s = f"[{s[: minusPos]},{s[minusPos+1:]}]"
                else:
                    print(f"WARNING: cant proc Br {s}")
                return s

            br = procBr(br)

            return BanPickScreenShot2MapAsset.ImgInfo(map, name, br)

    @staticmethod
    def Screenshot2ImgInfo(fileList):
        prog = Progress(len(fileList))
        shadow = AfterEffectOnLoadingScreen.loadShadow()
        for i, f in enumerate(fileList):
            img = cv.imread(f)
            info = BanPickScreenShot2MapAsset.ImgInfo.fromBanPickScreenShot(img)
            fileName = make_filename_safe(f"{info.name}.png")
            img = info.map
            img = AfterEffectOnLoadingScreen.applyShadow(img, shadow)
            savemat(img, fileName, path=BanPickScreenShot2MapAsset.pathOutput)
            prog.update(i)

        prog.setFinish()

        print("Done!")


BanPickScreenShot2MapAsset.pathOutput = r"C:\Users\Kita\Pictures\Screenshots\pathOutput"
BanPickScreenShot2MapAsset.Screenshot2ImgInfo(
    [
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 183152.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 183118.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 183106.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 183050.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 182914.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 182829.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 182746.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 182727.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 182656.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 182623.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 182550.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 181316.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 174724.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 174720.png",
        r"C:\Users\Kita\Pictures\Screenshots\Screenshot 2024-06-22 174709.png"
    ]
)
