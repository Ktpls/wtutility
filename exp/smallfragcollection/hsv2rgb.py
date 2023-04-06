
import sys
sys.path.append('.')
from utility import *

def hsv2rgb2(hsv):
    mats=np.array([
        [
            [np.cos(0),np.cos(2/3*np.pi),np.cos(4/3*np.pi)],
            [np.sin(0),np.sin(2/3*np.pi),np.sin(4/3*np.pi)],
            [1,0,0]
        ],
        [
            [np.cos(0),np.cos(2/3*np.pi),np.cos(4/3*np.pi)],
            [np.sin(0),np.sin(2/3*np.pi),np.sin(4/3*np.pi)],
            [0,1,0]
        ],
        [
            [np.cos(0),np.cos(2/3*np.pi),np.cos(4/3*np.pi)],
            [np.sin(0),np.sin(2/3*np.pi),np.sin(4/3*np.pi)],
            [0,0,1]
        ],
    ])
    h,s,v=hsv
    h=h*np.pi/180
    xyv=np.array([s*np.cos(h),s*np.sin(h),v])

    #find the corresponding case
    for c,m in enumerate(mats):
        rgb=np.linalg.inv(m)@xyv
        if np.argmax(rgb) == c:
            return rgb
    
    #not possible, theoretically
    return np.array((0,0,0))

    #to view all solutions
    # rgbs=np.zeros([3,3])
    # for c,m in enumerate(mats):
    #     rgbs[c]=np.linalg.inv(m)@xyv
    # return rgbs

def rgb2hsv(rgb):
    mats=np.array([
        [
            [np.cos(0),np.cos(2/3*np.pi),np.cos(4/3*np.pi)],
            [np.sin(0),np.sin(2/3*np.pi),np.sin(4/3*np.pi)],
            [1,0,0]
        ],
        [
            [np.cos(0),np.cos(2/3*np.pi),np.cos(4/3*np.pi)],
            [np.sin(0),np.sin(2/3*np.pi),np.sin(4/3*np.pi)],
            [0,1,0]
        ],
        [
            [np.cos(0),np.cos(2/3*np.pi),np.cos(4/3*np.pi)],
            [np.sin(0),np.sin(2/3*np.pi),np.sin(4/3*np.pi)],
            [0,0,1]
        ],
    ])
    xyv=mats[np.argmax(rgb)]@rgb
    x,y,v=xyv
    hsv=np.array([180/np.pi*np.arctan2(y,x),np.sqrt(x**2+y**2),v])
    return hsv

print(hsv2rgb2([240,1,1]))
#print(rgb2hsv([1,0,0]))
