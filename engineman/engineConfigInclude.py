import dataclasses
import typing


class Axis:
    def set(self, target): ...

    def get(self, newest=None): ...


@dataclasses.dataclass
class Gauges:
    oilRadiator: Axis
    radiator: Axis
    propPitch: Axis
    supercharger: Axis
    altitude: Axis


class AxisUnsupported(Exception): ...


class EngineConfig:

    def check(self, gauges: Gauges): ...


@dataclasses.dataclass
class EngineConfigBean:
    clazz: typing.Callable
    planeName: str | list[str]
    engineConfigName: str
    checkRate: float


class EngineConfigHost:

    @staticmethod
    def Register(
        planeName: str | list[str],
        checkRate: float = 5,
        engineConfigName: str = "",
    ):
        def toGetLogic(engineConfig: typing.Callable):
            if not hasattr(EngineConfigHost, "__configs__"):
                EngineConfigHost.__configs__ = list()
            EngineConfigHost.__configs__.append(
                EngineConfigBean(engineConfig, planeName, engineConfigName, checkRate)
            )
            return engineConfig

        return toGetLogic

    @staticmethod
    def GetConfigs():
        return EngineConfigHost.__configs__


def SetSuperchargerByAlt(gauges: Gauges, switchAlt: list):
    alt = gauges.altitude.get()
    if alt is not None:
        destStage = 0
        for i, a in enumerate(switchAlt):
            if alt > a:
                destStage = i
        gauges.supercharger.set(destStage + 1)


def MappingByStage(sections: list[tuple[float, float]]):
    """
    [
        [None, 1],
        [1000, 2],
        [2000, 3],
    ]
    """

    def mapping(x):
        ret = None
        for i, (spliter, val) in enumerate(sections):
            if i == 0:
                ret = val
            elif x >= spliter:
                ret = val
            else:
                break
        assert ret is not None
        return ret
    return mapping


def MappingAxis(axSrc: Axis, axDest: Axis, mapping: typing.Callable):
    axDest.set(mapping(axSrc.get()))
