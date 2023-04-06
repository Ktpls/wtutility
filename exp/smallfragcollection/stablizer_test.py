
import sys
sys.path.append('.')
from utility import *

timelen=20
samplenum=100
T=np.linspace(0,timelen,samplenum+1)
noisescale=0.5
I=(2*noisescale*np.random.random(T.shape)-noisescale)
DT=deltaX(T)
DI=deltaX(I)
s=stablizer(0.99,I[0])
E=np.zeros_like(T)
for i in range(2,len(E)):
    E[i]=s.sample(I[i-1],DT[i-1])
plt.plot(T,I)
plt.plot(T,E)
plt.legend(['X','E'])
plt.show()