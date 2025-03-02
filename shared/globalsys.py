from utilitypack.util_solid import *
from utilitypack.util_app import *
from .globalsys_config import *
from .queue4Bulletin import *
import logging


@Singleton
class GSLoggerBulletin(GSLogger):

    def __init__(self):
        GSLogger.__init__(self)

        bltHdl = BulletinHandler(logging.INFO)
        self.logger.addHandler(bltHdl)


# extend with bulletin support
GSLogger = GSLoggerBulletin


class HotKeyConfig:
    HotKey_PlottingScaleLock: list[int] | int
    HotKey_DistMeasCali: list[int] | int
    HotKey_StartCali: list[int] | int
    HotKey_StopCali: list[int] | int
    HotKey_SetPlottingScale: list[int] | int
    HotKey_FreshPlottingScale: list[int] | int
    HotKey_SwitchTelescope: list[int] | int
    HotKey_SwitchTelescopeMti: list[int] | int
    HotKey_HoldLeftAndTell: list[int] | int
    HotKey_MoveMouse_Direction_Up: list[int] | int
    HotKey_MoveMouse_Direction_Left: list[int] | int
    HotKey_MoveMouse_Direction_Down: list[int] | int
    HotKey_MoveMouse_Direction_Right: list[int] | int
    HotKey_MoveMouse_AssistKey: list[int] | int
    HotKey_HoldCAndTell: list[int] | int
    HotKey_LaunchSeries: list[int] | int
    HotKey_RefreshWifi: list[int] | int
    HotKey_EagleEyeDataCollector: list[int] | int
    HotKey_EagleEyeOnClick: list[int] | int
    HotKey_Glock: list[int] | int
    HotKey_EngineManSwitch: list[int] | int
    HotKey_Reboot: list[int] | int


class WtUtilityModule:
    def __init__(self, app: BulletinApp, keyConfig: HotKeyConfig = None):
        self.app = app
        self.keyConfig = keyConfig

    def load(self):
        pass

    def unload(self):
        pass

    @staticmethod
    def RegisterModule(module):
        if not hasattr(WtUtilityModule, "__modules__"):
            WtUtilityModule.__modules__ = list()
        WtUtilityModule.__modules__.append(module)
        return module
