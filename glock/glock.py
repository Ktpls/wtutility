from shared.globalsys import *


class mGlock(WtUtilityModule):

    def load(self):
        from . import glockimpl as glockimpl

        app = self.app

        gl = glockimpl.GLock()

        @app.Hotkey("Glock", app.config.HotKey_Glock)
        def glSwitchBusiness():
            if gl.isRunning():
                app.bulletin.putup(BulletinBoard.Poster("glock stopping"))
                gl.setOff()
                app.bulletin.putup(BulletinBoard.Poster("glock stopped"))
            else:
                gl.setOn()
                app.bulletin.putup(BulletinBoard.Poster("glock started"))
