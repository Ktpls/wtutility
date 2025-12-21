import queue
from utilitypack.util_solid import *
from .globalsys_config import *
import logging


@Singleton
class BulletinQueue(queue.Queue):
    def __init__(self) -> None:
        super().__init__(maxsize=queueBulletinMaxSize)

    def get(self):
        if not super().empty():
            try:
                return super().get(False)
            except queue.Empty:
                return None
        return None

    def put(self, msg):
        super().put(msg)


class BulletinHandler(logging.Handler):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.setFormatter(logging.Formatter(bulletinLogFormat))

    def emit(self, record):
        msg = self.format(record)
        BulletinQueue().put(msg)
