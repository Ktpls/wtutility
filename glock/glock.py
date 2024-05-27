from shared.globalsys import *
from utilitypack.util_app import BulletinApp


class mGlock(WtUtilityModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gl = None

    def load(self):
        from . import glockimpl as glockimpl

        app = self.app

        self.gl = gl = glockimpl.GLock()

        @app.Hotkey("Glock", app.config.HotKey_Glock)
        def glSwitchBusiness():
            if gl.isRunning():
                app.bulletin.putup(BulletinBoard.Poster("glock stopping"))
                gl.setOff()
                app.bulletin.putup(BulletinBoard.Poster("glock stopped"))
            else:
                gl.setOn()
                app.bulletin.putup(BulletinBoard.Poster("glock started"))

    def unload(self):
        if self.gl:
            self.gl.setOff()
        return super().unload()
