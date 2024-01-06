from .gameinput import *

from utilitypack import *


def holdMouseLeft():
    mouse.down(0)


def holdC():
    keydown(keycode.key_C)

class MoveMouseDirection(enum.Enum):
    up = 1
    down = 2
    left = 3
    right = 4

def move_mouse(Direction:MoveMouseDirection, MoveDelta=1):
    if Direction == MoveMouseDirection.up:
        mouse.movr(0, -MoveDelta)
    elif Direction == MoveMouseDirection.down:
        mouse.movr(0, MoveDelta)
    elif Direction == MoveMouseDirection.left:
        mouse.movr(-MoveDelta, 0)
    elif Direction == MoveMouseDirection.right:
        mouse.movr(MoveDelta, 0)