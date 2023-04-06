
import sys
sys.path.append('.')
from utility import *

timelen=10
samplenum=2000
T=np.linspace(0,timelen,samplenum)
DT=deltaX(T)

noisescale=0.5
I=T+(2*noisescale*np.random.random(T.shape)-noisescale)

E=np.zeros_like(T)
Etor=Estimator(0.99,I[:3],T[:3])
Ae=np.zeros_like(T)

E[3]=Etor.estimate(DT[3])
for i in range(3,len(E)-1):
    Etor.update(I[i],DT[i])
    E[i+1]=Etor.estimate(DT[i+1])
    Ae[i+1]=Etor.a.val()


Err=I-E
V=deltaX(I)/DT
dt=DT[-1]
myE=0.5*Ae[-2]*dt**2+V[-2]*dt+I[-2]
myErr=I[-1]-myE

Vtherotical=T
VErr=Vtherotical-V

plt.plot(T,E)
plt.plot(T,I)
plt.legend(range(4))
#error comes from regarding averange velocity between now and last sample as velocity now

plt.show()

