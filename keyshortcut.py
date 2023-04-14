from gameinput import *

from utilitypack import *


def holdMouseLeft():
    mouse.down(0)


def holdC():
    keydown(keycode.key_C)


def move_mouse(Direction, MoveDelta=1):
    if Direction == "up":
        mouse.movr(0, -MoveDelta)
    elif Direction == "down":
        mouse.movr(0, MoveDelta)
    elif Direction == "left":
        mouse.movr(-MoveDelta, 0)
    elif Direction == "right":
        mouse.movr(MoveDelta, 0)