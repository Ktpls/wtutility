from utilitypack.util_solid import *
from .globalsys_config import *
from .queue4Bulletin import *
import logging


@Singleton
class GSLogger:

    def __init__(self):
        # Create a logger
        logger = logging.getLogger(globalSysLoggerName)
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
