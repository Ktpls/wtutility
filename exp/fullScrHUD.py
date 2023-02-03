
import sys
sys.path.append('.')
from utility import *

resolution=[1080,1920]
m2show=np.zeros(np.concatenate((resolution,[4])),np.uint8)
terminate=False
gblhwnd=0

def WndProc(hwnd,msg,wParam,lParam):
  if msg == win32con.WM_PAINT:
    rect = win32gui.GetClientRect(hwnd)
    hdc,ps = win32gui.BeginPaint(hwnd)
    #background
    hbr=win32gui.CreateSolidBrush(0x0000000)
    win32gui.FillRect(hdc,rect,hbr)
    
    w=resolution[1]
    h=resolution[0]
    mfcDC=win32ui.CreateDCFromHandle(hdc)
    hcdc=mfcDC.CreateCompatibleDC()
    BitMap = win32ui.CreateBitmap()
    BitMap.CreateCompatibleBitmap(mfcDC, w, h)
    ctypes.WinDLL('gdi32.dll').SetBitmapBits(BitMap.GetHandle(), w*h*4, m2show.tobytes())
    hcdc.SelectObject(BitMap)
    win32gui.BitBlt(hdc,0,0,w, h , hcdc.GetHandleAttrib(), 0,0, win32con.SRCCOPY)
    win32gui.DrawText(hdc,'GUI Python',len('GUI Python'),rect,win32con.DT_SINGLELINE|win32con.DT_CENTER|win32con.DT_VCENTER)

    hcdc.DeleteDC()
    win32gui.EndPaint(hwnd,ps)
  elif msg==win32con.WM_SIZE:
    win32gui.InvalidateRect(hwnd,None,True)
  elif msg == win32con.WM_DESTROY:
    win32gui.PostQuitMessage(0)
  global stopwindow
  if terminate:
    win32gui.PostQuitMessage(0)
  return win32gui.DefWindowProc(hwnd,msg,wParam,lParam)

def setupWindow():
  def mainloop():
    wc = win32gui.WNDCLASS()
    wc.hbrBackground = win32con.COLOR_WINDOW
    wc.hCursor = win32gui.LoadCursor(0,win32con.IDI_APPLICATION)
    wc.lpszClassName = "Python no Windows"
    wc.lpfnWndProc = WndProc
    reg = win32gui.RegisterClass(wc)

    hwnd = win32gui.CreateWindow(
        reg,
        'www.jb51.net - Python',
        win32con.WS_POPUP,
        #win32con.WS_OVERLAPPEDWINDOW,
        0,
        0,
        resolution[1],
        resolution[0],
        0,
        0,
        0,
        None)
    win32gui.ShowWindow(hwnd,win32con.SW_SHOWNORMAL)
    win32gui.UpdateWindow(hwnd)

    win32gui.SetWindowLong(hwnd,win32con.GWL_EXSTYLE,
      win32gui.GetWindowLong(hwnd,win32con.GWL_EXSTYLE)+win32con.WS_EX_LAYERED+win32con.WS_EX_NOACTIVATE)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 0, win32con.LWA_COLORKEY)
    win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_SHOWWINDOW+win32con.SWP_NOSIZE+win32con.SWP_NOMOVE)

    global gblhwnd
    gblhwnd=hwnd
    win32gui.PumpMessages()
  t1 = threading.Thread(target=mainloop, args=())
  t1.start()
  time.sleep(1)

def setwindowcontent(m):
  alp=255*np.ones_like(m[:,:,0:1])
  global m2show
  m2show=np.concatenate((m,alp),2)

def updateWindow():
  try:
    win32gui.InvalidateRect(gblhwnd,None,True)
  except:
    pass
  finally:
    pass

def stopWindow():
  global terminate
  terminate=True
  updateWindow()

m0=cv.imread(r"D:\output\pycammot\anypainting.png")
m0=np.zeros(np.concatenate((resolution,[3])),np.uint8)
setwindowcontent(m0)
setupWindow()
t=0
while(True):
  t+=0.1
  m=m0.copy()
  m=cv.line(m,(250,250),(int(500*(0.5+0.5*np.cos(t))),int(500*(0.5-0.5*np.sin(t)))),(255,255,255))
  setwindowcontent(m)
  updateWindow()
  time.sleep(0.2)
  if t>10:
    break
stopWindow()