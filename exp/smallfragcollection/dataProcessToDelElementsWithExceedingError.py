from utilref import *
from utilitypack.util_pyplot import *

a = np.concatenate([np.random.normal(0, 1, (100)), np.random.normal(5, 1, (10))])
valid = np.full_like(a, True, dtype=np.bool_)


def showA():
    b = a[valid]
    mpp.toNextPlot()
    plt.hist(b, bins=20)


pltshape = [10, 10]
mpp = MassivePicturePlot(pltshape)
for i in range(np.prod(pltshape)):
    avg = np.mean(a, where=valid, axis=0, keepdims=True)
    std = np.std(a, where=valid, axis=0, keepdims=True)
    validNew = np.abs(a - avg) < 2 * std
    if (valid == validNew).all():
        break
    valid = validNew
    showA()
    avg = np.squeeze(avg)
    std = np.squeeze(std)
    plt.title(f"{i=}{avg=:.1f}{std=:.1f}")
plt.show()
