import openpyxl as opx
import traceback
import itertools
import sys
from ctypes.wintypes import RECT, HWND
from ctypes import windll, byref, c_ubyte
import win32api
import win32con
import win32ui
import win32gui
from copy import deepcopy
import os
import ctypes
import time
from time import sleep
import random
import threading
from typing import Dict, List, Callable

import cv2 as cv
import numpy as np

np.seterr(all='raise')


def deduplicate(l: List):
    yield from dict.fromkeys(l)


class logger:

    def __init__(self, path):
        self.path = path
        # wont fail
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.f = open(path, 'wb+')

    def log(self, content):
        self.f.write((content + '\n').encode('utf8'))
        self.f.flush()

    def __del__(self):
        self.f.close()

    def __call__(self, content):
        self.log(content)


def savemat(m, name=None, path=None, suffix='.png', autorename=True):
    if name is None:
        name = 'unnamed'
    if path is None:
        path = r'./output/'

    if not os.path.exists(path):
        os.makedirs(path)
    totalpath = os.path.join(path, name + suffix)
    # find suitable name
    if autorename and os.path.exists(totalpath) :
        suffix_idx = 0
        while (True):
            suffix_idx += 1
            newname = '{}-{}'.format(name, suffix_idx)
            totalpath = os.path.join(path, newname + suffix)
            if not os.path.exists(totalpath):
                break

    if not cv.imwrite(totalpath, m):
        raise IOError(f'Bad write {totalpath}')


def savematn(m: np.ndarray, name=None, path=None):
    mtmp = m.copy()
    cv.normalize(mtmp, mtmp, 0, 255, cv.NORM_MINMAX)
    savemat(mtmp, name, path)


def savematflt(m, multiplier=255, name=None, path=None):
    savemat(multiplier * m, name, path)


def forceviewmaxmin(m):
    ma = m.max()
    mi = m.min()
    print('ma', ma)
    print('mi', mi)
    pass


def regionsum(m, size, mask=None):
    if m.size <= 0:
        return m
    if mask is not None:
        mask[mask > 0] = 1
    if len(m.shape) > 2 and mask is not None:  # with channel dim
        mask = mask.reshape(mask.shape+(1,))
    return cv.filter2D(m if mask is None else m * mask, -1,
                       np.ones(size, np.float32))


# if notConsiderMaskInDenominator:
# denominator will not consider mask and boundary and be size[0]*size[1]
# else:
# denominator will be #pix nearby on mask
# u may ask mask==None does the same as notConsiderMaskInDenominator==True
# but if u want to use mask and dont want to be constrained by boundary. unimplemented though
def regionave(m,
              size,
              mask=None,
              notConsiderMaskInDenominator=True):
    if m.size <= 0:
        return m
    if mask is not None:
        mask = np.copy(mask)
        mask[mask > 0] = 1
    if mask is None or notConsiderMaskInDenominator:
        denominator = size[0] * size[1]
    else:
        denominator = (regionsum(mask, size) + 0.01)
        if len(m.shape) > 2:  # m with channel dim
            denominator = denominator.reshape(denominator.shape+(1,))
    return regionsum(m, size, mask) / denominator


def density(p, size):
    return regionave(p.astype('float'), size)


def densityfilter(p, size, thresh):
    dence = density(p, size)
    dence[dence < thresh] = 0
    return np.logical_and(p, dence)


def getWTHwnd():
    ret = win32gui.FindWindow('DagorWClass', None)
    if ret == win32con.NULL:
        raise Exception('FindWindow() failed')
    return ret


# reconstructed with no mfc


class screenshoter:

    def __init__(self, hwnd=0):
        self.wthwnd = hwnd
        # r = RECT()
        # windll.user32.GetClientRect(self.hwnd, byref(r))
        # self.res=[r.right,r.bottom]
        self.res = [1920, 1080]
        self.wtdc = windll.user32.GetDC(self.wthwnd)
        self.mydc = windll.gdi32.CreateCompatibleDC(self.wtdc)
        self.mybitmap = windll.gdi32.CreateCompatibleBitmap(
            self.wtdc, self.res[0], self.res[1])
        windll.gdi32.SelectObject(self.mydc, self.mybitmap)

    def __del__(self):
        windll.gdi32.DeleteObject(self.mybitmap)
        windll.gdi32.DeleteObject(self.mydc)
        windll.user32.ReleaseDC(self.wthwnd, self.wtdc)

    def shot(self):
        if windll.gdi32.BitBlt(self.mydc, 0, 0, self.res[0], self.res[1],
                               self.wtdc, 0, 0, win32con.SRCCOPY) == 0:
            raise BaseException('bad shot, {}'.format(
                windll.kernel32.GetLastError()))
        # 截图是BGRA排列，因此总元素个数需要乘以4
        total_bytes = self.res[0] * self.res[1] * 4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte * total_bytes
        windll.gdi32.GetBitmapBits(self.mybitmap, total_bytes,
                                   byte_array.from_buffer(buffer))
        return np.frombuffer(buffer,
                             dtype=np.uint8).reshape(self.res[1], self.res[0],
                                                     4)

    def shotbgr(self):
        return self.shot()[:, :, :3]

    def shotgray(self):
        return cv.cvtColor(self.shot(), cv.COLOR_BGRA2GRAY)


