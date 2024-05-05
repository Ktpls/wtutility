# %%
from utilref import *
from utilitypack.util_pyplot import *
import dataclasses
import pytesseract.pytesseract as pytesseract
import itertools

pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

"""
不利于处理陆战ABC3点，由于图标被wt缩放处理过
"""


@dataclasses.dataclass
class ImgInfo:
    map: np.ndarray
    name: str
    br: str


mapRect = [1253, 160, 1630, 537]
lineNameRect = [1230, 542, 1655, 560]
lineBrRect = [1365, 561, 1540, 585]
stdMapSize = [648, 648]
csvColumns = ["fileName", "name", "br"]
csvPath = r"output\proced\data.csv"
fixedCsvPath = r"output\proced\data_fixed.csv"

import pandas as pd


def Screenshot2ImgInfo():
    fileList = AllFileIn(r"output\mapsOrg")
    prog = Progress(len(fileList))

    def cutRoi(m, rect):
        return m[rect[1] : rect[3], rect[0] : rect[2]]

    def StringProc(s):
        return re.sub("[\r\n\t]", "_", s)

    data = []
    for i, f in enumerate(fileList):
        img = cv.imread(f)

        map = cutRoi(img, mapRect)
        map = cv.resize(map, stdMapSize, interpolation=cv.INTER_LANCZOS4)

        iname = cutRoi(img, lineNameRect)
        name = pytesseract.image_to_string(iname)
        name = StringProc(name)

        ibr = cutRoi(img, lineBrRect)
        br = pytesseract.image_to_string(ibr)
        br = StringProc(br)

        info = ImgInfo(map, name, br)

        fileName = make_filename_safe(f"{info.name}.png")
        savemat(info.map, fileName, path=r"output\proced")
        data.append([fileName, info.name, info.br])
        prog.update(i)

    prog.setFinish()

    df = pd.DataFrame(data, columns=csvColumns)
    df.to_csv(csvPath, index=False)

    print("Done!")


def Reorganize():
    df = pd.read_csv(csvPath)

    def procFileName(s: str):
        s = regex.sub(r"\W\w", lambda x: str.upper(x.group()), s)
        s = s.replace("{", "[").replace("}", "]").replace("_", "").replace(" ", "")
        return s

    def procName(s: str):
        s = procFileName(s)
        return s

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

    df["fileName"] = df["fileName"].apply(procFileName)
    df["name"] = df["name"].apply(procName)
    df["br"] = df["br"].apply(procBr)

    df.to_csv(fixedCsvPath, index=False)


def ApplyFixing():
    df = pd.read_csv(csvPath)
    dff = pd.read_csv(fixedCsvPath)
    root = r"C:\prog\wtutility\output\proced"

    def rename(f0, f1):
        os.system(rf'move "{root}\{f0}" "{root}\{f1}"')

    for l, row in df.iterrows():
        f0 = row["fileName"]
        lrow = dff.loc[l]
        f1 = lrow["fileName"]
        rename(f0, f1)


