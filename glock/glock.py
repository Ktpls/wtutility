from shared.globalsys import *
from utilitypack.util_app import BulletinApp


class mGlock(WtUtilityModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gl = None

    def load(self):
        from . import glockimpl as glockimpl

        app = self.app

        gl = self.gl = glockimpl.Glock(app.threadpool, glockimpl.g3DutyCycle)

        @app.Business()
        def update():
            gl.update()

        app.HotkeyFullFunction(
            "Glock3",
            glockimpl.Glock.k_glock,
            onKeyDown=lambda: gl.swEnable.on(),
            onKeyUp=lambda: gl.swEnable.off(),
        )

    def unload(self):
        self.gl = None
        return super().unload()
