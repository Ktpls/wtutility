
import sys
sys.path.append('.')
from utility import *

blockSize = 2
apertureSize = 3
k = 0.04

m=cv.imread(r"D:\output\pycammot\skymap.jpg")
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
m=np.array(m,np.float32)
savemat(m)

m=cv.normalize(m, m, 0, 256, cv.NORM_MINMAX);
mp=cv.cornerHarris(m, blockSize, apertureSize, k);
mp=cv.normalize(mp, mp, 0, 256, cv.NORM_MINMAX);
savemat(mp)

src_circled=m.copy()
# Drawing a circle around corners
for i in range(m.shape[0]):
    for j in range(m.shape[1]):
        if mp[i][j]>200:
            cv.circle(src_circled, [j,i], 4,  0);
            cv.circle(src_circled, [j,i], 5,  255);
            cv.circle(src_circled, [j,i], 6,  0);
savemat(src_circled)

exit()