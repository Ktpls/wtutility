from shared.globalsys import *
from utilitypack.util_app import BulletinApp


class mGlockG1(WtUtilityModule):
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


class mGlockG2(WtUtilityModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gl = None

    def load(self):
        from . import glockimpl as glockimpl

        app = self.app

        gl = self.gl = glockimpl.Glock2(glockimpl.g2Ratio, glockimpl.g2DutyCycle)

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

#G3
class mGlockG3(mGlockG2):
    def load(self):
        from . import glockimpl as glockimpl

        app = self.app

        gl = self.gl = glockimpl.Glock3(
            glockimpl.g2Ratio, app.threadpool, glockimpl.g3DutyCycle
        )

        @app.Business()
        def update():
            gl.update()

        app.HotkeyFullFunction(
            "Glock3",
            glockimpl.Glock3.k_glock,
            onKeyDown=lambda: gl.swEnable.on(),
            onKeyUp=lambda: gl.swEnable.off(),
        )

mGlock=mGlockG3