def activeWindow(hwnd):  # 窗口置顶
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                          win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
    win32gui.SetForegroundWindow(hwnd)


def sleepuntil(con: Callable, dt=0.01):
    while (not con()):
        time.sleep(dt)


'''
#init
hud=fullScrHUD()
hud.setup()
...
#main loop
#preparing to show
hud.clear
#init m1
m1=hud.getblankscreen()
#draw sth on m1
#then add m1 to hud
hud.addcontent(m1)
#or overwrite directly
hud.writecontent(m1)
#do the same for m2...
...
#ask hud to show
hud.update()
...
#on exit
hud.stop()
'''


class fullScrHUD:

    def __init__(self) -> None:
        self.resolution = [1080, 1920]
        self.terminate = False
        self.hwnd = 0
        self.m2show = self.getblankscreenwithalfa()
        self.m2draw = self.getblankscreenwithalfa()
        # set m2draw

    def setup(self):

        def WndProc(hwnd, msg, wParam, lParam):
            if msg == win32con.WM_PAINT:
                rect = win32gui.GetClientRect(hwnd)
                hdc, ps = win32gui.BeginPaint(hwnd)
                # background
                # hbr=win32gui.CreateSolidBrush(0x0000000)
                # win32gui.FillRect(hdc,rect,hbr)
                # win32gui.DeleteObject(hbr)

                w = self.resolution[1]
                h = self.resolution[0]
                mfcDC = win32ui.CreateDCFromHandle(hdc)
                hcdc = mfcDC.CreateCompatibleDC()
                BitMap = win32ui.CreateBitmap()
                BitMap.CreateCompatibleBitmap(mfcDC, w, h)
                ctypes.WinDLL('gdi32.dll').SetBitmapBits(
                    BitMap.GetHandle(), w * h * 4, self.m2show.tobytes())
                hcdc.SelectObject(BitMap)
                # myblendfunc=(win32con.AC_SRC_OVER,0,255,win32con.AC_SRC_ALPHA)
                # win32gui.AlphaBlend(hdc,0,0,w, h , hcdc.GetHandleAttrib(), 0,0,w, h,myblendfunc)
                win32gui.BitBlt(hdc, 0, 0, w, h, hcdc.GetHandleAttrib(), 0, 0,
                                win32con.SRCCOPY)
                win32gui.DeleteObject(BitMap.GetHandle())
                hcdc.DeleteDC()
                win32gui.EndPaint(hwnd, ps)
            elif msg == win32con.WM_SIZE:
                win32gui.InvalidateRect(hwnd, None, True)
            elif msg == win32con.WM_DESTROY:
                win32gui.PostQuitMessage(0)
            if self.terminate:
                win32gui.PostQuitMessage(0)
            return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

        def mainloop():
            wc = win32gui.WNDCLASS()
            hbrush = win32gui.CreateSolidBrush(0)
            wc.hbrBackground = hbrush
            wc.lpszClassName = "Python on Windows"
            wc.lpfnWndProc = WndProc
            reg = win32gui.RegisterClass(wc)

            hwnd = win32gui.CreateWindow(reg, 'Python', win32con.WS_POPUP, 0,
                                         0, self.resolution[1],
                                         self.resolution[0], 0, 0, 0, None)
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
            win32gui.UpdateWindow(hwnd)

            win32gui.SetWindowLong(
                hwnd, win32con.GWL_EXSTYLE,
                win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) +
                win32con.WS_EX_LAYERED + win32con.WS_EX_NOACTIVATE)
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 0,
                                                win32con.LWA_COLORKEY)
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                win32con.SWP_SHOWWINDOW + win32con.SWP_NOSIZE +
                win32con.SWP_NOMOVE)
            windll.user32.SetWindowDisplayAffinity(
                hwnd, 0x11)  # WDA_EXCLUDEDFROMCAPUTURE
            # can not use WDA_MONITOR, or get totally black screen

            self.hwnd = hwnd
            win32gui.PumpMessages()

        t1 = threading.Thread(target=mainloop, args=())
        t1.start()
        time.sleep(1)

    def writecontent(self, lt, content):
        self.m2draw[lt[0]:lt[0] + content.shape[0], lt[1]:lt[1] +
                    content.shape[1], :content.shape[2]] = content

    def clear(self):
        self.m2draw[:, :, :] = 0

    def getblankscreen(self):
        return np.zeros(self.resolution + [
            3,
        ], np.uint8)

    def getblankscreenwithalfa(self):
        return np.zeros(self.resolution + [
            4,
        ], np.uint8)

    def addcontentwithalfa(self, m):
        self.m2draw += m

    def addcontent(self, m):
        alp = 255 * np.ones_like(m[:, :, 0:1])
        self.m2draw += np.concatenate((m, alp), 2)

    def update(self):
        # swap
        tmp = self.m2show
        self.m2show = self.m2draw
        self.m2draw = tmp

        # needless to clear cuz entire screen will be set
        win32gui.InvalidateRect(self.hwnd, None, False)

    def stop(self):
        self.terminate = True
        self.update()

    @staticmethod
    def reverseMat2FitWindowsCoor(m):
        return np.flip(m, axis=0)


