import typing

from utilref import *


@EasyWrapper()
def printWrapperArg(f, essentialArg, optionalArg="default_prompt"):
    def f2():
        print(f'{essentialArg=}, {optionalArg=}')
        f()

    return f2


@EasyWrapper
def myWrapperWithoutParens(f):
    def f2():
        print("in no parens wrapper")
        f()

    return f2


@printWrapperArg("essential")
def realFCalledNoArg():
    print("in realFCalledNoArg")


@printWrapperArg("essential", optionalArg="optional")
def realFCalledWithArg():
    print("in realFCalledWithArg")


@myWrapperWithoutParens()
def FWithMyWrapperWithoutParens():
    print("in FWithMyWrapperWithoutParens")


@myWrapperWithoutParens
def FWithMyWrapperWithoutParensWithoutParens():
    print("in FWithMyWrapperWithoutParensWithoutParens")


realFCalledNoArg()
realFCalledWithArg()
FWithMyWrapperWithoutParens()
FWithMyWrapperWithoutParensWithoutParens()