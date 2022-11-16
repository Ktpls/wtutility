from copy import deepcopy
import os
import ctypes
import time
from time import sleep
import threading
from typing import Dict,List,Callable

import cv2 as cv
import numpy as np
np.seterr(all='raise')
import win32gui
import win32ui
import win32con
import win32api
def deduplicate(l:List):
    ret=[]
    for i in l:
        if i not in ret:
            ret.append(i)
    return ret

class logger:
    def __init__(self,path):
        self.path=path
        #wont fail
        dir=os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.f=open(path,'wb+')
    
    def log(self,content):
        self.f.write((content+'\n').encode('utf8'))
        self.f.flush()
    
    def __del__(self):
        self.f.close()

    def __call__(self, content):
        self.log(content)

def setoffwifi():
    os.system('netsh interface set interface name="WLAN" admin=disable')

def setonwifi():
    os.system('netsh interface set interface name="WLAN" admin=enable')

#pass in __file__
def setadmin(file):
    import sys
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    if not is_admin():
        quotedpy='"'+file+'"'
        if sys.version_info[0] == 3:
            ret=ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, quotedpy, None, 1)
        else:#in python2.x
            ret=ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(quotedpy), None, 1)
        exit()

DEFAULT_OUTPUT_ROOT=r'./output/'
def savemat(m,name=None,path=None):
    if path is None:
        path=DEFAULT_OUTPUT_ROOT
    if not os.path.exists(path):
        os.makedirs(path)
    if name is None:
        name='unnamed'
    totalpath=os.path.join(path,name+'.png')
    #find suitable name
    if os.path.exists(totalpath):
        suffix_idx=0
        while(True):
            suffix_idx+=1
            newname='{}-{}'.format(name,suffix_idx)
            totalpath=os.path.join(path,newname+'.png')
            if not os.path.exists(totalpath):
                break
    
    cv.imwrite(totalpath,m)

def savematn(m:np.ndarray,name=None,path=None):
    mtmp=m.copy()
    cv.normalize(mtmp,mtmp,0,255,cv.NORM_MINMAX)
    savemat(mtmp,name,path)

def savematflt(m,multiplier=255,name=None,path=None):
    savemat(multiplier*m,name,path)

def forceviewmaxmin(m):
    ma=m.max()
    mi=m.min()
    print('ma',ma)
    print('mi',mi)
    pass

def regionsum(m,size,mask=None):
    if m.size<=0:
        return m
    if mask is not None:
        mask[mask!=0]=1
    return cv.filter2D(
        m if mask is None else m*mask,
        -1,
        np.ones(size,np.float32)
        )

def regionave(m,size,mask=None):
    if m.size<=0:
        return m
    #0.01 for mask is fully black
    #why use ones_like(m) as mask rather than regionsum(m,size)/(size[0]*size[1])?
    #cuz the latter would be too big an area at the edge of pic, there is just no this many pixels
    mask=np.ones_like(m) if mask is None else mask
    return regionsum(m,size,mask)/(regionsum(mask,size)+0.01)

def density(p,size):
    return regionave(p.astype('float'),size)

def densityfilter(p,size,thresh):
    dence=density(p,size)
    dence[dence<thresh]=0
    return np.logical_and(p, dence)

def getWTHwnd():
    ret= win32gui.FindWindow('DagorWClass',None)
    if ret==win32con.NULL:
        raise Exception('FindWindow() failed')
    return ret



#reconstructed with no mfc
from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
class screenshoter:
    def __init__(self,hwnd):
        self.hwnd=hwnd
        # r = RECT()
        # windll.user32.GetClientRect(self.hwnd, byref(r))
        # self.res=[r.right,r.bottom]
        self.res=[1920,1080]
        self.dc = windll.user32.GetDC(self.hwnd)
        self.cdc = windll.gdi32.CreateCompatibleDC(self.dc)
        self.bitmap = windll.gdi32.CreateCompatibleBitmap(self.dc, self.res[0], self.res[1])
        windll.gdi32.SelectObject(self.cdc, self.bitmap)

    def __del__(self):
        windll.gdi32.DeleteObject(self.bitmap)
        windll.gdi32.DeleteObject(self.cdc)
        windll.user32.ReleaseDC(self.hwnd, self.dc)

    def shot(self):
        windll.gdi32.BitBlt(self.cdc, 0, 0, self.res[0], self.res[1], self.dc, 0, 0, win32con.SRCCOPY)
        # 截图是BGRA排列，因此总元素个数需要乘以4
        total_bytes = self.res[0]*self.res[1]*4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte*total_bytes
        windll.gdi32.GetBitmapBits(self.bitmap, total_bytes, byte_array.from_buffer(buffer))
        return np.frombuffer(buffer, dtype=np.uint8).reshape(self.res[1], self.res[0], 4)

    def shotbgr(self):
        return self.shot()[:,:,:3]

    def shotgray(self):
        return cv.cvtColor(self.shot(),cv.COLOR_BGRA2GRAY)



