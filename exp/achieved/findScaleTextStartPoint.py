
import sys
sys.path.append('.')
from utility import *

inputs=[]
walkroot=r'C:\file\code\Opdar\output'
for root,dir,file in os.walk(walkroot):
    if root !=walkroot:
        pass
    for f in file:
        inputs.append(os.path.join(root,f))

for f in inputs:
    filename=os.path.basename(f)
    filename=filename[:str.rfind(filename,'.')]
    f=cv.imread(f)
    f=f[:,:,0]
    height=f.shape[0]
    statistic=np.average(f,axis=0)
    statistic=statistic.reshape((1,)+statistic.shape+(1,))
    statistic=np.repeat(statistic,height,axis=0)
    f=f.reshape(f.shape+(1,))
    o=np.concatenate([np.zeros_like(f),f,statistic],axis=2)
    savemat(o,name=filename,path='output/fstsp/',autorename=False)