
import os
import sys
from autofreshmap_achievement import *


def main():
    if len(sys.argv)<2:
        exit()
    try:
        i=sys.argv[1]
        m=cv.imread(i)
        center=getMapSpawnCenter(m)
        print(center)
    except BaseException as err:
        print(err)
    os.system('pause')
main()