# class screenshoter:
#   def __init__(self,hwnd):
#       self.res=[1920,1080]
#       self.hwnd=hwnd
#       self.hwndDC = win32gui.GetWindowDC(self.hwnd)
#       if self.hwndDC==win32con.NULL:
#           raise Exception('GetWindowDC() failed')
#       self.mfcDC=win32ui.CreateDCFromHandle(self.hwndDC)
#       self.saveDC=self.mfcDC.CreateCompatibleDC()
#       self.saveBitMap = win32ui.CreateBitmap()
#       self.saveBitMap.CreateCompatibleBitmap(self.mfcDC, self.res[0], self.res[1])
#       self.saveDC.SelectObject(self.saveBitMap)

#   def __del__(self):
#       win32gui.DeleteObject(self.saveBitMap.GetHandle())
#       self.saveDC.DeleteDC()
#       self.mfcDC=None
#       win32gui.ReleaseDC(self.hwnd,self.hwndDC)

#   def shot(self):
#       self.saveDC.BitBlt((0,0),(self.res[0], self.res[1]) , self.mfcDC, (0,0), win32con.SRCCOPY)
#       m=self.saveBitMap.GetBitmapBits(self.res[0]* self.res[1] * 4);
#       m=np.frombuffer(m,np.uint8)
#       m=m.reshape([self.res[1], self.res[0],4])
#       return m

#   def shotgray(self):
#       return cv.cvtColor(self.shot(),cv.COLOR_BGRA2GRAY)


def activeWindow(hwnd):  # 窗口置顶
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
    win32gui.SetForegroundWindow(hwnd)


def sleepuntil(con,dt=0.01):
    while(not con()):
        time.sleep(dt)


class fullScrHUD:
    def __init__(self) -> None:
        self.resolution=[1080,1920]
        self.m2show=np.zeros(np.concatenate((self.resolution,[4])),np.uint8)
        self.terminate=False
        self.hwnd=0

    def setup(self):
        
        def WndProc(hwnd,msg,wParam,lParam):
            if msg == win32con.WM_PAINT:
                rect = win32gui.GetClientRect(hwnd)
                hdc,ps = win32gui.BeginPaint(hwnd)
                #background
                # hbr=win32gui.CreateSolidBrush(0x0000000)
                # win32gui.FillRect(hdc,rect,hbr)
                # win32gui.DeleteObject(hbr)
                
                w=self.resolution[1]
                h=self.resolution[0]
                mfcDC=win32ui.CreateDCFromHandle(hdc)
                hcdc=mfcDC.CreateCompatibleDC()
                BitMap = win32ui.CreateBitmap()
                BitMap.CreateCompatibleBitmap(mfcDC, w, h)
                ctypes.WinDLL('gdi32.dll').SetBitmapBits(BitMap.GetHandle(), w*h*4, self.m2show.tobytes())
                hcdc.SelectObject(BitMap)
                win32gui.BitBlt(hdc,0,0,w, h , hcdc.GetHandleAttrib(), 0,0, win32con.SRCCOPY)
                #win32gui.DrawText(hdc,'GUI Python',len('GUI Python'),rect,win32con.DT_SINGLELINE|win32con.DT_CENTER|win32con.DT_VCENTER)
                win32gui.DeleteObject(BitMap.GetHandle())
                hcdc.DeleteDC()
                win32gui.EndPaint(hwnd,ps)
            elif msg==win32con.WM_SIZE:
                win32gui.InvalidateRect(hwnd,None,True)
            elif msg == win32con.WM_DESTROY:
                win32gui.PostQuitMessage(0)
            if self.terminate:
                win32gui.PostQuitMessage(0)
            return win32gui.DefWindowProc(hwnd,msg,wParam,lParam)

        def mainloop():
            wc = win32gui.WNDCLASS()
            hbrush=win32gui.CreateSolidBrush(0)
            wc.hbrBackground = hbrush
            wc.lpszClassName = "Python on Windows"
            wc.lpfnWndProc = WndProc
            reg = win32gui.RegisterClass(wc)

            hwnd = win32gui.CreateWindow(
                reg,
                'Python',
                win32con.WS_POPUP,
                0,
                0,
                self.resolution[1],
                self.resolution[0],
                0,
                0,
                0,
                None)
            win32gui.ShowWindow(hwnd,win32con.SW_SHOWNORMAL)
            win32gui.UpdateWindow(hwnd)

            win32gui.SetWindowLong(
                hwnd,
                win32con.GWL_EXSTYLE,
                win32gui.GetWindowLong(
                    hwnd,
                    win32con.GWL_EXSTYLE)+
                    win32con.WS_EX_LAYERED+
                    win32con.WS_EX_NOACTIVATE)
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 0, win32con.LWA_COLORKEY)
            win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_SHOWWINDOW+win32con.SWP_NOSIZE+win32con.SWP_NOMOVE)

            self.hwnd=hwnd
            win32gui.PumpMessages()
        t1 = threading.Thread(target=mainloop, args=())
        t1.start()
        time.sleep(1)

    def setcontent(self,m):
        alp=255*np.ones_like(m[:,:,0:1])
        self.m2show=np.concatenate((m,alp),2)

    def update(self):
        win32gui.InvalidateRect(self.hwnd,None,False) #needless to clear cuz entire screen will be set

    def stop(self):
        self.terminate=True
        self.update()
    
    @staticmethod
    def reverseMat2FitWindowsCoor(m):
        return np.flip(m,axis=0)
    
    def setcontentwithalfa(self,m):
        self.m2show=m

