
from os import system
from autofreshmap_achievement import *


def main():
    setadmin(__file__)
    freshAMap()

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