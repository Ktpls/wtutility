from utilref import *
import sys
import traceback

customVar = {
    "tau": -0.5,
    "k": 3,
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
text = "tau*log(1/(k*tau)+1)"
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
