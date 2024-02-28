import sys
import os

sys.path.append(".")
from os import system
from .autofreshmap_implementation import *
import traceback


def main():
    pool = ThreadPoolExecutor()

    afm = freshAMap(pool=pool)

    try:

        def stopAfm():
            afm.stop()

        hkm = HotkeyManager([HotkeyManager.hotkeytask(win32con.VK_F5, stopAfm)])

        fpsm = FpsManager(5)
        activeWindow(GetWtHwnd())
        mouse.mov(*(0, 0))
        afm.go()
        # main loop
        while True:
            fpsm.WaitUntilNextFrame()
            if not afm.isRunning():
                break
            hkm.doAllDecidedKey(hkm.decideAllHotKey(), printonerr=True)
        if waitafterdone:
            os.system("pause")
    except Exception as err:
        traceback.print_exc()
        Rhythms.Error.play()
        if throwerrinmain:
            raise err
        system("pause")

    # testOneRaw()
    # addCutNewMap('Normandy')
    # setonwifi()
    # outputMapSpawnPointCenter(r".\asset\autofreshmap\map\Poland.png")

    # system('pause')


def test():
    activeWindow(GetWtHwnd())
    sleep(1)
    press(win32con.VK_RETURN)
