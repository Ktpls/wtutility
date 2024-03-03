from utilref import *


def unitTest():
    def vecadd(va: list, vb: list):
        assert len(va) == len(vb)
        return list(map(lambda x, y: x + y, va, vb))

    var = {**expparser.BasicConstantLib}
    func = {
        **expparser.BasicFunctionLib,
        "OptionalFunc": expparser.Utils.OptionalFunc(
            [expparser.Utils.NonOptional(), 0, 0], lambda x, y, z: x + y + z
        ),
        "vecadd": vecadd,
    }

    @dataclasses.dataclass
    class TestUnit:
        class ExpectedException:
            def __repr__(self) -> str:
                return "Exception"

        expression: str
        expected: str = "unspecified"
        result: str = ""

        def do(self):
            """
            ret: if passed
            """
            try:
                self.result = expparser.expparse(
                    self.expression,
                    var=var,
                    func=func,
                )
            except Exception as e:
                # raise e
                self.result = TestUnit.ExpectedException()

            if isinstance(self.expected, TestUnit.ExpectedException) and isinstance(
                self.result, TestUnit.ExpectedException
            ):
                return True
            elif str(self.result) == self.expected:
                return True
            else:
                print(f"{self.expression}")
                print(f"    expected: {self.expected}")
                print(f"    result: {self.result}")
                return False

    exp: list[TestUnit] = [
        TestUnit(r"CStr(1)", "1.0"),
        TestUnit(r"1,2,3", "[1.0, 2.0, 3.0]"),
        TestUnit(r"sin(pi/2)+2^2*2+--1", "10.0"),
        TestUnit(r"eq(1+0.1,1)", "False"),
        TestUnit(r"eq(1+0.1,1,0.2)", "True"),
        TestUnit(r'"test \" str"', 'test " str'),
        TestUnit(r"1!=2", "True"),
        TestUnit(r"2>=3", "False"),
        TestUnit(r"CList(1)", "[1.0]"),
        TestUnit(r"CBool(1)", "True"),
        TestUnit(r"CBool(0)", "False"),
        TestUnit(r'StrEq(CStr(1),"1.0")', "True"),
        TestUnit(r'CNum("1.23")+1', "2.23"),
        TestUnit(r"CNum(true)+1", "2.0"),
        TestUnit(r"CBool(0))))))))", "False"),
        TestUnit("1 ,\t2,\r\n3", "[1.0, 2.0, 3.0]"),
        TestUnit(r"vecadd((1,2),(3,4))", "[4.0, 6.0]"),
        TestUnit(r"OptionalFunc(1,,)", "1.0"),
        TestUnit(r"OptionalFunc(,1,)", TestUnit.ExpectedException()),
        TestUnit(r"((1,1),(2,2),(1,),1)", "[[1.0, 1.0], [2.0, 2.0], [1.0, None], 1.0]"),
    ]

    def splitline():
        print("#" * 30)

    unpassedNum = 0
    for i, e in enumerate(exp):
        if not e.do():
            unpassedNum += 1
            splitline()
    print(f"unpassedNum={unpassedNum}")
    if unpassedNum == 0:
        print("all passed!")


def benchMark():
    var = {**expparser.BasicConstantLib}
    func = {**expparser.BasicFunctionLib}
    exps = ["1+2+3+4+5+6+7+8+9+10+11+12+13+14+15+16+17+18+19+20"]
    exps = [expparser.compile(e) for e in exps]
    turnNum = 10_0000
    pg = Progress(turnNum)
    ps = perf_statistic().start()
    for t in range(turnNum):
        for e in exps:
            result = e.eval(var=var, func=func)
        pg.update(t)
    ps.stop()
    print(ps.time() / turnNum)


def playground():
    var = {**expparser.BasicConstantLib}
    func = {**expparser.BasicFunctionLib, "f": lambda x, y: x + y, 's3': lambda: 3}
    exp = "f(1,1),f(2,2),sin(pi/2),pi,s3()"
    result = expparser.compile(exp)
    print(result)
    print(result.eval(var, func))


benchMark()
