from utilitypack.util_solid import *
from utilitypack.util_app import *
from .globalsys_config import *
from .queue4Bulletin import *
import logging


@Singleton
class GSLogger:

    def __init__(self):
        EnsureDirectoryExists(logFilePath)
        # Create a logger
        logger = logging.getLogger(DefaultGlobalSysLoggerName)
        logger.setLevel(loggingLevel)

        # Add the handler to the logger
        bltHdl = BulletinHandler(logging.INFO)
        fileHdl = logging.FileHandler(
            os.path.join(logFilePath, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        )
        fileHdl.setFormatter(logging.Formatter(loggingFormat))
        for h in [
            bltHdl,
            fileHdl,
        ]:
            logger.addHandler(h)

        self.logger = logger

    @EasyWrapper
    @staticmethod
    def ExceptionLogged(f, execType=Exception):
        execType = tuple(NormalizeIterableOrSingleArgToIterable(execType))

        @functools.wraps(f)
        def f2(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except BaseException as err:
                if isinstance(err, execType):
                    GSLogger().logger.exception(err)
                raise err

        return f2


class HotKeyConfig:
    HotKey_PlottingScaleLock = None
    HotKey_DistMeasCali = None
    HotKey_StartCali = None
    HotKey_StopCali = None
    HotKey_SetPlottingScale = None
    HotKey_FreshPlottingScale = None
    HotKey_SwitchTelescope = None
    HotKey_SwitchTelescopeMti = None
    HotKey_HoldLeftAndTell = None
    HotKey_MoveMouse_Direction_Up = None
    HotKey_MoveMouse_Direction_Left = None
    HotKey_MoveMouse_Direction_Down = None
    HotKey_MoveMouse_Direction_Right = None
    HotKey_MoveMouse_AssistKey = None
    HotKey_HoldCAndTell = None
    HotKey_LaunchSeries = None
    HotKey_RefreshWifi = None
    HotKey_EagleEyeDataCollector = None
    HotKey_EagleEyeOnClick = None
    HotKey_Glock = None
    HotKey_EngineManSwitch = None
    HotKey_Reboot = None


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
