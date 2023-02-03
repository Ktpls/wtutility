
import sys
sys.path.append('.')
from utility import *

a=np.array([1,2,3,4,5])
b=(a>3)*a
print(b)