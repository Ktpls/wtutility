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
    __configs__ = list()

    @staticmethod
    def GetConfigs():
        return EngineConfigHost.__configs__


def HostedEngineConfig(
    planeName: str | list[str],
    checkRate: float = 5,
    engineConfigName: str = "",
):
    def toGetLogic(engineConfig: typing.Callable):
        EngineConfigHost.__configs__.append(
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
    mapped = mapping[0][1]
    for i in range(0, len(mapping)):
        if i + 1 >= len(mapping):
            mapped = mapping[i][1]
            break
        elif val <= mapping[i + 1][0]:
            mapped = mapping[i][1]
            break
    axDest.set(mapped)
