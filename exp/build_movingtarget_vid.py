
import sys
sys.path.append('.')
from utility import *

class render:
    def __init__(self,screensize,fps):
        self.screensize=screensize
        self.Opos=0.5*np.array(screensize,np.float32)
        self.fps=fps
        self.ti=0
        self.ss=screenshoter(0)
    
    def read(self):
        m=np.ones(self.screensize,np.float32)
        # screenshot=self.ss.shot()
        # gray_frame = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
        # m=gray_frame[0:self.screensize[0],0:self.screensize[1]]
        t=self.ti/self.fps
        coor=0.25*np.array([
            np.sin(t),
            np.sin(2*t)])
        Mupsidown=np.array([
            [1,0],
            [0,1]
        ])
        coor=Mupsidown@coor
        coorTran=np.array(self.screensize*(0.5+0.5*coor),np.int32)
        m=cv.circle(m,coorTran,10,0,-1)
        #m=cv.GaussianBlur(m,[11,11],0)
        return m
    
    def next(self):
        self.ti+=1

path=r'D:\output\f.avi'
screensize=np.array([1000,1000],np.int32)
fps = 10
vidlen=10
fourcc = cv.VideoWriter_fourcc(*'XVID')
out_gray = cv.VideoWriter(path, fourcc, fps, screensize, False)
rd=render(screensize,fps)
size2show=(screensize*0.5).astype('int')

for t in range(vidlen*fps):
    frame = rd.read()
    rd.next()
    out_gray.write((255*frame).astype('uint8'))

    rszd=cv.resize(frame,size2show)
    cv.imshow('gray', rszd)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break
    print(t)
out_gray.release()
win32api.Beep(1000,1000)