import sys
import os
from utilitypack.util_windows import *
from utilitypack.util_wt import *
sys.path.append(".")
from os import system
from .autofreshmap_implementation import *
import traceback


@GSBLogger.ExceptionLogged()
def main():
    pool = UTS_DEFAULT_THREAD_POOL

    afm = freshAMap()

    try:

        def stopAfm():
            afm.mq.put(MessagedThread.Message(freshAMap.MessageType.stop))

        def acceptMap():
            afm.mq.put(MessagedThread.Message(freshAMap.MessageType.acceptMap))

        hkm = HotkeyManager(
            [
                HotkeyManager.hotkeytask(win32con.VK_F5, stopAfm),
                HotkeyManager.hotkeytask([ord("A"), win32con.VK_F5], acceptMap),
            ]
        )

        fpsm = FpsManager(5)
        activeWindow(GetWtHwnd())
        mouse.mov(*(0, 0))
        f = pool.submit(freshAMap.run, afm)
        # main loop
        while not f.done():
            fpsm.WaitUntilNextFrame()
            hkm.dispatchMessage()
        if waitafterdone:
            os.system("pause")
    except Exception as err:
        traceback.print_exc()
        Rhythms.Error.play()
        if throwerrinmain:
            raise err
        system("pause")
