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

    business = []

    @WrapperAsMyTaste()
    def RegisterBusiness(foo):
        business.append(foo)
        return foo

    hotkeyaction = []
    threadpool = ThreadPoolExecutor(max_workers=10)

    @WrapperAsMyTaste()
    def RegisterHotkey(foo, prompt, key, continiousPress=None):
        print(f"{prompt:<20}{HotkeyManager.hotkeytask.getKeyRepr(key)}")
        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=key, foo=foo, continiousPress=continiousPress)
        )
        return foo

    StoppableThreadEasyUse = functools.partial(
        StoppableSomewhat.EasyUse,
        pool=threadpool,
        implType=StoppableThread,
        strategy_runonrunning=StoppableSomewhat.StrategyRunOnRunning.stop_and_rerun,
        strategy_error=StoppableSomewhat.StrategyError.print_error,
    )

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

        @RegisterHotkey("PlottingScaleLock", [ord("L"), OEM3])
        def SwitchPlottingScaleLock():
            wtdmp.psLocked = not wtdmp.psLocked
            if wtdmp.psLocked:
                bulletin.putup(
                    f"plotting scale locked, now is {wtdmp.lastDistMeasResultStaged.plottingscale}"
                )
            else:
                bulletin.putup("plotting scale unlocked")

        @RegisterHotkey("DistMeas&Cali", OEM3)
        @StoppableThreadEasyUse()
        def GoMeasureAndCali(self: StoppableSomewhat):
            bulletin.putup("measuring")
            result = wtdmp.solveMapMainLogic()
            bulletin.putup(result.prompt)
            if result.succeed:
                lastStaged = wtdmp.lastDistMeasResultStaged.result
                wtdmp.caliOperator.go(lastStaged)

        @RegisterHotkey("StartCali", [win32con.VK_CONTROL, OEM3])
        def startCali():
            lastStaged = wtdmp.lastDistMeasResultStaged.result
            if lastStaged is None:
                bulletin.putup("no staged dist result to cali")
                return
            wtdmp.caliOperator.go(lastStaged)
            bulletin.putup(f"caliberating to {lastStaged}")

        # not used that much. normally just switch out from snip mode
        # @RegisterHotkey("StopCali", [win32con.VK_SHIFT, OEM3])
        def stopCali():
            wtdmp.caliOperator.stop()
            bulletin.putup(f"cali stopped")

        @RegisterHotkey(
            "SetPlottingScale", [win32con.VK_CONTROL, win32con.VK_MENU, OEM3]
        )
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

        @RegisterHotkey("FreshPlottingScale", [ord("L"), ord("K"), OEM3])
        @StoppableThreadEasyUse()
        def freshPlottingScaleGo(self: StoppableSomewhat):
            nonlocal wtdmp
            bulletin.putup("freshing")
            bulletin.putup(wtdmp.freshPlottingScale())
            wtdmp.psLocked = True

    # telescope
    if usingtelescope:
        print("telescope activated")
        import telescope.telescope as telescope

        tele = telescope.telescope()

        @RegisterBusiness()
        def telemain():
            scope = tele.mainlooplogic()
            if scope is None:
                return
            hud.writecontent(np.flip(telescopepos), scope)

        @RegisterHotkey("SwitchTelescope", win32con.VK_F12)
        def switchtele():
            tele.enabled = not tele.enabled

    # key shortcuts
    if usingkeyshortcut:
        print("keyshortcut activated")
        import keyshortcut.keyshortcut as keyshortcut

        @RegisterHotkey("HoldLeftAndTell", win32con.VK_F10)
        def holdLeftAndTell():
            keyshortcut.holdMouseLeft()
            bulletin.putup(bulletinBoard.Poster("LeftHolding", 1))

        @RegisterHotkey("HoldCAndTell", win32con.VK_F11)
        def holdCAndTell():
            keyshortcut.holdC()
            bulletin.putup(bulletinBoard.Poster("CHolding", 1))

        @RegisterHotkey("LaunchSeries", [win32con.VK_RCONTROL, ord("K"), ord("O")])
        @StoppableThreadEasyUse()
        def launchSeriesGo(self: StoppableSomewhat):
            bulletin.putup("launching series")
            interval = 0.099
            num = 29 + 3
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
            )(functools.partial(keyshortcut.move_mouse, dire))

    # eagle eye
    if usingeagleeye:
        import eagleeye

        eedcstate = False

        @RegisterHotkey("EagleEyeDataCollector", win32con.VK_F8)
        def eedcswitch():
            nonlocal eedcstate
            if eedcstate:
                eagleeye.cachedShots = []
                eedcstate = False
                bulletin.putup(bulletinBoard.Poster("eedc off", 1))
            else:
                eedcstate = True
                bulletin.putup(bulletinBoard.Poster("eedc on", 1))

        @RegisterHotkey("EagleEyeOnClick", win32con.VK_LBUTTON)
        def eedcOnClickWithSwitch():
            if eedcstate:
                eagleeye.onClick()

        RegisterBusiness()(eagleeye.onFrame)

    if usingglock:
        print("glock activated")
        import glock.glock as glock

        gl = glock.GLock()

        @RegisterHotkey("Glock", [win32con.VK_RSHIFT, win32con.VK_F9])
        def glSwitchBusiness():
            if gl.isRunning():
                bulletin.putup(bulletinBoard.Poster("glock stopping"))
                gl.setOff()
                bulletin.putup(bulletinBoard.Poster("glock stopped"))
            else:
                gl.setOn()
                bulletin.putup(bulletinBoard.Poster("glock started"))

        # business.append(printRunning)

    @RegisterHotkey("Reboot", [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F12])
    def rebootfoo():
        hud.stop()
        bootAsAdmin(__file__)
        RythmReboot.play()
        sys.exit()

    hud = fullScrHUD()
    hud.setup()
    fpsm = fpsmanager(aiofps)
    hkm = HotkeyManager(hotkeyaction)

    @RegisterBusiness()
    def showBulletinAndUpdateHud():
        # show bulletin
        hud.writecontent(
            np.flip(bulletinoutputpos),
            aPicWithTextWithPil(bulletin.read(), maxsize=[400, 700], lineinterval=0),
        )

        hud.update()

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
                    


if __name__ == "__main__":
    main()
