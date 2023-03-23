import os
import subprocess
import sys
if len(sys.argv)>1:
    os.chdir(sys.argv[1])
while(True):
    ret=subprocess.run(["git", "pull"])
    print(ret)
    if ret.returncode==0:
        os.system("pause")
        break