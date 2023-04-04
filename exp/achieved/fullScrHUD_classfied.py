
import sys
sys.path.append('.')
from utility import *

class fullScrHUD:
    def __init__(self) -> None:
        self.resolution=[1080,1920]
        self.m2show=np.zeros(np.concatenate((self.resolution,[4])),np.uint8)
        self.terminate=False
        self.gblhwnd=0

    def setup(self):
        
        def WndProc(hwnd,msg,wParam,lParam):
            if msg == win32con.WM_PAINT:
                rect = win32gui.GetClientRect(hwnd)
                hdc,ps = win32gui.BeginPaint(hwnd)
                #background
                hbr=win32gui.CreateSolidBrush(0x0000000)
                #win32gui.FillRect(hdc,rect,hbr)
                
                w=self.resolution[1]
                h=self.resolution[0]
                mfcDC=win32ui.CreateDCFromHandle(hdc)
                hcdc=mfcDC.CreateCompatibleDC()
                BitMap = win32ui.CreateBitmap()
                BitMap.CreateCompatibleBitmap(mfcDC, w, h)
                ctypes.WinDLL('gdi32.dll').SetBitmapBits(BitMap.GetHandle(), w*h*4, hud.m2show.tobytes())
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
            if hud.terminate:
                win32gui.PostQuitMessage(0)
            return win32gui.DefWindowProc(hwnd,msg,wParam,lParam)

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
                self.resolution[1],
                self.resolution[0],
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

            self.gblhwnd=hwnd
            win32gui.PumpMessages()
        t1 = threading.Thread(target=mainloop, args=())
        t1.start()
        time.sleep(1)

    def setcontent(self,m):
        alp=255*np.ones_like(m[:,:,0:1])
        self.m2show=np.concatenate((m,alp),2)

    def updateWindow(self):
        try:
            #win32gui.InvalidateRect(self.gblhwnd,None,True)
            win32gui.InvalidateRect(self.gblhwnd,None,False)
        except:
            pass
        finally:
            pass

    def stop(self):
        self.terminate=True
        self.updateWindow()

m0=cv.imread(r"D:\output\pycammot\anypainting.png")
m0=np.zeros([1080,1920,3],np.uint8)
hud=fullScrHUD()
hud.setcontent(m0)
hud.setup()
t=0
while(True):
    t+=0.1
    m=m0.copy()
    m=cv.line(m,(960,540),(int(1920*(0.5+0.5*np.cos(t))),int(1080*(0.5-0.5*np.sin(t)))),(255,255,255))
    hud.setcontent(m)
    hud.updateWindow()
    time.sleep(0.2)
    if t>10:
        break
hud.stop()