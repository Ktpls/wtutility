import traceback
import re


def FixIndent(s, indentContent='    ', indentNum=1):
    mtc = list(re.finditer('^', s, re.MULTILINE))
    if len(mtc) == 0:
        return s
    reped = ''
    for i in range(len(mtc)):
        reped += s[mtc[i - 1].end() if i != 0 else 0:mtc[i].start(
        )] + indentContent * indentNum
    reped += s[mtc[-1].end():]
    return reped




foostr = '''
setRet(fooextra(123))
'''

def indented():
    try:
        # def foo():
        #     #just for grammar check
        #     pass
        def fooextra(para):
            return para + 1
        a=1
        def setRet(val):
            nonlocal a
            a=val
        lcls=locals()
        exec(foostr)
        print(a)
    except:
        traceback.print_exc()

indented()