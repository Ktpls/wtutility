from utilref import *
import sys
import traceback

text = ""
print("input exp:")
while True:
    line = input(">> ")
    if line == "":
        break
    text += line + "\n"
try:
    result = expparser.expparse(text)
except Exception as err:
    traceback.print_exc()
    result = str(err)
print(result)
os.system("pause")
