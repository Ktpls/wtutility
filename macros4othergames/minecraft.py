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

    @app.Hotkey("HoldLeft", [win32con.VK_CONTROL, win32con.VK_F10])
    @WithHotkeySwitch()
    def holdLeft():
        mouse.down(0)
        app.bulletin.putup(BulletinBoard.Poster("leftHolding", 1))

    def BindHotkeyHoldKeyboard(name: str, key: int):
        @app.Hotkey(name, [win32con.VK_MENU, key])
        @WithHotkeySwitch()
        @app.Async()
        def foo(*_):
            app.bulletin.putup(BulletinBoard.Poster("waiting", 1))
            Keyboard.KeyUp(key)
            for i in range(3):
                time.sleep(0.1)
            Keyboard.KeyDown(key)
            app.bulletin.putup(BulletinBoard.Poster("holding", 1))

        return foo

    BindHotkeyHoldKeyboard("HoldW", ord("W"))
    BindHotkeyHoldKeyboard("HoldCtrl", win32con.VK_CONTROL)

    @app.Hotkey("JumpHorse", [win32con.VK_CONTROL, ord("J")])
    @app.Async()
    @WithHotkeySwitch()
    def bestJumpOnHorse(*arg, **kw) -> None:
        app.bulletin.putup(BulletinBoard.Poster("going", 1))
        Keyboard.KeyDown(win32con.VK_SPACE)
        PreciseSleep(0.55)
        Keyboard.KeyUp(win32con.VK_SPACE)

    @app.Hotkey("TakeOff", [win32con.VK_CONTROL, ord("G")])
    @app.Async()
    @WithHotkeySwitch()
    def takeOff(*arg, **kw) -> None:
        Keyboard.KeyPress(win32con.VK_SPACE)
        PreciseSleep(0.25)
        Keyboard.KeyPress(win32con.VK_SPACE)
        PreciseSleep(0.05)
        mouse.click(1)

        app.bulletin.putup(BulletinBoard.Poster("takeOff"))

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
        app.HotkeyFullFunction(
            f"MoveMouse{name}",
            [win32con.VK_CONTROL, key],
            onKeyPress=WithHotkeySwitch()(
                functools.partial(keyshortcut.move_mouse, dire)
            ),
        )

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
