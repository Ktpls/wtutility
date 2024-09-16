from utilitypack.util_app import *
from utilitypack.util_winkey import *
from utilitypack.util_wt import *

k_exit = HotkeyManager.Key(win32conComp.VK_F12)
k_glock = HotkeyManager.Key(win32conComp.VK_OEM_3)
fpsm = FpsManager(10)
glockRatio = 0.5
pushSwitch = Switch(
    mlambda("""def (): Keyboard.KeyDown(ord('S'))""", globals(), locals()),
    mlambda("""def (): Keyboard.KeyUp(ord('S'))""", globals(), locals()),
)
while True:
    fpsm.WaitUntilNextFrame()
    if k_exit.GetKeyDown():
        break
    if k_glock.GetKeyDown():
        if InProbability(glockRatio):
            pushSwitch.on()
        else:
            pushSwitch.off()
