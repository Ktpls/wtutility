from utilitypack.util_app import *
from aio_config import *
import shared.globalsys as globalsys


def main():
    app = BulletinApp(fps=aiofps, hudFps=10)
    modules: list[globalsys.WtUtilityModule] = list()

    # wtdistmeas
    if usingwtdistmeaspy:
        print("wtdistmeaspy activated")
        from wtdmp.wtdistmeaspy import mWtdmp

        modules.append(mWtdmp(app, AioHotKeyConfig))

    # telescope
    if usingtelescope:
        print("telescope activated")
        from telescope.telescope import mTelescope

        modules.append(mTelescope(app, AioHotKeyConfig))

    # key shortcuts
    if usingkeyshortcut:
        print("keyshortcut activated")
        from keyshortcut.keyshortcut import mKeyshortcut

        modules.append(mKeyshortcut(app, AioHotKeyConfig))

    if usingglock:
        print("glock activated")
        from glock.glock import mGlock

        modules.append(mGlock(app, AioHotKeyConfig))

    if usingengineman:
        print("engineman activated")
        from engineman.engineman import mEngineman

        modules.append(mEngineman(app, AioHotKeyConfig))

    def loadModule(m: globalsys.WtUtilityModule):
        try:
            m.load()
        except Exception as e:
            print(f"Module load failed: {m.__class__}")
            print(traceback.format_exc())

    fut = [app.threadpool.submit(functools.partial(loadModule, m)) for m in modules]
    futures.wait(fut)

    @app.Hotkey("Reboot", AioHotKeyConfig.HotKey_Reboot)
    def rebootfoo():
        app.hud.stop()
        bootAsAdmin(__file__)
        Rhythms.Reboot.play()
        fut = [app.threadpool.submit(m.unload) for m in modules]
        futures.wait(fut)
        sys.exit()

    @app.Business()
    def PullBulletinQueueToBulletin():
        msg = globalsys.BulletinQueue().get()
        if msg is not None:
            app.bulletin.putup(msg)

    app.go()


if __name__ == "__main__":
    main()
