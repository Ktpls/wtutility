import os
import subprocess
import sys
import time
if len(sys.argv)>1:
    os.chdir(sys.argv[1])
def insistCalling(cmd):
    while(True):
        ret=subprocess.run(cmd)
        print(ret)
        if ret.returncode==0:
            break
        time.sleep(1)

insistCalling(["git", "pull"])
print("pull done")

insistCalling(["git", "push"])
print("push done")

os.system('pause')