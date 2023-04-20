from utilref import *
from scipy import interpolate


def toDistribution(m, znum=100):
    #m should be single channeled and in float
    mz = np.zeros(m.shape[0:2] + (znum, ), m.dtype)
    m = m.reshape(m.shape + (1, ))
    index = (m * znum).astype(np.int32)
    #just barely beyond upper bound of 99.9999, but this case do exists
    index[index == znum] -= 1
    np.put_along_axis(mz, index, m, 2)
    dy = mz.sum((0, 1))
    dy /= dy.sum() + 0.00001
    y = integral(dy, 0, True)
    x = np.linspace(0, 1, znum + 1)
    dx = derivative(x)
    return x, y, dx, dy


def preprocess(m):
    m = m.astype(np.float32) / 255
    return m


def ViewRGBDistribution():
    m = r"C:\Users\KITA\Pictures\pic\389c50a3c2399feaadc9f6e8d945b091397287828.jpg"
    m = cv.imread(m)
    m = preprocess(m)
    xys = [toDistribution(m[:, :, d], 255) for d in range(3)]
    forma = ['b', 'g', 'r']
    [plt.plot(x, y, forma[d]) for d, (x, y) in enumerate(xys)]
    plt.show()


def viewEffect(m, fig, shape, idx):
    imshowconfig = {'cmap': 'gray', 'vmin': 0, 'vmax': 1}
    m = cv.imread(m)
    m = preprocess(m)
    m = m[:, :, 0]
    x, y, dx, dy = toDistribution(m)
    fig.add_subplot(*shape, idx + 1).plot(x, y)
    fig.add_subplot(*shape, idx + 2).imshow(m, **imshowconfig)
    foo = interpolate.interp1d(x, y, assume_sorted=True)
    mp = foo(m)
    x, y, dx, dy = toDistribution(mp)
    fig.add_subplot(*shape, idx + 3).plot(x, y)
    fig.add_subplot(*shape, idx + 4).imshow(mp, **imshowconfig)


fig = plt.figure()
m = [
    r"C:\Users\KITA\Pictures\pic\31cb2f8611e1dd5f74ca56a3290e09f0397287828.jpg",
    r"C:\Users\KITA\Pictures\pic\389c50a3c2399feaadc9f6e8d945b091397287828.jpg",
    r"C:\Users\KITA\Pictures\pic\98034ab21a4106e1030a21903f9b9d12397287828.jpg",
    r"C:\Users\KITA\Pictures\pic\113242441324135.png",
    r"C:\Users\KITA\Pictures\pic\v2-a5a37d599ecb6e0142a74f8d5c1baefc_r.jpg",
    r"C:\Users\KITA\Pictures\pic\QQ20220930164723.jpg",
    r"C:\Users\KITA\Pictures\pic\v2-4a3f0a6aa1c9d483d088f05316e6c9cb_r.jpg",
    r"C:\Users\KITA\Pictures\pic\v2-4e1bb4e7018b6e54629bc9a0643987a8.jpeg",
    r"C:\Users\KITA\Pictures\pic\v2-4f00d697b2d447128f674f35bf1dbacd_r.jpg",
    r"C:\Users\KITA\Pictures\pic\v2-7adadce144fde6390033f0e90d710daf_r.jpg",
]
[viewEffect(p, fig, (5, 8), i * 4) for i, p in enumerate(m)]
plt.show()
