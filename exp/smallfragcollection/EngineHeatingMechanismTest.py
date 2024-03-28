from utilref import *
from globalsys.globalsys import *


fmroot = r"C:\file\code\notByMe\War-Thunder-Datamine-master\aces.vromfs.bin_u\gamedata\flightmodels\fm"


@dataclasses.dataclass
class EngineLoad:
    WaterTemperature: float
    OilTemperature: float
    WorkTime: float
    RecoverTime: float
    CurProgress: float


class MechanismTest:
    planeName: str = None
    loadn: list = list()
    valid: bool = False
    oilHealth: float = 1
    waterHealth: float = 1
    lastFuelAmount: float
    ps = perf_statistic()

    def recoverEngineHealth(self):
        self.ps.clear().start()
        self.oilHealth = 1
        self.waterHealth = 1

    def findLoadStage(self, val, key):
        for i in range(len(self.loadn)):
            if i >= len(self.loadn) - 1:
                return i
            if val < self.loadn[i + 1][key]:
                return i

    def getDamage(self, dt, val, loadNKey):
        stage = self.findLoadStage(val, loadNKey)
        workTime = self.loadn[stage].get("WorkTime", None)
        if workTime is None:
            damage = 0
        else:
            damage = dt / workTime
        return damage

    def refresh(self):
        try:
            # indicator = (
            #     Port8111.get(Port8111.QueryType.indicator)
            #     .expectValid()
            #     .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
            # )
            indicator = Port8111.BeanIndicatorAir(
                valid=True,
                type="itp-m1",
                oil_temperature=100,
                water_temperature=120,
                fuel=100,
            )
            planeName = indicator.type
        except Port8111.FetchFailure:
            planeName = None
        if planeName is None:
            self.valid = False
            self.planeName = None
            return
        elif planeName != self.planeName:
            # init plane
            blkx = ReadTextFile(os.path.join(fmroot, f"{planeName}.blkx"))
            blkx = json.loads(blkx)
            loadn = [
                (int(regex.findall("^Load(\d+)$", k)[0]), v)
                for k, v in blkx["EngineType0"]["Temperature"].items()
                if regex.match("^Load\d+$", k)
            ]
            loadn.sort(key=lambda x: x[0])
            loadn = [l[1] for l in loadn]
            self.planeName = planeName
            self.loadn = loadn
            self.lastFuelAmount = indicator.fuel
            self.recoverEngineHealth()

        newFuel = indicator.fuel
        # delta fuel here must overcome fuel value error
        if newFuel > self.lastFuelAmount + 0.1:
            # consider it as got refueled
            self.recoverEngineHealth()
        self.lastFuelAmount = newFuel
        dt = self.ps.time()
        self.ps.clear().start()

        self.oilHealth = max(
            0,
            self.oilHealth
            - self.getDamage(dt, indicator.oil_temperature, "OilTemperature"),
        )
        self.waterHealth = max(
            0,
            self.waterHealth
            - self.getDamage(dt, indicator.water_temperature, "WaterTemperature"),
        )


m = MechanismTest()
while True:
    m.refresh()
    print(f"{m.planeName=}, {m.oilHealth=}, {m.waterHealth=}")
    time.sleep(1)
