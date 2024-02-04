from concurrent.futures import ThreadPoolExecutor
import enum
from time import sleep
import ctypes
import dataclasses
import itertools
import functools
import math
import os
import random
import re
import sys
import threading
import time
import traceback
import typing
import inspect
import multiprocessing
from datetime import datetime
import copy

"""
solid
"""


def DictEq(a: typing.Dict, b: typing.Dict):
    if len(a) != len(b):
        return False
    for k in a.keys():
        if k not in b.keys():
            return False
        if a[k] != b[k]:
            return False
    return True


def ListEq(a: typing.List, b: typing.List):
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True


def deduplicate(l: typing.List):
    return list(set(l))


def flatten(iterable):
    result = []
    for item in iterable:
        if isinstance(item, (list, tuple)):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def digitsof(s: str):
    return "".join(list(filter(str.isdigit, list(s))))


def numinstr(s: str):
    # wont consider negative
    s = digitsof(s)
    return int(s) if len(s) > 0 else 0


def FunctionalWrapper(f: typing.Callable) -> typing.Callable:
    def f2(self, *args, **kwargs):
        f(self, *args, **kwargs)
        return self

    return f2


def UnfinishedWrapper(msg=None) -> typing.Callable[..., typing.Any]:
    if callable(msg):
        # calling without parens, works both on a class and a function
        foo = msg
        return UnfinishedWrapper()(foo)

    default_msg = "Unfinished"
    if msg is None:
        msg = default_msg

    def f2(foo):
        def f3(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            raise NotImplementedError(msg)

        return f3

    return f2


def WrapperAsMyTaste(wrappedLogic=None):
    """
    use like this
        @WrapperAsMyTaste()
        def yourWrapper(f, some_arg_your_wrapper_needs):
            ...
        @yourWrapper(some_arg_your_wrapper_needs)
        def RealFunc(func_arg):
            ...
    or
        @yourWrapper # if no arg for yourWrapper
        def RealFunc(func_arg):
            ...
    note that this is forbiden:
        @yourWrapper(some_callable)
        def RealFunc(func_arg):
            ...
    cuz wrapper is confused with if its processing the wrapped function or callable in arg
    use this instead if wrapper needs another callable more than the one you are wrapping
        @yourWrapper(keyword=some_callable)
        def RealFunc(func_arg):
            ...

    ###############
    note that python design is piece of shlt
    ###############
    """

    def toGetWrapperLogic(wrappedLogic):
        def newWrapper(*arg, **kw):
            def toGetFLogic(fLogic):
                return wrappedLogic(fLogic, *arg, **kw)

            if len(arg) == 1 and isinstance(arg[0], typing.Callable) and len(kw) == 0:
                # calling without parens
                return wrappedLogic(arg[0])
            else:
                return toGetFLogic

        return newWrapper

    if wrappedLogic is None:
        # calling without parens
        return toGetWrapperLogic
    else:
        return toGetWrapperLogic(wrappedLogic)


class logger:
    def __init__(self, path):
        self.path = path
        # wont fail
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.f = open(path, "wb+")

    def log(self, content):
        self.f.write((content + "\n").encode("utf8"))
        # self.f.flush()

    def __del__(self):
        self.f.close()

    def __call__(self, content):
        self.log(content)


def quickSummonCard(inteprob):
    # faster summon using division
    pos = random.random() * inteprob[-1]
    section = [0, len(inteprob)]

    def compare(n):
        # compare pos with section[n]
        if pos > inteprob[n]:
            return 1
        else:  # pos<=section[n]
            if pos > (inteprob[n - 1] if n >= 1 else 0):
                return 0
            else:
                return -1

    while True:
        mid = int((section[1] + section[0]) * 0.5)
        compresult = compare(mid)
        if compresult == 1:
            section[0] = mid + 1
        elif compresult == -1:
            section[1] = mid
        else:  # compresult==0
            return mid


class bulletinBoard:
    @dataclasses.dataclass
    class Poster:
        content: str
        starttime: float
        timeout: float
        overduetime: float

        def __init__(self, content, timeout=10):
            self.content = content
            self.starttime = time.perf_counter()
            self.timeout = timeout
            self.overduetime = time.perf_counter() + timeout

    def __init__(self, idlecontent):
        self.idlecontent = idlecontent
        self.content: typing.List["bulletinBoard.Poster"] = []

    def putup(self, poster: typing.Union[Poster, str]):
        if type(poster) == str:
            poster = bulletinBoard.Poster(poster)
        self.content.append(poster)

    def read(self):
        self.content = [c for c in self.content if c.overduetime > time.perf_counter()]
        rctt = list(range(len(self.content)))
        rctt.reverse()
        if len(self.content):
            return ("\n" + "-" * 10 + "\n").join(
                [self.content[c].content for c in rctt]
            )
        else:
            return self.idlecontent


def AllFileIn(path, includeFileInSubDir=True):
    ret = []
    for dirpath, dir, file in os.walk(path):
        if not includeFileInSubDir and dirpath != path:
            continue
        ret.extend([os.path.join(dirpath, f) for f in file])
    return ret


class StoppableSomewhat:
    class StrategyRunOnRunning(enum.Enum):
        # ignore = 0
        raise_error = 1
        stop_and_rerun = 2
        skip_and_return = 3

    class StrategyError(enum.Enum):
        ignore = 0
        raise_error = 1
        print_error = 2

    def __init__(
        self,
        strategy_runonrunning: "StoppableThread.StrategyRunOnRunning" = None,
        strategy_error: "StoppableThread.StrategyError" = None,
    ):
        self.strategy_runonrunning = (
            strategy_runonrunning
            if strategy_runonrunning is not None
            else StoppableThread.StrategyRunOnRunning.raise_error
        )
        self.strategy_error = (
            strategy_error
            if strategy_error is not None
            else StoppableThread.StrategyError.raise_error
        )

    def foo(self): ...

    def isRunning(self) -> bool: ...

    @FunctionalWrapper
    def go(self, *args, **kwargs): ...

    def stop(self): ...

    def timeToStop(self) -> bool: ...

    @staticmethod
    @WrapperAsMyTaste
    def EasyUse(f, implType=None, **kwStoppableSomewhat):
        """
        wrapper on function, and ready for use
        define function as:
            def f(self:StoppableProcess, [your arg]):
                ...
        so f can know when to stop
        every calling produces an instance
        """
        if implType is None:
            implType = StoppableThread
        if not issubclass(implType, StoppableSomewhat):
            raise NotImplementedError("doesn't work")
        if implType == StoppableProcess:
            raise NotImplementedError("doesn't work")

        class Thread4LongScript(implType):
            def foo(self, *arg, **kw) -> None:
                f(self, *arg, **kw)

        instance: StoppableSomewhat = Thread4LongScript(**kwStoppableSomewhat)

        def newF(*arg, **kw):
            instance.go(*arg, **kw)

        return newF


class StoppableThread(StoppableSomewhat):
    """
    derivate from it and override foo()
    """

    def __init__(
        self,
        strategy_runonrunning: "StoppableSomewhat.StrategyRunOnRunning" = None,
        strategy_error: "StoppableSomewhat.StrategyError" = None,
        pool: ThreadPoolExecutor = None,
    ) -> None:
        super().__init__(strategy_runonrunning, strategy_error)
        self.running: bool = False
        self.stopsignal: bool = True
        self.pool: ThreadPoolExecutor = (
            pool if pool is not None else ThreadPoolExecutor()
        )
        self.submit = None
        self.result = None

    def foo(self, *arg, **kw) -> None:
        raise NotImplementedError("should never run without overriding foo")

    def isRunning(self) -> bool:
        return self.running

    @FunctionalWrapper
    def go(self, *arg, **kw) -> None:
        if self.submit is not None:
            if (
                self.strategy_runonrunning
                == StoppableThread.StrategyRunOnRunning.raise_error
            ):
                raise RuntimeError("already running")
            elif (
                self.strategy_runonrunning
                == StoppableThread.StrategyRunOnRunning.stop_and_rerun
            ):
                self.stop()
            elif (
                self.strategy_runonrunning
                == StoppableThread.StrategyRunOnRunning.skip_and_return
            ):
                return
        self.running = True
        self.stopsignal = False

        def call() -> None:
            """
            wrapper so can call the passed "self"'s foo
            if not, can never know which overwritten foo should be called
            check if self.stopsignal when any place to break
            """
            try:
                self.result = self.foo(*arg, **kw)
            except Exception as e:
                if self.strategy_error == StoppableThread.StrategyError.raise_error:
                    raise e
                elif self.strategy_error == StoppableThread.StrategyError.print_error:
                    traceback.print_exc()
                elif self.strategy_error == StoppableThread.StrategyError.ignore:
                    pass
            self.running = False

        self.submit = self.pool.submit(call)

    @FunctionalWrapper
    def stop(self) -> None:
        if self.submit is None:
            return
        self.stopsignal = True
        self.submit.result()
        self.running = False
        self.submit = None

    def timeToStop(self) -> bool:
        return self.stopsignal


class StoppableProcess(StoppableSomewhat):
    class StoppableOnlyOnceProcess(multiprocessing.Process):
        def __init__(self, sp: "StoppableProcess", args, kwargs) -> None:
            multiprocessing.Process.__init__(self, args=args, kwargs=kwargs)
            self.sp = sp  # read only. cuz cant write

        # override
        def run(self, *args, **kwargs):
            try:
                result = self.sp.foo(*args, **kwargs)
            except Exception as e:
                if self.sp.strategy_error == StoppableThread.StrategyError.raise_error:
                    raise e
                elif (
                    self.sp.strategy_error == StoppableThread.StrategyError.print_error
                ):
                    traceback.print_exc()
                elif self.sp.strategy_error == StoppableThread.StrategyError.ignore:
                    pass
            # cant return result now
            # return result

    def __init__(
        self,
        strategy_runonrunning: "StoppableThread.StrategyRunOnRunning" = None,
        strategy_error: "StoppableThread.StrategyError" = None,
    ):
        StoppableSomewhat.__init__(self, strategy_runonrunning, strategy_error)
        self._stop_event = multiprocessing.Event()
        self.result = None
        self.submit: "StoppableProcess.StoppableOnlyOnceProcess" = None

    def foo(self):
        # This is a placeholder for the method to be overridden by the inherited class
        pass

    def isRunning(self) -> bool:
        return self.submit is not None and self.submit.is_alive()

    @FunctionalWrapper
    def go(self, *args, **kwargs):
        if self.isRunning():
            if (
                self.strategy_runonrunning
                == StoppableThread.StrategyRunOnRunning.raise_error
            ):
                raise RuntimeError("already running")
            elif (
                self.strategy_runonrunning
                == StoppableThread.StrategyRunOnRunning.stop_and_rerun
            ):
                self.stop()
            elif (
                self.strategy_runonrunning
                == StoppableThread.StrategyRunOnRunning.skip_and_return
            ):
                return
        self._stop_event.clear()
        self.submit = self.StoppableOnlyOnceProcess(self, args=args, kwargs=kwargs)
        self.submit.start()

    def stop(self):
        if not self.isRunning():
            return
        self._stop_event.set()
        self.submit.join()
        # self.result=...
        self.submit = None

    def timeToStop(self) -> bool:
        return self._stop_event.is_set()


def ReadFile(path):
    with open(path, "rb") as f:
        return f.read()


def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if len(directory) == 0:
        return
    if not os.path.exists(directory):
        os.makedirs(directory)


def WriteFile(path, content):
    ensure_directory_exists(path)
    with open(path, "wb+") as f:
        f.write(content.encode("utf-8"))


def ReadTextFile(path: str) -> str:
    return ReadFile(path).decode("utf-8")


def WriteTextFile(path: str, text: str):
    WriteFile(path, text.encode("utf-8"))


class Pipe:
    value: typing.Any = None

    def __init__(self, initValue: typing.Any = None, printStep: bool = False) -> None:
        self.printStep = printStep
        self.set(initValue)

    def get(self) -> typing.Any:
        return self.value

    @FunctionalWrapper
    def set(self, val: typing.Any) -> None:
        self.value = val
        if self.printStep:
            print(self.value)

    @FunctionalWrapper
    def do(self, foo: typing.Callable[[typing.Any], typing.Any]) -> "Pipe":
        self.set(foo(self.get()))
        return self

    def __repr__(self) -> str:
        return self.get().__repr__()


class Stream:
    content: list

    def __init__(self, iter: list | tuple | dict) -> None:
        if isinstance(iter, (list, tuple)):
            self.content = iter
        elif isinstance(iter, dict):
            self.content = iter.items()
        else:
            raise TypeError("iter must be list|tuple|dict")

    def sort(self, pred: typing.Callable[[typing.Any, typing.Any], int]):
        self.content.sort(key=functools.cmp_to_key(pred))
        return self

    def peek(self, pred: typing.Callable[[typing.Any], None]):
        for i in self.content:
            pred(i)
        return self
    def filter(self, pred: typing.Callable[[typing.Any], bool]):
        self.content = list(filter(pred, self.content))
        return self

    def map(self, pred: typing.Callable[[typing.Any], typing.Any]):
        self.content = list(map(pred, self.content))
        return self

    def flatMap(self, pred: "typing.Callable[[typing.Any],Stream]"):
        self.content = list(
            itertools.chain.from_iterable([s.content for s in map(pred, self.content)])
        )
        return self

    class Collector:
        def __init__(self, collectImpl):
            self.collectImpl = collectImpl

        def do(self, stream):
            return self.collectImpl(stream)

        @staticmethod
        def toList():
            return Stream.Collector(lambda stream: list(stream.content))

        @staticmethod
        def toDict(keyPred, valuePred):
            return Stream.Collector(
                lambda stream: {keyPred(i): valuePred(i) for i in stream.content}
            )

        @staticmethod
        def groupBy(keyPred):
            return Stream.Collector(
                lambda stream: {
                    key: list(group)
                    for key, group in itertools.groupby(
                        sorted(stream.content, key=keyPred), key=keyPred
                    )
                }
            )

    def collect(self, collector: "Stream.Collector"):
        return collector.do(self)


def GetTimeString():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")


class Progress:
    """
    irreversable!
    """

    def __init__(self, total: float, printPercentageStep: float = 0.1) -> None:
        self.total = total
        self.nowStage = 0
        self.printPercentageStep = printPercentageStep

    def update(self, current: float) -> None:
        while True:
            if current / self.total > self.nowStage * self.printPercentageStep:
                self.nowStage += 1
                print(f"{100 * current / self.total:>3.2f}%", end="\r")
            else:
                break

    def setFinish(self):
        self.update(self.total)


class expparser:
    """
    TODO:
    numlike
        tensor operator
        string operator
        named parameter in function call
            foo(1, 2, 3, a=1, b=2)
        delayed evaluation optimization
    """

    class TokenType(enum.Enum):
        NUMLIKE = 1
        OPR = 2
        BRA = 3
        KET = 4
        EOF = 5
        IDR = 6
        SPACE = 7
        COMMA = 8

    @dataclasses.dataclass(repr=True)
    class Token:
        type: "expparser.TokenType"
        value: typing.Any
        start: int
        end: int

    class __State(enum.Enum):
        START = 1
        NUM = 2
        NEG = 3
        OPR = 4
        END = 5
        IDR = 6

    @dataclasses.dataclass
    class __OprPriorityLeap:
        pos: int
        pribefore: int
        priafter: int

    class NumLikeUnionUtil:
        class NumLikeException(Exception):
            pass

        class NumLikeType(enum.Enum):
            NUM = 0
            STR = 1
            LIST = 2
            BOOL = 3
            NONE = 4

        @staticmethod
        def TypeOf(nl):
            if isinstance(nl, str):
                return expparser.NumLikeUnionUtil.NumLikeType.STR
            elif isinstance(nl, typing.Iterable):
                return expparser.NumLikeUnionUtil.NumLikeType.LIST
            elif isinstance(nl, float):
                return expparser.NumLikeUnionUtil.NumLikeType.NUM
            elif isinstance(nl, bool):
                return expparser.NumLikeUnionUtil.NumLikeType.BOOL
            elif nl is None:
                return expparser.NumLikeUnionUtil.NumLikeType.NONE
            else:
                raise expparser.NumLikeUnionUtil.NumLikeException()

        # imexplicit conversion
        @staticmethod
        def ToNum(nl):
            t = expparser.NumLikeUnionUtil.TypeOf(nl)
            if t == expparser.NumLikeUnionUtil.NumLikeType.NUM:
                return nl
            elif t == expparser.NumLikeUnionUtil.NumLikeType.BOOL:
                return 1.0 if nl else 0.0
            else:
                raise expparser.NumLikeUnionUtil.NumLikeException()

        @staticmethod
        def ToList(nl):
            t = expparser.NumLikeUnionUtil.TypeOf(nl)
            if t == expparser.NumLikeUnionUtil.NumLikeType.LIST:
                return list(nl)
            elif t == expparser.NumLikeUnionUtil.NumLikeType.STR:
                return [nl]
            elif t == expparser.NumLikeUnionUtil.NumLikeType.NUM:
                return [nl]
            elif t == expparser.NumLikeUnionUtil.NumLikeType.BOOL:
                return [nl]
            elif t == expparser.NumLikeUnionUtil.NumLikeType.NONE:
                return [nl]
            else:
                raise expparser.NumLikeUnionUtil.NumLikeException()

        @staticmethod
        def ToBool(nl):
            t = expparser.NumLikeUnionUtil.TypeOf(nl)
            if t == expparser.NumLikeUnionUtil.NumLikeType.NUM:
                return nl > 0
            elif t == expparser.NumLikeUnionUtil.NumLikeType.BOOL:
                return nl
            else:
                raise expparser.NumLikeUnionUtil.NumLikeException()

        @staticmethod
        def ToProperFormFromAny(nl):
            # the adaptor for data to be proper
            # after which there will be no int form, they all stored as float
            # this will deal with more situations, so TypeOf is not proper here
            if isinstance(nl, str):
                return nl
            elif isinstance(nl, typing.Iterable):
                return list(nl)
            elif isinstance(nl, float):
                return nl
            elif isinstance(nl, bool):
                # isinstance(True, int)==True
                return nl
            elif isinstance(nl, int):
                return float(nl)
            elif nl is None:
                return nl
            else:
                raise expparser.NumLikeUnionUtil.NumLikeException()

    class ParseException(Exception):
        pass

    @staticmethod
    def unpackParaArray(f):
        def f2(a):
            if (
                expparser.NumLikeUnionUtil.TypeOf(a)
                == expparser.NumLikeUnionUtil.NumLikeType.LIST
            ):
                return f(*a)
            else:
                return f(a)

        return f2

    @staticmethod
    def CList(a):
        if (
            expparser.NumLikeUnionUtil.TypeOf(a)
            == expparser.NumLikeUnionUtil.NumLikeType.LIST
        ):
            return a
        else:
            return [a]

    class OprException(Exception):
        pass

    class _OprType(enum.Enum):
        UNSPECIFIED = 0
        ADD = 1
        SUB = 2
        MUL = 3
        DIV = 4
        POW = 5
        NEG = 7  # available by manual transfering from sub
        NEQ = 8
        EQ = 9
        GT = 10
        GE = 11
        LT = 12
        LE = 13
        NOT = 14
        AND = 15
        OR = 16
        XOR = 17

        @staticmethod
        def __throw_opr_exception(s):
            raise expparser.OprException(f"bad opr {s}")

        def getPriority(self):
            if self in [
                expparser._OprType.OR,
                expparser._OprType.AND,
                expparser._OprType.XOR,
            ]:
                return 1
            elif self in [
                expparser._OprType.GT,
                expparser._OprType.GE,
                expparser._OprType.LT,
                expparser._OprType.LE,
                expparser._OprType.EQ,
                expparser._OprType.NEQ,
            ]:
                return 2
            elif self in [expparser._OprType.ADD, expparser._OprType.SUB]:
                return 3
            elif self in [expparser._OprType.MUL, expparser._OprType.DIV]:
                return 4
            elif self == expparser._OprType.POW:
                return 5
            elif self in [expparser._OprType.NEG, expparser._OprType.NOT]:
                # unaries
                return 99
            else:
                expparser._OprType.__throw_opr_exception(self)

        @staticmethod
        def fromStr(s):
            dict = {
                "+": expparser._OprType.ADD,
                "-": expparser._OprType.SUB,
                "*": expparser._OprType.MUL,
                "/": expparser._OprType.DIV,
                "^": expparser._OprType.POW,
                "=": expparser._OprType.EQ,
                "!=": expparser._OprType.NEQ,
                ">": expparser._OprType.GT,
                ">=": expparser._OprType.GE,
                "<": expparser._OprType.LT,
                "<=": expparser._OprType.LE,
                "!": expparser._OprType.NOT,
                "&": expparser._OprType.AND,
                "|": expparser._OprType.OR,
                "^^": expparser._OprType.XOR,
            }
            if s not in dict:
                expparser._OprType.__throw_opr_exception(s)
            return dict[s]

        def do(self, arg: typing.List["expparser.Token"]):
            if self == expparser._OprType.ADD:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) + expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.SUB:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) - expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.MUL:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) * expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.DIV:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) / expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.POW:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) ** expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.NEG:
                assert arg[0].type == expparser.TokenType.NUMLIKE
                return -expparser.NumLikeUnionUtil.ToNum(arg[0].value)
            elif self == expparser._OprType.NEQ:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) != expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.EQ:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) == expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.GT:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) > expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.GE:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) >= expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.LT:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) < expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.LE:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToNum(
                    arg[0].value
                ) <= expparser.NumLikeUnionUtil.ToNum(arg[1].value)
            elif self == expparser._OprType.NOT:
                assert arg[0].type == expparser.TokenType.NUMLIKE
                return not expparser.NumLikeUnionUtil.ToBool(arg[0].value)
            elif self == expparser._OprType.AND:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToBool(
                    arg[0].value
                ) and expparser.NumLikeUnionUtil.ToBool(arg[1].value)
            elif self == expparser._OprType.OR:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToBool(
                    arg[0].value
                ) or expparser.NumLikeUnionUtil.ToBool(arg[1].value)
            elif self == expparser._OprType.XOR:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                return expparser.NumLikeUnionUtil.ToBool(
                    arg[0].value
                ) ^ expparser.NumLikeUnionUtil.ToBool(arg[1].value)
            else:
                expparser._OprType.__throw_opr_exception(self)

        def isUnary(self):
            return self in [expparser._OprType.NEG, expparser._OprType.NOT]

    @staticmethod
    def __NextToken(s, i=0):
        @dataclasses.dataclass
        class matcher:
            exp: str
            tokenType: expparser.TokenType

            def tryMatch(self, s, i):
                match = re.match(self.exp, s[i:])
                if not match:
                    return None
                end = match.span()[1] + i
                return expparser.Token(self.tokenType, s[i:end], i, end)

        matcherList = [
            matcher(
                exp=r"^(<=)|(>=)|(\^\^)|(!=)", tokenType=expparser.TokenType.OPR
            ),  # two width operator, match before single widthed ones to get priority
            matcher(
                exp=r"^[*/+\-^=<>&|]", tokenType=expparser.TokenType.OPR
            ),  # single width operator
            matcher(exp=r"^[0-9]+(\.[0-9]+)?", tokenType=expparser.TokenType.NUMLIKE),
            matcher(exp=r'^".*?"', tokenType=expparser.TokenType.NUMLIKE),
            matcher(exp=r"^[A-Za-z_][A-Za-z0-9_]*", tokenType=expparser.TokenType.IDR),
            matcher(exp=r"^\(", tokenType=expparser.TokenType.BRA),
            matcher(exp=r"^\)", tokenType=expparser.TokenType.KET),
            matcher(exp=r"^,", tokenType=expparser.TokenType.COMMA),
            matcher(exp=r"^$", tokenType=expparser.TokenType.EOF),
            matcher(exp=r"^[\s\r\n\t]+", tokenType=expparser.TokenType.SPACE),
        ]

        def getNextToken(s, i):
            for m in matcherList:
                ret = m.tryMatch(s, i)
                if ret:
                    if ret.type == expparser.TokenType.NUMLIKE:
                        # here is only num and str without other numlike types
                        if len(ret.value) >= 2 and ret.value[0] == '"':
                            # hardest case is "the \" string"
                            # its string
                            strstart = ret.start
                            strbuffer = ""
                            while True:
                                if len(ret.value) > 2 and ret.value[-2] == "\\":
                                    # cancel the former " and \, add " back
                                    strbuffer += ret.value[1:-2] + '"'
                                    # move on to the next section
                                    # m == matcher[the str one] now
                                    ret = m.tryMatch(s, ret.end - 1)
                                else:
                                    strbuffer += ret.value[1:-1]
                                    break
                            ret.start = strstart
                            ret.value = strbuffer
                        else:
                            ret.value = float(ret.value)
                    elif ret.type == expparser.TokenType.OPR:
                        ret.value = expparser._OprType.fromStr(ret.value)
                    elif ret.type == expparser.TokenType.SPACE:
                        return getNextToken(s, ret.end)
                    return ret
            raise expparser.ParseException(f"unexpected token at {i}")

        return getNextToken(s, i)

    @dataclasses.dataclass
    class __ExpParserResult:
        val: typing.Any
        end: int
        endedby: "expparser.TokenType"

    @staticmethod
    def __expparse_recursive_comma_collector_wrapped(
        s, varList: typing.Dict, funcList: typing.Dict, i=0
    ):
        nextval = expparser.__expparse_recursive(s, varList, funcList, i)
        if nextval.endedby == expparser.TokenType.COMMA:
            vallist = [nextval.val]
            while True:
                nextval = expparser.__expparse_recursive(
                    s, varList, funcList, nextval.end
                )
                vallist.append(nextval.val)
                if nextval.endedby != expparser.TokenType.COMMA:
                    break
            retval = vallist
        else:
            retval = nextval.val
        return expparser.__ExpParserResult(
            val=retval, end=nextval.end, endedby=nextval.endedby
        )

    @staticmethod
    def __expparse_recursive(
        s,
        varList: typing.Dict,
        funcList: typing.Dict,
        startPos=0,
    ):
        # fsm fields
        state = expparser.__State.START
        token: expparser.Token = None
        # never modify peekToken
        peekToken = expparser.__NextToken(s, startPos)

        # buffer
        tokenList: typing.List[expparser.Token] = list()
        commaList = list()

        # for operator priority
        oprRisingBeginPosList: typing.List[expparser.__OprPriorityLeap] = list()

        def RaiseTokenException(token: expparser.Token):
            raise expparser.ParseException(
                f'unexpected {token.type}("{token.value}") at {token.start}'
            )

        def ClearOprSectionAssumingPeer(begin, end):
            nonlocal tokenList, oprRisingBeginPosList
            # cache the section to use easily pop and push
            section = tokenList[begin:end]
            while True:
                if len(section) == 1:
                    break
                val2 = section.pop()
                opr = section.pop()
                assert opr.type == expparser.TokenType.OPR
                if opr.value.isUnary():
                    val2.value = opr.value.do(arg=[val2])
                    section.append(val2)
                else:
                    val1 = section.pop()
                    val1.value = opr.value.do(arg=[val1, val2])
                    section.append(val1)
            tokenList = tokenList[:begin] + section + tokenList[end:]
            RemapToken()
            oprRisingBeginPosList.pop()

        def AddNewVirtualTokenValuedByCalculation(
            subresult: expparser.__ExpParserResult,
        ):
            nonlocal token, peekToken, state, tokenList
            tokenList.append(
                expparser.Token(
                    expparser.TokenType.NUMLIKE,
                    subresult.val,
                    token.start,
                    subresult.end,
                )
            )
            RemapToken()
            peekToken = expparser.__NextToken(s, subresult.end)

        def DealWithBra():
            nonlocal token, peekToken, state, tokenList
            if peekToken.type == expparser.TokenType.KET:
                """
                a no para call bracket pair
                cant parse with recursive function, which expects a value
                """
                subresult = expparser.__ExpParserResult(
                    [], peekToken.end, expparser.TokenType.KET
                )
            else:
                subresult = expparser.__expparse_recursive_comma_collector_wrapped(
                    s, varList, funcList, token.end
                )
            tokenList.pop()  # remove the bra
            AddNewVirtualTokenValuedByCalculation(subresult)
            state = expparser.__State.NUM

        def DealWithIdentifier():
            nonlocal token, peekToken, state, tokenList
            if peekToken.type == expparser.TokenType.BRA:
                # its a call
                fooName = token.value
                assert fooName in funcList
                # manually move on
                MoveForwardToNextToken()
                DealWithBra()
                para = tokenList[-1].value
                if (
                    expparser.NumLikeUnionUtil.TypeOf(para)
                    == expparser.NumLikeUnionUtil.NumLikeType.LIST
                ):
                    value = funcList[fooName](*para)
                else:
                    value = funcList[fooName](para)
                tokenList[-1].value = expparser.NumLikeUnionUtil.ToProperFormFromAny(
                    value
                )
                tokenList = tokenList[:-2] + tokenList[-1:]  # remove the func name
                RemapToken()
            else:
                # its a var
                assert token.value in varList
                # overwrite the identifier with num
                token.value = expparser.NumLikeUnionUtil.ToProperFormFromAny(
                    varList[token.value]
                )
                token.type = expparser.TokenType.NUMLIKE
            state = expparser.__State.NUM

        def MoveForwardToNextToken():
            nonlocal token, peekToken, tokenList
            token = peekToken
            peekToken = expparser.__NextToken(s, token.end)
            tokenList.append(token)
            # RemapToken() # not essential here
            # modifying token also applies on tokenList[-1]

        def RemapToken():
            nonlocal tokenList, token
            # reset token to last of token list after modifying tokenList structure
            if len(tokenList) != 0:
                token = tokenList[-1]
            else:
                # calling any member on this will cause exception
                token = None

        def doWhenReadNewOpr():
            nonlocal state, oprRisingBeginPosList, token, tokenList
            state = expparser.__State.OPR
            lastOprPrior = (
                oprRisingBeginPosList[-1].priafter
                if len(oprRisingBeginPosList) > 0
                else 0
            )
            opr = token.value.getPriority()
            if opr > lastOprPrior:
                oprRisingBeginPosList.append(
                    expparser.__OprPriorityLeap(len(tokenList) - 1, lastOprPrior, opr)
                )  # len(tokenList) - 1 for opr
            elif opr < lastOprPrior:
                while True:
                    lastOprPrior = (
                        oprRisingBeginPosList[-1].priafter
                        if len(oprRisingBeginPosList) > 0
                        else 0
                    )
                    if opr >= lastOprPrior:
                        break
                        # clear since last rising, until flat
                        # len(tokenList)-1 since the lowering opr has been appended
                    """
                    for unary, the token before first opr is unwanted to calc
                    for binary, its necessary
                    """
                    ClearOprSectionAssumingPeer(
                        (
                            oprRisingBeginPosList[-1].pos
                            if tokenList[oprRisingBeginPosList[-1].pos].value.isUnary()
                            else oprRisingBeginPosList[-1].pos - 1
                        ),
                        len(tokenList) - 1,  # the new opr
                    )
                if opr > lastOprPrior:
                    # new opr is the new rising
                    oprRisingBeginPosList.append(
                        expparser.__OprPriorityLeap(
                            len(tokenList) - 1,
                            lastOprPrior,
                            opr,
                        )
                    )

        def dealWithExpressionEndSign():
            nonlocal state, oprRisingBeginPosList, token, tokenList
            expendpos = token.end
            endtype = token.type
            tokenList.pop()  # remove the eof or ket or comma, end sign anyway
            RemapToken()
            if len(tokenList) == 0:
                # empty
                val = None
            else:
                # clear all
                while True:
                    if len(oprRisingBeginPosList) == 0:
                        break
                    ClearOprSectionAssumingPeer(
                        (
                            oprRisingBeginPosList[-1].pos
                            if tokenList[oprRisingBeginPosList[-1].pos].value.isUnary()
                            else oprRisingBeginPosList[-1].pos - 1
                        ),
                        len(tokenList),
                    )
                val = tokenList[-1].value
            return expparser.__ExpParserResult(val, expendpos, endtype)

        # the fsm illustrated in notebook
        while True:
            MoveForwardToNextToken()
            if state == expparser.__State.START or state == expparser.__State.OPR:
                # expecting numlike, but possible to meet bra, identifier, or unary operator, eof, comma, ket
                if token.type == expparser.TokenType.BRA:
                    DealWithBra()
                elif token.type == expparser.TokenType.NUMLIKE:
                    state = expparser.__State.NUM
                elif token.type == expparser.TokenType.IDR:
                    DealWithIdentifier()
                elif token.type == expparser.TokenType.OPR:
                    # maybe unary operator
                    if token.value == expparser._OprType.SUB:
                        # to neg
                        tokenList[-1].value = expparser._OprType.NEG
                    if not token.value.isUnary():
                        RaiseTokenException(token)
                    doWhenReadNewOpr()
                elif token.type in [
                    expparser.TokenType.EOF,
                    expparser.TokenType.KET,
                    expparser.TokenType.COMMA,
                ]:
                    # return
                    state = expparser.__State.END
                    return dealWithExpressionEndSign()
                else:
                    RaiseTokenException(token)
            elif state == expparser.__State.NUM:
                if token.type == expparser.TokenType.OPR:
                    doWhenReadNewOpr()
                elif token.type in [
                    expparser.TokenType.EOF,
                    expparser.TokenType.KET,
                    expparser.TokenType.COMMA,
                ]:
                    # return
                    state = expparser.__State.END
                    return dealWithExpressionEndSign()
                else:
                    RaiseTokenException(token)
            elif state == expparser.__State.END:
                RaiseTokenException(token)

    @staticmethod
    def elementparse(s):
        i = 0
        tokenList: typing.List[expparser.Token] = []
        while True:
            token = expparser.__NextToken(s, i)
            tokenList.append(token)
            i = token.end
            if token.type == expparser.TokenType.EOF:
                break
        var = []
        func = []
        for i, tk in enumerate(tokenList):
            if tk.type == expparser.TokenType.IDR:
                # peek
                # wont index overflow cuz there is eof and eof is not identifier
                if tokenList[i + 1].type == expparser.TokenType.BRA:
                    func.append(tk.value)
                else:
                    var.append(tk.value)
        return var, func

    @staticmethod
    def expparse(s, var={}, func={}):
        return expparser.__expparse_recursive_comma_collector_wrapped(s, var, func).val

    class Utils:
        class NonOptionalException(Exception):
            pass

        class NonOptional:
            @staticmethod
            def checkParamListIfNonOptional(paramList):
                for i, p in enumerate(paramList):
                    if isinstance(p, expparser.Utils.NonOptional):
                        raise expparser.Utils.NonOptionalException(
                            f"Nonoptional parameter {i} unspecified"
                        )
                return paramList

        @staticmethod
        def OptionalFunc(defaultParam: typing.List, func: typing.Callable):
            def newFunc(*param):
                newParam = [
                    a if a is not None else d for a, d in zip(param, defaultParam)
                ]
                if len(param) < len(defaultParam):
                    newParam.extend(defaultParam[len(param) :])
                expparser.Utils.NonOptional.checkParamListIfNonOptional(newParam)
                return func(*newParam)

            return newFunc

    BasicFunctionLib = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        "exp": math.exp,
        "log": math.log,
        "sqrt": math.sqrt,
        "abs": abs,
        "sign": lambda x: 1 if x > 0 else -1 if x < 0 else 0,
        "floor": math.floor,
        "ceil": math.ceil,
        "neg": lambda x: -x,
        "iif": lambda cond, x, y: x if expparser.NumLikeUnionUtil.ToBool(cond) else y,
        "eq": lambda x, y, ep=0.001: abs(x - y) < ep,
        "StrEq": lambda x, y: x == y,
        "CStr": str,
        "CNum": float,
        "CBool": bool,
        "CList": CList,
    }

    BasicConstantLib = {
        "e": math.e,
        "pi": math.pi,
        "true": True,
        "false": False,
        "none": None,
    }


