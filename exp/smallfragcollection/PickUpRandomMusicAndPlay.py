import subprocess
from utilref import *
import numpy as np



musicPath = r"C:\CloudMusic"
player=r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"

files = AllFileIn(musicPath)
f = files[np.random.choice(len(files))]
print(f)
subprocess.call([player, f])