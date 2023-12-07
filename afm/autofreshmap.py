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
            for t in [500, 1000, 1500]:
                win32api.Beep(t, 100)

        hkm = HotkeyManager([HotkeyManager.hotkeytask(win32con.VK_F5, stopAfm)])

        fpsm = fpsmanager(1)
        activeWindow(getWTHwnd())
        mouse.mov(*(0, 0))
        afm.go()
        # main loop
        while True:
            fpsm.WaitUntilNextFrame()
            if not afm.getRunning():
                break
            hkm.doAllDecidedKey(hkm.decideAllHotKey(), printonerr=True)
        if waitafterdone:
            os.system("pause")
    except Exception as err:
        traceback.print_exc()
        RythmError.play()
        if throwerrinmain:
            raise err
        system("pause")

    # testOneRaw()
    # addCutNewMap('Normandy')
    # setonwifi()
    # outputMapSpawnPointCenter(r".\asset\autofreshmap\map\Poland.png")

    # system('pause')


def test():
    activeWindow(getWTHwnd())
    sleep(1)
    press(keycode.key_Enter)
