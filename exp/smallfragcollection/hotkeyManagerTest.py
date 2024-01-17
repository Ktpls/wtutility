import time

ta = time.perf_counter()
from utilref import *

tb = time.perf_counter()
print(f"loading util costs {tb-ta}")


def promptCalling(name):
    def f2():
        print(f"calling {name}")

    return f2


hotkeyaction = [
    HotkeyManager.hotkeytask(
        key=[[win32con.VK_CONTROL, ord("A")], [win32con.VK_CONTROL, ord("A")]],
        foo=promptCalling("AA"),
    ),
    HotkeyManager.hotkeytask(
        key=[[win32con.VK_CONTROL, ord("A")], [win32con.VK_CONTROL, ord("S")]],
        foo=promptCalling("AS"),
    ),
]
hkm = HotkeyManager(hotkeyaction)
print("loaded")
while True:
    decideresult = hkm.decideAllHotKey()
    hkm.doAllDecidedKey(decideresult, True, False)
    time.sleep(0.1)
