import enum
import dataclasses
import regex
import typing
import json
from utilref import *


s = ReadTextFile(r"C:\Users\KITA\Desktop\testai.blkx")
d = Blkx.fromText(s).toDict()
j = json.dumps(d, indent=4)
WriteTextFile(r"C:\Users\KITA\Desktop\testai.json", j)
pass
