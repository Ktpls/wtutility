from concurrent.futures import ThreadPoolExecutor
from utilref import *
from utilitypack.util_app import *
from utilitypack.util_winkey import *
import keyshortcut.keyshortcutimpl as keyshortcut
from macroutility import *
import traceback
import functools
import time


def main():
    """
    simplified from wt aio
    """
    app = BulletinApp(fps=2)

    print("keyshortcut activated")

    hotkeySwitch = Switch(
        onSetOn=lambda: app.bulletin.putup(BulletinBoard.Poster("hkmEnabled")),
        onSetOff=lambda: app.bulletin.putup(BulletinBoard.Poster("hkmDisabled")),
        initial=True,
    )

    @EasyWrapper
    def WithHotkeySwitch(f):
        def foo(*arg, **kw):
            if hotkeySwitch():
                f(*arg, **kw)
            else:
                app.bulletin.putup(BulletinBoard.Poster("hotkey disabled", 1))

        return foo

    @app.Hotkey("Run", [win32con.VK_MENU, ord("W")])
    @app.AsyncLongScript()
    @WithHotkeySwitch()
    def holdW(*arg, **kw) -> None:
        app.bulletin.putup(BulletinBoard.Poster("waiting", 1))
        for i in range(3):
            time.sleep(0.1)
        Keyboard.KeyDown(ord("W"))
        Keyboard.KeyDown(win32con.VK_SHIFT)
        app.bulletin.putup(BulletinBoard.Poster("wHolding", 1))
        print("1")

    @app.Hotkey("Reboot", [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F12])
    @WithHotkeySwitch()
    def rebootfoo():
        app.hud.stop()
        bootAsAdmin(__file__)
        Rhythms.Reboot.play()
        sys.exit()

    @app.Hotkey("HKDisable", [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F11])
    def taskSwitch():
        hotkeySwitch.switch()

    app.go()


def emotion():
    app = BulletinApp()


main()
