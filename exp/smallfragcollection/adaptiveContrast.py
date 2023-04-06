
import sys
sys.path.append('.')
from utility import *
def modval(x):
    #return np.arctan(x)*15*2/np.pi
    return x*5
m=cv.imread(r"C:\Program Files\WarThunder\wtequ\Opdar\output\unnamed-5.png")
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
m=m.astype('float')
regave=regionave(m,[10,10])
m+=modval(m-regave)
savemat(m)