# %%
def GetAfterEffectOnLoadingScreen():
    highQuality = [
        r"asset\autofreshmap\map\airHighQuality\[Operation]Bastogne(LightVehicles).Png",
        r"asset\autofreshmap\map\airHighQuality\[Operation]CentralTunisia(LightVehicles).Png",
        r"asset\autofreshmap\map\airHighQuality\[Operation]Cochinchina(LightVehicles).Png",
        r"asset\autofreshmap\map\airHighQuality\[Operation]ConsolidationOfPositionsOnSicily(LightVehicles).png",
        r"asset\autofreshmap\map\airHighQuality\[Operation]Counteroffensive(LightVehicles).png",
        r"asset\autofreshmap\map\airHighQuality\[Operation]CounterstrikeUnderSmolensk(LightVehicles).png",
        r"asset\autofreshmap\map\airHighQuality\[Operation]Essen(LightVehicles).png",
        r"asset\autofreshmap\map\airHighQuality\[Operation]HenanProvince(LightVehicles).png",
        r"asset\autofreshmap\map\airHighQuality\[Operation]LakeLadoga(LightVehicles).png",
        r"asset\autofreshmap\map\airHighQuality\[Operation]Mozdok(LightVehicles).png",
        r"asset\autofreshmap\map\airHighQuality\[Operation]NearEast(LightVehicles).png",
    ]
    unshadowedReconstructed = [
        r"asset\autofreshmap\map\air\[AirBattle]France1944.Png",
        r"asset\autofreshmap\map\air\[AirBattle]HurtgenSecondBattle.Png",
        r"asset\autofreshmap\map\air\[AirBattle]Moscow1941.Png",
        r"asset\autofreshmap\map\air\[AirBattle]OperationIskra.Png",
        r"asset\autofreshmap\map\air\[AlternateHistory]Afghanistan.Png",
        r"asset\autofreshmap\map\air\[AlternateHistory]BerlinSummer1945.Png",
        r"asset\autofreshmap\map\air\[AlternateHistory]KrymskSummer1945.Png",
        r"asset\autofreshmap\map\air\[AlternateHistory]Spain.Png",
        r"asset\autofreshmap\map\air\[Event]OperationUranus.Png",
        r"asset\autofreshmap\map\air\[FrontLine]Korsun.Png",
        r"asset\autofreshmap\map\air\[FrontLine]Kuban.Png",
        r"asset\autofreshmap\map\air\[FrontLine]Kursk.Png",
        r"asset\autofreshmap\map\air\[FrontLine]Ladoga.Png",
        r"asset\autofreshmap\map\air\[FrontLine]Mozdok.Png",
        r"asset\autofreshmap\map\air\[MilitaryExercise]PreparationForLandingOnHokkaido.Png",
        r"asset\autofreshmap\map\air\[Operation]Afghanistan.Png",
        r"asset\autofreshmap\map\air\[Operation]Bastogne(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]BattleAtMalta.Png",
        r"asset\autofreshmap\map\air\[Operation]BattleForBastogne.Png",
        r"asset\autofreshmap\map\air\[Operation]BattleForSpain.Png",
        r"asset\autofreshmap\map\air\[Operation]BattleForTheRhine.Png",
        r"asset\autofreshmap\map\air\[Operation]BattleForVietnam.Png",
        r"asset\autofreshmap\map\air\[Operation]BattleOfTunisia.Png",
        r"asset\autofreshmap\map\air\[Operation]Berlin.Png",
        r"asset\autofreshmap\map\air\[Operation]BourbonIsland.Png",
        r"asset\autofreshmap\map\air\[Operation]Britain.Png",
        r"asset\autofreshmap\map\air\[Operation]Bulge.Png",
        r"asset\autofreshmap\map\air\[Operation]CentralTunisia(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]ChinaCivilWar1946.Png",
        r"asset\autofreshmap\map\air\[Operation]City.Png",
        r"asset\autofreshmap\map\air\[Operation]Cochinchina(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]ConsolidationOfPositionsOnSicily(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Counteroffensive(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]CounterstrikeUnderSmolensk(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]DefendingStalingrad.Png",
        r"asset\autofreshmap\map\air\[Operation]ElAlamein.Png",
        r"asset\autofreshmap\map\air\[Operation]Essen(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]GolanHeights(AirSpawns).Png",
        r"asset\autofreshmap\map\air\[Operation]GolanHeights.Png",
        r"asset\autofreshmap\map\air\[Operation]Guadalcanal.Png",
        r"asset\autofreshmap\map\air\[Operation]HenanProvince(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Honolulu(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Hurtgen.Png",
        r"asset\autofreshmap\map\air\[Operation]IwoJima.Png",
        r"asset\autofreshmap\map\air\[Operation]Kamchatka.Png",
        r"asset\autofreshmap\map\air\[Operation]KamchatkaEast.Png",
        r"asset\autofreshmap\map\air\[Operation]KhalkhinGol.Png",
        r"asset\autofreshmap\map\air\[Operation]Korea.Png",
        r"asset\autofreshmap\map\air\[Operation]Korsun.Png",
        r"asset\autofreshmap\map\air\[Operation]Kuban.Png",
        r"asset\autofreshmap\map\air\[Operation]Kursk.Png",
        r"asset\autofreshmap\map\air\[Operation]LadogaWinter1941.Png",
        r"asset\autofreshmap\map\air\[Operation]LaizhouBay.Png",
        r"asset\autofreshmap\map\air\[Operation]LakeLadoga(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]LakeLadoga.Png",
        r"asset\autofreshmap\map\air\[Operation]Malta.Png",
        r"asset\autofreshmap\map\air\[Operation]Midway.Png",
        r"asset\autofreshmap\map\air\[Operation]Moscow.Png",
        r"asset\autofreshmap\map\air\[Operation]Moscow42ndKilometer.Png",
        r"asset\autofreshmap\map\air\[Operation]MoscowNaro-Fominsk.Png",
        r"asset\autofreshmap\map\air\[Operation]MoscowSerpukhov.Png",
        r"asset\autofreshmap\map\air\[Operation]Mozdok(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]MozdokWinter1943.Png",
        r"asset\autofreshmap\map\air\[Operation]NearEast(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]NewGuinea.Png",
        r"asset\autofreshmap\map\air\[Operation]Norway.Png",
        r"asset\autofreshmap\map\air\[Operation]Peleliu.Png",
        r"asset\autofreshmap\map\air\[Operation]Poland.Png",
        r"asset\autofreshmap\map\air\[Operation]PortMoresby(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Pyrenees.Png",
        r"asset\autofreshmap\map\air\[Operation]RoadToGrozny.Png",
        r"asset\autofreshmap\map\air\[Operation]RockyCanyon.Png",
        r"asset\autofreshmap\map\air\[Operation]RockyPillars.Png",
        r"asset\autofreshmap\map\air\[Operation]Ruhr.Png",
        r"asset\autofreshmap\map\air\[Operation]Saipan.Png",
        r"asset\autofreshmap\map\air\[Operation]Sicily.Png",
        r"asset\autofreshmap\map\air\[Operation]Sinai.Png",
        r"asset\autofreshmap\map\air\[Operation]Smolensk1941.Png",
        r"asset\autofreshmap\map\air\[Operation]Smolensk1943.Png",
        r"asset\autofreshmap\map\air\[Operation]SoutheasternCity.Png",
        r"asset\autofreshmap\map\air\[Operation]Spain.Png",
        r"asset\autofreshmap\map\air\[Operation]TheLastBattleOfKhalkhynGol(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Vietnam.Png",
        r"asset\autofreshmap\map\air\[Operation]WakeIsland(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]YooPassage(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Zhengzhou.Png",
    ]

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


