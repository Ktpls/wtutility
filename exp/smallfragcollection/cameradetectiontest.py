
import sys
sys.path.append('.')
from utility import *

m=[
    cv.imread(r"D:\output\pycammot\shot 2022.07.09 20.50.11.jpg"),
    cv.imread(r"D:\output\pycammot\shot 2022.07.09 20.50.12.jpg")
]
#answer is 231,32
for i in range(len(m)):
    m[i]=cv.cvtColor(m[i],cv.COLOR_BGR2GRAY)
    m[i]=np.array(m[i],np.float32)/256

cd=cameradetector(m[0])
result=cd.detect(m[1],True)
print(result.x)