from concurrent.futures import ThreadPoolExecutor
import keyshortcut.gameinput as gameinput
from utilitypack.utility import *
from utilitypack.util_app import *
from aio_config import *
import functools
import keyshortcut.keyshortcut as keyshortcut
import shared.globalsys as globalsys


def main():
    app = BulletinApp(fps=aiofps, config=HotKeyConfig)

    # wtdistmeas
    if usingwtdistmeaspy:
        print("wtdistmeaspy activated")

    # telescope
    if usingtelescope:
        print("telescope activated")

    # key shortcuts
    if usingkeyshortcut:
        print("keyshortcut activated")

    if usingglock:
        print("glock activated")

    if usingengineman:
        print("engineman activated")

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
