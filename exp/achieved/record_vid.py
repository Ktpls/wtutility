
import sys
from time import sleep
sys.path.append('.')
from utility import *

def sleepuntil(con,dt=0.01):
    while(not con()):
        sleep(dt)
def getHwnd():
    ret= win32gui.FindWindow('DagorWClass',None)
    if ret==win32con.NULL:
        raise Exception('FindWindow() failed')
    return ret

path=r".\output\wtshot.avi"

screensize=np.array([1920,1080],np.int32)
fps = 5
vidlen=10
fourcc = cv.VideoWriter_fourcc(*'XVID')
out_gray = cv.VideoWriter(path, fourcc, fps, screensize)
hwnd=getHwnd()
#hwnd=0
print(hwnd)
ss=screenshoter(hwnd)
win32api.Beep(1000,1000)
t0=time.perf_counter()

lastT=time.perf_counter()
for t in range(vidlen*fps):
    frame = ss.shotbgr()
    if t==0:
        savemat(frame,'1stFrame')
    #frame_gray=cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    out_gray.write(frame)
    sleepuntil(lambda :time.perf_counter()-lastT>1.0/fps)
    lastT=time.perf_counter()

t1=time.perf_counter()
print(t1-t0)
out_gray.release()
win32api.Beep(1000,1000)