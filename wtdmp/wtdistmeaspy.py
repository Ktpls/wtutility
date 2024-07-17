from shared.globalsys import *


class mWtdmp(WtUtilityModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wtdmp = None

    def load(self):
        from . import wtdistmeaspyimpl as wtdistmeaspyimpl

        wtdmp = wtdistmeaspyimpl.wtdistmeaspy()
        self.wtdmp = wtdmp

        app = self.app

        @app.Hotkey("PlottingScaleLock", self.keyConfig.HotKey_PlottingScaleLock)
        def SwitchPlottingScaleLock():
            wtdmp.psLocked = not wtdmp.psLocked
            if wtdmp.psLocked:
                app.bulletin.putup(
                    f"plotting scale locked, now is {wtdmp.lastDistMeasResultStaged.plottingscale}"
                )
            else:
                app.bulletin.putup("plotting scale unlocked")

        @app.Hotkey("DistMeas&Cali", self.keyConfig.HotKey_DistMeasCali)
        @app.Async()
        def GoMeasureAndCali(self: StoppableSomewhat):
            app.bulletin.putup("measuring")
            result = wtdmp.solveMapMainLogic()
            app.bulletin.putup(result.prompt)
            if result.succeed:
                lastStaged = wtdmp.lastDistMeasResultStaged.result
                wtdmp.caliOperator.go(lastStaged)

        @app.Hotkey("StartCali", self.keyConfig.HotKey_StartCali)
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

        @app.Hotkey("SetPlottingScale", self.keyConfig.HotKey_SetPlottingScale)
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
                    wtdistmeaspyimpl.Keyboard.KeyPressDelay(win32con.VK_RETURN)
                    wtdistmeaspyimpl.Keyboard.KeyPressDelay(ord("1"))
                elif (
                    session.sessionEndType
                    == HotkeyManager.InputSession.SessionInstance.SessionEndType.CANCEL
                ):
                    app.bulletin.putup("plotting scale canceled")
                    wtdistmeaspyimpl.Keyboard.KeyPressDelay(win32con.VK_ESCAPE)

            app.inputSession.IntoSession(
                SetPlottingScaleLock,
                [HotkeyManager.InputSession.InputTypeEnabled.NUMBER],
            )

        @app.Hotkey("FreshPlottingScale", self.keyConfig.HotKey_FreshPlottingScale)
        @app.Async()
        def freshPlottingScaleGo(self: StoppableSomewhat):
            nonlocal wtdmp
            app.bulletin.putup("freshing")
            app.bulletin.putup(wtdmp.freshPlottingScale())
            wtdmp.psLocked = True
