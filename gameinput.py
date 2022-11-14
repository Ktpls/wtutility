import time

import keycode
from ctypes import POINTER, c_ulong, Structure, c_ushort, c_short, c_long, byref, windll, pointer, sizeof, Union

SendInput = windll.user32.SendInput
PUL = POINTER(c_ulong)


class KeyBdInput(Structure):
    _fields_ = [("wVk", c_ushort), ("wScan", c_ushort), ("dwFlags", c_ulong),
                ("time", c_ulong), ("dwExtraInfo", PUL)]


class HardwareInput(Structure):
    _fields_ = [("uMsg", c_ulong), ("wParamL", c_short), ("wParamH", c_ushort)]


class MouseInput(Structure):
    _fields_ = [("dx", c_long), ("dy", c_long), ("mouseData", c_ulong),
                ("dwFlags", c_ulong), ("time", c_ulong), ("dwExtraInfo", PUL)]


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

def press(k):
    keydown(k)
    time.sleep(0.1)
    keyup(k)
    time.sleep(0.4)

def hold(k, t):
    keydown(k)
    time.sleep(t)
    keyup(k)
    time.sleep(0.5)


def key_down(k):
    keydown(k)
    time.sleep(0.1)


def key_up(k):
    keyup(k)
    time.sleep(0.1)


def wtpress(k):
    keydown(k)
    time.sleep(0.2)
    keyup(k)
    time.sleep(2)

def moveto(p):
    windll.user32.SetCursorPos(int(p[0]), int(p[1]))

def click(p):
    moveto(p)
    time.sleep(0.05)
    windll.user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.01)
    windll.user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.1)