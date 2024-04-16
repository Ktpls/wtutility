from utilref import *
from afm.autofreshmap_implementation import *


def doOne(i):
    try:
        print(f"doing {i}")
        startpos = i.rfind("\\") + 1
        endpos = i.find(".", startpos)  # -1 on failure
        name = i[startpos:endpos] if endpos != -1 else i[startpos:]
        o = assetpath2realpath(mapname2assetpath(name))

        mml = cv.imread(i)
        mm = cutmap(mml)
        if cv.imwrite(o, mm):
            print(f"done into {o}")
        else:
            print(f"failed {o}")
    except Exception as err:
        print(err)


def main():
    if len(sys.argv) < 2:
        exit()
    i_s = sys.argv[1:]
    [doOne(i) for i in i_s]
    os.system("pause")


main()
