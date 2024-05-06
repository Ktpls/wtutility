from utilitypack.util_app import *
from aio_config import *
import shared.globalsys as globalsys
from engineman import engineman
from glock import glock
from keyshortcut import keyshortcut
from telescope import telescope
from wtdmp import wtdistmeaspy


def main():
    app = BulletinApp(fps=aiofps, config=HotKeyConfig)
    modules: list[globalsys.WtUtilityModule] = list()

    # wtdistmeas
    if usingwtdistmeaspy:
        print("wtdistmeaspy activated")
        modules.append(wtdistmeaspy.mWtdmp(app))

    # telescope
    if usingtelescope:
        print("telescope activated")
        modules.append(telescope.mTelescope(app))

    # key shortcuts
    if usingkeyshortcut:
        print("keyshortcut activated")
        modules.append(keyshortcut.mKeyshortcut(app))

    if usingglock:
        print("glock activated")
        modules.append(glock.mGlock(app))

    if usingengineman:
        print("engineman activated")
        modules.append(engineman.mEngineman(app))

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
