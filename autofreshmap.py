
from os import system
from autofreshmap_achievement import *
import traceback

def main():
    setadmin(__file__)
    try:
        freshAMap()
    except:
        traceback.print_exc()
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