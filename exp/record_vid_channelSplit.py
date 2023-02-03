
import sys
from time import sleep
sys.path.append('.')
from utility import *

def sleepuntil(con,dt=0.01):
    while(not con()):
        sleep(dt)

path=r"D:\output\pycammot\wtplane{}.avi"

screensize=np.array([1920,1080],np.int32)
fps = 5
vidlen=10
fourcc = cv.VideoWriter_fourcc(*'XVID')
out_gray = [
    cv.VideoWriter(path.format(0), fourcc, fps, screensize, False),
    cv.VideoWriter(path.format(1), fourcc, fps, screensize, False),
    cv.VideoWriter(path.format(2), fourcc, fps, screensize, False),
    cv.VideoWriter(path.format('g'), fourcc, fps, screensize, False)
    ]
wthwnd=getWTHwnd()
print(wthwnd)
ss=screenshoter(getWTHwnd())
win32api.Beep(1000,1000)
t0=time.perf_counter()

lastT=time.perf_counter()
for t in range(vidlen*fps):
    frame = ss.shot()
    if t==0:
        savemat(frame,'1stFrame')

    for v in range(3):
        frame_channel=frame[:,:,v]
        out_gray[v].write(frame_channel)
    frame_gray=cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    out_gray[3].write(frame_gray)

    sleepuntil(lambda :time.perf_counter()-lastT>1.0/fps)
    lastT=time.perf_counter()

t1=time.perf_counter()
print(t1-t0)
for v in range(4):
    out_gray[v].release()
win32api.Beep(1000,1000)