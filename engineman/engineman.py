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
    typeCache: "dict[Port8111.QueryType, Port8111Cache.SingleTypeCache]" = dict()

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
                > AnnotationUtil.getAnnotations(Port8111Cache).fetchInterval
            ):
                self.update()
            return self.value

    def get(self, queryType: Port8111.QueryType, mustUpdate=None):
        if queryType not in self.typeCache:
            self.typeCache[queryType] = self.SingleTypeCache(queryType)
        return self.typeCache[queryType].get(mustUpdate=mustUpdate)


@AnnotationUtil.Annotation(pressTime=0.05)
class FunctionalKey:
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
        self.hold(AnnotationUtil.getAnnotations(FunctionalKey).pressTime)

    @staticmethod
    def Unbounded():
        return ClassNone()


@dataclasses.dataclass
class Solution:
    toEnable: typing.Callable
    toDisable: typing.Callable

    @staticmethod
    def tryAction(
        action: typing.Callable,
        solution: "Solution | list[Solution]",
    ):
        """
        got some problems with this
        one cant set radiator to manual mode when in auto engine control mode
        so solutions are not independent, they are coupled with each other
        """
        solution = NormalizeIterableOrSingleArgToIterable(solution)
        # iterate all possible solution combination to finish action successfully
        solutionCombinationMax = 2 ** len(solution) - 1

        def getSolState(comb, idx):
            return comb & (1 << idx)

        def applySolComb(idx):
            for i in range(len(solution)):
                if getSolState(idx, i):
                    solution[i].toEnable()

        def unapplySolComb(idx):
            for i in range(len(solution)):
                if getSolState(idx, i):
                    solution[i].toDisable()

        def transferSol(idxOld, idxNew):
            for i in range(len(solution)):
                old = getSolState(idxOld, i)
                new = getSolState(idxNew, i)
                if old == new:
                    pass
                elif old and not new:
                    solution[i].toDisable()
                elif not old and new:
                    solution[i].toEnable()

        nowSolComb = 0
        while True:
            if action():
                break
            if nowSolComb < solutionCombinationMax:
                transferSol(nowSolComb, nowSolComb + 1)
                nowSolComb += 1
            else:
                unapplySolComb(nowSolComb)
                raise AxisUnsupported()


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
    solution: Solution | list[Solution] = dataclasses.field(default_factory=list)

    def switchManualControl(self):
        self.switchManualControlKey.press()

    def setTo(self, target):
        pass

    def getVal(self, mustUpdate=None):
        pass

    def tryChange(self, action):
        def inner():
            prev = self.getVal()
            if prev is None:
                raise AxisUnsupported()
            action()
            PreciseSleep(0.1)
            after = self.getVal(mustUpdate=True)
            if after is None:
                raise AxisUnsupported()
            return not FloatEq(prev, after)

        Solution.tryAction(inner, self.solution)


class DiscreteAxis(Axis):
    def switch(self):
        self.tryChange(lambda: self.switchTapPositionKey.press())

    def setTo(self, target):
        while True:
            nowVal = self.getVal()
            if nowVal is None:
                raise AxisUnsupported()
            if nowVal != target:
                self.switch()
            else:
                break


@AnnotationUtil.Annotation(errAllowed=0.01, keyboardSensitivity=0.03)
class ContiniousAxis(Axis):
    # pid params expect axis value within [0,1]
    controller = PIDController(3, 0, 0.25)

    def turnUp(self, holdTime):
        self.tryChange(lambda: self.turnUpKey.hold(holdTime))

    def turnDown(self, holdTime):
        self.tryChange(lambda: self.turnDownKey.hold(holdTime))

    def setTo(self, target):
        keyboardSensitivity = AnnotationUtil.getAnnotations(
            ContiniousAxis
        ).keyboardSensitivity
        while True:
            nowVal = self.getVal()
            if nowVal is None:
                raise AxisUnsupported()
            err = target - nowVal
            if abs(err) <= AnnotationUtil.getAnnotations(ContiniousAxis).errAllowed:
                break
            ctrl = self.controller.update(err)
            if abs(ctrl) < keyboardSensitivity:
                # keyboard can't respond fast enough
                # may cause bouncing, but will be safe if errAllowed is big enough
                ctrl = ctrl / abs(ctrl) * keyboardSensitivity
            if ctrl > 0:
                self.turnUp(ctrl)
            else:
                self.turnDown(abs(ctrl))