def isKBDown(k):
    return win32api.GetAsyncKeyState(k) and 0x1

class perf_statistic:
    def __init__(self):
        self.starttime=0
        self.totaltime=0
        self.cycle=0

    def start(self):
        self.starttime=time.perf_counter()
    
    def stop(self):
        self.totaltime+=time.perf_counter()-self.starttime
        self.cycle+=1
    
    def read_ave_t(self):
        return self.totaltime/self.cycle if self.cycle>0 else 0

def convolve_norm(m,k):
    summer=np.ones_like(k)
    mag=np.sqrt(cv.filter2D(m**2,-1,summer))
    ret=cv.filter2D(m,-1,k)
    return ret/mag

class fpsmanager:
    def __init__(self,fps=60):
        self.lt=time.perf_counter()
        self.frametime=1/fps
    
    def next(self):
        sleepuntil(lambda :time.perf_counter()-self.lt>self.frametime, dt=0.5*self.frametime)
        self.lt=time.perf_counter()

class hotkeymanager:
    def __init__(self, keyconcerned):
        self.kc=deepcopy(keyconcerned)

    def getkeys(self):
        return {k:isKBDown(k) for k in self.kc}

rgb2hsvmat=np.array([
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
hsv2rgbmat=[np.linalg.inv(m) for m in rgb2hsvmat]
def hsv2rgb(hsv):
    h,s,v=hsv
    h=h*np.pi/180
    xyv=np.array([s*np.cos(h),s*np.sin(h),v])

    #find the corresponding case
    for c,m in enumerate(hsv2rgbmat):
        rgb=m@xyv
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
    xyv=rgb2hsvmat[np.argmax(rgb)]@rgb
    x,y,v=xyv
    hsv=np.array([180/np.pi*np.arctan2(y,x),np.sqrt(x**2+y**2),v])
    return hsv

def rgb2bgr(rgb):
    m=np.array([
        [0,0,1],
        [0,1,0],
        [1,0,0]
    ])
    return m@rgb

def arrayshift(a,n):
    if n >= 0:
        return np.concatenate((np.full(n, np.nan), a[:-n]))
    else:
        return np.concatenate((a[-n:], np.full(-n, np.nan)))
    
def hsv2opencv8bithsv(hsv):
    return np.array([0.5,2.55,2.55])*np.array(hsv)

def digitsof(s:str):
    return ''.join(list(filter(str.isdigit,list(s))))

#wont consider negative
def numinstr(s:str):
    s=digitsof(s)
    return int(s) if len(s)>0 else 0