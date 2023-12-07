from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import enum
from time import sleep
from typing import Dict, List, Callable, Iterable, Any
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


def FunctionalWrapper(f: Callable[..., Any]) -> Callable[..., Any]:
    def f2(self, *args: Any, **kwargs: Any) -> Any:
        f(self, *args, **kwargs)
        return self

    return f2


def UnfinishedWrapper(msg=None) -> Callable[..., Any]:
    if callable(msg):
        # calling without parens, works both on a class and a function
        foo = msg
        return UnfinishedWrapper()(foo)

    default_msg = "Unfinished"
    if msg is None:
        msg = default_msg

    def f2(foo):
        def f3(*args: Any, **kwargs: Any) -> Any:
            raise NotImplementedError(msg)

        return f3

    return f2


class logger:
    def __init__(self, path):
        self.path = path
        # wont fail
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.f = open(path, "wb+")

    @FunctionalWrapper
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

    @FunctionalWrapper
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


class StoppableThread:
    """
    derivate from it and override foo()
    """

    class BehaviorOnTryingRuningWhenRunning(enum.Enum):
        # ignore = 0
        raise_error = 1
        stop_and_rerun = 2
        skip_and_return = 3

    class StrategyOnError(enum.Enum):
        ignore = 0
        raise_error = 1
        print_error = 2

    def __init__(
        self,
        behavior_run_on_running: "StoppableThread.BehaviorOnTryingRuningWhenRunning" = BehaviorOnTryingRuningWhenRunning.raise_error,
        strategy_on_error: "StoppableThread.StrategyOnError" = StrategyOnError.raise_error,
        pool: ThreadPoolExecutor = None,
    ) -> None:
        self.running: bool = False
        self.stopsignal: bool = True
        self.pool: ThreadPoolExecutor = (
            pool if pool is not None else ThreadPoolExecutor()
        )
        self.submit = None
        self.result = None
        self.behavior_run_on_running = behavior_run_on_running
        self.strategy_on_error = strategy_on_error

    def foo(self, *arg, **kw) -> None:
        raise NotImplementedError("should never run without overriding foo")

    def getRunning(self) -> bool:
        return self.running

    @FunctionalWrapper
    def go(self, *arg, **kw) -> None:
        if self.submit is not None:
            if (
                self.behavior_run_on_running
                == StoppableThread.BehaviorOnTryingRuningWhenRunning.raise_error
            ):
                raise RuntimeError("already running")
            elif (
                self.behavior_run_on_running
                == StoppableThread.BehaviorOnTryingRuningWhenRunning.stop_and_rerun
            ):
                self.stop()
            elif (
                self.behavior_run_on_running
                == StoppableThread.BehaviorOnTryingRuningWhenRunning.skip_and_return
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
                if (
                    self.strategy_on_error
                    == StoppableThread.StrategyOnError.raise_error
                ):
                    raise e
                elif (
                    self.strategy_on_error
                    == StoppableThread.StrategyOnError.print_error
                ):
                    traceback.print_exc()
                elif self.strategy_on_error == StoppableThread.StrategyOnError.ignore:
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

    def ifTimeToStop(self) -> bool:
        return self.stopsignal


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
    value: Any = None

    def __init__(self, initValue: Any = None, printStep: bool = False) -> None:
        self.printStep = printStep
        self.set(initValue)

    def get(self) -> Any:
        return self.value

    @FunctionalWrapper
    def set(self, val: Any) -> None:
        self.value = val
        if self.printStep:
            print(self.value)

    @FunctionalWrapper
    def do(self, foo: Callable[[Any], Any]) -> "Pipe":
        self.set(foo(self.get()))
        return self

    def __repr__(self) -> str:
        return self.get().__repr__()


def GetTimeString():
    return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())


