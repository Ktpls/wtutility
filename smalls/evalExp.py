from utilref import *
import sys

try:
    i = 1
    if sys.argv[i] == "-e":
        i += 1
        exp = sys.argv[i]
    else:
        exp = ReadTextFile(sys.argv[i])
    print(expparser.expparse(exp))
except Exception as err:
    print(err)
os.system("pause")
