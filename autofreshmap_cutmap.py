
import os
import sys
from autofreshmap_achievement import *


def main():
    if len(sys.argv)<2:
        exit()
    try:
        i=sys.argv[1]
        startpos=i.rfind('\\')+1
        endpos=i.find('.',startpos) #-1 on failure
        name=i[startpos:endpos] if endpos!=-1 else i[startpos:]
        o=mapname2path(name)
        
        pointlt=np.array(standardMapLeftTopPoint)
        pointrd=pointlt+[648,648]
        mml=cv.imread(i)
        mm=mml[pointlt[1]:pointrd[1],pointlt[0]:pointrd[0]]
        cv.imwrite(o,mm)
        
        print('done into {}'.format(o))
    except BaseException as err:
        print(err)
    os.system('pause')
main()