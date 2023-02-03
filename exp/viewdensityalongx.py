from utilref import *
import sys
m=cv.imread(sys.argv[1])
m=m[:,:,0].astype(np.float32)/255
rou=np.average(m,axis=0)
plt.plot(rou,label='$\\rho$')
windowsize=10
conv=np.correlate(rou,np.ones(windowsize,np.float32)/windowsize,'same')
plt.plot(conv,label='conv')
plt.legend()
plt.show()
