from concurrent.futures import ThreadPoolExecutor
from utilref import *
from utilitypack.util_app import *
from macroutility import *
import traceback
import functools
import time


def main():
    """
    simplified from wt aio
    """
    app = BulletinApp()

    print("keyshortcut activated")
    import keyshortcut.keyshortcut as keyshortcut

    hotkeySwitch = Switch(True)

    @EasyWrapper
    def WithHotkeySwitch(f):
        def foo(*arg, **kw):
            if hotkeySwitch():
                f(*arg, **kw)
            else:
                app.bulletin.putup(bulletinBoard.Poster("hotkey disabled", 1))

        return foo

    @app.Hotkey("HoldLeft", [win32con.VK_CONTROL, win32con.VK_F10])
    @WithHotkeySwitch()
    def holdLeft():
        keyshortcut.mouse.down(0)
        app.bulletin.putup(bulletinBoard.Poster("leftHolding", 1))

    @app.Hotkey("HoldW", [win32con.VK_MENU, ord("W")])
    @app.AsyncLongScript()
    @WithHotkeySwitch()
    def holdW(*arg, **kw) -> None:
        app.bulletin.putup(bulletinBoard.Poster("waiting", 1))
        for i in range(5):
            keyshortcut.keydown(keyshortcut.keycode.key_W)
            time.sleep(0.1)
        keyshortcut.keydown(keyshortcut.keycode.key_W)
        app.bulletin.putup(bulletinBoard.Poster("wHolding", 1))

    @app.Hotkey("JumpHorse", [win32con.VK_CONTROL, ord("J")])
    @app.AsyncLongScript()
    @WithHotkeySwitch()
    def bestJumpOnHorse(*arg, **kw) -> None:
        app.bulletin.putup(bulletinBoard.Poster("going", 1))
        keyshortcut.keydown(keyshortcut.keycode.key_Spacebar)
        PreciseSleep(0.55)
        keyshortcut.keyup(keyshortcut.keycode.key_Spacebar)

    @app.Hotkey("TakeOff", [win32con.VK_CONTROL, ord("G")])
    @app.AsyncLongScript()
    @WithHotkeySwitch()
    def takeOff(*arg, **kw) -> None:
        keyshortcut.press(keyshortcut.keycode.key_Spacebar)
        PreciseSleep(0.25)
        keyshortcut.press(keyshortcut.keycode.key_Spacebar)
        PreciseSleep(0.05)
        keyshortcut.mouse.click(1)

        app.bulletin.putup(bulletinBoard.Poster("takeOff"))

    for key, dire, name in [
        [
            win32con.VK_UP,
            keyshortcut.MoveMouseDirection.up,
            "Up",
        ],
        [
            win32con.VK_LEFT,
            keyshortcut.MoveMouseDirection.left,
            "Left",
        ],
        [
            win32con.VK_DOWN,
            keyshortcut.MoveMouseDirection.down,
            "Down",
        ],
        [
            win32con.VK_RIGHT,
            keyshortcut.MoveMouseDirection.right,
            "Right",
        ],
    ]:
        app.Hotkey(
            f"MoveMouse{name}", [win32con.VK_CONTROL, key], continiousPress=True
        )(WithHotkeySwitch()(functools.partial(keyshortcut.move_mouse, dire)))

    @app.Hotkey("Reboot", [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F12])
    @WithHotkeySwitch()
    def rebootfoo():
        app.hud.stop()
        bootAsAdmin(__file__)
        RythmReboot.play()
        sys.exit()

    @app.Hotkey("HKDisable", [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F11])
    def taskSwitch():
        hotkeySwitch.switch()
        if hotkeySwitch():
            app.bulletin.putup(bulletinBoard.Poster("hkmEnabled"))
        else:
            app.bulletin.putup(bulletinBoard.Poster("hkmDisabled"))

    app.go()

def emotion():
    app=BulletinApp()

main()
