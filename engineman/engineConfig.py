from .engineConfigInclude import *
from utilitypack import *


@engineConfigHost.Register(planeName="g_55s", checkRate=60)
class G55S(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.oilRadiator.setToMaxAnyway()
        gauges.radiator.set(0.80)
        gauges.propPitch.set(0.95)


@engineConfigHost.Register(planeName="yak-3_france")
class Yak3(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(0.20)
        gauges.propPitch.set(1.00)
        alt = gauges.altitude.get()
        if alt is not None:
            if alt > 1700:
                gauges.supercharger.set(2)
            else:
                gauges.supercharger.set(1)


@engineConfigHost.Register(planeName="j2m5_30mm")
class Raiden(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(0.30)
        gauges.propPitch.set(0.95)
        alt = gauges.altitude.get()
        if alt is not None:
            if alt > 2500:
                gauges.supercharger.set(2)
            else:
                gauges.supercharger.set(1)
