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
    result = expparser.expparse(text, var={**expparser.BasicConstantLib},func={**expparser.BasicFunctionLib, 'd':lambda x,y:np.sqrt(x**2+y**2)})
except Exception as err:
    traceback.print_exc()
    result = str(err)
print(result)
os.system("pause")
