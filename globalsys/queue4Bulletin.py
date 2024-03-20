import queue
from utilitypack.util_solid import *
from .globalsys_config import *
import logging


@Singleton
class BulletinQueue(queue.Queue):
    def __init__(self) -> None:
        super().__init__(maxsize=queueBulletinMaxSize)

    def get(self):
        try:
            return super().get(False)
        except queue.Empty:
            return None

    def put(self, msg):
        super().put(msg)


class BulletinHandler(logging.Handler):
    def __init__(self, level):
        super().__init__(level)
        self.setFormatter(logging.Formatter(bulletinLogFormat))

    def emit(self, record):
        msg = self.format(record)
        BulletinQueue().put(msg)
