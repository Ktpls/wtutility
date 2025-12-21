from utilitypack.util_solid import *
from utilitypack.util_np import *
from utilitypack.util_ocv import *
from utilitypack.util_windows import *
from utilitypack.util_app import *
from .globalsys_config import *
from .queue4Bulletin import *
import logging


def init_root_logger(with_bulletin_handler=False):
    root_logger = logging.getLogger()
    root_logger.setLevel(loggingLevel)
    format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    h = logging.StreamHandler()
    h.setFormatter(format)
    root_logger.addHandler(h)

    EnsureDirectoryExists(logFilePath)
    h = logging.FileHandler(
        os.path.join(
            logFilePath, f"{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
        ),
        encoding="utf-8",
    )
    h.setFormatter(format)
    root_logger.addHandler(h)

    if with_bulletin_handler:
        h = BulletinHandler(logging.INFO)
        root_logger.addHandler(h)


@EasyWrapper
@staticmethod
def ExceptionLogged(f, logger: logging.Logger, execType=Exception):
    execType = tuple(NormalizeIterableOrSingleArgToIterable(execType))

    @functools.wraps(f)
    def f2(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseException as err:
            if isinstance(err, execType):
                logger.error(f"{err}\n{traceback.format_exc()}")
            raise err

    return f2


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
    HotKey_SwitchWifi: list[int] | int
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