def sleepuntil(con: typing.Callable, dt=None, sleepImpl=None):
    if sleepImpl is None:
        sleepImpl = time.sleep
    if dt is None:
        dt = 0.025
    while not con():
        sleepImpl(dt)


class perf_statistic:
    """
    calculate the time past between start() to now, directly by perf_counter()-starttime
    record all accumulated time before start(), but uncleared after stop()
    so start and stop are also playing roles as resume and pause
    countcycle() will increase the cycle count, helping to calculate average time in a loop-like task
    clear() will clear all accumulated time, stops counting
    """

    def __init__(self, startnow=False):
        self.clear()
        if startnow:
            self.start()

    @FunctionalWrapper
    def clear(self):
        self._starttime = None
        self._stagedtime = 0
        self._cycle = 0

    @FunctionalWrapper
    def start(self):
        self._starttime = time.perf_counter()

    @FunctionalWrapper
    def countcycle(self):
        self._cycle += 1

    @FunctionalWrapper
    def stop(self):
        if self._starttime is None:
            return
        self._stagedtime += self._timeCurrentlyCounting()
        self._starttime = None

    def time(self):
        return self._stagedtime + self._timeCurrentlyCounting()

    def aveTime(self):
        return self.time() / (self._cycle if self._cycle > 0 else 1)

    def _timeCurrentlyCounting(self):
        return (
            time.perf_counter() - self._starttime if self._starttime is not None else 0
        )


