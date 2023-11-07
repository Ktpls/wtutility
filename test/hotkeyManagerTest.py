from utilref import *
import time


def foo():
    print("calling foo")


hotkeyaction = [HotkeyManager.hotkeytask(key=[win32con.VK_F1], foo=foo)]
hkm = HotkeyManager(hotkeyaction)
while True:
    decideresult = hkm.decideAllHotKey()
    hkm.doAllDecidedKey(decideresult, True, False)
    time.sleep(0.1)
