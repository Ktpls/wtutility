from macroutility import *

app = MacroApp(fps=2)


for nk, rk in zip([win32con.VK_F1], [win32con.VK_NUMPAD1]):

    @app.Hotkey("Numpad", [win32con.VK_LCONTROL, win32con.VK_LMENU, nk])
    @app.WithHotkeySwitch()
    def _(*arg, **kw) -> None:
        app.bulletin.putup(BulletinBoard.Poster("Numpad"))
        Keyboard.KeyPress(rk)


app.go()
