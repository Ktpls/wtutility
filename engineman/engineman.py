from utilitypack.utility import *
import keyshortcut.keyshortcut as keyshortcut
from .engineConfigInclude import *
from .engineConfig import *
from .engineman_config import *
from shared.globalsys import *


@Singleton
class DetachedEngineManStopSignal:

    class DetachedEngineManStopSignalCalledException(Exception): ...

    def __init__(self):
        self.val = False

    def set(self):
        self.val = True

    def reset(self):
        self.val = False

    def get(self):
        return self.val

    def throwOnIsSet(self):
        """
        call this on check point in time consuming works
        """
        if self.get():
            GSLogger().logger.debug("throw On DetachedEngineManStopSignal")
            raise DetachedEngineManStopSignal.DetachedEngineManStopSignalCalledException()

    @EasyWrapper
    @staticmethod
    def DEMSSCExceptionProcessed(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except (
                DetachedEngineManStopSignal.DetachedEngineManStopSignalCalledException
            ) as err:
                ...

        return wrapper


def GetAllEngineConfig():
    import engineman.engineConfig as engineConfig

    ret = dict()
    for k, v in engineConfig.__dict__.items():
        if v.__class__ == type and issubclass(v, engineConfig.EngineConfig):
            ret[k] = v
    print(ret)


def AxisUnsupportedProcessed(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AxisUnsupported as err:
            ...

    return wrapper


def GetFailureToAxisUnsupported(f):
    def wrapper(*args, **kwargs):
        ret = None
        try:
            ret = f(*args, **kwargs)
        except Port8111.FetchFailure as err:
            raise AxisUnsupported()
        if ret is None:
            # f returing None means no such field in 8111
            raise AxisUnsupported()
        return ret

    return wrapper


class ClassNone:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def __func_none(*args, **kwargs):
        pass

    def __getattr__(self, name: str):
        return ClassNone.__func_none


class WtFunctionalKey(keyshortcut.FunctionalKey):
    def hold(self, holdTime):
        if not WarthunderWindow().isFocus():
            raise AxisUnsupported()
        super().hold(holdTime)
        PreciseSleep(keyPressInterval)

    @staticmethod
    def Unbounded():
        return ClassNone()


@dataclasses.dataclass
class Solution:
    toEnable: typing.Callable
    toDisable: typing.Callable

    @staticmethod
    def tryAction(
        action: typing.Callable[[], bool],  # return bool indicating if success
        solution: "Solution | list[Solution]",
    ):
        solution = NormalizeIterableOrSingleArgToIterable(solution)
        nextSolId = 0
        if not action():
            while True:
                DetachedEngineManStopSignal().throwOnIsSet()
                if nextSolId < len(solution):
                    solution[nextSolId].toEnable()
                    PreciseSleep(SolutionInterval)
                    if not action():
                        solution[nextSolId].toDisable()
                        PreciseSleep(SolutionInterval)
                        nextSolId += 1
                    else:
                        break
                else:
                    raise AxisUnsupported()


class ReadOnlyAxis(Axis):
    def set(self, target):
        raise AxisUnsupported()


@dataclasses.dataclass
class ControlableEngineAxis(Axis):
    switchManualControlKey: WtFunctionalKey = dataclasses.field(
        default_factory=WtFunctionalKey.Unbounded
    )
    turnUpKey: WtFunctionalKey = dataclasses.field(
        default_factory=WtFunctionalKey.Unbounded
    )
    turnDownKey: WtFunctionalKey = dataclasses.field(
        default_factory=WtFunctionalKey.Unbounded
    )
    switchTapPositionKey: WtFunctionalKey = dataclasses.field(
        default_factory=WtFunctionalKey.Unbounded
    )
    solution: Solution | list[Solution] = dataclasses.field(default_factory=list)

    def switchManualControl(self):
        self.switchManualControlKey.press()

    def tryChange(
        self,
        action,
        issuccessful: typing.Callable[[float, float], bool] = None,
    ):
        if issuccessful is None:
            issuccessful = ControlableEngineAxis.trychange_issuccessful_eq

        def inner():
            DetachedEngineManStopSignal().throwOnIsSet()
            prev = self.get()
            action()
            PreciseSleep(delayAfterAction)
            after = self.get(newest=True)
            issu = issuccessful(prev, after)
            return issu

        Solution.tryAction(inner, self.solution)

    @staticmethod
    def trychange_issuccessful_eq(prev, after):
        return not FloatEq(prev, after)


class DiscreteCEAxis(ControlableEngineAxis):
    def switch(self):
        self.tryChange(lambda: self.switchTapPositionKey.press())

    def set(self, target):
        while True:
            DetachedEngineManStopSignal().throwOnIsSet()
            nowVal = self.get()
            if nowVal is None:
                raise AxisUnsupported()
            if nowVal != target:
                self.switch()
            else:
                break


class ContiniousCEAxis(ControlableEngineAxis):
    # pid params expect axis value within [0,1]
    controller = PIDController(4, 0, 0.1)
    valMax = 1
    valMin = 0

    def turnUp(self, holdTime):
        if holdTime < keyPressMiniumHoldingTime:
            holdTime = keyPressMiniumHoldingTime

        def issucc(prev, after):
            GSLogger().logger.debug(
                f"turnUpIsSucc {self.__class__=} {(a:=(after > prev))=} {(b:=holdTime <= continousCeAxisMinSensitivity)=} {(c:=FloatEq(prev, self.valMax))=}"
            )
            return a or b or c

        self.tryChange(
            lambda: self.turnUpKey.hold(holdTime),
            issucc,
        )

    def turnDown(self, holdTime):
        if holdTime < keyPressMiniumHoldingTime:
            holdTime = keyPressMiniumHoldingTime

        def issucc(prev, after):
            GSLogger().logger.debug(
                f"turnDownIsSucc {self.__class__=}, {(a:=(after < prev))=} {(b:=holdTime <= continousCeAxisMinSensitivity)=} {(c:=FloatEq(prev, self.valMin))=}"
            )
            return a or b or c

        self.tryChange(
            lambda: (self.turnDownKey.hold(holdTime)),
            issucc,
        )

    def set(self, target):
        while True:
            DetachedEngineManStopSignal().throwOnIsSet()
            nowVal = self.get()
            err = target - nowVal
            if abs(err) <= continousControlableEngineAxisErrorAllowed:
                break
            ctrl = self.controller.update(err)
            absctrl = abs(ctrl)
            if ctrl > 0:
                self.turnUp(absctrl)
            else:
                self.turnDown(absctrl)


SwitchManualEngineControl = WtFunctionalKey(
    [
        keyshortcut.win32conComp.VK_LCONTROL,
        keyshortcut.win32conComp.VK_OEM_MINUS,
    ]
)


def SolutionOfRadiatorOilRadiatorPropPitch(yourself: ContiniousCEAxis):
    def enableManEngCtrl_ManAxisCtrl():
        GSLogger().logger.debug("Solution enableManEngCtrl_ManAxisCtrl doing")
        SwitchManualEngineControl.press()
        PreciseSleep(0.5)
        yourself.switchManualControl()

    def disableManEngCtrl_ManAxisCtrl():
        GSLogger().logger.debug("Solution disableManEngCtrl_ManAxisCtrl doing")
        yourself.switchManualControl()
        PreciseSleep(0.5)
        SwitchManualEngineControl.press()

    def switchAxisManualControl():
        GSLogger().logger.debug("Solution switchAxisManualControl doing")
        yourself.switchManualControl()

    def switchManualEngineControl():
        GSLogger().logger.debug("Solution switchManualEngineControl doing")
        SwitchManualEngineControl.press()

    return [
        Solution(
            toEnable=switchAxisManualControl,
            toDisable=switchAxisManualControl,
        ),
        Solution(
            toEnable=enableManEngCtrl_ManAxisCtrl,
            toDisable=disableManEngCtrl_ManAxisCtrl,
        ),
        Solution(
            toEnable=switchManualEngineControl,
            toDisable=switchManualEngineControl,
        ),
    ]


@Singleton
class OilRadiator(ContiniousCEAxis):
    def __init__(self):
        super().__init__(
            turnUpKey=WtFunctionalKey(keyshortcut.win32conComp.VK_OEM_PLUS),
            turnDownKey=WtFunctionalKey(keyshortcut.win32conComp.VK_OEM_MINUS),
            switchManualControlKey=WtFunctionalKey(
                [
                    win32con.VK_RMENU,
                    keyshortcut.win32conComp.VK_RIGHT_MID_BRACKET,
                ]
            ),
            solution=SolutionOfRadiatorOilRadiatorPropPitch(self),
        )

    @GetFailureToAxisUnsupported
    def get(self, newest=None):
        indicator = (
            Port8111Cache()
            .get(Port8111.QueryType.indicator, newest)
            .expectValid()
            .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
        )
        return Coalesce(
            indicator.oil_radiator_indicator,
            indicator.oil_radiator_lever,
            indicator.oil_radiator_lever1_1,
        )

    @AxisUnsupportedProcessed
    def setToMaxAnyway(self):
        getSupported = False
        try:
            self.get()
            getSupported = True
        except AxisUnsupported:
            getSupported = False
        if getSupported:
            self.set(1.0)
        else:
            self.turnUpKey.hold(5)


@Singleton
class Radiator(ContiniousCEAxis):
    def __init__(self):
        super().__init__(
            turnUpKey=WtFunctionalKey(keyshortcut.win32conComp.VK_RIGHT_MID_BRACKET),
            turnDownKey=WtFunctionalKey(keyshortcut.win32conComp.VK_LEFT_MID_BRACKET),
            switchManualControlKey=WtFunctionalKey(
                [
                    win32con.VK_RMENU,
                    keyshortcut.win32conComp.VK_RIGHT_MID_BRACKET,
                ]
            ),
            solution=SolutionOfRadiatorOilRadiatorPropPitch(self),
        )

    @GetFailureToAxisUnsupported
    def get(self, newest=None):
        return (
            Port8111Cache()
            .get(Port8111.QueryType.state, newest)
            .expectValid()
            .engine.radiator.value[0]
            / 100
        )


@Singleton
class PropPitch(ContiniousCEAxis):
    def __init__(self):
        super().__init__(
            turnUpKey=WtFunctionalKey(keyshortcut.win32conComp.VK_QUOTE),
            turnDownKey=WtFunctionalKey(keyshortcut.win32conComp.VK_SEMICOLON),
            switchManualControlKey=WtFunctionalKey(
                [win32con.VK_RMENU, keyshortcut.win32conComp.VK_QUOTE]
            ),
            solution=SolutionOfRadiatorOilRadiatorPropPitch(self),
        )

    @GetFailureToAxisUnsupported
    def get(self, newest=None):
        return (
            Port8111Cache()
            .get(Port8111.QueryType.state, newest)
            .expectValid()
            .engine.RPM_throttle.value[0]
            / 100
        )


@Singleton
class Supercharger(DiscreteCEAxis):
    def __init__(self):
        super().__init__(
            switchTapPositionKey=WtFunctionalKey(
                [
                    keyshortcut.win32conComp.VK_ADD,
                ]
            ),
            solution=[
                Solution(
                    toEnable=lambda: SwitchManualEngineControl.press(),
                    toDisable=lambda: SwitchManualEngineControl.press(),
                ),
            ],
        )

    @GetFailureToAxisUnsupported
    def get(self, newest=None):
        return (
            Port8111Cache()
            .get(Port8111.QueryType.state, newest)
            .expectValid()
            .engine.compressor_stage.value[0]
        )


@Singleton
class Altitude(ReadOnlyAxis):

    @GetFailureToAxisUnsupported
    def get(self, newest=None):
        indi: Port8111.BeanIndicatorAir = (
            Port8111Cache()
            .get(Port8111.QueryType.indicator, newest)
            .expectValid()
            .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
        )
        return Coalesce(indi.altitude_hour, indi.altitude_min, indi.altitude_10k)


@Singleton
class OilTemp(ReadOnlyAxis):

    @GetFailureToAxisUnsupported
    def get(self, newest=None):
        indi: Port8111.BeanIndicatorAir = (
            Port8111Cache()
            .get(Port8111.QueryType.indicator, newest)
            .expectValid()
            .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
        )
        return indi.oil_temperature


@Singleton
class WaterTemp(ReadOnlyAxis):

    @GetFailureToAxisUnsupported
    def get(self, newest=None):
        indi: Port8111.BeanIndicatorAir = (
            Port8111Cache()
            .get(Port8111.QueryType.indicator, newest)
            .expectValid()
            .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
        )
        return indi.water_temperature


@Singleton
class VehicleName(ReadOnlyAxis):

    @GetFailureToAxisUnsupported
    def get(self, newest=None):
        return (
            Port8111Cache()
            .get(Port8111.QueryType.indicator, newest)
            .expectValid()
            .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
            .type
        )


def getGauges():
    return Gauges(
        oilRadiator=OilRadiator(),
        radiator=Radiator(),
        propPitch=PropPitch(),
        supercharger=Supercharger(),
        altitude=Altitude(),
        oilTemp=OilTemp(),
        waterTemp=WaterTemp(),
    )


@Singleton
class EngineMan:
    planeName: str = None
    serviceClass: typing.Callable = None
    serviceInstance: EngineConfig = None
    lastCheckTime: float = None
    services: dict[str, EngineConfigBean] = dict()

    def __init__(self):
        self.gauges = getGauges()
        for i in EngineConfigHost.GetConfig():
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
            except Exception as err:
                """
                get failure and axisunsupported failure are processed in get and set,
                config.check wont need to face them
                stop signal passes by to the outter loop
                """
                if isinstance(
                    err,
                    DetachedEngineManStopSignal.DetachedEngineManStopSignalCalledException,
                ):
                    raise err
                else:
                    print(err)
                    GSLogger().logger.error(err)
                    traceback.print_exc()
                    raise err

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
            planeName = VehicleName().get()
        except AxisUnsupported:
            planeName = None
        self.setService(planeName)
        if self.seviceNowValid():
            if (
                time.perf_counter() - self.lastCheckTime
                > self.services[planeName].checkRate
            ):
                GSLogger().logger.debug(
                    f"engineman service doing checking, {planeName=}"
                )
                self.serviceDoCheck()


class DetachedEngineMan(StoppableThread):
    def __init__(self, pool: keyshortcut.ThreadPoolExecutor = None) -> None:
        super().__init__(
            StoppableSomewhat.StrategyRunOnRunning.stop_and_rerun,
            StoppableSomewhat.StrategyError.print_error,
            pool,
        )

    def stop(self):
        DetachedEngineManStopSignal().set()
        super().stop()

    def foo(self):
        em = EngineMan()
        DetachedEngineManStopSignal().reset()
        while True:
            if self.timeToStop():
                break
            try:
                em.check()
            except (
                DetachedEngineManStopSignal.DetachedEngineManStopSignalCalledException
            ):
                ...
            PreciseSleep(detachedEngineManLoopInterval)