class fpsmanager:
    def __init__(self, fps=60):
        self.lt = time.perf_counter()
        self.frametime = 1 / fps

    def WaitUntilNextFrame(self, sleepImpl=None):
        sleepuntil(
            lambda: time.perf_counter() - self.lt > self.frametime,
            dt=0.5 * self.frametime,
            sleepImpl=sleepImpl,
        )
        self.SetToNextFrame()

    def CheckIfTimeToDoNextFrame(self) -> bool:
        """
        usage
        if fpsmanager.CheckIfTimeToDoNextFrame():
            fpsmanager.SetToNextFrame()
            do your task here
        used in doing stuff peroidically, but in another loop with different peroid
        so have to check if it is time to do it
        """
        result = time.perf_counter() - self.lt > self.frametime
        return result

    def SetToNextFrame(self):
        self.lt = time.perf_counter()


def longDelay(t, interval=0.5):
    round = math.ceil(t / interval)
    for i in range(round):
        time.sleep(interval)


def CostlySleep(t):
    endtime = time.perf_counter() + t
    while True:
        if time.perf_counter() >= endtime:
            break


def PreciseSleep(t):
    # to stop oscilation in autoCali due to sleep() precise
    # to my suprise time.sleep() is quite precise
    if t > 0.0005773010000120849:
        # too rough
        sleep(t)
    else:
        CostlySleep(t)


