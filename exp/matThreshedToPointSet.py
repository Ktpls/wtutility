
import sys
sys.path.append('.')
from utility import *
A=np.linspace(0,10,5)
B=0.5*A
idx = np.where(A>5)
idx=idx[0]
C=B[idx]
pass