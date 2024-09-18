from shared.globalsys import *
from utilitypack.util_app import BulletinApp


class mGlock_Old(WtUtilityModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gl = None

    def load(self):
        from . import glockimpl as glockimpl

        app = self.app

        self.gl = gl = glockimpl.GLock()

        @app.Hotkey("Glock", self.keyConfig.HotKey_Glock)
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


class mGlock(WtUtilityModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gl = None

    def load(self):
        from . import glockimpl as glockimpl

        app = self.app

        gl = self.gl = glockimpl.Glock2(glockimpl.g2_ratio, glockimpl.g2_dutyCycle)

        @app.Business()
        def update():
            gl.update()

        app.HotkeyFullFunction(
            "Glock2",
            glockimpl.Glock2.k_glock,
            onKeyDown=lambda: gl.swEnable.on(),
            onKeyUp=lambda: gl.swEnable.off(),
        )

    def unload(self):
        if self.gl:
            self.gl.swEnable.off()
        self.gl = None
        return super().unload()
