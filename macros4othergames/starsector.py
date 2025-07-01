from macroutility import *
import win32clipboard

app = MacroApp(fps=2)
app.BasicHotkey()

def Input(c: str):
    def control_key(key: int):
        return Switch(
            onSetOn=lambda: Keyboard.KeyDown(key),
            onSetOff=lambda: Keyboard.KeyUp(key),
        )

    shift = control_key(win32con.VK_SHIFT)
    for c in c:
        # shift.setTo(ord("A") <= ord(c) <= ord("Z"))
        Keyboard.KeyPress(ord(c))


class Console:
    def __enter__(self):
        with Keyboard.HoldingKey(win32con.VK_CONTROL):
            Keyboard.KeyPress(win32con.VK_BACK)
        return self

    def __exit__(self,*a,**kw):
        Keyboard.KeyPress(win32con.VK_ESCAPE)

    def write(self, cmd: str):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(cmd, win32clipboard.CF_TEXT)
        win32clipboard.CloseClipboard()
        Keyboard.KeyUp(win32con.VK_SHIFT)
        Keyboard.KeyUp(win32con.VK_CONTROL)
        with Keyboard.HoldingKey(win32con.VK_CONTROL):
            Keyboard.KeyPress(ord("V"))
        Keyboard.KeyPress(win32con.VK_RETURN)
        PreciseSleep(0.5)


def WriteConsole(cmd: str):
    with Console() as console:
        console.write(cmd)


@app.Hotkey("FreshStore", [win32con.VK_F5])
@app.Async()
@app.WithHotkeySwitch()
def FreshStore(*a, **kw) -> None:
    app.bulletin.putup(BulletinBoard.Poster("FreshStore"))
    WriteConsole("ForceMarketUpdate")
    mouse.click(0)

@app.Hotkey("GoHome", [win32con.VK_LCONTROL, ord('H')])
@app.Async()
@app.WithHotkeySwitch()
def FreshStore(*a, **kw) -> None:
    app.bulletin.putup(BulletinBoard.Poster("GoHome"))
    WriteConsole("goto penelope's")
    WriteConsole("goto ithaca")


@app.Hotkey("GeneralF4", [win32con.VK_LCONTROL, win32con.VK_F4])
@app.Async()
@app.WithHotkeySwitch()
def GeneralF4(*a, **kw) -> None:
    app.bulletin.putup(BulletinBoard.Poster("GeneralF4"))
    Keyboard.KeyUp(win32con.VK_CONTROL)
    for i in range(2):
        with Console() as console:
            console.write("ForceDeployAll ")
            console.write("Nuke")

@app.Hotkey("SurveyPlanet", [win32con.VK_LCONTROL, ord('S')])
@app.Async()
@app.WithHotkeySwitch()
def SurveyPlanet(*a, **kw) -> None:
    app.bulletin.putup(BulletinBoard.Poster("SurveyPlanet"))
    Keyboard.KeyUp(win32con.VK_CONTROL)
    Keyboard.KeyPress(ord('1'))
    Keyboard.KeyPress(ord('G'))
    Keyboard.KeyPress(ord('G'))
    Keyboard.KeyPress(ord('Q'))
    Keyboard.KeyPress(win32con.VK_ESCAPE)


clickLeft = MousePressRepeater(0, 0.01)


@app.Hotkey("RepClick Left", [win32con.VK_RCONTROL, win32con.VK_RMENU, win32con.VK_F10])
@app.WithHotkeySwitch()
def RepClickLeft(*arg, **kw) -> None:
    clickLeft.autoSwitch()
    app.bulletin.putup(BulletinBoard.Poster("RepClick Left"))


app.go()
