from utilref import *
import sys
import traceback

customVar = {
    "y": 1e9,
}
customFunc = {
    "d": lambda x, y: np.sqrt(x**2 + y**2),
}

text = ""
print("input exp:")
while True:
    line = input(">> ")
    if line == "":
        break
    text += line + "\n"
text = "(1-6*y)/3"
try:
    result = expparser.expparse(
        text,
        var={**expparser.BasicConstantLib, **customVar},
        func={**expparser.BasicFunctionLib, **customFunc},
    )
except Exception as err:
    traceback.print_exc()
    result = str(err)
print(result)
os.system("pause")
