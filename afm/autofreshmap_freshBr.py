from os import system
from autofreshmap_implementation import *
import traceback


def main():
    try:
        activeWindow(getWTHwnd())
        FreshBr(
            BannedVehicleInfoSourceCode="""
MiG21SMT
Su17M2
MiG21MF
A-10ALate
JaguarGR1A
MirageIII
A-5C
Su-25
"""[
                1:-1
            ],
            WantedVehicleInfoSourceCode="""
G91R
MiG15
F86F
F86A
A4
Me163
F84F
SwiftF
Scimitar
Ki200
J-2
SAAB-105
"""[
                1:-1
            ],
        )
        if waitaftergoodmap:
            os.system("pause")

    except Exception as err:
        traceback.print_exc()
        win32api.Beep(1000, 1000)
        win32api.Beep(500, 1000)
        if throwerrinmain:
            raise err
        system("pause")


main()
