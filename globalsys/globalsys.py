from utilitypack.utility import *
from .globalsys_config import *
from .queue4Bulletin import *
import logging


@Singleton
class GSLogger:

    def __init__(self):
        # Create a logger
        logger = logging.getLogger()
        logger.setLevel(loggingLevel)

        # Create a custom file handler
        file_handler = BulletinHandler(logging.INFO)

        # Create a formatter and add it to the handler
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)

        # Logging information
        logger.info("This is an informational message")
