
import sys
sys.path.append('.')
from utility import *


m=cv.imread(r"C:\Program Files\WarThunder\wtequ\Opdar\autofreshmapasset\rawmaterial\AbandonedFactory.png")
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
m=m.astype('float')/255
rnd=np.random.random_sample(m.shape)
out=np.zeros_like(m)
out[m>rnd]=1
savematflt(out)