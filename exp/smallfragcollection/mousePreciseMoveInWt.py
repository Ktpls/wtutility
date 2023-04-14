import pyautogui
import time
import win32api
from utilref import *
import gameinput
def move_mouse(Direction,MoveDelta):
    if Direction == "up":
        gameinput.mouse.movr(0, -MoveDelta)
    elif Direction == "down":
        gameinput.mouse.movr(0, MoveDelta)
    elif Direction == "left":
        gameinput.mouse.movr(-MoveDelta, 0)
    elif Direction == "right":
        gameinput.mouse.movr(MoveDelta, 0)
for i in range(3):
    time.sleep(1)
    win32api.Beep((i+1)*500,100)
for i in range(100):
    move_mouse("left",1)
    time.sleep(0.1)