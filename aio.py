from concurrent.futures import ThreadPoolExecutor
import keyshortcut.gameinput as gameinput
from utilitypack.utility import *
from utilitypack.util_app import *
from aio_config import *
import functools
import keyshortcut.keyshortcut as keyshortcut
import shared.globalsys as globalsys


def main():
    app = BulletinApp(fps=aiofps)

    # wtdistmeas
    if usingwtdistmeaspy:
        print("wtdistmeaspy activated")
        import wtdmp.wtdistmeaspy as wtdistmeaspy

        wtdmp = wtdistmeaspy.wtdistmeaspy()

        @app.Hotkey("PlottingScaleLock", HotKey_PlottingScaleLock)
        def SwitchPlottingScaleLock():
            wtdmp.psLocked = not wtdmp.psLocked
            if wtdmp.psLocked:
                app.bulletin.putup(
                    f"plotting scale locked, now is {wtdmp.lastDistMeasResultStaged.plottingscale}"
                )
            else:
                app.bulletin.putup("plotting scale unlocked")

        @app.Hotkey("DistMeas&Cali", HotKey_DistMeasCali)
        @app.AsyncLongScript()
        def GoMeasureAndCali(self: StoppableSomewhat):
            app.bulletin.putup("measuring")
            result = wtdmp.solveMapMainLogic()
            app.bulletin.putup(result.prompt)
            if result.succeed:
                lastStaged = wtdmp.lastDistMeasResultStaged.result
                wtdmp.caliOperator.go(lastStaged)

        @app.Hotkey("StartCali", HotKey_StartCali)
        def startCali():
            lastStaged = wtdmp.lastDistMeasResultStaged.result
            if lastStaged is None:
                app.bulletin.putup("no staged dist result to cali")
                return
            wtdmp.caliOperator.go(lastStaged)
            app.bulletin.putup(f"caliberating to {lastStaged}")

        # not used that much. normally just switch out from snip mode
        # @RegisterHotkey("StopCali", HotKey_StopCali)
        def stopCali():
            wtdmp.caliOperator.stop()
            app.bulletin.putup(f"cali stopped")

        @app.Hotkey("SetPlottingScale", HotKey_SetPlottingScale)
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
                    result = Numinstr(session.content)
                    wtdmp.lastDistMeasResultStaged.plottingscale = result
                    app.bulletin.putup(f"plotting scale locked at {result}")
                    gameinput.key_press(win32con.VK_RETURN)
                    gameinput.key_press(ord("1"))
                elif (
                    session.sessionEndType
                    == HotkeyManager.InputSession.SessionInstance.SessionEndType.CANCEL
                ):
                    app.bulletin.putup("plotting scale canceled")
                    gameinput.key_press(win32con.VK_ESCAPE)

            app.inputSession.IntoSession(
                SetPlottingScaleLock,
                [HotkeyManager.InputSession.InputTypeEnabled.NUMBER],
            )

        @app.Hotkey("FreshPlottingScale", HotKey_FreshPlottingScale)
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

        tele = telescope.Telescope(app.threadpool)
        teleSwitch = Switch(onSetOn=lambda: tele.go(), onSetOff=lambda: tele.stop())

        @app.Business()
        def telemain():
            if not teleSwitch():
                return
            scope = tele.get()
            app.hud.writecontent(np.flip(telescope.telescopepos), scope)

        app.Hotkey("SwitchTelescope", HotKey_SwitchTelescope)(
            lambda: teleSwitch.switch()
        )

        mtiIns = telescope.MTI(app.threadpool)
        mtiSwitch = Switch(onSetOn=lambda: mtiIns.go(), onSetOff=lambda: mtiIns.stop())

        @app.Business()
        def mtiMain():
            if not mtiSwitch():
                return
            view = mtiIns.getResult()
            app.hud.writecontent(np.flip(telescope.mtiRect[:2]), view)

        app.Hotkey("SwitchTelescopeMti", HotKey_SwitchTelescopeMti)(
            lambda: mtiSwitch.switch()
        )

    # key shortcuts
    if usingkeyshortcut:
        print("keyshortcut activated")

        @app.Hotkey("HoldLeftAndTell", HotKey_HoldLeftAndTell)
        def holdLeftAndTell():
            keyshortcut.holdMouseLeft()
            app.bulletin.putup(BulletinBoard.Poster("LeftHolding", 1))

        @app.Hotkey("HoldCAndTell", HotKey_HoldCAndTell)
        def holdCAndTell():
            keyshortcut.holdC()
            app.bulletin.putup(BulletinBoard.Poster("CHolding", 1))

        @app.Hotkey("LaunchSeries", HotKey_LaunchSeries)
        @app.AsyncLongScript()
        def launchSeriesGo(self: StoppableSomewhat):
            app.bulletin.putup("launching series")
            keyshortcut.launchSeriesGo(self)
            app.bulletin.putup(f"launch done")

        @app.Hotkey("RefreshWifi", HotKey_RefreshWifi)
        @app.AsyncLongScript()
        def refreshWifi(self: StoppableSomewhat):
            app.bulletin.putup("refreshing wifi")
            wifi = WifiRefresher()
            wifi.setOff()
            time.sleep(1)
            wifi.setOn()
            app.bulletin.putup(f"refresh done")

        for key, dire, name in [
            [
                HotKey_MoveMouse_Direction_Up,
                keyshortcut.MoveMouseDirection.up,
                "Up",
            ],
            [
                HotKey_MoveMouse_Direction_Left,
                keyshortcut.MoveMouseDirection.left,
                "Left",
            ],
            [
                HotKey_MoveMouse_Direction_Down,
                keyshortcut.MoveMouseDirection.down,
                "Down",
            ],
            [
                HotKey_MoveMouse_Direction_Right,
                keyshortcut.MoveMouseDirection.right,
                "Right",
            ],
        ]:
            app.Hotkey(
                f"MoveMouse{name}",
                ArrayFlatten([HotKey_MoveMouse_AssistKey, key]),
                continiousPress=True,
            )(functools.partial(keyshortcut.move_mouse, dire))

    # eagle eye
    if usingeagleeye:
        import eagleeye.eagleeye as eagleeye

        eedcstate = False

        @app.Hotkey("EagleEyeDataCollector", HotKey_EagleEyeDataCollector)
        def eedcswitch():
            nonlocal eedcstate
            if eedcstate:
                eagleeye.cachedShots = []
                eedcstate = False
                app.bulletin.putup(BulletinBoard.Poster("eedc off", 1))
            else:
                eedcstate = True
                app.bulletin.putup(BulletinBoard.Poster("eedc on", 1))

        @app.Hotkey("EagleEyeOnClick", HotKey_EagleEyeOnClick)
        def eedcOnClickWithSwitch():
            if eedcstate:
                eagleeye.onClick()

        app.Business()(eagleeye.onFrame)

    if usingglock:
        print("glock activated")
        import glock.glock as glock

        gl = glock.GLock()

        @app.Hotkey("Glock", HotKey_Glock)
        def glSwitchBusiness():
            if gl.isRunning():
                app.bulletin.putup(BulletinBoard.Poster("glock stopping"))
                gl.setOff()
                app.bulletin.putup(BulletinBoard.Poster("glock stopped"))
            else:
                gl.setOn()
                app.bulletin.putup(BulletinBoard.Poster("glock started"))

    if usingengineman:
        print("engineman activated")
        import engineman.engineman as engineman

        em = engineman.DetachedEngineMan(pool=app.threadpool)

        def on():
            em.go()
            app.bulletin.putup(BulletinBoard.Poster("engineman started"))

        def off():
            em.stop()
            app.bulletin.putup(BulletinBoard.Poster("engineman stopped"))

        emSwitch = Switch(onSetOn=on, onSetOff=off)

        @app.Hotkey("EngineManSwitch", HotKey_EngineManSwitch)
        def emSwitchBusiness():
            emSwitch.switch()

    @app.Hotkey("Reboot", HotKey_Reboot)
    def rebootfoo():
        app.hud.stop()
        bootAsAdmin(__file__)
        Rhythms.Reboot.play()
        sys.exit()

    @app.Business()
    def PullBulletinQueueToBulletin():
        msg = globalsys.BulletinQueue().get()
        if msg is not None:
            app.bulletin.putup(msg)

    app.go()


if __name__ == "__main__":
    main()
