from shared.globalsys import *


class mEngineman(WtUtilityModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.em = None

    def load(self):
        from . import enginemanimpl as enginemanimpl

        app = self.app

        self.em = em = enginemanimpl.DetachedEngineMan(pool=app.threadpool)

        def on():
            em.go()
            app.bulletin.putup(BulletinBoard.Poster("engineman started"))

        def off():
            em.stop()
            app.bulletin.putup(BulletinBoard.Poster("engineman stopped"))

        emSwitch = Switch(onSetOn=on, onSetOff=off)

        @app.Hotkey("EngineManSwitch", app.config.HotKey_EngineManSwitch)
        def emSwitchBusiness():
            emSwitch.switch()
