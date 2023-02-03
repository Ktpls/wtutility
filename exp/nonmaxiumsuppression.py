
from utilref import *

[os.remove(f) for f in AllFileIn('./output')]
m=cv.imread(r"C:\file\code\wtutility\asset\autofreshmap\map\Japan.png")
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
savemat(m)
m=m.astype(np.float32)/255
for i in range(5):
    regave=regionave(m,[9,9])
    m=m-regave
    m[m<0]=0
    savematflt(m)