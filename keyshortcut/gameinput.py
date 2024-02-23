import time
import utilitypack.util_windows
import keyshortcut.keycodeWinCode as keycode
import dataclasses
from ctypes import (
    POINTER,
    c_ulong,
    Structure,
    c_ushort,
    c_short,
    c_long,
    byref,
    windll,
    pointer,
    sizeof,
    Union,
)

SendInput = windll.user32.SendInput
PUL = POINTER(c_ulong)


class KeyBdInput(Structure):
    _fields_ = [
        ("wVk", c_ushort),
        ("wScan", c_ushort),
        ("dwFlags", c_ulong),
        ("time", c_ulong),
        ("dwExtraInfo", PUL),
    ]


class HardwareInput(Structure):
    _fields_ = [("uMsg", c_ulong), ("wParamL", c_short), ("wParamH", c_ushort)]


class MouseInput(Structure):
    _fields_ = [
        ("dx", c_long),
        ("dy", c_long),
        ("mouseData", c_ulong),
        ("dwFlags", c_ulong),
        ("time", c_ulong),
        ("dwExtraInfo", PUL),
    ]


class Input_I(Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]


class Input(Structure):
    _fields_ = [("type", c_ulong), ("ii", Input_I)]


# Actuals Functions


def keydown(hexKeyCode):
    extra = c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, pointer(extra))
    x = Input(c_ulong(1), ii_)
    windll.user32.SendInput(1, pointer(x), sizeof(x))


def keyup(hexKeyCode):
    extra = c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, pointer(extra))
    x = Input(c_ulong(1), ii_)
    windll.user32.SendInput(1, pointer(x), sizeof(x))


import pyautogui

# def keydown(keycode):
#     pyautogui.keyDown(keycode)


# def keyup(keycode):
#     pyautogui.keyUp(keycode)


def press(k, interval=0.1):
    keydown(k)
    utilitypack.util_windows.PreciseSleep(interval)
    keyup(k)
    # time.sleep(0.4)


def hold(k, t):
    keydown(k)
    utilitypack.util_windows.PreciseSleep(t)
    keyup(k)


def key_down(k):
    keydown(k)
    utilitypack.util_windows.PreciseSleep(0.1)


def key_up(k):
    keyup(k)
    utilitypack.util_windows.PreciseSleep(0.1)


def key_press(k):
    keydown(k)
    utilitypack.util_windows.PreciseSleep(0.2)
    keyup(k)
    
@dataclasses.dataclass
class HoldingKey:
    key: int
    def __enter__(self):
        keydown(self.key)
    
    def __exit__(self, exc_type, exc_value, traceback):
        keyup(self.key)

def moveto(p):
    windll.user32.SetCursorPos(int(p[0]), int(p[1]))


import win32con


class mouse:
    __downk2f = {
        0: win32con.MOUSEEVENTF_LEFTDOWN,
        1: win32con.MOUSEEVENTF_RIGHTDOWN,
        2: win32con.MOUSEEVENTF_MIDDLEDOWN,
    }
    __upk2f = {
        0: win32con.MOUSEEVENTF_LEFTUP,
        1: win32con.MOUSEEVENTF_RIGHTUP,
        2: win32con.MOUSEEVENTF_MIDDLEUP,
    }

    @staticmethod
    def __callevent(dwflags, x=0, y=0):
        windll.user32.mouse_event(dwflags, x, y, 0, 0)

    @staticmethod
    def down(key):
        mouse.__callevent(mouse.__downk2f[key])

    @staticmethod
    def up(key):
        mouse.__callevent(mouse.__upk2f[key])

    @staticmethod
    def click(key, interval=0.1):
        mouse.down(key)
        utilitypack.util_windows.PreciseSleep(interval)
        mouse.up(key)

    @staticmethod
    def mov(x, y):
        mouse.__callevent(
            win32con.MOUSEEVENTF_MOVE + win32con.MOUSEEVENTF_ABSOLUTE, x, y
        )

    @staticmethod
    def movr(x, y):
        mouse.__callevent(win32con.MOUSEEVENTF_MOVE, x, y)


def mouseup():
    windll.user32.mouse_event(4, 0, 0, 0, 0)


def mousedown():
    windll.user32.mouse_event(2, 0, 0, 0, 0)


def click(p):
    moveto(p)
    time.sleep(0.05)
    mousedown()
    time.sleep(0.01)
    mouseup()
    time.sleep(0.1)
