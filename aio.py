from concurrent.futures import ThreadPoolExecutor
import keyshortcut.gameinput as gameinput, keyshortcut.keycodeWinCode as keycode
from utilitypack.utility import *
from utilitypack.util_app import *
from aio_config import *
import functools

telescopepos = (100, 100)


def main():
    app = BulletinApp(fps=aiofps)

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

        @app.Hotkey("PlottingScaleLock", [ord("L"), OEM3])
        def SwitchPlottingScaleLock():
            wtdmp.psLocked = not wtdmp.psLocked
            if wtdmp.psLocked:
                app.bulletin.putup(
                    f"plotting scale locked, now is {wtdmp.lastDistMeasResultStaged.plottingscale}"
                )
            else:
                app.bulletin.putup("plotting scale unlocked")

        @app.Hotkey("DistMeas&Cali", OEM3)
        @app.AsyncLongScript()
        def GoMeasureAndCali(self: StoppableSomewhat):
            app.bulletin.putup("measuring")
            result = wtdmp.solveMapMainLogic()
            app.bulletin.putup(result.prompt)
            if result.succeed:
                lastStaged = wtdmp.lastDistMeasResultStaged.result
                wtdmp.caliOperator.go(lastStaged)

        @app.Hotkey("StartCali", [win32con.VK_CONTROL, OEM3])
        def startCali():
            lastStaged = wtdmp.lastDistMeasResultStaged.result
            if lastStaged is None:
                app.bulletin.putup("no staged dist result to cali")
                return
            wtdmp.caliOperator.go(lastStaged)
            app.bulletin.putup(f"caliberating to {lastStaged}")

        # not used that much. normally just switch out from snip mode
        # @RegisterHotkey("StopCali", [win32con.VK_SHIFT, OEM3])
        def stopCali():
            wtdmp.caliOperator.stop()
            app.bulletin.putup(f"cali stopped")

        @app.Hotkey("SetPlottingScale", [win32con.VK_CONTROL, win32con.VK_MENU, OEM3])
        def SetPlottingScale():
            app.bulletin.putup("input plotting scale")

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
                    app.bulletin.putup(f"plotting scale locked at {result}")
                    gameinput.key_press(keycode.key_Enter)
                    gameinput.key_press(keycode.key_1)
                elif (
                    session.sessionEndType
                    == HotkeyManager.InputSession.SessionInstance.SessionEndType.CANCEL
                ):
                    app.bulletin.putup("plotting scale canceled")
                    gameinput.key_press(keycode.key_Esc)

            app.inputSession.IntoSession(
                SetPlottingScaleLock,
                [HotkeyManager.InputSession.InputTypeEnabled.NUMBER],
            )

        @app.Hotkey("FreshPlottingScale", [ord("L"), ord("K"), OEM3])
        @app.AsyncLongScript()
        def freshPlottingScaleGo(self: StoppableSomewhat):
            nonlocal wtdmp
            app.bulletin.putup("freshing")
            app.bulletin.putup(wtdmp.freshPlottingScale())
            wtdmp.psLocked = True

    # telescope
    if usingtelescope:
        print("telescope activated")
        import telescope.telescope as telescope

        tele = telescope.telescope()

        @app.Business()
        def telemain():
            scope = tele.mainlooplogic()
            if scope is None:
                return
            app.hud.writecontent(np.flip(telescopepos), scope)

        @app.Hotkey("SwitchTelescope", win32con.VK_F12)
        def switchtele():
            tele.enabled = not tele.enabled

    # key shortcuts
    if usingkeyshortcut:
        print("keyshortcut activated")
        import keyshortcut.keyshortcut as keyshortcut

        @app.Hotkey("HoldLeftAndTell", win32con.VK_F10)
        def holdLeftAndTell():
            keyshortcut.holdMouseLeft()
            app.bulletin.putup(bulletinBoard.Poster("LeftHolding", 1))

        @app.Hotkey("HoldCAndTell", win32con.VK_F11)
        def holdCAndTell():
            keyshortcut.holdC()
            app.bulletin.putup(bulletinBoard.Poster("CHolding", 1))

        @app.Hotkey("LaunchSeries", [win32con.VK_RCONTROL, ord("K"), ord("O")])
        @app.AsyncLongScript()
        def launchSeriesGo(self: StoppableSomewhat):
            app.bulletin.putup("launching series")
            interval = 0.01
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

            app.bulletin.putup(f"launch done")

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
            )(functools.partial(keyshortcut.move_mouse, dire))

    # eagle eye
    if usingeagleeye:
        import eagleeye.eagleeye as eagleeye

        eedcstate = False

        @app.Hotkey("EagleEyeDataCollector", win32con.VK_F8)
        def eedcswitch():
            nonlocal eedcstate
            if eedcstate:
                eagleeye.cachedShots = []
                eedcstate = False
                app.bulletin.putup(bulletinBoard.Poster("eedc off", 1))
            else:
                eedcstate = True
                app.bulletin.putup(bulletinBoard.Poster("eedc on", 1))

        @app.Hotkey("EagleEyeOnClick", win32con.VK_LBUTTON)
        def eedcOnClickWithSwitch():
            if eedcstate:
                eagleeye.onClick()

        app.Business()(eagleeye.onFrame)

    if usingglock:
        print("glock activated")
        import glock.glock as glock

        gl = glock.GLock()

        @app.Hotkey("Glock", [win32con.VK_RSHIFT, win32con.VK_F9])
        def glSwitchBusiness():
            if gl.isRunning():
                app.bulletin.putup(bulletinBoard.Poster("glock stopping"))
                gl.setOff()
                app.bulletin.putup(bulletinBoard.Poster("glock stopped"))
            else:
                gl.setOn()
                app.bulletin.putup(bulletinBoard.Poster("glock started"))

    @app.Hotkey("Reboot", [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F12])
    def rebootfoo():
        app.hud.stop()
        bootAsAdmin(__file__)
        RythmReboot.play()
        sys.exit()

    app.go()


if __name__ == "__main__":
    main()
