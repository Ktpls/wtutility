
from os import system
from autofreshmap_implementation import *
import traceback


def main():
    
    try:
        
        activeWindow(getWTHwnd())
        FreshBr()
        if waitaftergoodmap:
            os.system('pause')
    except Exception as err:
        traceback.print_exc()
        win32api.Beep(1000,1000)
        win32api.Beep(500,1000)
        if throwerrinmain:
            raise err
        system('pause')

# main()


