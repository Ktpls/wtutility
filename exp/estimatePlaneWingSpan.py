
import sys
sys.path.append('.')
from utility import *
def fit_errmax(P):
    ave=P.sum(0)/P.shape[0]
    ave=np.repeat(ave.reshape([1,2]),P.shape[0],axis=0)
    Pcenterized=P-ave
    #X==P[:,0], Y==P[:,1]
    delta=(Pcenterized[:,0]**2-Pcenterized[:,1]**2).sum()
    gamma=(Pcenterized[:,0]*Pcenterized[:,1]).sum()
    base=np.sqrt(delta**2+4*gamma**2)
    cosphi=delta/base
    sinphi=2*gamma/base
    cosita=-cosphi
    sinita=-sinphi
    Apsi=np.sqrt((1-cosita)/2)
    Bpsi=np.sqrt((cosita+1)/2)
    Bpsi=Bpsi if sinita>0 else -Bpsi
    return -Apsi,Bpsi,Pcenterized

#binary mat
def mat2pointset(m):
    idx=np.array(np.where(m>0))
    X=idx[0].reshape([idx.shape[1],1])
    Y=idx[1].reshape([idx.shape[1],1])
    P=np.concatenate((X,Y),axis=1)
    return P


def estimateWingSpan(m):
    ps=mat2pointset(m)
    A,B,Pc=fit_errmax(ps)
    dist2=(A*Pc[:,0]+B*Pc[:,1])**2
    dist2max=dist2.max()
    return 2*np.sqrt(dist2max)
m=cv.imread(r"D:\output\pycammot\bf110.png")
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
wingspan=estimateWingSpan(m)
print(wingspan)