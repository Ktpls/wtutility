from macroutility import *

for k in [
    win32con.VK_NUMPAD0,
    win32con.VK_NUMPAD1,
    win32con.VK_NUMPAD2,
    win32con.VK_NUMPAD4,
    win32con.VK_NUMPAD5,
]:
    Keyboard.KeyPress(k)
    PreciseSleep(0.25)