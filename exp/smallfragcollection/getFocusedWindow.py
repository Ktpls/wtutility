import win32gui
import time
from utilref import *
def get_window_with_focus():
    fore = win32gui.GetForegroundWindow()
    window_text = win32gui.GetWindowText(fore)
    print(f"{win32gui.GetWindowText(fore)=}, \t{win32gui.GetWindowText(GetWtHwnd())}")

while True:
    get_window_with_focus()
    time.sleep(1)