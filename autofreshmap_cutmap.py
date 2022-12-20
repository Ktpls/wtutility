
import os
import sys
from autofreshmap_implementation import *


def doOne(i):
    try:
        print(f'doing {i}')
        startpos=i.rfind('\\')+1
        endpos=i.find('.',startpos) #-1 on failure
        name=i[startpos:endpos] if endpos!=-1 else i[startpos:]
        o=assetpath2realpath(mapname2assetpath(name))
        
        pointlt=np.array(standardMapLeftTopPoint)
        pointrd=pointlt+[648,648]
        mml=cv.imread(i)
        mm=mml[pointlt[1]:pointrd[1],pointlt[0]:pointrd[0]]
        ret=cv.imwrite(o,mm)
        
        print(f'done into {o}')
        print(f'result is {ret}')
    except BaseException as err:
        print(err)

def main():
    if len(sys.argv)<2:
        exit()
    i_s=sys.argv[1:]
    [doOne(i) for i in i_s]
    os.system('pause')
main()