from concurrent.futures import ThreadPoolExecutor
from utilref import *
from macroutility import *
import traceback
import functools
import time

bulletinoutputpos = (100, 500)


def main():
    """
    simplified from wt aio
    """
    bulletin = bulletinBoard("(*≧ω≦)")

    # 热键
    hotkeyaction = []
    threadpool = ThreadPoolExecutor()

    print("keyshortcut activated")
    import keyshortcut.keyshortcut as keyshortcut

    def splitLine():
        print("#" * 10)

    @WrapperAsMyTaste()
    def RegisterHotkey(foo, prompt, key, continiousPress=None):
        print(f"{prompt:<15}{HotkeyManager.hotkeytask.getKeyRepr(key)}")
        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=key, foo=foo, continiousPress=continiousPress)
        )
        return foo

    hotkeySwitch = True

    @WrapperAsMyTaste()
    def WrapperHotkeySwitch(f):
        def foo(*arg, **kw):
            nonlocal hotkeySwitch
            if hotkeySwitch:
                f(*arg, **kw)
            else:
                bulletin.putup(bulletinBoard.Poster("hotkey disabled", 1))

        return foo

    AsyncTimeCostlyProcessInPool = functools.partial(
        AsyncTimeCostlyProcess, pool=threadpool
    )

    @RegisterHotkey("HoldLeft", [win32con.VK_CONTROL, win32con.VK_F10])
    @WrapperHotkeySwitch()
    def holdLeft():
        keyshortcut.mouse.down(0)
        bulletin.putup(bulletinBoard.Poster("leftHolding", 1))

    @RegisterHotkey("HoldW", [win32con.VK_MENU, ord("W")])
    @AsyncTimeCostlyProcessInPool()
    @WrapperHotkeySwitch()
    def holdW(*arg, **kw) -> None:
        bulletin.putup(bulletinBoard.Poster("waiting", 1))
        time.sleep(0.5)
        keyshortcut.keydown(keyshortcut.keycode.key_W)
        bulletin.putup(bulletinBoard.Poster("wHolding", 1))

    @RegisterHotkey("JumpHorse", [win32con.VK_CONTROL, ord("J")])
    @AsyncTimeCostlyProcessInPool()
    @WrapperHotkeySwitch()
    def bestJumpOnHorse(*arg, **kw) -> None:
        bulletin.putup(bulletinBoard.Poster("going", 1))
        keyshortcut.keydown(keyshortcut.keycode.key_Spacebar)
        PreciseSleep(0.55)
        keyshortcut.keyup(keyshortcut.keycode.key_Spacebar)

    @RegisterHotkey("TakeOff", [win32con.VK_CONTROL, ord("G")])
    @AsyncTimeCostlyProcessInPool()
    @WrapperHotkeySwitch()
    def takeOff(*arg, **kw) -> None:
        keyshortcut.press(keyshortcut.keycode.key_Spacebar)
        PreciseSleep(0.25)
        keyshortcut.press(keyshortcut.keycode.key_Spacebar)
        PreciseSleep(0.05)
        keyshortcut.mouse.click(1)

        bulletin.putup(bulletinBoard.Poster("tookOff"))

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
        RegisterHotkey(
            f"MoveMouse{name}", [win32con.VK_CONTROL, key], continiousPress=True
        )(WrapperHotkeySwitch()(functools.partial(keyshortcut.move_mouse, dire)))

    @RegisterHotkey("Reboot", [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F12])
    @WrapperHotkeySwitch()
    def rebootfoo():
        hud.stop()
        bootAsAdmin(__file__)
        RythmReboot.play()
        sys.exit()

    @RegisterHotkey(
        "HKDisable", [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F11]
    )
    def taskSwitch():
        nonlocal hotkeySwitch
        hotkeySwitch = not hotkeySwitch
        if hotkeySwitch:
            bulletin.putup(bulletinBoard.Poster("hkmEnabled"))
        else:
            bulletin.putup(bulletinBoard.Poster("hkmDisabled"))

    buz = list()

    hud = fullScrHUD().setup()

    def showBulletinAndUpdateHud():
        # show bulletin
        hud.writecontent(
            np.flip(bulletinoutputpos),
            aPicWithTextWithPil(bulletin.read(), maxsize=[400, 700], lineinterval=0),
        )

        hud.update()

    buz.append(showBulletinAndUpdateHud)

    mainloop(10, hotkeyaction, buz)


main()