def isKBDown(k):
    return win32api.GetAsyncKeyState(k) and 0x1


class perf_statistic:

    def __init__(self, startnow=False):
        self.clear()
        if startnow:
            self.start()

    def clear(self):
        self._starttime = None
        self._stagedtime = 0
        self._cycle = 0

    def start(self):
        self._starttime = time.perf_counter()

    def countcycle(self):
        self._cycle += 1

    def stop(self):
        if self._starttime is None:
            return
        self._stagedtime += self._timeCurrentlyCounting()
        self._starttime = None

    def aveTime(self):
        return self._timeCurrentlyCounting() / self._cycle if self._cycle > 0 else 0

    def _timeCurrentlyCounting(self):
        return time.perf_counter() - self._starttime

    def time(self):
        return self._stagedtime+self._timeCurrentlyCounting()


def convolve_norm(m, k):
    summer = np.ones_like(k)
    mag = np.sqrt(cv.filter2D(m**2, -1, summer))
    ret = cv.filter2D(m, -1, k)
    return ret / mag


class fpsmanager:

    def __init__(self, fps=60):
        self.lt = time.perf_counter()
        self.frametime = 1 / fps

    def BlockUntilNextFrame(self):
        sleepuntil(lambda: time.perf_counter() - self.lt > self.frametime,
                   dt=0.5 * self.frametime)
        self.lt = time.perf_counter()

    '''
    usage
    use it with mutiple fpsmanagers
    if time is apropriate, ret true and update time
    if fpsmanager.CheckIfTimeToDoNextFrame():
        do your task here
    '''

    def CheckIfTimeToDoNextFrame(self) -> bool:
        result = time.perf_counter() - self.lt > self.frametime
        if result:
            self.lt = time.perf_counter()
        return result


class hotkeymanager:
    # to piorer ctrl+c than c
    # responde no c after doing ctrl+c

    class hotkeytask:

        def __init__(self, key, foo) -> None:
            self.key = [key] if type(key) is int else key
            self.foo = foo

    def __init__(self, hotkeytasklist: List[hotkeytask]):
        keyconcerned = [hka.key for hka in hotkeytasklist]
        keyconcerned = list(itertools.chain.from_iterable(keyconcerned))
        keyconcerned = list(deduplicate(keyconcerned))
        self.kc = keyconcerned

        self.hktl = deepcopy(hotkeytasklist)

        def piorered(a: hotkeymanager.hotkeytask, b: hotkeymanager.hotkeytask):
            def include(a: hotkeymanager.hotkeytask, b: hotkeymanager.hotkeytask):
                for k in b.key:
                    if k not in a.key:
                        return False
                return True
            # a>b and b<a, not equal
            return include(a, b) and not include(b, a)
        self.piorinfo = [
            [aidx
             for aidx, a in enumerate(hotkeytasklist)
             if aidx != bidx and piorered(a, b)
             ]
            for bidx, b in enumerate(hotkeytasklist)
        ]

    def decideAllHotKey(self) -> List[bool]:
        keysts = {k: isKBDown(k) for k in self.kc}
        from enum import Enum

        class respondstate(Enum):
            false = 0
            true = 1
            unknown = 2
        respondtable = [respondstate.unknown for hk in self.hktl]

        def decideRespondState(i):
            # checked
            if respondtable[i] != respondstate.unknown:
                return

            # all key pressed
            if all([keysts[k] for k in self.hktl[i].key]):

                # didnt check piored, check it
                [decideRespondState(p) for p in self.piorinfo[i]
                 if respondtable[p] == respondstate.unknown]

                # no piored responded
                if all([respondtable[p] == respondstate.false for p in self.piorinfo[i]]):
                    respondtable[i] = respondstate.true
                else:
                    respondtable[i] = respondstate.false
            else:
                # not respond this
                respondtable[i] = respondstate.false
        for hkidx, hk in enumerate(self.hktl):
            decideRespondState(hkidx)

        assert (all([rt != respondstate.unknown for rt in respondtable]))

        return [respondtable[hkidx] == respondstate.true for hkidx, hk in enumerate(self.hktl)]

    def doAllDecidedKey(self, decideresult, throwonerr=False):
        for i in range(len(decideresult)):
            if decideresult[i]:
                try:
                    self.hktl[i].foo()
                except Exception as e:
                    if throwonerr:
                        raise e
                    else:
                        traceback.print_exc()


