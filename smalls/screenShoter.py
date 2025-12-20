from utilitypack.util_solid import *
from utilitypack.util_windows import *
from utilitypack.util_ocv import *
from utilitypack.util_app import *
import functools
import keyshortcut.keyshortcut as keyshortcut
import shared.globalsys as globalsys


def main():
    app = BulletinApp(fps=10)

    ss = screenshoter()

    @app.Hotkey("ScreenShot", keyshortcut.win32conComp.VK_SCROLL)
    def SwitchPlottingScaleLock():
        p = ss.shotbgr()
        savemat(p, name=GetTimeString())
        app.bulletin.putup("screen captured")
        Rhythms.Success.asyncPlay()

    app.go()


if __name__ == "__main__":
    main()
