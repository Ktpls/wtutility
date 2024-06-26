from utilitypack.util_app import *
from aio_config import *
import shared.globalsys as globalsys


def main():
    app = BulletinApp(fps=aiofps, config=HotKeyConfig, hudFps=1)
    modules: list[globalsys.WtUtilityModule] = list()

    # wtdistmeas
    if usingwtdistmeaspy:
        print("wtdistmeaspy activated")
        from wtdmp.wtdistmeaspy import mWtdmp

        modules.append(mWtdmp(app))

    # telescope
    if usingtelescope:
        print("telescope activated")
        from telescope.telescope import mTelescope

        modules.append(mTelescope(app))

    # key shortcuts
    if usingkeyshortcut:
        print("keyshortcut activated")
        from keyshortcut.keyshortcut import mKeyshortcut

        modules.append(mKeyshortcut(app))

    if usingglock:
        print("glock activated")
        from glock.glock import mGlock

        modules.append(mGlock(app))

    if usingengineman:
        print("engineman activated")
        from engineman.engineman import mEngineman

        modules.append(mEngineman(app))

    futures = [app.threadpool.submit(m.load) for m in modules]
    [f.result() for f in futures]

    @app.Hotkey("Reboot", app.config.HotKey_Reboot)
    def rebootfoo():
        app.hud.stop()
        bootAsAdmin(__file__)
        Rhythms.Reboot.play()
        futures = [app.threadpool.submit(m.unload) for m in modules]
        [f.result() for f in futures]
        sys.exit()

    @app.Business()
    def PullBulletinQueueToBulletin():
        msg = globalsys.BulletinQueue().get()
        if msg is not None:
            app.bulletin.putup(msg)

    app.go()


if __name__ == "__main__":
    main()
