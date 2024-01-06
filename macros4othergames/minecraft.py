from concurrent.futures import ThreadPoolExecutor
from utilref import *
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

    K_HoldLeft = [win32con.VK_CONTROL, win32con.VK_F10]
    print("HoldLeft")
    print(HotkeyManager.hotkeytask.getKeyRepr(K_HoldLeft))

    K_HoldW = [[win32con.VK_MENU, ord("W")]]
    print("HoldW")
    print(HotkeyManager.hotkeytask.getKeyRepr(K_HoldW))

    K_JumpHorse = [[win32con.VK_CONTROL, ord("J")]]
    print("JumpHorse")
    print(HotkeyManager.hotkeytask.getKeyRepr(K_JumpHorse))

    K_TakeOff = [[win32con.VK_CONTROL, ord("G")]]
    print("JumpHorse")
    print(HotkeyManager.hotkeytask.getKeyRepr(K_JumpHorse))

    K_Reboot = [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F12]
    print("Reboot")
    print(HotkeyManager.hotkeytask.getKeyRepr(K_Reboot))

    K_HKEnable = [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F11]
    print("HKEnable")
    print(HotkeyManager.hotkeytask.getKeyRepr(K_HKEnable))

    print("MoveMouse")
    print("Ctrl+UpDownLeftRight")

    hotkeySwitch = True

    def WrapperHotkeySwitch(f):
        def foo(*arg, **kw):
            nonlocal hotkeySwitch
            if hotkeySwitch:
                f(*arg, **kw)
            else:
                bulletin.putup(bulletinBoard.Poster("hotkey disabled", 1))

        return foo

    @WrapperHotkeySwitch
    def holdLeftAndTell():
        keyshortcut.mouse.down(0)
        bulletin.putup(bulletinBoard.Poster("leftHolding", 1))

    hotkeyaction.append(HotkeyManager.hotkeytask(key=K_HoldLeft, foo=holdLeftAndTell))

    class holdWAndTell(StoppableThread):
        @WrapperHotkeySwitch
        def foo(self, *arg, **kw) -> None:
            bulletin.putup(bulletinBoard.Poster("waiting", 1))
            time.sleep(0.5)
            keyshortcut.keydown(keyshortcut.keycode.key_W)
            bulletin.putup(bulletinBoard.Poster("wHolding", 1))

    hotkeyaction.append(
        HotkeyManager.hotkeytask(
            key=K_HoldW,
            foo=lambda: holdWAndTell(pool=threadpool).go(),
        )
    )

    class bestJumpOnHorse(StoppableThread):
        @WrapperHotkeySwitch
        def foo(self, *arg, **kw) -> None:
            bulletin.putup(bulletinBoard.Poster("going", 1))
            keyshortcut.keydown(keyshortcut.keycode.key_Spacebar)
            PreciseSleep(0.55)
            keyshortcut.keyup(keyshortcut.keycode.key_Spacebar)

    hotkeyaction.append(
        HotkeyManager.hotkeytask(
            key=K_JumpHorse,
            foo=lambda: bestJumpOnHorse(pool=threadpool).go(),
        )
    )

    class takeOff(StoppableThread):
        @WrapperHotkeySwitch
        def foo(self, *arg, **kw) -> None:
            keyshortcut.press(keyshortcut.keycode.key_Spacebar)
            PreciseSleep(0.25)
            keyshortcut.press(keyshortcut.keycode.key_Spacebar)
            PreciseSleep(0.05)
            keyshortcut.mouse.click(1)

            bulletin.putup(bulletinBoard.Poster("tookOff"))

    hotkeyaction.append(
        HotkeyManager.hotkeytask(
            key=K_TakeOff,
            foo=lambda: takeOff(pool=threadpool).go(),
        )
    )

    keylist = [
        win32con.VK_UP,
        win32con.VK_LEFT,
        win32con.VK_DOWN,
        win32con.VK_RIGHT,
    ]
    direction = [
        keyshortcut.MoveMouseDirection.up,
        keyshortcut.MoveMouseDirection.left,
        keyshortcut.MoveMouseDirection.down,
        keyshortcut.MoveMouseDirection.right,
    ]
    kd = zip(keylist, direction)

    @WrapperHotkeySwitch
    def fooMouse(*arg, **kw):
        keyshortcut.move_mouse(*arg, **kw)

    for pair in kd:
        hotkeyaction.append(
            HotkeyManager.hotkeytask(
                key=[win32con.VK_CONTROL, pair[0]],
                foo=functools.partial(fooMouse, pair[1]),
                continiousPress=True,
            )
        )

    @WrapperHotkeySwitch
    def rebootfoo():
        hud.stop()
        bootAsAdmin(__file__)
        RythmReboot.play()
        sys.exit()

    hotkeyaction.append(HotkeyManager.hotkeytask(key=K_Reboot, foo=rebootfoo))

    def taskSwitch():
        nonlocal hotkeySwitch
        hotkeySwitch = not hotkeySwitch
        if hotkeySwitch:
            bulletin.putup(bulletinBoard.Poster("hkmEnabled"))
        else:
            bulletin.putup(bulletinBoard.Poster("hkmDisabled"))

    hotkeyaction.append(
        HotkeyManager.hotkeytask(
            key=K_HKEnable,
            foo=taskSwitch,
        )
    )

    hud = fullScrHUD()
    hud.setup()
    fpsm = fpsmanager(10)
    hkm = HotkeyManager(hotkeyaction)

    # main loop
    while True:
        fpsm.WaitUntilNextFrame()
        hud.clear()

        decideresult = hkm.decideAllHotKey()

        try:
            hkm.doAllDecidedKey(decideresult, True, False)
        except SystemExit as e:
            raise e
        except Exception as e:
            RythmError.play()
            print("#" * 10)
            traceback.print_exc()
            print("#" * 10)
            raise e

        # show bulletin
        hud.writecontent(
            np.flip(bulletinoutputpos),
            aPicWithTextWithPil(bulletin.read(), maxsize=[400, 700], lineinterval=0),
        )

        hud.update()


main()
