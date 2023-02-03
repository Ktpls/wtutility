
import sys
sys.path.append('.')
from antiairfirecontrol import *


#be as many as t this many white points around someone white, will be still qualified as single point
def singlepoint_detect(m,t):
    detector=np.array([
        [-1,-1,-1],
        [-1, t,-1],
        [-1,-1,-1],
    ])
    singles=cv.filter2D(m,-1,detector)
    #>0, not >=
    singles=cv.threshold(singles,0,1,cv.THRESH_BINARY)[1]
    return singles

X=np.linspace(-2,2,500)
Y=X.copy()
X,Y=np.meshgrid(X,Y)
m=np.exp(-X**2-Y**2)+0.1*np.random.rand(500,500)
savematflt(m)
m=cv.threshold(m,0.5,1,cv.THRESH_BINARY)[1]
savematflt(m)
while(True):

    singles=singlepoint_detect(m,2)
    savematflt(singles)
    m=m*(1-singles)
    savematflt(m)
    if singles.sum()<10:
        break
