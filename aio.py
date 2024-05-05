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
        modules.append(wtdistmeaspy.mWtdmp())

    # telescope
    if usingtelescope:
        print("telescope activated")
        modules.append(telescope.mTelescope())

    # key shortcuts
    if usingkeyshortcut:
        print("keyshortcut activated")
        modules.append(keyshortcut.mKeyshortcut())

    if usingglock:
        print("glock activated")
        modules.append(glock.mGlock())

    if usingengineman:
        print("engineman activated")
        modules.append(engineman.mEngineman())
    for m in modules:
        m.load()

    @app.Hotkey("Reboot", app.config.HotKey_Reboot)
    def rebootfoo():
        app.hud.stop()
        bootAsAdmin(__file__)
        Rhythms.Reboot.play()
        sys.exit()

    @app.Business()
    def PullBulletinQueueToBulletin():
        msg = globalsys.BulletinQueue().get()
        if msg is not None:
            app.bulletin.putup(msg)

    app.go()


if __name__ == "__main__":
    main()
