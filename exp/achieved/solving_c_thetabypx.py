
import sys

from matplotlib import markers
sys.path.append('.')
from utility import *
from pointsfitting import *

file=[
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor0.png",
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor1.png",
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor2.png",
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor3.png",
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor4.png",
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor5.png",
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor6.png",
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor7.png",
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor8.png",
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor9.png",
    r"D:\output\pycammot\notusing\flash_shots\focused\flawless_wt_screen_savor10.png"
]

dist=np.array([
    0.82,
    0.68,
    0.56,
    0.46,
    0.40,
    0.40,
    0.44,
    0.54,
    0.64,
    0.77,
    0.91
])

wingspans=np.zeros_like(dist)

for s in range(len(file)):
    m=cv.imread(file[s])
    m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
    center=(np.array([m.shape[1],m.shape[0]])*0.5).astype('int32')
    _,wingspans[s]=planetracker(m,center,100)

C=0.0226/dist/wingspans*1000
Cave=C.sum()/len(C)
print(Cave)
plt.plot(wingspans,C,'.')
Pest=genSample(0,-1,0,100,10)
plt.plot(Pest[:,0],Cave+Pest[:,1])
plt.show()