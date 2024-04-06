# %%
from utilref import *
import numpy as np
from matplotlib import pyplot as plt

plotLayout = 230
i = 0


def myImshow(m, title):
    global i
    i += 1
    plt.subplot(plotLayout + i)
    plt.imshow(m, cmap="gray")
    plt.title(title), plt.xticks([]), plt.yticks([])


img = cv.imread(
    r"C:\file\code\wtutility\output\img2test\unnamed-1.png", 0
)  # 0表示灰度图
img = np.float32(img) / 255  # 转换格式


myImshow(img, "Input Image")


def deambient(m):
    ambient = np.mean(m)
    m = np.clip(m - ambient, 0, 1)
    return m


img = deambient(img)
myImshow(img, "deambient")


# def dftProc(m):
#     flags = cv.DFT_COMPLEX_OUTPUT
#     dft = cv.dft(m, flags=flags)
#     # 将图像频谱中的零频率分量会被移到频域图像的中心位置
#     dft_shift = np.fft.fftshift(dft)
#     h, w, _ = dft_shift.shape
#     pointO = np.array([h, w]) // 2
#     X = np.arange(0, w).reshape(1, -1)
#     Y = np.arange(0, h).reshape(-1, 1)
#     dft_shift[((X - pointO[1]) / w) ** 2 + ((Y - pointO[0]) / h) ** 2 > (0.2) ** 2] = 0

#     # 得到灰度图能表示的形式
#     magnitude_spectrum = 20 * np.log1p(
#         cv.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
#     )

#     imgback = cv.idft(np.fft.fftshift(dft_shift), flags=flags)
#     imgback = cv.magnitude(imgback[:, :, 0], imgback[:, :, 1])
#     imgback /= h * w
#     return imgback, magnitude_spectrum


# img, magDft = dftProc(img)

# myImshow(magDft, "Magnitude Spectrum")
# myImshow(img, "imgback")


def ObjectFilterTrad(m: np.ndarray):
    backgroundrange = 41
    adptthresh = 0.1
    abslthresh = 0.1
    rhothresh = 0.1
    # adaptive thresh
    ave = regionave(m, [backgroundrange, backgroundrange])
    mAdat = (m - ave) / (ave + EPS)
    mAdat = (mAdat >= adptthresh).astype(np.uint8)

    # abs thresh
    mAbst = np.copy(m)
    mAbst = (mAbst >= abslthresh).astype(np.uint8)

    m = (mAdat * mAbst).astype(np.float32)

    # density thresh
    # rho = regionave(m, [backgroundrange, backgroundrange])
    # mRhoThreshed = (rho >= rhothresh).astype(np.uint8)

    # m = cv.medianBlur(m, 3)

    # m = (m * mRhoThreshed).astype(np.float32)
    return m


img = ObjectFilterTrad(img)


myImshow(img, "ObjectFilterTrad")

plt.show()
