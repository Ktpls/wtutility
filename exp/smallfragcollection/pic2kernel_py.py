
import sys
sys.path.append('.')
from utility import *
def pic2kernel(p:np.ndarray):
    maque=p.copy()
    
    maque[maque[:,:,0]!=maque[:,:,1]][0]=0
    return maque

def mataccess():
    m=np.array([
        [[1,1],[1,1]],
        [[1,1],[1,0]]
    ])
    maque=np.zeros(m.shape[:2])
    maque[m[:,:,1]!=m[:,:,0]]=22
    print(maque)

mataccess()