# GetAfterEffectOnLoadingScreen()


# %%
def AddShadowMaskOnReconstructed():

    reconstructed = [
        r"asset\autofreshmap\map\air\[AirBattle]France1944.Png",
        r"asset\autofreshmap\map\air\[AirBattle]HurtgenSecondBattle.Png",
        r"asset\autofreshmap\map\air\[AirBattle]Moscow1941.Png",
        r"asset\autofreshmap\map\air\[AirBattle]OperationIskra.Png",
        r"asset\autofreshmap\map\air\[AlternateHistory]Afghanistan.Png",
        r"asset\autofreshmap\map\air\[AlternateHistory]BerlinSummer1945.Png",
        r"asset\autofreshmap\map\air\[AlternateHistory]KrymskSummer1945.Png",
        r"asset\autofreshmap\map\air\[AlternateHistory]Spain.Png",
        r"asset\autofreshmap\map\air\[Event]OperationUranus.Png",
        r"asset\autofreshmap\map\air\[FrontLine]Korsun.Png",
        r"asset\autofreshmap\map\air\[FrontLine]Kuban.Png",
        r"asset\autofreshmap\map\air\[FrontLine]Kursk.Png",
        r"asset\autofreshmap\map\air\[FrontLine]Ladoga.Png",
        r"asset\autofreshmap\map\air\[FrontLine]Mozdok.Png",
        r"asset\autofreshmap\map\air\[MilitaryExercise]PreparationForLandingOnHokkaido.Png",
        r"asset\autofreshmap\map\air\[Operation]Afghanistan.Png",
        r"asset\autofreshmap\map\air\[Operation]Bastogne(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]BattleAtMalta.Png",
        r"asset\autofreshmap\map\air\[Operation]BattleForBastogne.Png",
        r"asset\autofreshmap\map\air\[Operation]BattleForSpain.Png",
        r"asset\autofreshmap\map\air\[Operation]BattleForTheRhine.Png",
        r"asset\autofreshmap\map\air\[Operation]BattleForVietnam.Png",
        r"asset\autofreshmap\map\air\[Operation]BattleOfTunisia.Png",
        r"asset\autofreshmap\map\air\[Operation]Berlin.Png",
        r"asset\autofreshmap\map\air\[Operation]BourbonIsland.Png",
        r"asset\autofreshmap\map\air\[Operation]Britain.Png",
        r"asset\autofreshmap\map\air\[Operation]Bulge.Png",
        r"asset\autofreshmap\map\air\[Operation]CentralTunisia(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]ChinaCivilWar1946.Png",
        r"asset\autofreshmap\map\air\[Operation]City.Png",
        r"asset\autofreshmap\map\air\[Operation]Cochinchina(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]ConsolidationOfPositionsOnSicily(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Counteroffensive(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]CounterstrikeUnderSmolensk(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]DefendingStalingrad.Png",
        r"asset\autofreshmap\map\air\[Operation]ElAlamein.Png",
        r"asset\autofreshmap\map\air\[Operation]Essen(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]GolanHeights(AirSpawns).Png",
        r"asset\autofreshmap\map\air\[Operation]GolanHeights.Png",
        r"asset\autofreshmap\map\air\[Operation]Guadalcanal.Png",
        r"asset\autofreshmap\map\air\[Operation]HenanProvince(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Honolulu(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Hurtgen.Png",
        r"asset\autofreshmap\map\air\[Operation]IwoJima.Png",
        r"asset\autofreshmap\map\air\[Operation]Kamchatka.Png",
        r"asset\autofreshmap\map\air\[Operation]KamchatkaEast.Png",
        r"asset\autofreshmap\map\air\[Operation]KhalkhinGol.Png",
        r"asset\autofreshmap\map\air\[Operation]Korea.Png",
        r"asset\autofreshmap\map\air\[Operation]Korsun.Png",
        r"asset\autofreshmap\map\air\[Operation]Kuban.Png",
        r"asset\autofreshmap\map\air\[Operation]Kursk.Png",
        r"asset\autofreshmap\map\air\[Operation]LadogaWinter1941.Png",
        r"asset\autofreshmap\map\air\[Operation]LaizhouBay.Png",
        r"asset\autofreshmap\map\air\[Operation]LakeLadoga(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]LakeLadoga.Png",
        r"asset\autofreshmap\map\air\[Operation]Malta.Png",
        r"asset\autofreshmap\map\air\[Operation]Midway.Png",
        r"asset\autofreshmap\map\air\[Operation]Moscow.Png",
        r"asset\autofreshmap\map\air\[Operation]Moscow42ndKilometer.Png",
        r"asset\autofreshmap\map\air\[Operation]MoscowNaro-Fominsk.Png",
        r"asset\autofreshmap\map\air\[Operation]MoscowSerpukhov.Png",
        r"asset\autofreshmap\map\air\[Operation]Mozdok(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]MozdokWinter1943.Png",
        r"asset\autofreshmap\map\air\[Operation]NearEast(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]NewGuinea.Png",
        r"asset\autofreshmap\map\air\[Operation]Norway.Png",
        r"asset\autofreshmap\map\air\[Operation]Peleliu.Png",
        r"asset\autofreshmap\map\air\[Operation]Poland.Png",
        r"asset\autofreshmap\map\air\[Operation]PortMoresby(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Pyrenees.Png",
        r"asset\autofreshmap\map\air\[Operation]RoadToGrozny.Png",
        r"asset\autofreshmap\map\air\[Operation]RockyCanyon.Png",
        r"asset\autofreshmap\map\air\[Operation]RockyPillars.Png",
        r"asset\autofreshmap\map\air\[Operation]Ruhr.Png",
        r"asset\autofreshmap\map\air\[Operation]Saipan.Png",
        r"asset\autofreshmap\map\air\[Operation]Sicily.Png",
        r"asset\autofreshmap\map\air\[Operation]Sinai.Png",
        r"asset\autofreshmap\map\air\[Operation]Smolensk1941.Png",
        r"asset\autofreshmap\map\air\[Operation]Smolensk1943.Png",
        r"asset\autofreshmap\map\air\[Operation]SoutheasternCity.Png",
        r"asset\autofreshmap\map\air\[Operation]Spain.Png",
        r"asset\autofreshmap\map\air\[Operation]TheLastBattleOfKhalkhynGol(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Vietnam.Png",
        r"asset\autofreshmap\map\air\[Operation]WakeIsland(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]YooPassage(LightVehicles).Png",
        r"asset\autofreshmap\map\air\[Operation]Zhengzhou.Png",
    ]
    dstroot = r"asset\autofreshmap\map\airshadowed"
    EnsureDirectoryExists(dstroot)
    shadow = r"asset\autofreshmap\statesign\avg_minn,maxx=[0.38048921403451735,1.2050963220176332].png"
    minn, maxx = [0.38048921403451735, 1.2050963220176332]
    shadow = (cv.imread(shadow)[:, :, 0:1] / 255) * (maxx - minn) + minn

    for src in reconstructed:
        dst = os.path.join(dstroot, os.path.basename(src))
        m = cv.imread(src)
        m = m * shadow
        cv.imwrite(dst, m)

#%%
# AddShadowMaskOnReconstructed()

highQuality = r"asset\autofreshmap\map\airHighQuality\[Operation]Counteroffensive(LightVehicles).png"
reconstructed = r"asset\autofreshmap\map\airshadowed\[Operation]Counteroffensive(LightVehicles).Png"
def read(path):
    return cv.imread(path)[:, :, 0:1].astype(np.float32)/255
highQuality = read(highQuality)
reconstructed = read(reconstructed)
delta=(reconstructed-highQuality)**2
plt.imshow(delta)