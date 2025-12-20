from macroutility import *


app = MacroApp(fps=5)


@app.Hotkey("HoldW", [win32conComp.VK_OEM_3])
# @app.WithHotkeySwitch()
def holdRight():
    Keyboard.KeyUp(ord("W"))
    Keyboard.KeyDown(ord("W"))
    app.bulletin.putup(BulletinBoard.Poster("holdW", 1))


app.go()
