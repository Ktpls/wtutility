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
        execType = NormalizeIterableOrSingleArgToIterable(execType)

        @functools.wraps(f)
        def f2(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except BaseException as err:
                for e in execType:
                    if isinstance(err, e):
                        GSLogger().logger.exception(err)
                        break
                raise err
        return f2


class WtUtilityModule:
    def __init__(self, app: BulletinApp):
        self.app = app

    def load(self):
        pass

    def unload():
        pass

    @staticmethod
    def RegisterModule(module):
        if not hasattr(WtUtilityModule, "__modules__"):
            WtUtilityModule.__modules__ = list()
        WtUtilityModule.__modules__.append(module)
        return module
