import enum
import utilitypack.util_winkey as winkey
from shared.globalsys import HotKeyConfig


class GameMode(enum.Enum):
    arb = 0
    garb = 1
    grb = 2


gm = GameMode.arb


def getByMode(d: dict):
    return d.get(gm, None)


usingwtdistmeaspy = getByMode(
    {GameMode.arb: False, GameMode.garb: False, GameMode.grb: True}
)
usingtelescope = getByMode(
    {GameMode.arb: False, GameMode.garb: True, GameMode.grb: True}
)
usingkeyshortcut = True
usingeagleeye = False
usingglock = getByMode(
    {GameMode.arb: True, GameMode.garb: False, GameMode.grb: False}
)
usingengineman = True

throwErrorInBus = False
throwErrorInHotkey = False

aiofps = 30


class AioHotKeyConfig(HotKeyConfig):
    HotKey_PlottingScaleLock = [ord("L"), winkey.win32conComp.VK_OEM_3]
    HotKey_DistMeasCali = winkey.win32conComp.VK_OEM_3
    HotKey_StartCali = [
        winkey.win32conComp.VK_CONTROL,
        winkey.win32conComp.VK_OEM_3,
    ]
    HotKey_StopCali = [winkey.win32conComp.VK_SHIFT, winkey.win32conComp.VK_OEM_3]
    HotKey_SetPlottingScale = [
        winkey.win32conComp.VK_CONTROL,
        winkey.win32conComp.VK_MENU,
        winkey.win32conComp.VK_OEM_3,
    ]
    HotKey_FreshPlottingScale = [winkey.win32conComp.VK_RSHIFT, ord("L"), winkey.win32conComp.VK_OEM_3]
    HotKey_SwitchTelescope = winkey.win32conComp.VK_F12
    HotKey_SwitchTelescopeMti = [
        winkey.win32conComp.VK_RCONTROL,
        winkey.win32conComp.VK_F12,
    ]
    HotKey_HoldLeftAndTell = winkey.win32conComp.VK_F10
    HotKey_MoveMouse_Direction_Up = winkey.win32conComp.VK_UP
    HotKey_MoveMouse_Direction_Left = winkey.win32conComp.VK_LEFT
    HotKey_MoveMouse_Direction_Down = winkey.win32conComp.VK_DOWN
    HotKey_MoveMouse_Direction_Right = winkey.win32conComp.VK_RIGHT
    HotKey_MoveMouse_AssistKey = winkey.win32conComp.VK_CONTROL
    HotKey_HoldCAndTell = winkey.win32conComp.VK_F11
    HotKey_LaunchSeries = [winkey.win32conComp.VK_RCONTROL, ord("K"), ord("O")]
    HotKey_RefreshWifi = [
        winkey.win32conComp.VK_RCONTROL,
        winkey.win32conComp.VK_RSHIFT,
        ord("K"),
    ]
    HotKey_EagleEyeDataCollector = winkey.win32conComp.VK_F8
    HotKey_EagleEyeOnClick = winkey.win32conComp.VK_LBUTTON
    HotKey_Glock = [winkey.win32conComp.VK_RSHIFT, winkey.win32conComp.VK_F9]
    HotKey_EngineManSwitch = [
        winkey.win32conComp.VK_RCONTROL,
        winkey.win32conComp.VK_RSHIFT,
        winkey.win32conComp.VK_F10,
    ]
    HotKey_Reboot = [
        winkey.win32conComp.VK_CONTROL,
        winkey.win32conComp.VK_SHIFT,
        winkey.win32conComp.VK_F12,
    ]
