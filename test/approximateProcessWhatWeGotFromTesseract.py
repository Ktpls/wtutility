from utilref import *
from autofreshmap_implementation import *


def doCutPlayer(m):
    # 400,330 -> 600,700
    playerlistLeftTop = [450, 330]
    playerlistRightDown = [600, 700]
    # actually player vehicles
    m = m[
        playerlistLeftTop[1] : playerlistRightDown[1],
        playerlistLeftTop[0] : playerlistRightDown[0],
    ]
    savemat(m)
    return m


def doTesseract(m):
    import pytesseract.pytesseract as pytesseract

    pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    return pytesseract.image_to_string(m, lang="eng")


def doWithTesseractOutput(output):
    asg = ApproximateStandardizationGuide(
        r"""
//confusing
[A4]->A
[Ss5]->S
[0Oo]->O
[Cc]->C
[Ili1Jj7T]->I
[Kk]->K
[Mm]->M
[Pp]->P
[UuVv]->U
[Ww]->W
[Xx]->X
[Zz]->Z
//nation marks
^O->
^#->
//unexpected
[^A-Za-z0-9\(\)\n]->
"""[
            1:-1
        ]
    )

    VehicleList = """
G91R
MiG15
MiG17
F86F
F86A
A4
"""[
        1:-1
    ]

    VehicleList = VehicleInfo.compile(VehicleList, asg)
    # raw from real tesseract result
    players = output

    VehicleInfo.detectAnyInOutputOfTesseract(players, VehicleList, asg)


out = (
    Pipe(cv.imread(r"C:\Users\Kita\Desktop\playerList.png"), printStep=True)
    .do(doCutPlayer)
    .do(doTesseract)
    .do(doWithTesseractOutput)
)
print(out)
