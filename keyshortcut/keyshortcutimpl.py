from utilitypack.util_winkey import *
from utilitypack.util_windows import *
from utilitypack.util_solid import *
import enum


def holdMouseLeft():
    mouse.down(0)


def holdC():
    Keyboard.KeyDown(ord("C"))


class MoveMouseDirection(enum.Enum):
    up = 1
    down = 2
    left = 3
    right = 4


def move_mouse(Direction: MoveMouseDirection, MoveDelta=1):
    if Direction == MoveMouseDirection.up:
        mouse.movr(0, -MoveDelta)
    elif Direction == MoveMouseDirection.down:
        mouse.movr(0, MoveDelta)
    elif Direction == MoveMouseDirection.left:
        mouse.movr(-MoveDelta, 0)
    elif Direction == MoveMouseDirection.right:
        mouse.movr(MoveDelta, 0)


def launchSeriesGo(self: StoppableSomewhat):

    interval = 0.1
    num = 29 + 10
    Keyboard.KeyDown(win32con.VK_LCONTROL)
    for i in range(num):
        if self.timeToStop():
            break
        Keyboard.KeyDown(win32con.VK_SPACE)
        PreciseSleep(0.03)
        Keyboard.KeyUp(win32con.VK_SPACE)
        PreciseSleep(interval)
    Keyboard.KeyUp(win32con.VK_LCONTROL)


class StatefulWifiRefresher(WifiRefresher, Switch):
    def __init__(self):
        WifiRefresher.__init__(self)
        Switch.__init__(
            self, onSetOn=self._onSetOn, onSetOff=self._onSetOff, value=True
        )

    def _onSetOn(self):
        WifiRefresher.setOn(self)

    def _onSetOff(self):
        WifiRefresher.setOff(self)
