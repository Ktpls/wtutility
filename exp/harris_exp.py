
import sys
sys.path.append('.')
from utility import *

ss=screenshoter(0)
m=ss.shot()
m=m[:,:,:3]
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
m=np.array(m,np.float32)
savemat(m)
m=cv.normalize(m, m, 0, 256, cv.NORM_MINMAX);
savemat(m)

blockSize = 2
apertureSize = 3
k = 0.04
m=cv.cornerHarris(m, blockSize, apertureSize, k);
m=cv.normalize(m, m, 0, 256, cv.NORM_MINMAX);
savemat(m)

src_circled=m.copy()
# Drawing a circle around corners
for i in range(m.shape[1]):
    for j in range(m.shape[0]):
        if m[i][j]>200:
            cv.circle(src_circled, [i, j], 5,  255);
savemat(src_circled)