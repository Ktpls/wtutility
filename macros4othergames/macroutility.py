
import sys
sys.path.append('..')
from utility import fpsmanager,hotkeymanager,deduplicate
from gameinput import *
from time import sleep
import traceback



def mainloop(fps,hotkeyactionlist):
    fps = fpsmanager(fps)
    #main loop
    hkm = hotkeymanager(hotkeyactionlist)
    
    while (True):
        fps.next()
        keystate = hkm.getkeys()
        try:
            [hka.foo() for hka in hotkeyactionlist if hotkeymanager.iskeycalling(hka.key, keystate)]
        except BaseException as e:
            traceback.print_exc()