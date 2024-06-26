from shared.globalsys import *


class mKeyshortcut(WtUtilityModule):

    def load(self):
        from . import keyshortcutimpl as keyshortcutimpl

        app = self.app
        @app.Hotkey("HoldLeftAndTell", app.config.HotKey_HoldLeftAndTell)
        def holdLeftAndTell():
            keyshortcutimpl.holdMouseLeft()
            app.bulletin.putup(BulletinBoard.Poster("LeftHolding", 1))

        @app.Hotkey("HoldCAndTell", app.config.HotKey_HoldCAndTell)
        def holdCAndTell():
            keyshortcutimpl.holdC()
            app.bulletin.putup(BulletinBoard.Poster("CHolding", 1))

        @app.Hotkey("LaunchSeries", app.config.HotKey_LaunchSeries)
        @app.Async()
        def launchSeriesGo(self: StoppableSomewhat):
            app.bulletin.putup("launching series")
            keyshortcutimpl.launchSeriesGo(self)
            app.bulletin.putup(f"launch done")

        @app.Hotkey("RefreshWifi", app.config.HotKey_RefreshWifi)
        @app.Async()
        def refreshWifi(self: StoppableSomewhat):
            app.bulletin.putup("refreshing wifi")
            wifi = WifiRefresher()
            wifi.setOff()
            time.sleep(1)
            wifi.setOn()
            app.bulletin.putup(f"refresh done")

        for key, dire, name in [
            [
                app.config.HotKey_MoveMouse_Direction_Up,
                keyshortcutimpl.MoveMouseDirection.up,
                "Up",
            ],
            [
                app.config.HotKey_MoveMouse_Direction_Left,
                keyshortcutimpl.MoveMouseDirection.left,
                "Left",
            ],
            [
                app.config.HotKey_MoveMouse_Direction_Down,
                keyshortcutimpl.MoveMouseDirection.down,
                "Down",
            ],
            [
                app.config.HotKey_MoveMouse_Direction_Right,
                keyshortcutimpl.MoveMouseDirection.right,
                "Right",
            ],
        ]:
            app.Hotkey(
                f"MoveMouse{name}",
                ArrayFlatten([app.config.HotKey_MoveMouse_AssistKey, key]),
                continiousPress=True,
            )(functools.partial(keyshortcutimpl.move_mouse, dire))
