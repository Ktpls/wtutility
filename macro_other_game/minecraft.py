from macroutility import *


app = MacroApp(fps=2)

app.BasicHotkey()
app.bind_hold_mouse_left()
app.bhhk.bind_cleanning()
app.bhhk.bind("W", ord("W"))
app.bhhk.bind("Ctrl", win32con.VK_CONTROL)
app.bhhk.bind("Space", win32con.VK_SPACE)
app.bhhk.bind("Shift", win32con.VK_SHIFT)

@app.Hotkey("HoldRight", [win32con.VK_RCONTROL, win32con.VK_RSHIFT, win32con.VK_F10])
@app.WithHotkeySwitch()
def holdRight():
    mouse.down(1)
    app.bulletin.putup(BulletinBoard.Poster("holdRight", 1))


@app.Hotkey("JumpHorse", [win32con.VK_CONTROL, ord("J")])
@app.Async()
@app.WithHotkeySwitch()
def bestJumpOnHorse(*arg, **kw) -> None:
    app.bulletin.putup(BulletinBoard.Poster("going", 1))
    Keyboard.KeyDown(win32con.VK_SPACE)
    PreciseSleep(0.55)
    Keyboard.KeyUp(win32con.VK_SPACE)


@app.Hotkey("TakeOff", [win32con.VK_CONTROL, ord("G")])
@app.Async()
@app.WithHotkeySwitch()
def takeOff(*arg, **kw) -> None:
    Keyboard.KeyPress(win32con.VK_SPACE)
    PreciseSleep(0.25)
    Keyboard.KeyPress(win32con.VK_SPACE)
    PreciseSleep(0.05)
    mouse.click(1)
    app.bulletin.putup(BulletinBoard.Poster("takeOff"))


app.go()