SwitchManualEngineControl = FunctionalKey(
    [
        keyshortcut.win32conComp.VK_LCONTROL,
        keyshortcut.win32conComp.VK_OEM_MINUS,
    ]
)


class OilRadiator(ContiniousAxis):
    def __init__(self):
        super().__init__(
            turnUpKey=FunctionalKey(keyshortcut.win32conComp.VK_OEM_PLUS),
            turnDownKey=FunctionalKey(keyshortcut.win32conComp.VK_OEM_MINUS),
            switchManualControlKey=FunctionalKey(
                [
                    win32con.VK_RMENU,
                    keyshortcut.win32conComp.VK_RIGHT_MID_BRACKET,
                ]
            ),
            solution=[
                Solution(
                    toEnable=lambda: SwitchManualEngineControl.press(),
                    toDisable=lambda: SwitchManualEngineControl.press(),
                ),
                Solution(
                    toEnable=lambda: self.switchManualControl(),
                    toDisable=lambda: self.switchManualControl(),
                ),
            ],
        )

    def getVal(self, mustUpdate=None):
        got = Port8111Cache().get(Port8111.QueryType.indicator)
        if Axis.checkIfNotAirIndicator(got):
            return None
        return got.__dict__["oilradiator"]  # which will fail

    def setToMaxAnyway(self):
        self.turnUp(5)


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
            solution=[
                Solution(
                    toEnable=lambda: SwitchManualEngineControl.press(),
                    toDisable=lambda: SwitchManualEngineControl.press(),
                ),
                Solution(
                    toEnable=lambda: self.switchManualControl(),
                    toDisable=lambda: self.switchManualControl(),
                ),
            ],
        )

    def getVal(self, mustUpdate=None):
        try:
            result = (
                Port8111Cache()
                .get(Port8111.QueryType.state, mustUpdate)
                .expectValid()
                .engine.radiator.value[0]
                / 100
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
            solution=[
                Solution(
                    toEnable=lambda: SwitchManualEngineControl.press(),
                    toDisable=lambda: SwitchManualEngineControl.press(),
                ),
                Solution(
                    toEnable=lambda: self.switchManualControl(),
                    toDisable=lambda: self.switchManualControl(),
                ),
            ],
        )

    def getVal(self, mustUpdate=None):
        try:
            result = (
                Port8111Cache()
                .get(Port8111.QueryType.state, mustUpdate)
                .expectValid()
                .engine.RPM_throttle.value[0]
                / 100
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
            ),
            solution=[
                Solution(
                    toEnable=lambda: SwitchManualEngineControl.press(),
                    toDisable=lambda: SwitchManualEngineControl.press(),
                ),
            ],
        )

    def getVal(self, mustUpdate=None):
        try:
            result = (
                Port8111Cache()
                .get(Port8111.QueryType.state, mustUpdate)
                .expectValid()
                .engine.compressor_stage.value[0]
            )
            if result is not None:
                return result
            return None
        except Port8111.FetchFailure:
            return None


class EngineMan:

    def setEngineStatusDemo(self):
        Radiator().setTo(0.75)
        PropPitch().setTo(0.75)
        Supercharger().setTo(2)


activeWindow(GetWtHwnd())
for i in range(2):
    PreciseSleep(1)
    Rhythms.Notify.play()
EngineMan().setEngineStatusDemo()
Rhythms.Success.play()
pass
