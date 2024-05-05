import enum
import keyshortcut.keyshortcut as keyshortcut


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
    {GameMode.arb: True, GameMode.garb: True, GameMode.grb: True}
)
usingkeyshortcut = True
usingeagleeye = False
usingglock = False
usingengineman = True

throwErrorInBus = False
throwErrorInHotkey = False

aiofps = 10


class HotKeyConfig:
    HotKey_PlottingScaleLock = [ord("L"), keyshortcut.win32conComp.VK_OEM_3]
    HotKey_DistMeasCali = keyshortcut.win32conComp.VK_OEM_3
    HotKey_StartCali = [
        keyshortcut.win32conComp.VK_CONTROL,
        keyshortcut.win32conComp.VK_OEM_3,
    ]
    HotKey_StopCali = [keyshortcut.win32conComp.VK_SHIFT, keyshortcut.win32conComp.VK_OEM_3]
    HotKey_SetPlottingScale = [
        keyshortcut.win32conComp.VK_CONTROL,
        keyshortcut.win32conComp.VK_MENU,
        keyshortcut.win32conComp.VK_OEM_3,
    ]
    HotKey_FreshPlottingScale = [ord("L"), ord("K"), keyshortcut.win32conComp.VK_OEM_3]
    HotKey_SwitchTelescope = keyshortcut.win32conComp.VK_F12
    HotKey_SwitchTelescopeMti = [
        keyshortcut.win32conComp.VK_RCONTROL,
        keyshortcut.win32conComp.VK_F12,
    ]
    HotKey_HoldLeftAndTell = keyshortcut.win32conComp.VK_F10
    HotKey_MoveMouse_Direction_Up = keyshortcut.win32conComp.VK_UP
    HotKey_MoveMouse_Direction_Left = keyshortcut.win32conComp.VK_LEFT
    HotKey_MoveMouse_Direction_Down = keyshortcut.win32conComp.VK_DOWN
    HotKey_MoveMouse_Direction_Right = keyshortcut.win32conComp.VK_RIGHT
    HotKey_MoveMouse_AssistKey = keyshortcut.win32conComp.VK_CONTROL
    HotKey_HoldCAndTell = keyshortcut.win32conComp.VK_F11
    HotKey_LaunchSeries = [keyshortcut.win32conComp.VK_RCONTROL, ord("K"), ord("O")]
    HotKey_RefreshWifi = [
        keyshortcut.win32conComp.VK_RCONTROL,
        keyshortcut.win32conComp.VK_RSHIFT,
        ord("K"),
    ]
    HotKey_EagleEyeDataCollector = keyshortcut.win32conComp.VK_F8
    HotKey_EagleEyeOnClick = keyshortcut.win32conComp.VK_LBUTTON
    HotKey_Glock = [keyshortcut.win32conComp.VK_RSHIFT, keyshortcut.win32conComp.VK_F9]
    HotKey_EngineManSwitch = [
        keyshortcut.win32conComp.VK_RCONTROL,
        keyshortcut.win32conComp.VK_RSHIFT,
        keyshortcut.win32conComp.VK_F10,
    ]
    HotKey_Reboot = [
        keyshortcut.win32conComp.VK_CONTROL,
        keyshortcut.win32conComp.VK_SHIFT,
        keyshortcut.win32conComp.VK_F12,
    ]
