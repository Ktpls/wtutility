from .engineConfigInclude import *


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
        SetSuperchargerByAlt(gauges, [1700])


@EngineConfigHost.Register(planeName="j2m5_30mm")
class Raiden(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(0.30)
        gauges.propPitch.set(0.95)
        SetSuperchargerByAlt(gauges, [2500])
