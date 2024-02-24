from utilref import *
import keyshortcut.keyshortcut as keyshortcut


class ClassNone:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def __func_none(*args, **kwargs):
        pass

    def __getattr__(self, name: str):
        return ClassNone.__func_none


class AxisUnsupported(Exception):
    pass


@Singleton
@AnnotationUtil.Annotation(fetchInterval=0.25)
class Port8111Cache:
    # use cache to cancel complex coupling between various data consumers under requirement of reducing http request cost
    typcCache: "dict[Port8111.QueryType, Port8111Cache.SingleTypeCache]" = dict()

    @dataclasses.dataclass
    class SingleTypeCache:
        queryType: Port8111.QueryType
        lastUpdateTime: float = dataclasses.field(init=False, default=None)
        value: typing.Any = dataclasses.field(init=False, default=None)

        def update(self):
            self.value = Port8111.get(self.queryType)
            self.lastUpdateTime = time.perf_counter()

        def get(self, mustUpdate=None):
            if mustUpdate is None:
                mustUpdate = False
            if (
                mustUpdate
                or self.lastUpdateTime is None
                or time.perf_counter() - self.lastUpdateTime
                > AnnotationUtil.getAnnotations(Port8111Cache)["fetchInterval"]
            ):
                self.update()
            return self.value

    def get(self, queryType: Port8111.QueryType, mustUpdate=None):
        if queryType not in self.typcCache:
            self.typcCache[queryType] = self.SingleTypeCache(queryType)
        return self.typcCache[queryType].get(mustUpdate=mustUpdate)


class FunctionalKey:
    PRESS_TIME = 0.01
    key: list[int]

    def __init__(self, key: int | list[int]) -> None:
        self.key = NormalizeIterableOrSingleArgToIterable(key)
        assert len(self.key) >= 1

    def hold(self, holdTime):
        for k in self.key:
            keyshortcut.keydown(k)
        PreciseSleep(holdTime)
        for k in reversed(self.key):
            keyshortcut.keyup(k)

    def press(self):
        self.hold(FunctionalKey.PRESS_TIME)

    @staticmethod
    def Unbounded():
        return ClassNone()


@dataclasses.dataclass
class Axis:
    switchManualControlKey: FunctionalKey = dataclasses.field(
        default_factory=FunctionalKey.Unbounded
    )
    turnUpKey: FunctionalKey = dataclasses.field(
        default_factory=FunctionalKey.Unbounded
    )
    turnDownKey: FunctionalKey = dataclasses.field(
        default_factory=FunctionalKey.Unbounded
    )
    switchTapPositionKey: FunctionalKey = dataclasses.field(
        default_factory=FunctionalKey.Unbounded
    )

    def switchManualControl(self):
        self.switchManualControlKey.press()

    def setTo(self, target):
        pass

    def getVal(self, mustUpdate=None):
        pass

    @staticmethod
    def tryAction(
        action: typing.Callable,
        solutionOnFailure: typing.Callable | list[typing.Callable],
    ):
        solutionOnFailure = NormalizeIterableOrSingleArgToIterable(solutionOnFailure)
        for i in solutionOnFailure:
            if not action():
                i()
            else:
                return
        raise AxisUnsupported()


class DiscreteAxis(Axis):
    def switch(self):
        self.switchTapPositionKey.press()


class ContiniousAxis(Axis):
    controller = PIDController(0.1, 0, 0.1)
    errAllowed = 0.01

    def turnUp(self, holdTime):
        self.turnUpKey.hold(holdTime)

    def turnDown(self, holdTime):
        def turnDown_inner():
            prev = self.getVal()
            if prev is None:
                raise AxisUnsupported()
            self.turnDownKey.hold(holdTime)
            after = self.getVal(mustUpdate=True)
            if after is None:
                raise AxisUnsupported()
            return FloatEq(prev, after) and not FloatEq(prev, 0)

        self.tryAction(turnDown_inner, self.switchManualControl)

    def setTo(self, target):
        count = 0
        while True:
            nowVal = self.getVal()
            if nowVal is None:
                raise AxisUnsupported()
            err = target - nowVal
            if abs(err) <= ContiniousAxis.errAllowed:
                break
            ctrl = self.controller.update(err)
            if ctrl > 0:
                self.turnUp(ctrl)
            else:
                self.turnDown(abs(ctrl))
            count += 1


class OilRadiator(ContiniousAxis):
    def __init__(self):
        super().__init__(
            turnUpKey=FunctionalKey(keyshortcut.win32conComp.VK_OEM_PLUS),
            turnDownKey=FunctionalKey(keyshortcut.win32conComp.VK_OEM_MINUS),
            switchManualControlKey=FunctionalKey(
                [
                    win32con.VK_RMENU,
                    keyshortcut.win32conComp.VK_OEM_6,
                ]
            ),
        )

    def getVal(self, mustUpdate=None):
        got = Port8111Cache().get(Port8111.QueryType.indicator)
        if Axis.checkIfNotAirIndicator(got):
            return None
        return got.__dict__["oilradiator"]  # which will fail


class Radiator(ContiniousAxis):
    def __init__(self):
        super().__init__(
            turnUpKey=FunctionalKey(keyshortcut.win32conComp.VK_RIGHT_MID_BRACKET),
            turnDownKey=FunctionalKey(keyshortcut.win32conComp.VK_LEFT_MID_BRACKET),
            switchManualControlKey=FunctionalKey(
                [
                    win32con.VK_RMENU,
                    keyshortcut.win32conComp.VK_RIGHT_MID_BRACKET,
                ]
            ),
        )

    def getVal(self, mustUpdate=None):
        try:
            result = (
                Port8111Cache()
                .get(Port8111.QueryType.indicator, mustUpdate)
                .expectValid()
                .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
                .radiator
            )
            if result is not None:
                return result
            result = (
                Port8111Cache()
                .get(Port8111.QueryType.state, mustUpdate)
                .expectValid()
                .engine.radiator.value[0]
            )
            if result is not None:
                return result
            return None
        except Port8111.FetchFailure:
            return None


class PropPitch(ContiniousAxis):
    def __init__(self):
        super().__init__(
            turnUpKey=FunctionalKey(keyshortcut.win32conComp.VK_QUOTE),
            turnDownKey=FunctionalKey(keyshortcut.win32conComp.VK_SEMICOLON),
            switchManualControlKey=FunctionalKey(
                [win32con.VK_RMENU, keyshortcut.win32conComp.VK_QUOTE]
            ),
        )

    def getVal(self, mustUpdate=None):
        try:
            result = (
                Port8111Cache()
                .get(Port8111.QueryType.indicator, mustUpdate)
                .expectValid()
                .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
                .prop_pitch
            )
            if result is not None:
                return result
            return None
        except Port8111.FetchFailure:
            return None


class Supercharger(DiscreteAxis):
    def __init__(self):
        super().__init__(
            switchTapPositionKey=FunctionalKey(
                [
                    win32con.VK_LCONTROL,
                    win32con.VK_LMENU,
                    keyshortcut.win32conComp.VK_OEM_PLUS,
                ]
            )
        )


class EngineMan:

    def setEngineStatusDemo(self):
        Radiator().setTo(0)
        PropPitch().setTo(0)


"""
playground here
wdD4d4=-=-=
"""

# activeWindow(GetWtHwnd())
# for i in range(2):
#     PreciseSleep(1)
#     Rhythms.Notify.play()
keyshortcut.press(187)
# with keyshortcut.HoldingKey(win32con.VK_LWIN):
#     keyshortcut.press(ord("D"))
# EngineMan().setEngineStatusDemo()

pass
