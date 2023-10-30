import win32api
import win32con
import time

while True:
    print(win32api.GetAsyncKeyState(ord("1")) & 0x8000)
    time.sleep(0.5)
