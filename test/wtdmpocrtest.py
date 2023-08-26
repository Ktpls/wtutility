# %%
from utilref import *

sys.path.append("..")
from wtdistmeaspy_ocrimpl import implCNN

with open(r"C:\prog\wtutility\test\wtdmpocrtest\wtdmpocrtestxlsx.xlsx", "r") as inputfile:
    filelist = inputfile.read().split("\n")
widthheightratio = 3

col = int(np.ceil(np.sqrt(len(filelist) / widthheightratio)))
row = widthheightratio * col


imshowconfig = {"cmap": "gray", "vmin": 0, "vmax": 1}
npp = nestedPyPlot([row, col], [1, 1], plt.figure(figsize=(16, 16)))
implCNN.init()
for i, f in enumerate(filelist):
    npp.subplot(i, 0)
    a = f.replace('"', "")
    b = cv.imread(f.replace('"', ""), cv.IMREAD_GRAYSCALE)
    f = cv.imread(f.replace('"', ""), cv.IMREAD_GRAYSCALE).astype(np.float32) / 255
    label = implCNN.ocr(f, None, lambda x: None)
    plt.imshow(f, **imshowconfig)
    plt.title(label)
plt.show()
