import dataclasses
import typing
import functools


class Axis:
    def set(self, target): ...

    def get(self, newest=None): ...


class LambdaAxis(Axis):
    def __init__(self, func):
        self.func = func

    def get(self, newest=None):
        return self.func()


@dataclasses.dataclass
class Gauges:
    oilRadiator: Axis
    radiator: Axis
    propPitch: Axis
    supercharger: Axis
    altitude: Axis
    oilTemp: Axis
    waterTemp: Axis


class AxisUnsupported(Exception): ...


class EngineConfig:

    def check(self, gauges: Gauges): ...


class SimpleEngineConfig(EngineConfig):
    PP = None
    RAD = None
    ORAD = None
    ALTSC = None
    SET_TO_MAX_ANYWAY = property(lambda self: "max")

    def check(self, gauges: Gauges):
        if self.PP is not None:
            gauges.propPitch.set(self.PP)
        if self.RAD is not None:
            gauges.radiator.set(self.RAD)
        if self.ORAD is not None:
            if self.ORAD == self.SET_TO_MAX_ANYWAY:
                gauges.oilRadiator.setToMaxAnyway()
            else:
                gauges.oilRadiator.set(self.ORAD)
        if self.ALTSC is not None:
            MappingAxis(
                gauges.altitude,
                gauges.supercharger,
                [
                    [None, 1],
                    [3750, 2],
                ],
            )


@dataclasses.dataclass
class EngineConfigBean:
    clazz: typing.Callable
    planeName: str | list[str]
    engineConfigName: str
    checkRate: float


class EngineConfigHost:
    __configs__ = list()

    @staticmethod
    def PutConfig(config: EngineConfigBean):
        EngineConfigHost.__configs__.append(config)

    @staticmethod
    def GetConfig():
        return EngineConfigHost.__configs__


def HostedEngineConfig(
    planeName: str | list[str],
    checkRate: float = 10,
    engineConfigName: str = "",
):
    def toGetLogic(engineConfig: typing.Callable):
        EngineConfigHost.PutConfig(
            EngineConfigBean(engineConfig, planeName, engineConfigName, checkRate)
        )
        return engineConfig

    return toGetLogic


def MappingAxis(axSrc: Axis, axDest: Axis, mapping: list[tuple[float, float]]):
    """
    mapping is like:
    [
        [None, 1],
        [1000, 2],
        [2000, 3],
    ]
    """
    assert len(mapping) >= 1
    val = axSrc.get()
    mapped = None
    for i in range(0, len(mapping)):
        if i + 1 >= len(mapping) or val < mapping[i + 1][0]:
            mapped = mapping[i][1]
            break
    axDest.set(mapped)
