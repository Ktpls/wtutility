from macroutility import *


app = MacroApp(fps=2)

app.BasicHotkey()
app.bhhk.bind("Ctrl", win32con.VK_CONTROL)
app.bhhk.bind("Z", ord('Z'))


app.go()
