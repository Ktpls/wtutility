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


Port8111UpdateInterval = 0.25


@Singleton
class Port8111Cache:
    # use cache to cancel complex coupling between various data consumers under requirement of reducing http request cost
    @dataclasses.dataclass
    class SingleTypeCache:
        queryType: Port8111.QueryType
        lastUpdateTime: float
        value: typing.Any = None

        def update(self):
            self.value = Port8111.get(self.queryType)
            self.lastUpdateTime = time.perf_counter()

        def get(self, key: str, mustUpdate=False):
            if time.perf_counter() - self.lastUpdateTime > Port8111UpdateInterval:
                self.update()
            elif mustUpdate:
                self.update()
            return self.value.__dict__.get(key, None)

    def get(self, queryType: Port8111.QueryType, key: str):
        pass


class FunctionalKey:
    PRESS_TIME = 0.01
    key: list[int]

    def __init__(self, key: int | list[int]) -> None:
        if isinstance(key, typing.Iterable):
            pass
        elif isinstance(key, int):
            key = [key]
        self.key = key
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

    def getVal(self):
        pass


class DiscreteAxis(Axis):
    def switch(self):
        self.switchTapPositionKey.press()


class ContiniousAxis(Axis):
    controller = PIDController(0.1, 0, 0.1)
    errAllowed = 1

    def turnUp(self, holdTime):
        self.turnUpKey.hold(holdTime)

    def turnDown(self, holdTime):
        self.turnDownKey.hold(holdTime)

    def setTo(self, target):
        count = 0
        while True:
            nowVal = self.getVal()
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
            turnUpKey=FunctionalKey(keyshortcut.keycode.key_Equals),
            turnDownKey=FunctionalKey(keyshortcut.keycode.key_Minus),
            switchManualControlKey=FunctionalKey(
                [
                    keyshortcut.keycode.key_RightAlt,
                    keyshortcut.keycode.key_RightBigBracket,
                ]
            ),
        )


class Radiator(ContiniousAxis):
    def __init__(self):
        super().__init__(
            turnUpKey=FunctionalKey(keyshortcut.keycode.key_RightBigBracket),
            turnDownKey=FunctionalKey(keyshortcut.keycode.key_LeftBigBracket),
            switchManualControlKey=FunctionalKey(
                [
                    keyshortcut.keycode.key_RightAlt,
                    keyshortcut.keycode.key_RightBigBracket,
                ]
            ),
        )


class PropPitch(ContiniousAxis):
    def __init__(self):
        super().__init__(
            turnUpKey=FunctionalKey(keyshortcut.keycode.key_Quote),
            turnDownKey=FunctionalKey(keyshortcut.keycode.key_Colon),
            switchManualControlKey=FunctionalKey(
                [keyshortcut.keycode.key_RightAlt, keyshortcut.keycode.key_Quote]
            ),
        )


class Supercharger(DiscreteAxis):
    def __init__(self):
        super().__init__(
            switchTapPositionKey=FunctionalKey(keyshortcut.keycode.key_NumpadPlus)
        )


class EngineMan:

    def setEngineStatusDemo(self):
        rad = Radiator()
        orad = OilRadiator()
        pit = PropPitch()
        axis: list[Axis] = [rad, orad, pit]
        for c in axis:
            c.setTo(0)


activeWindow(GetWtHwnd())
for i in range(5):
    PreciseSleep(1)
    Rythm.RythmNotify.play()
EngineMan().setEngineStatusDemo()
