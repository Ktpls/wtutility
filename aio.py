from concurrent.futures import ThreadPoolExecutor
import keyshortcut.gameinput as gameinput, keyshortcut.keycodeWinCode as keycode
from utilitypack.utility import *
from aio_config import *
import traceback
import hashlib
import functools

bulletinoutputpos = (100, 500)
telescopepos = (100, 100)


def main():
    # 告示板
    idlebulletincontents = [
        ["(=ω=)", 66],
        ["(*≧ω≦)", 30],
        ["($ω$)", 1],
        ["(＞д＜)", 1],
        ["(￣ω￣;)", 1],
        ["(0v0)", 1],
    ]

    # 每天固定一种
    seed = time.strftime("%Y-%m-%d", time.localtime()).encode("utf-8")
    seed = hashlib.md5(seed).digest()
    seed = int.from_bytes(seed[:8], "big")
    bulletin = bulletinBoard(
        idlebulletincontents[
            summonCard(
                [c[1] for c in idlebulletincontents],
                np.random.Generator(np.random.PCG64(seed)),
            )
        ][0]
    )

    # 日常运作的业务
    business = []
    # 热键
    hotkeyaction = []
    threadpool = ThreadPoolExecutor(max_workers=10)

    # wtdistmeas
    if usingwtdistmeaspy:
        print("wtdistmeaspy activated")
        import wtdmp.wtdistmeaspy as wtdistmeaspy

        wtdmp = wtdistmeaspy.wtdistmeaspy()
        """
        VK_OEM_3=0xC0
        Used for miscellaneous characters; it can vary by keyboard.
        For the US standard keyboard, the '`~' key
        """
        OEM3 = 0xC0

        def SwitchPlottingScaleLock():
            wtdmp.psLocked = not wtdmp.psLocked
            if wtdmp.psLocked:
                bulletin.putup(
                    f"plotting scale locked, now is {wtdmp.lastDistMeasResultStaged.plottingscale}"
                )
            else:
                bulletin.putup("plotting scale unlocked")

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=[ord("L"), OEM3], foo=SwitchPlottingScaleLock)
        )

        class GoMeasureAndCali(StoppableThread):
            def foo(self, *args, **kwargs):
                result = wtdmp.solveMapMainLogic()
                bulletin.putup(result.prompt)
                if result.succeed:
                    lastStaged = wtdmp.lastDistMeasResultStaged.result
                    wtdmp.caliOperator.go(lastStaged)

        goMeasureAndCali = GoMeasureAndCali(
            StoppableThread.Strategy_RunOnRunning.stop_and_rerun, threadpool
        )

        def hkcallWTDistMeas():
            bulletin.putup("measuring")
            goMeasureAndCali.go()

        hotkeyaction.append(HotkeyManager.hotkeytask(key=OEM3, foo=hkcallWTDistMeas))

        def startCali():
            lastStaged = wtdmp.lastDistMeasResultStaged.result
            if lastStaged is None:
                bulletin.putup("no staged dist result to cali")
                return
            wtdmp.caliOperator.go(lastStaged)
            bulletin.putup(f"caliberating to {lastStaged}")

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=[win32con.VK_CONTROL, OEM3], foo=startCali)
        )

        def stopCali():
            wtdmp.caliOperator.stop()
            bulletin.putup(f"cali stopped")

        # not used that much. normally just switch out from snip mode
        # hotkeyaction.append(
        #     hotkeymanager.hotkeytask(key=[win32con.VK_SHIFT, OEM3], foo=stopCali)
        # )

        def SetPlottingScale():
            nonlocal inputSession
            bulletin.putup("input plotting scale")

            def SetPlottingScaleLock(
                session: HotkeyManager.InputSession.SessionInstance,
            ):
                if (
                    session.sessionEndType
                    == HotkeyManager.InputSession.SessionInstance.SessionEndType.OK
                ):
                    nonlocal wtdmp
                    wtdmp.psLocked = True
                    result = numinstr(session.content)
                    wtdmp.lastDistMeasResultStaged.plottingscale = result
                    bulletin.putup(f"plotting scale locked at {result}")
                    gameinput.key_press(keycode.key_Enter)
                    gameinput.key_press(keycode.key_1)
                elif (
                    session.sessionEndType
                    == HotkeyManager.InputSession.SessionInstance.SessionEndType.CANCEL
                ):
                    bulletin.putup("plotting scale canceled")
                    gameinput.key_press(keycode.key_Esc)

            inputSession.IntoSession(
                SetPlottingScaleLock,
                [HotkeyManager.InputSession.InputTypeEnabled.NUMBER],
            )

        hotkeyaction.append(
            HotkeyManager.hotkeytask(
                key=[win32con.VK_CONTROL, win32con.VK_MENU, OEM3],
                foo=SetPlottingScale,
            )
        )

        def freshPlottingScale():
            class ThFreshPs(StoppableThread):
                def __init__(
                    self,
                    pool: ThreadPoolExecutor,
                ) -> None:
                    super().__init__(
                        StoppableThread.Strategy_RunOnRunning.stop_and_rerun,
                        pool,
                    )

                def foo(self, *args, **kwargs):
                    nonlocal wtdmp
                    bulletin.putup(wtdmp.freshPlottingScale())
                    wtdmp.psLocked = True

            bulletin.putup("freshing")
            ThFreshPs(threadpool).go()

        hotkeyaction.append(
            HotkeyManager.hotkeytask(
                key=[ord("L"), ord("K"), OEM3],
                foo=freshPlottingScale,
            )
        )

    # telescope
    if usingtelescope:
        print("telescope activated")
        import telescope.telescope as telescope

        tele = telescope.telescope()

        def telemain():
            scope = tele.mainlooplogic()
            if scope is None:
                return
            hud.writecontent(np.flip(telescopepos), scope)

        business.append(telemain)

        def switchtele():
            tele.enabled = not tele.enabled

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=win32con.VK_F12, foo=switchtele)
        )

    # key shortcuts
    if usingkeyshortcut:
        print("keyshortcut activated")
        import keyshortcut.keyshortcut as keyshortcut

        def holdLeftAndTell():
            keyshortcut.holdMouseLeft()
            bulletin.putup(bulletinBoard.Poster("LeftHolding", 1))

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=win32con.VK_F10, foo=holdLeftAndTell)
        )

        def holdCAndTell():
            keyshortcut.holdC()
            bulletin.putup(bulletinBoard.Poster("CHolding", 1))

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=win32con.VK_F11, foo=holdCAndTell)
        )

        class LaunchSeries(StoppableThread):
            def __init__(
                self,
                pool: ThreadPoolExecutor,
            ) -> None:
                super().__init__(
                    StoppableThread.Strategy_RunOnRunning.stop_and_rerun,
                    pool,
                )

            def foo(self, *args, **kwargs):
                bulletin.putup("launching series")
                interval = 0.099
                num = 29+3
                keyshortcut.keydown(keycode.key_LeftControl)
                for i in range(num):
                    if self.timeToStop():
                        break
                    keyshortcut.keydown(keycode.key_Spacebar)
                    PreciseSleep(0.03)
                    keyshortcut.keyup(keycode.key_Spacebar)
                    PreciseSleep(interval)
                keyshortcut.keyup(keycode.key_LeftControl)

                bulletin.putup(f"launch done")

        launchSeries = LaunchSeries(threadpool)
        hotkeyaction.append(
            HotkeyManager.hotkeytask(
                key=[
                    win32con.VK_RCONTROL,
                    ord("K"),
                    ord("O"),
                ],
                foo=lambda: launchSeries.go(),
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

    # eagle eye
    if usingeagleeye:
        import eagleeye

        eedcstate = False

        def eedcswitch():
            nonlocal eedcstate
            if eedcstate:
                eagleeye.cachedShots = []
                eedcstate = False
                bulletin.putup(bulletinBoard.Poster("eedc off", 1))
            else:
                eedcstate = True
                bulletin.putup(bulletinBoard.Poster("eedc on", 1))

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=win32con.VK_F8, foo=eedcswitch)
        )

        def eedcOnClickWithSwitch():
            if eedcstate:
                eagleeye.onClick()

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=win32con.VK_LBUTTON, foo=eedcOnClickWithSwitch)
        )
        business.append(eagleeye.onFrame)

    if usingglock:
        print("glock activated")
        import glock.glock as glock

        agl = glock.GLock(2)

        def glBuzWrap():
            isCtrling, duration = agl.business()
            if isCtrling:
                bulletin.putup(bulletinBoard.Poster(f"glock", 0.2))

        business.append(glBuzWrap)

    def rebootfoo():
        hud.stop()
        bootAsAdmin(__file__)
        RythmReboot.play()
        sys.exit()

    hotkeyaction.append(
        HotkeyManager.hotkeytask(
            key=[win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F12], foo=rebootfoo
        )
    )

    hud = fullScrHUD()
    hud.setup()
    fpsm = fpsmanager(aiofps)
    hkm = HotkeyManager(hotkeyaction)

    def swapHKM(newHkm):
        nonlocal hkm
        old = hkm
        hkm = newHkm
        return old

    inputSession = HotkeyManager.InputSession(swapHKM, bulletin)

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
            if throwErrorInHotkey:
                raise e

        for bus in business:
            try:
                bus()
            except Exception as e:
                RythmError.play()
                print("#" * 10)
                traceback.print_exc()
                print("#" * 10)
                if throwErrorInBus:
                    raise e

        # show bulletin
        hud.writecontent(
            np.flip(bulletinoutputpos),
            aPicWithTextWithPil(bulletin.read(), maxsize=[400, 700], lineinterval=0),
        )

        hud.update()


if __name__ == "__main__":
    main()