rgb2hsvmat = np.array([
    [[np.cos(0), np.cos(2 / 3 * np.pi),
      np.cos(4 / 3 * np.pi)],
     [np.sin(0), np.sin(2 / 3 * np.pi),
      np.sin(4 / 3 * np.pi)], [1, 0, 0]],
    [[np.cos(0), np.cos(2 / 3 * np.pi),
      np.cos(4 / 3 * np.pi)],
     [np.sin(0), np.sin(2 / 3 * np.pi),
      np.sin(4 / 3 * np.pi)], [0, 1, 0]],
    [[np.cos(0), np.cos(2 / 3 * np.pi),
      np.cos(4 / 3 * np.pi)],
     [np.sin(0), np.sin(2 / 3 * np.pi),
      np.sin(4 / 3 * np.pi)], [0, 0, 1]],
])
hsv2rgbmat = [np.linalg.inv(m) for m in rgb2hsvmat]


def hsv2rgb(hsv):
    h, s, v = hsv
    h = h * np.pi / 180
    xyv = np.array([s * np.cos(h), s * np.sin(h), v])

    # find the corresponding case
    for c, m in enumerate(hsv2rgbmat):
        rgb = m @ xyv
        if np.argmax(rgb) == c:
            return rgb

    #not possible, theoretically
    return np.array((0, 0, 0))

    # to view all solutions
    # rgbs=np.zeros([3,3])
    # for c,m in enumerate(mats):
    #     rgbs[c]=np.linalg.inv(m)@xyv
    # return rgbs


def rgb2hsv(rgb):
    xyv = rgb2hsvmat[np.argmax(rgb)] @ rgb
    x, y, v = xyv
    hsv = np.array([180 / np.pi * np.arctan2(y, x), np.sqrt(x**2 + y**2), v])
    return hsv


def rgb2bgr(rgb):
    m = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]])
    return m @ rgb


# positive as right
def arrayshift(a, n, fill=np.nan):
    if n == 0:
        return a
    elif n > 0:
        # a[:-n] will not work as intended on n==0
        return np.concatenate((np.full(n, fill), a[:-n]))
    else:
        return np.concatenate((a[-n:], np.full(-n, fill)))


def hsv2opencv8bithsv(hsv):
    return np.array([0.5, 2.55, 2.55]) * np.array(hsv)


def digitsof(s: str):
    return ''.join(list(filter(str.isdigit, list(s))))


# wont consider negative


def numinstr(s: str):
    s = digitsof(s)
    return int(s) if len(s) > 0 else 0

# summon from card pool

# impl using np


def summonCard(inteprob, generator=None):
    # norm
    prob = np.array(inteprob, dtype=np.float32)
    prob /= prob.sum()
    if generator is None:
        return np.random.choice(np.arange(len(prob)), p=prob)
    else:
        return generator.choice(np.arange(len(prob)), p=prob)


# faster summon using division


def quickSummonCard(inteprob):
    pos = random.random() * inteprob[-1]
    section = [0, len(inteprob)]

    def compare(n):
        # compare pos with section[n]
        if pos > inteprob[n]:
            return 1
        else:  # pos<=section[n]
            if pos > (inteprob[n - 1] if n >= 1 else 0):
                return 0
            else:
                return -1

    while (True):
        mid = int((section[1] + section[0]) * 0.5)
        compresult = compare(mid)
        if compresult == 1:
            section[0] = mid + 1
        elif compresult == -1:
            section[1] = mid
        else:  # compresult==0
            return mid


