import win32gui
import win32con
def WndProc(hwnd,msg,wParam,lParam):
  if msg == win32con.WM_PAINT:
    hdc,ps = win32gui.BeginPaint(hwnd)
    rect = win32gui.GetClientRect(hwnd)
    win32gui.DrawText(hdc,'GUI Python',len('GUI Python'),rect,win32con.DT_SINGLELINE|win32con.DT_CENTER|win32con.DT_VCENTER)
    win32gui.EndPaint(hwnd,ps)
  elif msg==win32con.WM_SIZE:
    #win32gui.UpdateWindow(hwnd)
    r=win32gui.InvalidateRect(hwnd,None,True)
  elif msg == win32con.WM_DESTROY:
    win32gui.PostQuitMessage(0)
  return win32gui.DefWindowProc(hwnd,msg,wParam,lParam)
wc = win32gui.WNDCLASS()
wc.hbrBackground = win32con.COLOR_BTNFACE + 1
wc.hCursor = win32gui.LoadCursor(0,win32con.IDI_APPLICATION)
wc.lpszClassName = "Python no Windows"
wc.lpfnWndProc = WndProc
reg = win32gui.RegisterClass(wc)
hwnd = win32gui.CreateWindow(reg,'www.jb51.net - Python',win32con.WS_OVERLAPPEDWINDOW,win32con.CW_USEDEFAULT,win32con.CW_USEDEFAULT,win32con.CW_USEDEFAULT,win32con.CW_USEDEFAULT,0,0,0,None)
win32gui.ShowWindow(hwnd,win32con.SW_SHOWNORMAL)
win32gui.UpdateWindow(hwnd)
win32gui.PumpMessages()

# while(True):
#   msg=win32gui.GetMessage(hwnd,0,0)
#   if msg==None:
#     break
#   msg=win32gui.TranslateMessage(msg)
#   win32gui.DispatchMessage(msg)