"""
wanted
any wrapper, decorated with @WrapperAsMyTaste, can deal with
    @wrapper
    def f():
        ...
and
    @wrapper(...)
    def f():
        ...
easily

..or consider to forbid this kind of usage
    @wrapper
    def f():
        ...


piece of shlt, abandoned now
"""
import typing

from utilref import *
def WrapperAsMyTaste():
    """
    use like this
        @WrapperAsMyTaste()
        def myWrapper(f, some_arg_your_wrapper_needs):
            ...
        @myWrapper([arg_for_wrapper])
        def RealFunc(func_arg):
            ...
    note that this is forbiden:
        @myWrapper
        def RealFunc(func_arg):
            ...
    use if no arg for myWrapper
        @myWrapper()
        def RealFunc(func_arg):
            ...
    """

    def toGetWrapperLogic(wrapperLogic):
        def newWrapper(*arg, **kw):
            def toGetFLogic(fLogic):
                return wrapperLogic(fLogic, *arg, **kw)

            return toGetFLogic

        return newWrapper

    return toGetWrapperLogic


@WrapperAsMyTaste()
def myWrapper(f, essentialArg, optionalArg="default_prompt"):
    def f2():
        print(essentialArg, optionalArg)
        f()

    return f2


@myWrapper('essential')
def realFCalledNoArg():
    print("in realFCalledNoArg")


@myWrapper('essential', optionalArg='optional')
def realFCalledWithArg():
    print("in realFCalledWithArg")


realFCalledNoArg()
realFCalledWithArg()
