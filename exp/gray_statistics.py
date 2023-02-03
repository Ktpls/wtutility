
import sys
sys.path.append('.')
from utility import *

m=cv.imread(r"D:\output\pycammot\skymap.jpg")
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
m=np.array(m,np.float32)
savemat(m)
hist=cv.calcHist(m,[0],None,[256],[0,255])


def statistics(m,samplenum=100):
    mi=m.min()
    ma=m.max()
    dx=samplenum/(ma-mi)
    X=np.linspace(mi,ma,samplenum+1)
    s=np.zeros(samplenum+1,np.float32)
    for x in range(m.shape[1]):
        for y in range(m.shape[0]):
            s[np.floor((m[y][x]-mi)*dx)]+=1
    return X,s

# X,s=statistics(m)
# s=np.log(s+1)

plt.plot(hist)
plt.show()
