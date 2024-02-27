from utilitypack import *
import keyshortcut.keyshortcut as keyshortcut
from .engineConfig import *
from .engineman_config import *


class ClassNone:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def __func_none(*args, **kwargs):
        pass

    def __getattr__(self, name: str):
        return ClassNone.__func_none


@Singleton
class WarthunderWindow(Cache):
    def __init__(self):
        def toFetch():
            try:
                return GetWtHwnd()
            except:
                return None

        def isValid(hwnd):
            try:
                return hwnd is None and hwnd != 0 and win32gui.IsWindow(hwnd)
            except:
                return False

        super().__init__(
            toFetch=toFetch,
            isValid=isValid,
            outdatedTime=10,
        )

    def isFocus(self):
        hwnd = self.get()
        try:
            # GetFocus not working
            return self.testValid() and win32api.GetFocus() == self.get()
        except Exception as e:
            return False


@Singleton
@AnnotationUtil.Annotation(fetchInterval=1)
class Port8111Cache:
    # use cache to cancel complex coupling between various data consumers under requirement of reducing http request cost
    typeCache: "dict[Port8111.QueryType, Port8111Cache.SingleTypeCache]" = dict()

    class SingleTypeCache(Cache):
        queryType: Port8111.QueryType

        def __init__(self, queryType):
            super().__init__(
                toFetch=lambda: Port8111.get(queryType),
                outdatedTime=AnnotationUtil.getAnnotations(Port8111Cache).fetchInterval,
            )
            self.queryType = queryType

    def get(self, queryType: Port8111.QueryType, mustUpdate=None):
        if queryType not in self.typeCache:
            self.typeCache[queryType] = self.SingleTypeCache(queryType)
        return self.typeCache[queryType].get(newest=mustUpdate)


@AnnotationUtil.Annotation(pressTime=0.05)
class FunctionalKey:
    key: list[int]

    def __init__(self, key: int | list[int]) -> None:
        self.key = NormalizeIterableOrSingleArgToIterable(key)
        assert len(self.key) >= 1

    def hold(self, holdTime):
        if not WarthunderWindow().isFocus():
            print("badFocus")
            raise AxisUnsupported()
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


class ReadOnlyAxis(Axis):
    def set(self, target):
        raise AxisUnsupported()


@dataclasses.dataclass
class ControlableEngineAxis(Axis):
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

    def tryChange(self, action):
        def inner():
            prev = self.get()
            if prev is None:
                raise AxisUnsupported()
            action()
            PreciseSleep(0.1)
            after = self.get(mustUpdate=True)
            if after is None:
                raise AxisUnsupported()
            return not FloatEq(prev, after)

        Solution.tryAction(inner, self.solution)


class DiscreteCEAxis(ControlableEngineAxis):
    def switch(self):
        self.tryChange(lambda: self.switchTapPositionKey.press())

    def set(self, target):
        while True:
            nowVal = self.get()
            if nowVal is None:
                raise AxisUnsupported()
            if nowVal != target:
                self.switch()
            else:
                break


@AnnotationUtil.Annotation(errAllowed=0.01, keyboardSensitivity=0.03)
class ContiniousCEAxis(ControlableEngineAxis):
    # pid params expect axis value within [0,1]
    controller = PIDController(3, 0, 0.25)

    def turnUp(self, holdTime):
        self.tryChange(lambda: self.turnUpKey.hold(holdTime))

    def turnDown(self, holdTime):
        self.tryChange(lambda: self.turnDownKey.hold(holdTime))

    def set(self, target):
        keyboardSensitivity = AnnotationUtil.getAnnotations(
            ContiniousCEAxis
        ).keyboardSensitivity
        while True:
            nowVal = self.get()
            if nowVal is None:
                raise AxisUnsupported()
            err = target - nowVal
            if abs(err) <= AnnotationUtil.getAnnotations(ContiniousCEAxis).errAllowed:
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


@Singleton
class OilRadiator(ContiniousCEAxis):
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
                    toEnable=lambda: OilRadiator.switchManualControl(),
                    toDisable=lambda: OilRadiator.switchManualControl(),
                ),
            ],
        )

    def get(self, mustUpdate=None):
        try:
            return (
                Port8111Cache()
                .get(Port8111.QueryType.indicator, mustUpdate)
                .expectValid()
                .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
                .oil_radiator_indicator
            )
        except Port8111.FetchFailure:
            return None

    def setToMaxAnyway(self):
        if self.get() is not None:
            self.set(1.0)
        else:
            self.turnUpKey.hold(5)


