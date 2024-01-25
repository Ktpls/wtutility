from utilref import *

# print(expparser.expparse("CBool(1)", func={"CBool": bool}))


def test():
    def vecadd(va: typing.List, vb: typing.List):
        assert len(va) == len(vb)
        return list(map(lambda x, y: x + y, va, vb))

    var = {**expparser.BasicConstantLib}
    func = {
        **expparser.BasicFunctionLib,
        "DelayedEvaluation": lambda: 999,
        "OptionalFunc": expparser.Utils.OptionalFunc(
            [expparser.Utils.NonOptional(), 0, 0], lambda x, y, z: x + y + z
        ),
        "vecadd": vecadd,
    }

    @dataclasses.dataclass
    class TestUnit:
        class ExpectedException:
            def __repr__(self) -> str:
                return "Expected Exception"

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
            except:
                self.result = TestUnit.ExpectedException()

            if str(self.result) == self.expected:
                return True
            elif isinstance(self.expected, TestUnit.ExpectedException) and isinstance(
                self.result, TestUnit.ExpectedException
            ):
                return True
            else:
                print(
                    f"""
{self.expression}
    expected: {self.expected}
    result: {self.result}
"""[
                        1:-1
                    ]
                )
                return False

    exp: typing.List[TestUnit] = [
        TestUnit(
            r'sin(pi/2)+2^2*2+--1,eq(1+0.1,1),eq(1+0.1,1,0.2),streq("test \" str","test \" str"),1!=2,2>=3',
            "[10.0, False, True, True, True, False]",
        ),
        TestUnit(
            r'CList(1),CBool(1),CBool(0),streq(CStr(1),"1.0"),CStr(true),CNum("1.23")+1,CNum(true)+1',
            "[[1.0], True, False, True, 'True', 2.23, 2.0]",
        ),
        TestUnit(r"CBool(0))))))))", "False"),
        TestUnit("1 ,\t2,\r\n3", "[1.0, 2.0, 3.0]"),
        TestUnit(
            r"DelayedEvaluation()+1,OptionalFunc(1,,),vecadd((1,2),(3,4))",
            "[1000.0, 1.0, [4.0, 6.0]]",
        ),
        TestUnit(r"OptionalFunc(,1,)", TestUnit.ExpectedException()),
        TestUnit(r"((1,1),(2,2),(1,),1)", "[[1.0, 1.0], [2.0, 2.0], [1.0], 1.0]"),
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


test()
