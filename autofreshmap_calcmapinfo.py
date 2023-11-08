import os
import sys
from autofreshmap_implementation import *


def nicelyformatarraylike(a):
    return f'[{", ".join([str(i) for i in a])}]'


def main():
    if len(sys.argv) < 2:
        exit()
    try:
        i = sys.argv[1]
        m = cv.imread(i)
        if m.size == 0:
            raise Exception('load img failed in {}'.format(i))

        #spawn
        for c in ['blue', 'red']:
            pos = getMapSpawnCenter(m, c).round().astype('int')
            [print(f'{c} spawn at {nicelyformatarraylike(pos)}')]
        pointmask = cv.imread(assetpath2realpath(
            signName2Path('zonemask')))[:, :, 0]
        
        #zone
        for p in ['A', 'B', 'C','redA', 'redB', 'blueA', 'blueB']:
            temp = cv.imread(assetpath2realpath(signName2Path(p)))
            result = threshedmatchtemplate(m, temp, pointmask,
                                           detectpointsimilarity)
            if result is None:
                print(f'{p} point not detected')
            else:
                print(f'{p} point at {nicelyformatarraylike(result)}')

    except Exception as err:
        print(err)
    finally:
        os.system('pause')


main()