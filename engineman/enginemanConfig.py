from enginemanConfigInclude import *


@engineConfigHost.Register(planeName="g_55s", engineConfigName="g55s", checkRate=60)
class G55S(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.oilRadiator.setToMaxAnyway()
        gauges.radiator.set(0.80)
        gauges.propPitch.set(0.95)


@engineConfigHost.Register(planeName="yak-3_france", engineConfigName="yak3")
class Yak3(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(0.50)
        gauges.propPitch.set(0.95)
        alt = gauges.altitude.get()
        if alt is not None:
            if alt > 1700:
                gauges.supercharger.set(2)
            else:
                gauges.supercharger.set(1)
