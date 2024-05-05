from shared.globalsys import *


class mTelescope(WtUtilityModule):

    def load(self):
        from . import telescopeimpl as telescopeimpl
        app=self.app

        tele = telescopeimpl.Telescope(app.threadpool)
        teleSwitch = Switch(onSetOn=lambda: tele.go(), onSetOff=lambda: tele.stop())

        @app.Business()
        def telemain():
            if not teleSwitch():
                return
            scope = tele.get()
            app.hud.writecontent(np.flip(telescopeimpl.telescopepos), scope)

        app.Hotkey("SwitchTelescope", app.config.HotKey_SwitchTelescope)(
            lambda: teleSwitch.switch()
        )

        mtiIns = telescopeimpl.MTI(app.threadpool)
        mtiSwitch = Switch(onSetOn=lambda: mtiIns.go(), onSetOff=lambda: mtiIns.stop())

        @app.Business()
        def mtiMain():
            if not mtiSwitch():
                return
            view = mtiIns.getResult()
            app.hud.writecontent(np.flip(telescopeimpl.mtiRect[:2]), view)

        app.Hotkey("SwitchTelescopeMti", app.config.HotKey_SwitchTelescopeMti)(
            lambda: mtiSwitch.switch()
        )
