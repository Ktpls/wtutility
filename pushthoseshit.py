import os
import subprocess
os.chdir(r".")
while(True):
    ret=subprocess.run(["git", "pull"])
    print(ret)
    if ret.returncode==0:
        os.system("pause")
        break