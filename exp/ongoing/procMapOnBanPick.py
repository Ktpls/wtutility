from utilref import *


import pytesseract.pytesseract as pytesseract

pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

'''
不利于处理陆战ABC3点，由于图标被wt缩放处理过
'''

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


ApplyFixing()