@Singleton
class Radiator(ContiniousCEAxis):
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

    def get(self, mustUpdate=None):
        try:
            return (
                Port8111Cache()
                .get(Port8111.QueryType.state, mustUpdate)
                .expectValid()
                .engine.radiator.value[0]
                / 100
            )
        except Port8111.FetchFailure:
            return None


@Singleton
class PropPitch(ContiniousCEAxis):
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

    def get(self, mustUpdate=None):
        try:
            return (
                Port8111Cache()
                .get(Port8111.QueryType.state, mustUpdate)
                .expectValid()
                .engine.RPM_throttle.value[0]
                / 100
            )
        except Port8111.FetchFailure:
            return None


@Singleton
class Supercharger(DiscreteCEAxis):
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

    def get(self, mustUpdate=None):
        try:
            return (
                Port8111Cache()
                .get(Port8111.QueryType.state, mustUpdate)
                .expectValid()
                .engine.compressor_stage.value[0]
            )
        except Port8111.FetchFailure:
            return None


@Singleton
class Altitude(ReadOnlyAxis):

    def get(self, mustUpdate=None):
        try:
            indi = (
                Port8111Cache()
                .get(Port8111.QueryType.indicator, mustUpdate)
                .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
                .expectValid()
            )
            return indi.altitude_hour or indi.altitude_min or indi.altitude_10k
        except Port8111.FetchFailure:
            return None


@Singleton
class EngineMan:
    planeName: str = None
    serviceClass: typing.Callable = None
    serviceInstance: EngineConfig = None
    lastCheckTime: float = None
    services: dict[str, EngineConfigBean] = dict()

    def __init__(self):
        self.gauges = Gauges(
            oilRadiator=OilRadiator(),
            radiator=Radiator(),
            propPitch=PropPitch(),
            supercharger=Supercharger(),
            altitude=Altitude(),
        )
        for i in engineConfigHost.configs:
            service: EngineConfigBean = i
            service.planeName = NormalizeIterableOrSingleArgToIterable(
                service.planeName
            )
            for p in service.planeName:
                self.services[p] = service

    def terminateService(self):
        if self.seviceNowValid():
            self.planeName = None
            self.serviceClass = None
            self.serviceInstance = None
            self.lastCheckTime = None

    def initializeService(self, planeName):
        if planeName not in self.services:
            return
        self.planeName = planeName
        self.serviceClass = self.services[planeName].clazz
        self.serviceInstance = self.serviceClass()
        self.serviceDoCheck()

    def seviceNowValid(self):
        return self.serviceInstance is not None

    def serviceDoCheck(self):
        if self.seviceNowValid():
            self.lastCheckTime = time.perf_counter()
            try:
                self.serviceInstance.check(self.gauges)
            except AxisUnsupported:
                pass

    def setService(self, planeName):
        if self.planeName == planeName or (
            planeName in self.services
            and self.serviceClass == self.services[planeName].clazz
        ):
            pass
        else:
            self.terminateService()
            if planeName is not None and planeName in self.services:
                self.initializeService(planeName)

    def check(self):
        planeName = None
        try:
            planeName = (
                Port8111Cache()
                .get(Port8111.QueryType.indicator)
                .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
                .expectValid()
                .type
            )
        except Port8111.FetchFailure:
            pass
        self.setService(planeName)
        if self.seviceNowValid():
            if (
                time.perf_counter() - self.lastCheckTime
                > self.services[planeName].checkRate
            ):
                self.serviceDoCheck()

    def setEngineStatusDemo(self):
        OilRadiator().setToMaxAnyway()
        Radiator().set(0.75)
        PropPitch().set(0.75)
        Supercharger().set(2)


class DetachedEngineMan(StoppableThread):
    def main(self):
        em = EngineMan()
        while True:
            if self.timeToStop():
                break
            em.check()
            PreciseSleep(detachedEngineManLoopInterval)


pass

# activeWindow(GetWtHwnd())
# for i in range(2):
#     PreciseSleep(1)
#     Rhythms.Notify.play()
# EngineMan().setEngineStatusDemo()
# Rhythms.Success.play()
