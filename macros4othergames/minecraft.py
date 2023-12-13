from concurrent.futures import ThreadPoolExecutor
from utilitypack.utility import *
import traceback
import functools

bulletinoutputpos = (100, 500)


def main():
    """
    simplified from wt aio
    """
    bulletin = bulletinBoard("(=w=)")

    # 热键
    hotkeyaction = []
    threadpool = ThreadPoolExecutor()

    print("keyshortcut activated")
    import keyshortcut.keyshortcut as keyshortcut

    def holdLeftAndTell():
        keyshortcut.mouse.down(0)
        bulletin.putup(bulletinBoard.Poster("LeftHolding", 1))

    hotkeyaction.append(
        HotkeyManager.hotkeytask(key=win32con.VK_F10, foo=holdLeftAndTell)
    )

    def holdCAndTell():
        keyshortcut.keydown(keyshortcut.keycode.key_C)
        bulletin.putup(bulletinBoard.Poster("CHolding", 1))

    hotkeyaction.append(
        HotkeyManager.hotkeytask(
            key=[[win32con.VK_CONTROL], [ord("C")]], foo=holdCAndTell
        )
    )

    def holdCAndTell():
        keyshortcut.keydown(keyshortcut.keycode.key_W)
        bulletin.putup(bulletinBoard.Poster("WHolding", 1))

    hotkeyaction.append(
        HotkeyManager.hotkeytask(
            key=[[win32con.VK_CONTROL], [ord("W")]], foo=holdCAndTell
        )
    )

    keylist = [
        win32con.VK_UP,
        win32con.VK_LEFT,
        win32con.VK_DOWN,
        win32con.VK_RIGHT,
    ]
    direction = ["up", "left", "down", "right"]
    kd = zip(keylist, direction)
    for pair in kd:
        hotkeyaction.append(
            HotkeyManager.hotkeytask(
                key=[win32con.VK_CONTROL, pair[0]],
                foo=functools.partial(keyshortcut.move_mouse, pair[1]),
                continiousPress=True,
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
            aPicWithText(bulletin.read(), maxsize=[400, 700]),
        )

        hud.update()


main()
