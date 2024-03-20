from .engineConfigInclude import *
from .utilref import *

"""
in game control setting

radiator, oilRadiator, propPitch
    Relative control step = 0%
    Sensitivity = 50%
"""


@HostedEngineConfig(planeName="g_55s", checkRate=60)
class G55S(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(0.80)
        gauges.oilRadiator.setToMaxAnyway()


@HostedEngineConfig(planeName="yak-3_france")
class Yak3(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(1.00)
        gauges.radiator.set(0.25)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [2350, 2],
            ],
        )


@HostedEngineConfig(planeName="j2m5_30mm")
class Raiden(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(0.35)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [2400, 2],
            ],
        )


@HostedEngineConfig(planeName="i_29")
class I29(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(1.00)
        gauges.radiator.set(0.60)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [3500, 2],
            ],
        )


@HostedEngineConfig(planeName="p-63a-5_ussr")
class P63A5(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(0.4)


@HostedEngineConfig(planeName="saab_j21a_1")
class SaabJ21A(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.75)
        gauges.oilRadiator.set(1.0)
        gauges.radiator.set(1.0)


@HostedEngineConfig(planeName="il_8_1944")
class Il8(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(0.5)


@HostedEngineConfig(planeName="be_6")
class Be6(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.93)
        gauges.radiator.set(1.0)


@HostedEngineConfig(planeName="itp_m1")
class Itp(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.52)
        gauges.radiator.set(1.0)
        gauges.oilRadiator.set(1.0)


@HostedEngineConfig(planeName="p-47d_ussr")
class P47D(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(1.0)
        gauges.oilRadiator.set(1.0)