def longDelay(t, interval=0.5):
    round = math.ceil(t / interval)
    for i in range(round):
        time.sleep(interval)


def WrapperOfMultiLineText(s):
    """
        to process text like this
        var=WrapperOfMultilLineText(${threeQuotes}
    your
    multiline
    content
    here
    ${threeQuotes})
    """
    return s[1:-1]


@dataclasses.dataclass
class PIDController:
    @dataclasses.dataclass
    class AnalizerFrameData:
        partp: float
        parti: float
        partd: float
        error: float
        integral: float
        derivative: float

    kp: float
    ki: float
    kd: float
    integralLimitMin: float = None
    integralLimitMax: float = None
    analizerMode: bool = False
    last_error: float = dataclasses.field(default=0, init=False)
    integral: float = dataclasses.field(default=0, init=False)

    def update(self, error, dt=1):
        self.integral += error * dt
        if self.integralLimitMax is not None and self.integral > self.integralLimitMax:
            self.integral = self.integralLimitMax
        if self.integralLimitMin is not None and self.integral < self.integralLimitMin:
            self.integral = self.integralLimitMin
        derivative = (error - self.last_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.last_error = error
        if self.analizerMode:
            return output, self.AnalizerFrameData(
                partp=self.kp * error,
                parti=self.ki * self.integral,
                partd=self.kd * derivative,
                error=error,
                integral=self.integral,
                derivative=derivative,
            )
        else:
            return output


class OneOrderLinearFilter:
    def __init__(self, N, initial_val=None):
        self.a = N / (N + 1)
        self.b = 1 / (N + 1)
        self.previous_output = initial_val if initial_val else 0

    def update(self, input_sample):
        output_sample = self.a * self.previous_output + self.b * input_sample
        self.previous_output = output_sample
        return output_sample


class Stage:
    def step(self, dt):
        raise NotImplementedError("")

    t = property(fget=lambda self: None)


class SyncExecutableManager:
    def __init__(self, pool: ThreadPoolExecutor) -> None:
        self.pool = pool
        self.selist: typing.List[SyncExecutable] = []

    def step(self):
        # call this on wolf update
        # make sure set running before submitting. or would be possibly kicked out here
        self.selist = [
            e for e in self.selist if e.state != SyncExecutable.STATE.stopped
        ]
        for se in self.selist:
            se.cond.acquire(True)
            if se.state == SyncExecutable.STATE.suspended:
                # knowing not satisfied, skip waking up
                if se.waitWhat():
                    se.cond.notify_all()
                    se.cond.wait()
            else:
                se.cond.notify_all()
                se.cond.wait()
            se.cond.release()

    def submit(self, se: "SyncExecutable", foo: typing.Callable):
        self.selist.append(se)
        return self.pool.submit(foo)


class SyncExecutable:
    # for impl serialized but sync mechanization in async foo
    # stage is something with t readable
    class STATE(enum.Enum):
        stopped = 0
        running = 1
        suspended = 2

    def __init__(
        self, stage: Stage, sem: SyncExecutableManager, raiseOnErr=True
    ) -> None:
        self.stage = stage
        self.sem = sem
        self.cond = threading.Condition()
        self.state = self.STATE.stopped
        self.future = None
        self.raiseOnErr = raiseOnErr
        self.waitWhat = None

    # override
    def main(self, **arg):
        raise BaseException("not implemented")

    def run(self, **arg):
        def foo():
            self.cond.acquire(True)
            try:
                self.main(**arg)
            except BaseException as e:
                if self.raiseOnErr:
                    traceback.print_exc()
                    raise e
                else:
                    traceback.print_exc()
            self.state = self.STATE.stopped
            self.cond.notify_all()  # no more sleep, aks sem to get up
            self.cond.release()

        if not self.isworking():
            self.state = self.STATE.running
            self.future = self.sem.submit(self, foo)
        return self

    # available in main
    def sleepUntil(self, untilWhat, timeout=None):
        overduetime = self.stage.t + timeout if timeout else None

        def untilWhatOrTimeOut():
            return untilWhat() or (overduetime and self.stage.t >= overduetime)

        # give right of check to manager, so can i save cost of thread switching
        self.waitWhat = untilWhatOrTimeOut
        self.state = self.STATE.suspended
        while True:
            """
            do this in main thread so cancelling thread switching cost
            """
            if untilWhatOrTimeOut():
                break
            # register
            self.cond.notify_all()
            self.cond.wait()
        self.waitWhat = None
        self.state = self.STATE.running

    # available in main
    def delay(self, delaytime):
        self.sleepUntil(lambda: False, delaytime)

    # available in main
    def stepOneFrame(self):
        self.cond.notify_all()
        self.cond.wait()

    def isworking(self):
        return self.state != self.STATE.stopped


class AccessibleQueue:
    Annotation = lambda T: typing.List[T]

    class AQException(Exception):
        pass

    def __init__(self, maxsize=1):
        self._maxsize = maxsize
        self._cursize = 0
        self._sptr = 0
        self._eptr = 0
        self._q = [None] * maxsize

    def push(self, val):
        if self.isFull():
            raise AccessibleQueue.AQException("queue full")
        self._q[self._eptr] = val
        self._eptr += 1
        self._eptr %= self._maxsize
        self._cursize += 1

    def pop(self):
        if self.isEmpty():
            raise AccessibleQueue.AQException("queue empty")
        val = self._q[self._sptr]
        self._sptr += 1
        self._sptr %= self._maxsize
        self._cursize -= 1
        return val

    def push__pop_if_full(self, val):
        if self.isFull():
            self.pop()
        self.push(val)

    def resize(self, newsize):
        if newsize < self._cursize:
            raise AccessibleQueue.AQException("newsize too small")
        # guess resizing list will realloc anyway
        l2 = list([None] * newsize)
        for i in range(self._cursize):
            l2[i] = self[i]
        self._q = l2

        self._maxsize = newsize

    def __indexMapping(self, i):
        if i < 0:
            i = self._cursize + i
        return (i + self._sptr) % self._maxsize

    def __len__(self):
        return self._cursize

    def isFull(self):
        return self._cursize == self._maxsize

    def isEmpty(self):
        return self._cursize == 0

    def __getitem__(self, i: int | slice):
        if isinstance(i, int):
            if i >= self._cursize:
                raise AccessibleQueue.AQException("index out of range")
            return self._q[self.__indexMapping(i)]
        elif isinstance(i, slice):
            return [
                self[j]
                for j in range(
                    i.start if i.start is not None else 0,
                    i.stop if i.stop is not None else self._cursize,
                    i.step if i.step is not None else 1,
                )
            ]

    def ToList(self):
        return [self[i] for i in range(len(self))]


IdentityMapping = lambda x: x


class BeanUtil:
    @dataclasses.dataclass
    class Option:
        ignoreNoneInSrc: bool = True

    """
    have to deal with dict, object, and class(only on dest)
    """

    @staticmethod
    def __GetEmptyInstance(cls):
        return cls()

    @staticmethod
    def __FieldConversionFunc(obj, field):
        return obj.__annotations__.get(field, IdentityMapping)

    @staticmethod
    def __GetterOf(obj):
        if isinstance(obj, dict):
            return lambda: obj.items()
        return lambda: obj.__dict__.items()

    @staticmethod
    def __SetterOf(obj):
        if isinstance(obj, dict):

            def DictSetter(obj, k, v):
                if k in obj:
                    obj[k] = v

            return DictSetter

        def ObjSetter(obj, k, v):
            if k in obj.__dict__:
                obj.__setattr__(k, BeanUtil.__FieldConversionFunc(obj, k)(v))

        return ObjSetter

    @staticmethod
    def __DictOrObj2DictOrObjCopy(src: object, dst: object, option: "BeanUtil.Option"):
        Getter = BeanUtil.__GetterOf(src)
        Setter = BeanUtil.__SetterOf(dst)
        for k, v in Getter():
            if option.ignoreNoneInSrc and v is None:
                continue
            Setter(dst, k, v)

    @staticmethod
    def __DictOrObj2ClassCopy(
        src: object, dst: typing.Callable, option: "BeanUtil.Option"
    ):
        dstobj = BeanUtil.__GetEmptyInstance(dst)
        BeanUtil.__DictOrObj2DictOrObjCopy(src, dstobj, option)
        return dstobj

    @staticmethod
    def BeanCopy(src, dst: object, option: "BeanUtil.Option" = Option()):
        if inspect.isclass(dst):
            return BeanUtil.__DictOrObj2ClassCopy(src, dst, option)
        else:
            BeanUtil.__DictOrObj2DictOrObjCopy(src, dst, option)


@WrapperAsMyTaste
def AllOptionalInit(clz):
    oldInit = clz.__init__
    kws = [k for k in oldInit.__annotations__.keys() if k != "return"]

    def initNone(self, **kwargs):
        nonlocal oldInit, kws
        for k in kws:
            if k not in kwargs:
                kwargs[k] = None
        oldInit(self, **kwargs)

    clz.__init__ = initNone
    return clz


class Container:
    __content = None

    def get(self):
        return self.__content

    def set(self, newContent):
        self.__content = newContent

    def isEmpty(self):
        return self.__content is None


class Switch:
    def __init__(self, initial=False):
        self.__value = initial

    def on(self):
        self.__value = True

    def off(self):
        self.__value = False

    def switch(self):
        self.__value = not self.__value

    def __call__(self) -> bool:
        return self.__value


def inProbability(p: float) -> bool:
    return random.random() < p


def flipCoin() -> bool:
    return inProbability(0.5)