class expparser:
    """
    TODO:
    numlike
        tensor support
        string support
        considering impl operator on those types
    """

    class TokenType(enum.Enum):
        NUMLIKE = 1
        OPR = 2
        BRA = 3
        KET = 4
        EOF = 5
        IDR = 6

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

    BasicFunctionLib = {
        "sin": unpackParaArray(math.sin),
        "cos": unpackParaArray(math.cos),
        "tan": unpackParaArray(math.tan),
        "asin": unpackParaArray(math.asin),
        "acos": unpackParaArray(math.acos),
        "atan": unpackParaArray(math.atan),
        "atan2": unpackParaArray(math.atan2),
        "exp": unpackParaArray(math.exp),
        "log": unpackParaArray(math.log),
        "sqrt": unpackParaArray(math.sqrt),
        "abs": unpackParaArray(abs),
        "sign": unpackParaArray(lambda x: 1 if x > 0 else -1 if x < 0 else 0),
        "floor": unpackParaArray(math.floor),
        "ceil": unpackParaArray(math.ceil),
        "neg": unpackParaArray(lambda x: -x),
        "iif": unpackParaArray(
            lambda cond, x, y: x if expparser.NumLikeUnionUtil.ToBool(cond) else y
        ),
        "eq": unpackParaArray(lambda x, y, ep=0.001: abs(x - y) < ep),
        "streq": unpackParaArray(lambda x, y: x == y),
        "array": lambda a: a,
        "CStr": unpackParaArray(str),
        "CNum": unpackParaArray(float),
        "CBool": unpackParaArray(bool),
        "CList": unpackParaArray(CList),
        "WrapSingle": lambda a: [a],
    }
    BasicConstantLib = {"e": math.e, "pi": math.pi, "true": True, "false": False}

    class OprException(Exception):
        pass

    class _OprType(enum.Enum):
        UNSPECIFIED = 0
        ADD = 1
        SUB = 2
        MUL = 3
        DIV = 4
        POW = 5
        COMMA = 6
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
            if self == expparser._OprType.COMMA:
                return 1
            elif self in [
                expparser._OprType.OR,
                expparser._OprType.AND,
                expparser._OprType.XOR,
            ]:
                return 2
            elif self in [
                expparser._OprType.GT,
                expparser._OprType.GE,
                expparser._OprType.LT,
                expparser._OprType.LE,
                expparser._OprType.EQ,
                expparser._OprType.NEQ,
            ]:
                return 3
            elif self in [expparser._OprType.ADD, expparser._OprType.SUB]:
                return 4
            elif self in [expparser._OprType.MUL, expparser._OprType.DIV]:
                return 5
            elif self == expparser._OprType.POW:
                return 6
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
                ",": expparser._OprType.COMMA,
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

        def do(self, arg: typing.List["expparser.Token"], serial=0):
            # take several tokens and return numlike
            if self == expparser._OprType.COMMA:
                assert (
                    arg[0].type == expparser.TokenType.NUMLIKE
                    and arg[1].type == expparser.TokenType.NUMLIKE
                )
                # comma behaves differently with serial==0 and serial==other
                if serial == 0:
                    return [arg[0].value] + [arg[1].value]
                else:
                    return expparser.NumLikeUnionUtil.ToList(arg[0].value) + [
                        arg[1].value
                    ]
            elif self == expparser._OprType.ADD:
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
                exp=r"^[*/+\-^,=<>&|]", tokenType=expparser.TokenType.OPR
            ),  # single width operator
            matcher(exp=r"^[0-9]+(\.[0-9]+)?", tokenType=expparser.TokenType.NUMLIKE),
            matcher(exp=r'^".*?"', tokenType=expparser.TokenType.NUMLIKE),
            matcher(exp=r"^[A-Za-z_][A-Za-z0-9_]*", tokenType=expparser.TokenType.IDR),
            matcher(exp=r"^\(", tokenType=expparser.TokenType.BRA),
            matcher(exp=r"^\)", tokenType=expparser.TokenType.KET),
            matcher(exp=r"^$", tokenType=expparser.TokenType.EOF),
        ]
        # "the \" string"
        for m in matcherList:
            ret = m.tryMatch(s, i)
            if ret:
                if ret.type == expparser.TokenType.NUMLIKE:
                    # here is only num and str without other numlike types
                    if len(ret.value) >= 2 and ret.value[0] == '"':
                        # its string
                        strstart = ret.start
                        strbuffer = ""
                        while True:
                            if len(ret.value) > 2 and ret.value[-2] == "\\":
                                # cancel the former " and \, add " back
                                strbuffer += ret.value[1:-2] + '"'
                                # move on to the next section
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
                return ret
        raise expparser.ParseException(f"unexpected token at {i}")

    @dataclasses.dataclass
    class __ExpParserResult:
        val: typing.Any
        end: int

    @staticmethod
    def __expparse_recursive(s, varList: typing.Dict, funcList: typing.Dict, i=0):
        # fsm fields
        state = expparser.__State.START
        token: expparser.Token = None
        # never modify peekToken
        peekToken = expparser.__NextToken(s, i)

        # buffer
        tokenList: typing.List[expparser.Token] = []

        # for operator priority
        oprRisingBeginPosList: typing.List[expparser.__OprPriorityLeap] = [
            expparser.__OprPriorityLeap(0, 0, 0)
        ]

        def RaiseTokenException(token: expparser.Token):
            raise expparser.ParseException(
                f'unexpected {token.type}("{token.value}") at {token.start}'
            )

        def ClearOprSectionAssumingPeer(begin, end):
            nonlocal tokenList, oprRisingBeginPosList
            i = begin
            val = tokenList[i]
            i += 1
            peerPriority = None
            serial = 0
            while True:
                if i >= end:
                    break
                opr = tokenList[i]
                i += 1
                val2 = tokenList[i]
                i += 1
                if peerPriority:
                    assert opr.value.getPriority() == peerPriority
                else:
                    peerPriority = opr.value.getPriority()
                val.value = opr.value.do(serial=serial, arg=[val, val2])
                serial += 1
            # replace the peer section into its result
            tokenList = (
                tokenList[:begin]
                + [expparser.Token(expparser.TokenType.NUMLIKE, val.value, 0, 0)]
                + tokenList[end:]
            )
            RemapToken()
            oprRisingBeginPosList.pop()
            return val

        def DealWithBra():
            nonlocal token, peekToken, state, tokenList
            subresult = expparser.__expparse_recursive(s, varList, funcList, token.end)
            tokenList.pop()  # remove the bra
            tokenList.append(
                expparser.Token(expparser.TokenType.NUMLIKE, subresult.val, 0, 0)
            )
            RemapToken()
            peekToken = expparser.__NextToken(s, subresult.end)
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
                tokenList[-1].value = expparser.NumLikeUnionUtil.ToProperFormFromAny(
                    funcList[fooName](para)
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

        # the fsm illustrated in notebook
        while True:
            MoveForwardToNextToken()
            if state == expparser.__State.START or state == expparser.__State.OPR:
                # expecting numlike, but possible to meet bra, identifier, or unary operator
                def DealWithUnaryOperatorIfNeeded():
                    nonlocal state, token, peekToken, tokenList
                    while True:
                        # do in a loop to deal with nested unary
                        if (
                            len(tokenList) >= 2
                            and tokenList[-2].type == expparser.TokenType.OPR
                            and tokenList[-2].value.isUnary()
                        ):
                            # before it is unary operator, do it
                            token.value = tokenList[-2].value.do(arg=[token])
                            tokenList = tokenList[:-2] + [token]
                            RemapToken()
                        else:
                            break

                if token.type == expparser.TokenType.BRA:
                    DealWithBra()
                    DealWithUnaryOperatorIfNeeded()
                elif token.type == expparser.TokenType.NUMLIKE:
                    state = expparser.__State.NUM
                    DealWithUnaryOperatorIfNeeded()
                elif token.type == expparser.TokenType.IDR:
                    DealWithIdentifier()
                    DealWithUnaryOperatorIfNeeded()
                elif token.type == expparser.TokenType.OPR:
                    # maybe unary operator
                    state = expparser.__State.OPR
                    if token.value == expparser._OprType.SUB:
                        # to neg
                        tokenList[-1].value = expparser._OprType.NEG
                    if not token.value.isUnary():
                        RaiseTokenException(token)
                    # will be calced after read the num
                else:
                    RaiseTokenException(token)
            elif state == expparser.__State.NUM:
                if token.type == expparser.TokenType.OPR:
                    state = expparser.__State.OPR
                    lastOprPrior = oprRisingBeginPosList[-1].priafter
                    opr = token.value.getPriority()
                    if opr > lastOprPrior:
                        oprRisingBeginPosList.append(
                            expparser.__OprPriorityLeap(
                                len(tokenList) - 2, lastOprPrior, opr
                            )
                        )  # -2 for num and opr
                    elif opr < lastOprPrior:
                        while True:
                            if opr >= oprRisingBeginPosList[-1].priafter:
                                break
                            # clear since last rising, until flat
                            # len(tokenList)-1 since the lowering opr has been appended
                            ClearOprSectionAssumingPeer(
                                oprRisingBeginPosList[-1].pos, len(tokenList) - 1
                            )
                        if opr > oprRisingBeginPosList[-1].priafter:
                            # new opr is the new rising
                            oprRisingBeginPosList.append(
                                expparser.__OprPriorityLeap(
                                    len(tokenList) - 2,
                                    oprRisingBeginPosList[-1].priafter,
                                    opr,
                                )
                            )
                elif (
                    token.type == expparser.TokenType.KET
                    or token.type == expparser.TokenType.EOF
                ):
                    state = expparser.__State.END
                    expendpos = token.end
                    tokenList.pop()  # remove the eof or ket
                    RemapToken()
                    # clear all
                    while True:
                        if len(oprRisingBeginPosList) == 0:
                            break
                        ClearOprSectionAssumingPeer(
                            oprRisingBeginPosList[-1].pos, len(tokenList)
                        )
                    return expparser.__ExpParserResult(tokenList[0].value, expendpos)
                else:
                    RaiseTokenException(token)
            elif state == expparser.__State.END:
                RaiseTokenException(token)

    @staticmethod
    def parseelement(s):
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
        return expparser.__expparse_recursive(s, var, func).val

    @staticmethod
    def test():
        var = {**expparser.BasicConstantLib}
        func = {**expparser.BasicFunctionLib}

        @dataclasses.dataclass
        class TestUnit:
            expression: str
            expected: str = "unspecified"
            result: str = ""

        exp: typing.List[TestUnit] = [
            TestUnit(r"sin(pi/2)", "1.0"),
            TestUnit(r"1+2^2*2+--1", "10.0"),
            TestUnit(r'streq("test \" str","test \" str")', "True"),
            TestUnit(r"eq(1+0.1,1)", "False"),
            TestUnit(r"eq(1+0.1,1,0.2)", "True"),
            TestUnit(r"1!=2^^2>=3", "True"),
            TestUnit(r"CList(1))", "[1.0]"),
            TestUnit(r"CBool(1))", "True"),
            TestUnit(r"CBool(0))", "False"),
            TestUnit(r'streq(CStr(1),"1.0")', "True"),
            TestUnit(r"CStr(true)", "True"),
            TestUnit(r'CNum("1.23")+1', "2.23"),
            TestUnit(r"CNum(true)+1", "2.0"),
            TestUnit(r"array(array(1,0),array(0,1))", "[[1.0, 0.0], [0.0, 1.0]]"),
            TestUnit(r"WrapSingle(WrapSingle(1))", "[[1.0]]"),
        ]
        unpassed: typing.List[TestUnit] = []

        def splitline():
            print("#" * 30)

        for e in exp:
            result = expparser.expparse(
                e.expression,
                var=var,
                func=func,
            )
            if str(result) == e.expected:
                ifpass = True
            else:
                ifpass = False
                e.result = result
                unpassed.append(e)
            print(
                f"""
exp: {e.expression}
    elements: {expparser.parseelement(e.expression)}
    expected: {e.expected}
    result: {result}
    {"pass" if ifpass else "fail"}
"""[
                    1:-1
                ]
            )
            splitline()
        if len(unpassed) == 0:
            print("all passed")
        else:
            print("unpassed")
            splitline()
            for u in unpassed:
                print(
                    f"""
{u.expression}
    expected: {u.expected}
    result: {u.result}
"""[
                        1:-1
                    ]
                )
                splitline()


def sleepuntil(con: Callable, dt=0.1):
    while not con():
        time.sleep(dt)


class perf_statistic:
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

    @FunctionalWrapper
    def WaitUntilNextFrame(self):
        sleepuntil(
            lambda: time.perf_counter() - self.lt > self.frametime,
            dt=0.5 * self.frametime,
        )
        self.SetToNextFrame()

    @FunctionalWrapper
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

    @FunctionalWrapper
    def SetToNextFrame(self):
        self.lt = time.perf_counter()


def longDelay(t, interval=0.5):
    round = math.ceil(t / interval)
    for i in range(round):
        time.sleep(interval)


# to stop oscilation in autoCali due to sleep() precise
def PreciseSleep(t):
    if t > 0.1:
        # too rough
        sleep(t)
    else:
        endtime = time.perf_counter() + t
        while True:
            if time.perf_counter() >= endtime:
                break


def longDelay(t, interval=0.5):
    round = math.ceil(t / interval)
    for i in range(round):
        time.sleep(interval)


# to stop oscilation in autoCali due to sleep() precise
def PreciseSleep(t):
    if t > 0.1:
        # too rough
        sleep(t)
    else:
        endtime = time.perf_counter() + t
        while True:
            if time.perf_counter() >= endtime:
                break


def WrapperOfMultiLineText(s):
    '''
    to process text like this 
    var=WrapperOfMultilLineText(${threeQuotes}
your
multiline
content
here
${threeQuotes})
    '''
    return s[1:-1]