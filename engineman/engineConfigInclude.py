import dataclasses
import typing


class Axis:
    def set(self, target): ...

    def get(self, mustUpdate=None): ...


@dataclasses.dataclass
class Gauges:
    oilRadiator: Axis
    radiator: Axis
    propPitch: Axis
    supercharger: Axis
    altitude: Axis


class AxisUnsupported(Exception):...


class EngineConfig:

    def check(self, gauges: Gauges): ...


@dataclasses.dataclass
class EngineConfigBean:
    clazz: typing.Callable
    planeName: str | list[str]
    engineConfigName: str
    checkRate: float


class EngineConfigHost:
    configs: "list[EngineConfigHost.EngineConfigBean]" = list()

    def Register(
        self,
        planeName: str | list[str],
        checkRate: float = 10,
        engineConfigName: str = "",
    ):
        def toGetLogic(engineConfig: typing.Callable):
            self.configs.append(
                EngineConfigBean(engineConfig, planeName, engineConfigName, checkRate)
            )
            return engineConfig

        return toGetLogic


engineConfigHost = EngineConfigHost()