class toast:
    messagelist = []

    def sendmessage(self, content, peroid):
        self.messagelist.append({
            'ctt': content,
            'st': time.perf_counter(),
            'per': peroid
        })

    def updatemsglist(self):
        nowtime = time.perf_counter()

        def filterfoo(m):
            return m['per'] > m['ctt'] - nowtime

        messagelist = [m for m in messagelist if filterfoo(m)]
        msgs = [m['ctt'] for m in messagelist]

    def getallmsg(self):
        self.updatemsglist()
        return '\n'.join(self.messagelist)


# new msg covers the lasts


class bulletinBoard:

    def __init__(self, idlecontent):
        self.idlecontent = idlecontent
        self.content = ''
        self.overduetime = time.perf_counter()

    def putup(self, content, timeout):
        self.content = content
        self.overduetime = time.perf_counter() + timeout

    def read(self):
        if time.perf_counter() < self.overduetime:
            return self.content
        else:
            return self.idlecontent


def outputlines2mat(m, pos, content, lineheight=25, textcolor=[255, 255, 255]):
    m = m.copy()
    line = content.split('\n')
    for i, l in enumerate(line):
        cv.putText(m, l,
                   pos.astype('int32') + [0, i * lineheight],
                   cv.FONT_HERSHEY_SIMPLEX, 1, textcolor)
    return m


# different impl., ret with content bounding box


def outputlines2mat2(m,
                     pos,
                     content,
                     textcolor=[255, 255, 255],
                     lineinterval=10):
    pos = np.array(pos).astype('int')
    line = content.split('\n')
    yoffset = 0
    xmax = 0
    fontFace = cv.FONT_HERSHEY_DUPLEX
    fontScale = 1
    thickness = 1
    for i, l in enumerate(line):
        size = np.array(cv.getTextSize(l, fontFace, fontScale, thickness)[0])
        yoffset += size[1] + lineinterval if i != 0 else size[1]
        if xmax < size[0]:
            xmax = size[0]
        m = cv.putText(m,
                       l,
                       pos + [0, yoffset],
                       fontFace,
                       fontScale,
                       textcolor,
                       thickness=thickness)
    box = [pos, pos + [xmax, yoffset]]
    return m, box


def aPicWithText(content,
                 maxsize=[1080, 1920],
                 textcolor=[255, 255, 255],
                 lineinterval=10):
    m = np.zeros(maxsize + [
        3,
    ], np.uint8)
    m, bbox = outputlines2mat2(m, np.array([0, 0]), content, textcolor,
                               lineinterval)
    mshape = np.array(bbox[1]) + [0, 8]  # ret wrong for unknown reason
    m = m[:mshape[1], :mshape[0]]
    m = addShadow2HUD(m)
    return m


def addShadow2HUD(m, thickness=2, color=50):
    gray = cv.cvtColor(m, cv.COLOR_BGR2GRAY)
    kernelshape = 2 * thickness + 1
    edgekernel = np.ones([kernelshape, kernelshape])
    edgekernel[thickness, thickness] = -100  # anchor pix must be black
    # edgekernel=np.array([
    #     [1,1,1],
    #     [1,-80,1],
    #     [1,1,1],
    # ])
    edge = cv.filter2D(gray, -1, edgekernel)
    edge = cv.threshold(edge, 0, 1, cv.THRESH_BINARY)[1]
    edge = edge.reshape(edge.shape + (1, ))
    return m + edge * color


# pass in __file__
def bootAsAdmin(file):
    quotedpy = '"' + file + '"'
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable,
                                              quotedpy, None, 1)


def setadmin(file):

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        bootAsAdmin(file)
        exit()


def zfunc(xl, yl, xr, yr):
    slope = (yr - yl) / (xr - xl)

    def foo_single(x):
        if x < xl:
            return yl
        elif x > xr:
            return yr
        else:
            return (x - xl) * slope + yl

    def foo_ndarray(x):
        x = np.copy(x)
        x[x < xl] = yl
        x[x > xr] = yr
        x = (x - xl) * slope + yl
        return x

    def foo_universal(x):
        if type(x) is np.ndarray:
            return foo_ndarray(x)
        else:
            return foo_single(x)

    return foo_universal


class DataCollector:
    randNameLen = 10

    def __init__(self, outputpath) -> None:
        self.outputpath = outputpath

    @staticmethod
    def geneName():
        charset = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        idx = np.random.choice(range(len(charset)),
                               DataCollector.randNameLen, replace=True)
        return ''.join([charset[i] for i in idx])

    def save(self, m):
        savemat(m, f'{DataCollector.geneName()}', path=self.outputpath)


def Xls2ListList(path):
    return [[ele.value for ele in row] for row in (opx.load_workbook(path).active.rows)]
