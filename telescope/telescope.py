from .telescope_implementation import *
class telescope:
    def __init__(self) -> None:
        self.enabled=False
    def seton(self):
        self.enabled=True
    def setoff(self):
        self.enabled=False
    def mainlooplogic(self):
        return gettelescopeview() if self.enabled else None
