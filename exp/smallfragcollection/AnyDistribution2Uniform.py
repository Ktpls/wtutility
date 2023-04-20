from utilref import *

x = np.linspace(0, 1, 100)
dx = derivative(x)
dy = np.sin(x * 10) + 1
dy[-1] = np.nan
dy /= dy[:-1].sum()  #norm
y = integral(dy, 0)
gamma = dy / dx
dz = dx * gamma
z = integral(dz, 0)

plt.plot(x, y)
plt.plot(z, y)
plt.show()