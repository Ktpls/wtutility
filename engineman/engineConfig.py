from .engineConfigInclude import *

"""
in game control setting
Relative control step of radiator, oilRadiator, propPitch should set to 2%
"""


@EngineConfigHost.Register(planeName="g_55s", checkRate=60)
class G55S(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.oilRadiator.setToMaxAnyway()
        gauges.radiator.set(0.80)
        gauges.propPitch.set(0.95)


@EngineConfigHost.Register(planeName="yak-3_france")
class Yak3(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(0.20)
        gauges.propPitch.set(1.00)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            MappingByStage(
                [
                    [None, 1],
                    [1700, 2],
                ]
            ),
        )


@EngineConfigHost.Register(planeName="j2m5_30mm")
class Raiden(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(0.30)
        gauges.propPitch.set(0.95)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            MappingByStage(
                [
                    [None, 1],
                    [2500, 2],
                ]
            ),
        )


@EngineConfigHost.Register(planeName="i_29")
class I29(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(0.60)
        gauges.propPitch.set(1.00)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            MappingByStage(
                [
                    [None, 1],
                    [3500, 2],
                ]
            ),
        )


@EngineConfigHost.Register(planeName="p-63a-5_ussr")
class P63A5(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(1.0)
