# %%
from utilref import *
import matplotlib.pyplot as plt

# %%


def affineTransformation(m):

    def zoom(rate):
        return np.array(
            [
                [rate, 0, 0],
                [0, rate, 0],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

    def shift(x, y):
        return np.array(
            [
                [1, 0, x],
                [0, 1, y],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

    def flip(lr, ud):
        return np.array(
            [
                [lr, 0, 0],
                [0, ud, 0],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

    def rot(the):
        return np.array(
            [
                [np.cos(the), np.sin(the), 0],
                [-np.sin(the), np.cos(the), 0],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

    def identity():
        return np.array(
            [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

    t = 30 * np.pi / 180
    r = 1
    x, y = 0, 0
    lr, ud = 1, -1
    h, w, c = m.shape
    mataffine = (
        identity()
        @ shift(0.5 * w, 0.5 * h)
        # @ flip(lr, ud)
        # @ shift(x, y)
        # @ zoom(r)
        # @ rot(t)
        @ shift(-0.5 * w, -0.5 * h)
    )[0:2, :]
    m = cv.warpAffine(
        m, mataffine, np.flip(m.shape[0:2]), borderMode=cv.BORDER_REPLICATE
    )
    return m


m = (
    cv.imread(
        r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\spl\0-1.png"
    ).astype(np.float32)
    / 255
)
plt.imshow(m)
m = affineTransformation(m)
plt.imshow(m)
