
import sys
sys.path.append('.')
from utility import *

timelen=10
samplenum=100
T=np.linspace(0,timelen,samplenum)
DT=deltaX(T)
I=[np.cos(T),np.sin(T)]

E=[np.zeros_like(T),np.zeros_like(T)]
Et=[Estimator(I[0][:3],T[:3]),Estimator(I[1][:3],T[:3])]

for ti in range(3,len(T)-1):
    for c in range(2):
        Et[c].update(I[c][ti],DT[ti])
    for c in range(2):
        E[c][ti+1]=Et[c].estimate(DT[ti+1])

plt.plot(E[0],E[1])
plt.plot(I[0],I[1])
plt.legend(range(4))
#error comes from regarding averange velocity between now and last sample as velocity now

plt.show()

