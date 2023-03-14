import os
import subprocess
os.chdir(r"C:\file\code\wfexp")
while(True):
    ret=subprocess.run(["git", "push"])
    print(ret)