import sys
import os

sys.path.append(".")
from os import system
from .autofreshmap_implementation import *
import traceback


@GSLogger.ExceptionLogged()
def main():
    pool = futures.ThreadPoolExecutor()

    afm = freshAMap()

    try:

        def stopAfm():
            afm.stop()

        hkm = HotkeyManager([HotkeyManager.hotkeytask(win32con.VK_F5, stopAfm)])

        fpsm = FpsManager(5)
        activeWindow(GetWtHwnd())
        mouse.mov(*(0, 0))
        f = pool.submit(freshAMap.run, afm)
        # main loop
        while f.running():
            fpsm.WaitUntilNextFrame()
            hkm.doAllDecidedKey(hkm.decideAllHotKey(), printonerr=True)
        if waitafterdone:
            os.system("pause")
    except Exception as err:
        traceback.print_exc()
        Rhythms.Error.play()
        if throwerrinmain:
            raise err
        system("pause")
