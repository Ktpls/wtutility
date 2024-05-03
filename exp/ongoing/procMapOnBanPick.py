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
def afterEffectOnLoadingScreen():
    highQuality = [
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]Bastogne(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]CentralTunisia(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]Cochinchina(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]ConsolidationOfPositionsOnSicily(LightVehicles).png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]Counteroffensive(LightVehicles).png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]CounterstrikeUnderSmolensk(LightVehicles).png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]Essen(LightVehicles).png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]HenanProvince(LightVehicles).png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]LakeLadoga(LightVehicles).png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]Mozdok(LightVehicles).png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\airHighQuality\[Operation]NearEast(LightVehicles).png",
        ############
        r"C:\file\code\wtutility\asset\autofreshmap\map\38thParallel.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\AbandonedFactory.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\AbandonedTown.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\AdvanceToTheRhine.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Alaska.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\AmericanDesert.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\AralSea.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\ArcticPier.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\ArcticPolarBase.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\ArdennesDomination#1.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\ArdennesDomination#2.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\AshRiver.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\BattleOfHurtgenForestConquest#1.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\BattleOfHurtgenForestDomination#1.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Berlin.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Breslau.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Campania.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\CargoPort.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Carpathians.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\EasternEurope.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\EuropeanProvince.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\FieldsOfNormandy.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\FieldsOfPoland(winter).png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\FieldsOfPoland.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Finland.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\FireArc.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\FrozenPass.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\FuldaDomination#1.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\FuldaDomination#2.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Japan.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Jungle.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Karelia.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Kurban.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\MaginotLineDomination#1.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\MaginotLineDomination#1Winter.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\MaginotLineDomination#2.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\MaginotLineDomination#2Winter.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\MiddleEast.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Mozdok#1.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Mozdok#2.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Normandy.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Poland(winter).png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Poland.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\PortNovorossiysk.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\PortNovorossiyskBattle#1.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\PortNovorossiyskBattle.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Pradesh.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\RedDesert.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\SandsOfSinai.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\SandsOfTunisia.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\SecondBattleOfElAlameinConquest#1.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\SecondBattleOfElAlameinDomination#1.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\SecondBattleOfElAlameinDomination#2.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Serversk-13.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Sinai.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Spaceport.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Stalingrad.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\SunCity.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\SurroundingsOfVolokolamsk.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Sweden.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\TestSite-2271.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Tunisia.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\VietnamDomination#1.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\VietnamDomination#2.png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\Volokolamsk.png",
    ]
    reconstructed = [
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Bastogne(LightVehicles).Png",
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]CentralTunisia(LightVehicles).Png",
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Cochinchina(LightVehicles).Png",
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]ConsolidationOfPositionsOnSicily(LightVehicles).Png",
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Counteroffensive(LightVehicles).Png",
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]CounterstrikeUnderSmolensk(LightVehicles).Png",
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Essen(LightVehicles).Png",
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]HenanProvince(LightVehicles).Png",
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]LakeLadoga(LightVehicles).Png",
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Mozdok(LightVehicles).Png",
        # r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]NearEast(LightVehicles).Png",
        ##############################
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[AirBattle]France1944.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[AirBattle]HurtgenSecondBattle.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[AirBattle]Moscow1941.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[AirBattle]OperationIskra.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[AlternateHistory]Afghanistan.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[AlternateHistory]BerlinSummer1945.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[AlternateHistory]KrymskSummer1945.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[AlternateHistory]Spain.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Event]OperationUranus.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[FrontLine]Korsun.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[FrontLine]Kuban.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[FrontLine]Kursk.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[FrontLine]Ladoga.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[FrontLine]Mozdok.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[MilitaryExercise]PreparationForLandingOnHokkaido.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Afghanistan.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Bastogne(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]BattleAtMalta.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]BattleForBastogne.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]BattleForSpain.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]BattleForTheRhine.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]BattleForVietnam.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]BattleOfTunisia.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Berlin.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]BourbonIsland.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Britain.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Bulge.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]CentralTunisia(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]ChinaCivilWar1946.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]City.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Cochinchina(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]ConsolidationOfPositionsOnSicily(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Counteroffensive(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]CounterstrikeUnderSmolensk(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]DefendingStalingrad.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]ElAlamein.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Essen(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]GolanHeights(AirSpawns).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]GolanHeights.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Guadalcanal.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]HenanProvince(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Honolulu(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Hurtgen.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]IwoJima.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Kamchatka.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]KamchatkaEast.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]KhalkhinGol.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Korea.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Korsun.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Kuban.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Kursk.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]LadogaWinter1941.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]LaizhouBay.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]LakeLadoga(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]LakeLadoga.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Malta.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Midway.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Moscow.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Moscow42ndKilometer.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]MoscowNaro-Fominsk.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]MoscowSerpukhov.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Mozdok(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]MozdokWinter1943.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]NearEast(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]NewGuinea.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Norway.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Peleliu.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Poland.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]PortMoresby(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Pyrenees.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]RoadToGrozny.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]RockyCanyon.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]RockyPillars.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Ruhr.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Saipan.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Sicily.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Sinai.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Smolensk1941.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Smolensk1943.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]SoutheasternCity.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Spain.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]TheLastBattleOfKhalkhynGol(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Vietnam.Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]WakeIsland(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]YooPassage(LightVehicles).Png",
        r"C:\file\code\wtutility\asset\autofreshmap\map\air\[Operation]Zhengzhou.Png",
    ]

    def ReadBrightness(m):
        m = cv.imread(m).astype(np.float32) / 255
        # m = cv.cvtColor(m, cv.COLOR_BGR2RGB)
        v = np.max(m, axis=2, keepdims=True)
        return v

    highQuality = [ReadBrightness(f) for f in highQuality]
    reconstructed = [ReadBrightness(f) for f in reconstructed]
    # V = list()
    AveV = np.zeros(highQuality[0].shape[0:2] + (1,))
    i = 0
    prog = Progress(len(highQuality) * len(highQuality))
    for h in range(len(highQuality)):
        for r in range(len(reconstructed)):
            # V.append((highQuality[h] - reconstructed[r]))
            AveV += highQuality[h] - reconstructed[r]
            i += 1
            prog.update(i)
    prog.setFinish()
    # V = np.array(V)

    def procExperimentData(V):
        def FullSqrt(x):
            mag = np.abs(x)
            return np.sign(x) * np.where(mag > 1, mag**0.5, mag)

        # it = 0
        # while True:
        #     AveV = np.average(V, axis=0, keepdims=True)
        #     DeltaV = V - AveV
        #     StdV = np.average(DeltaV**2, axis=0, keepdims=True) ** 0.5
        #     V = AveV + FullSqrt(DeltaV / StdV) * StdV
        #     it += 1
        #     if it > 5:
        #         break
        return np.average(V.squeeze(0), axis=0, keepdims=True)

    # plt.imshow(np.average(V, axis=0))
    # AveV = procExperimentData(V)
    Avev = AveV / i
    plt.imshow(AveV)


afterEffectOnLoadingScreen()
