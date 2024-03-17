import queue
from utilitypack.util_solid import *
from globalsys_config import *
import logging


@Singleton
class BulletinQueue(queue.Queue):
    def __init__(self) -> None:
        super().__init__(maxsize=queueBulletinMaxSize)


class BulletinHandler(logging.Handler):
    def __init__(self, level):
        super().__init__(level)
        self.setFormatter(logging.Formatter(bulletinLogFormat))

    def emit(self, record):
        # Call the original emit method to write the log record to the file
        msg = self.format(record)
        BulletinQueue().put(msg)


# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a custom file handler
file_handler = BulletinHandler(logging.INFO)

# Create a formatter and add it to the handler
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)

# Logging information
logger.info("This is an informational message")
