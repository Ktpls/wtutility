
import sys
sys.path.append('.')
from utility import *

#P is like [n,2]
def fit(P):
    ave=P.sum(0)/P.shape[0]
    ave=np.repeat(ave.reshape([1,2]),P.shape[0],axis=0)
    P=P-ave
    #X==P[:,0], Y==P[:,1]
    delta=(P[:,0]**2-P[:,1]**2).sum()
    gamma=(P[:,0]*P[:,1]).sum()
    base=np.sqrt(delta**2+4*gamma**2)
    cosphi=delta/base
    sinphi=2*gamma/base
    Apsi=np.sqrt((1-cosphi)/2)
    Bpsi=np.sqrt((cosphi+1)/2)
    Bpsi=Bpsi if sinphi>0 else -Bpsi
    return -Apsi,Bpsi,P


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

def genSample(A,B,start,end,num):
    Nsp=num
    T=np.linspace(start,end,Nsp)
    T=np.repeat(T.reshape([Nsp,1]),2,axis=1).reshape([Nsp,2])
    Coef=np.array([-B,A]).reshape([1,2])
    Coef=np.repeat(Coef,Nsp,axis=0).reshape([Nsp,2])
    Psp=Coef*T
    return Psp

def main():
    
    #accurate samples
    Paccu=genSample(1,0,-100,100,200)
    noise=0*(np.random.random(Paccu.shape)-0.5)
    #experiment samples
    P=Paccu+noise
    #calc
    Aest,Best,Pexp=fit_errmax(P)
    print(Aest,Best)
    #use estimation
    Pest=genSample(Aest,Best,-100,100,20)
    #show
    plt.plot(Pexp[:,0],Pexp[:,1],'.')
    plt.plot(Pest[:,0],Pest[:,1])
    plt.show()