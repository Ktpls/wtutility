from shared.globalsys import *
from utilitypack.util_app import BulletinApp


class mTelescope(WtUtilityModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mtiIns = None

    def load(self):
        from . import telescopeimpl as telescopeimpl

        app = self.app

        tele = telescopeimpl.Telescope(app.threadpool)
        regionTele = app.hud.addRegion(fullScrHUD.Region(telescopeimpl.telescopepos))

        def teleSwitchOff():
            tele.stop()
            regionTele.content = None

        teleSwitch = Switch(onSetOn=lambda: tele.go(), onSetOff=teleSwitchOff)

        @app.Business(period=1 / telescopeimpl.telescopeFps)
        def telemain():
            if not teleSwitch():
                return
            regionTele.content = tele.get()

        app.Hotkey("SwitchTelescope", app.config.HotKey_SwitchTelescope)(
            lambda: teleSwitch.switch()
        )

        self.mtiIns = mtiIns = telescopeimpl.MTI(app.threadpool)
        regionMti = app.hud.addRegion(fullScrHUD.Region(telescopeimpl.mtiRect[:2]))

        def teleMtiOff():
            mtiIns.stop()
            regionMti.content = None

        mtiSwitch = Switch(onSetOn=lambda: mtiIns.go(), onSetOff=teleMtiOff)

        @app.Business(period=1 / telescopeimpl.mtiFps)
        def mtiMain():
            if not mtiSwitch():
                return
            regionMti.content = mtiIns.getResult()

        app.Hotkey("SwitchTelescopeMti", app.config.HotKey_SwitchTelescopeMti)(
            lambda: mtiSwitch.switch()
        )

    def unload(self):
        if self.mtiIns:
            self.mtiIns.stop()
        return super().unload()
