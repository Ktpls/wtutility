
from utilref import fpsmanager,hotkeymanager,deduplicate
from gameinput import *
from time import sleep
import traceback



def mainloop(fps,hotkeyactionlist):
    fps = fpsmanager(fps)
    #main loop
    hkm = hotkeymanager(hotkeyactionlist)
    
    while (True):
        fps.next()
        hkm.doAllDecidedKey(hkm.decideAllHotKey())