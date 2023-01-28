
from os import system
from autofreshmap_implementation import *
import traceback

def main():
    setadmin(__file__)
    try:
        
        activeWindow(getWTHwnd())
        mouse.mov(*(0,0))
        freshAMap()
    except BaseException as err:
        traceback.print_exc()
        win32api.Beep(1000,1000)
        win32api.Beep(500,1000)
        if throwerrinmain:
            raise err
        else:
            system('pause')
        
    #testOneRaw()
    #addCutNewMap('Normandy')
    #setonwifi()
    # outputMapSpawnPointCenter(r".\asset\autofreshmap\map\Poland.png")
    
    #system('pause')

def test():
    activeWindow(getWTHwnd())
    sleep(1)
    press(keycode.key_Enter)

main()











