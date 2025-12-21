import sys
import os
from utilitypack.util_windows import *
from utilitypack.util_winkey import *
from utilitypack.util_wt import *

sys.path.append(".")
from os import system
from . import autofreshmap_implementation as afmimpl
import traceback
import logging
from shared.globalsys import *

logger = logging.getLogger(__name__)


@ExceptionLogged(logger=logger)
def main():
    pool = UTS_DEFAULT_THREAD_POOL

    afm = afmimpl.freshAMap()

    try:

        def stopAfm():
            afm.mq.put(MessagedThread.Message(afmimpl.freshAMap.MessageType.stop))

        def acceptMap():
            afm.mq.put(MessagedThread.Message(afmimpl.freshAMap.MessageType.acceptMap))

        hkm = HotkeyManager(
            [
                HotkeyManager.hotkeytask(win32con.VK_F5, stopAfm),
                HotkeyManager.hotkeytask([ord("A"), win32con.VK_F5], acceptMap),
            ]
        )

        fpsm = FpsManager(5)
        activeWindow(GetWtHwnd())
        mouse.mov(*(0, 0))
        f = pool.submit(afmimpl.freshAMap.run, afm)
        # main loop
        while not f.done():
            fpsm.WaitUntilNextFrame()
            hkm.dispatchMessage()
        if afmimpl.waitafterdone:
            os.system("pause")
    except Exception as err:
        traceback.print_exc()
        Rhythms.Error.play()
        if afmimpl.throwerrinmain:
            raise err
        system("pause")
