

# %%
import pytesseract.pytesseract as ptact
import re
from utilref import *

tesseractpath = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
ptact.tesseract_cmd = tesseractpath


def safename(name):
    return re.sub('[\\\\/:*?"<>|\r\n]', '-', name)


def autolabel(m):
    #pad for tesseract, she needs this
    m = np.pad(m, 3, 'constant', constant_values=(0, 0))
    label = ptact.image_to_string(
        m.astype('uint8'), lang='eng', config='--psm 7')
    label = label.replace('\r', '').replace('\n', '')
    return label


def islabeldigit(l):
    return l in \
        [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
        ]


def classify(m):
    label = safename(autolabel(m))
    savepath = rf'./output/labeled/{label if islabeldigit(label) else "10"}/'
    try:
        savemat(m, path=savepath, name=label)
    except OSError as ose:
        savemat(m, path=savepath, name='oserrname')


# %%
def classifyall(path):
    flist=AllFileIn(path)
    for i,f in enumerate(flist):
        m=cv.imread(f)[:,:,0]
        classify(m)
        if i%100==0:
            print(f'{i} of {len(flist)}')
classifyall(r"C:\file\code\wtutility\exp\DLOnPlottingScale\wtdmpsocr\output")
# %%
