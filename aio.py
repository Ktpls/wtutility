from utilitypack.util_app import *
from utilitypack.util_windows import *
from aio_config import *
import shared.globalsys as globalsys

@globalsys.GSBLogger.ExceptionLogged()
def main():
    app = BulletinApp(fps=AioConfig.aiofps, hudFps=AioConfig.hudFps)
    modules: list[globalsys.WtUtilityModule] = list()

    # wtdistmeas
    if AioConfig.usingwtdistmeaspy:
        print("wtdistmeaspy activated")
        from wtdmp.wtdistmeaspy import mWtdmp

        modules.append(mWtdmp(app, AioConfig))

    # telescope
    if AioConfig.usingtelescope:
        print("telescope activated")
        from telescope.telescope import mTelescope

        modules.append(mTelescope(app, AioConfig))

    # key shortcuts
    if AioConfig.usingkeyshortcut:
        print("keyshortcut activated")
        from keyshortcut.keyshortcut import mKeyshortcut

        modules.append(mKeyshortcut(app, AioConfig))

    if AioConfig.usingglock:
        print("glock activated")
        from glock.glock import mGlock

        modules.append(mGlock(app, AioConfig))

    if AioConfig.usingengineman:
        print("engineman activated")
        from engineman.engineman import mEngineman

        modules.append(mEngineman(app, AioConfig))

    def loadModule(m: globalsys.WtUtilityModule):
        try:
            m.load()
        except Exception as e:
            print(f"Module load failed: {m.__class__}")
            print(traceback.format_exc())

    fut = [app.threadpool.submit(functools.partial(loadModule, m)) for m in modules]
    concurrent.futures.wait(fut)

    @app.Hotkey("Reboot", AioConfig.HotKey_Reboot)
    def rebootfoo():
        app.hud.stop()
        bootAsAdmin(__file__)
        Rhythms.Reboot.play()
        fut = [app.threadpool.submit(m.unload) for m in modules]
        concurrent.futures.wait(fut)
        sys.exit()

    @app.Business(globalsys.lowPriorityTaskPeriod)
    def PullBulletinQueueToBulletin():
        msg = globalsys.BulletinQueue().get()
        if msg is not None:
            app.bulletin.putup(msg)

    app.go()


if __name__ == "__main__":
    setadmin(__file__)
    main()
