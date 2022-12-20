
import os
import sys
from autofreshmap_implementation import *


def main():
    if len(sys.argv)<2:
        exit()
    try:
        i=sys.argv[1]
        m=cv.imread(i)
        if m.size==0:
            raise BaseException('load img failed in {}'.format(i))
        print(f'blue at {getMapSpawnCenter(m,"blue")}')
        print(f'red at {getMapSpawnCenter(m,"red")}')
    except BaseException as err:
        print(err)
    finally:
        os.system('pause')

main()