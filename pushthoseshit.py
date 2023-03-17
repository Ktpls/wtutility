import os
import subprocess
os.chdir(r"C:\file\code\wtutility")
while(True):
    ret=subprocess.run(["git", "pull"])
    print(ret)
    if ret.returncode==0:
        os.system("pause")
        break