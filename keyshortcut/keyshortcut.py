from shared.globalsys import *
from utilitypack.util_winkey import *

class mKeyshortcut(WtUtilityModule):

    def load(self):
        from . import keyshortcutimpl as keyshortcutimpl

        app = self.app

        @app.Hotkey("HoldLeftAndTell", self.keyConfig.HotKey_HoldLeftAndTell)
        def holdLeftAndTell():
            keyshortcutimpl.holdMouseLeft()
            app.bulletin.putup(BulletinBoard.Poster("LeftHolding", 1))

        @app.Hotkey("HoldCAndTell", self.keyConfig.HotKey_HoldCAndTell)
        def holdCAndTell():
            keyshortcutimpl.holdC()
            app.bulletin.putup(BulletinBoard.Poster("CHolding", 1))

        @app.Hotkey("LaunchSeries", self.keyConfig.HotKey_LaunchSeries)
        @app.Async()
        def launchSeriesGo(self: StoppableSomewhat):
            app.bulletin.putup("launching series")
            keyshortcutimpl.launchSeriesGo(self)
            app.bulletin.putup(f"launch done")

        @app.Hotkey("RefreshWifi", self.keyConfig.HotKey_RefreshWifi)
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
                self.keyConfig.HotKey_MoveMouse_Direction_Up,
                keyshortcutimpl.MoveMouseDirection.up,
                "Up",
            ],
            [
                self.keyConfig.HotKey_MoveMouse_Direction_Left,
                keyshortcutimpl.MoveMouseDirection.left,
                "Left",
            ],
            [
                self.keyConfig.HotKey_MoveMouse_Direction_Down,
                keyshortcutimpl.MoveMouseDirection.down,
                "Down",
            ],
            [
                self.keyConfig.HotKey_MoveMouse_Direction_Right,
                keyshortcutimpl.MoveMouseDirection.right,
                "Right",
            ],
        ]:
            app.HotkeyFullFunction(
                f"MoveMouse{name}",
                ArrayFlatten([self.keyConfig.HotKey_MoveMouse_AssistKey, key]),
                onKeyPress=functools.partial(keyshortcutimpl.move_mouse, dire)
            )
