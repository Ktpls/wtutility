from utilref import *
import sys

text = ""
print("input exp:")
while True:
    line = input(">> ")
    if line == "":
        break
    text += line + "\n"
print(expparser.expparse(text))
os.system("pause")
