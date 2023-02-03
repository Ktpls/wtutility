
import sys
sys.path.append('.')
from utilref import *

def window_capture():
    resolution=[1920,1080]
    hwnd = 0
    #hwnd=win32gui.FindWindow('DagorWClass','War Thunder')
    hwnd=getWTHwnd()
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC=win32ui.CreateDCFromHandle(hwndDC)
    saveDC=mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    w = resolution[0]
    h = resolution[1]
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0,0),(w, h) , mfcDC, (0,0), win32con.SRCCOPY)
    m=saveBitMap.GetBitmapBits(w * h * 4);
    m=np.frombuffer(m,np.uint8)
    m=m.reshape([h,w,4])
    return m


def window_capture_nomfc():
    resolution=[1920,1080]
    #hwnd=win32gui.FindWindow('DagorWClass','War Thunder')
    #hwnd=getWTHwnd()
    hwnd = 0
    #wtdc = windll.user32.GetDC(hwnd)
    wtdc=win32gui.GetWindowDC(hwnd)
    mydc = windll.gdi32.CreateCompatibleDC(wtdc)
    mybitmap = windll.gdi32.CreateCompatibleBitmap(
        wtdc, resolution[0], resolution[1])
    windll.gdi32.SelectObject(mydc, mybitmap)
    #if windll.gdi32.BitBlt(mydc, 0, 0, resolution[0], resolution[1], wtdc, 0, 0, win32con.SRCCOPY) == 0:
    if win32gui.BitBlt(mydc,0,0,resolution[0], resolution[1],wtdc,0,0,win32con.SRCCOPY)==0:
        raise BaseException('bad shot, {}'.format(
            windll.kernel32.GetLastError()))
    total_bytes = resolution[0]*resolution[1]*4
    buffer = bytearray(total_bytes)
    byte_array = c_ubyte*total_bytes
    windll.gdi32.GetBitmapBits(
        mybitmap, total_bytes, byte_array.from_buffer(buffer))
    windll.gdi32.DeleteObject(mybitmap)
    windll.gdi32.DeleteObject(mydc)
    windll.user32.ReleaseDC(hwnd, wtdc)
    return np.frombuffer(buffer, dtype=np.uint8).reshape(resolution[1], resolution[0], 4)


def window_capture_nodump():
    resolution=[1920,1080]
    hwnd=getWTHwnd()
    #hwnd=0
    hdc = windll.user32.GetDC(hwnd)
    hbitmap=windll.gdi32.GetCurrentObject(hdc, win32con.OBJ_BITMAP)
    # shift=500
    # win32gui.BitBlt(hdc,shift,shift,resolution[0]-shift, resolution[1]-shift,hdc,shift,shift,win32con.SRCCOPY)
    win32gui.BitBlt(hdc,0,0,resolution[0], resolution[1],hdc,0,0,win32con.SRCCOPY)
    total_bytes = resolution[0]*resolution[1]*4
    buffer = bytearray(total_bytes)
    byte_array = c_ubyte*total_bytes
    windll.gdi32.GetBitmapBits(
        hbitmap, total_bytes, byte_array.from_buffer(buffer))
    windll.user32.ReleaseDC(hwnd, hdc)
    return np.frombuffer(buffer, dtype=np.uint8).reshape(resolution[1], resolution[0], 4)


def window_capture_printwindow():
    resolution=[1920,1080]
    #hwnd=getWTHwnd()
    #hwnd = 0
    #hwnd=win32gui.GetDesktopWindow()
    hwnd=0x0007069E
    wtdc = windll.user32.GetDC(hwnd)
    mydc = windll.gdi32.CreateCompatibleDC(wtdc)
    mybitmap = windll.gdi32.CreateCompatibleBitmap(
        wtdc, resolution[0], resolution[1])
    windll.gdi32.SelectObject(mydc, mybitmap)
    ret=windll.user32.PrintWindow(hwnd,mydc, 1)
    print(ret)
    print(win32api.GetLastError())
    total_bytes = resolution[0]*resolution[1]*4
    buffer = bytearray(total_bytes)
    byte_array = c_ubyte*total_bytes
    windll.gdi32.GetBitmapBits(
        mybitmap, total_bytes, byte_array.from_buffer(buffer))
    windll.gdi32.DeleteObject(mybitmap)
    windll.gdi32.DeleteObject(mydc)
    windll.user32.ReleaseDC(hwnd, wtdc)
    return np.frombuffer(buffer, dtype=np.uint8).reshape(resolution[1], resolution[0], 4)

def window_capture_mfcprintwindow():
    resolution=[1920,1080]
    #hwnd = 0
    #hwnd=win32gui.FindWindow('DagorWClass','War Thunder')
    #hwnd=getWTHwnd()
    hwnd=0x0001044A
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC=win32ui.CreateDCFromHandle(hwndDC)
    saveDC=mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    w = resolution[0]
    h = resolution[1]
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    #saveDC.BitBlt((0,0),(w, h) , mfcDC, (0,0), win32con.SRCCOPY)
    ret=windll.user32.PrintWindow(hwnd,saveDC.GetSafeHdc(), 0)
    print(ret)
    print(win32api.GetLastError())
    m=saveBitMap.GetBitmapBits(w * h * 4);
    m=np.frombuffer(m,np.uint8)
    m=m.reshape([h,w,4])
    return m

m=window_capture_nodump()
savemat(m)
