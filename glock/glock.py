from concurrent.futures import ThreadPoolExecutor
from utilitypack.util_solid import StoppableThread
from utilitypack.util_wt import *
import keyshortcut.gameinput as gameinput
from .glock_config import *


class Reporter:
    def __init__(self, interval, reportBusiness) -> None:
        self.t0 = time.perf_counter()
        self.interval = interval
        self.reportBusiness = reportBusiness

    def update(self):
        tnow = time.perf_counter()
        if tnow - self.t0 > self.interval:
            self.reportBusiness()
            self.t0 = tnow


class GPush(StoppableProcess):
    ratio: float
    disabled = -1
    full = 2

    @staticmethod
    def isFull(x):
        return x > 1

    @staticmethod
    def isZero(x):
        return x < 0

    def __init__(
        self, ratio: multiprocessing.Value, bad8111Exit: multiprocessing.Event
    ) -> None:
        self.ratio = ratio
        self.bad8111Exit = bad8111Exit
        super().__init__(
            strategy_runonrunning=StoppableThread.StrategyRunOnRunning.skip_and_return,
        )

    def foo(self):
        def report():
            if not GPush.isZero(ratio):
                Rhythms.Notify.play()
            if print_ctrl_ratio:
                print(f"ratio: {self.ratio.value}")

        reporter = Reporter(5, report)
        period = 0.025
        while not self.timeToStop() and not self.bad8111Exit.is_set():
            ratio = self.ratio.value
            if GPush.isZero(ratio):
                # diabled
                PreciseSleep(period)
            elif GPush.isFull(ratio):
                # key will be realeased until some point that not full
                gameinput.keydown(ord("S"))
                PreciseSleep(period)
            else:
                topush = ratio * period
                torelax = (1 - ratio) * period
                gameinput.hold(ord("S"), topush)
                # PreciseSleep(topush)
                PreciseSleep(torelax)
            reporter.update()


class SepDerivativer:
    def __init__(self, val0, t0):
        self.val0 = val0
        self.t0 = t0

    def update(self, v, t):
        ret = (v - self.val0) / (t - self.t0)
        self.val0 = v
        self.t0 = t
        return ret


class Sampler(StoppableProcess):
    def __init__(
        self,
        ratio: multiprocessing.Value,
        bad8111Exit: multiprocessing.Event,
        lim: float,
    ) -> None:
        super().__init__(
            StoppableThread.StrategyRunOnRunning.skip_and_return,
            StoppableThread.StrategyError.print_error,
        )
        self.ratio = ratio
        self.bad8111Exit = bad8111Exit
        self.lim = lim

    def foo(self):
        GMax = 13
        pushMax = (self.lim - GMax) * (-0.5) / (GMax - 1)
        fullPushExceed = (GMax - self.lim) * 0.75
        controller = PIDController(
            kp=0.05 * 1 / fullPushExceed,
            ki=1.0 * 1 / fullPushExceed,
            kd=0.2 * 1 / fullPushExceed,
            integralLimitMax=0,
            integralLimitMin=-fullPushExceed,
            # analizerMode=True,
        )
        # input filter
        oolfi = OneOrderLinearFilter(0, 0)
        # control filter
        oolfc = OneOrderLinearFilter(0, 0)
        fps = fpsmanager(10)

        def calcEnerge(h, tas):
            return h * 9.8 + 0.5 * tas**2

        state = Port8111.get(Port8111.QueryType.state)
        if state is None or state.valid is False:
            energyNow = 0
        else:
            energyNow = calcEnerge(state.H.value, state.TAS.value)
        sepderi = SepDerivativer(energyNow, time.perf_counter())
        ps4pid = perf_statistic(startnow=True)
        # dc = []
        ps4dctime = perf_statistic(startnow=True)
        while not self.timeToStop():
            fps.WaitUntilNextFrame(sleepImpl=PreciseSleep)
            """
            request.get always return until the last millisecond before time out
            """
            state = Port8111.get(Port8111.QueryType.state, timeout=0.1)
            if state is None or state.valid is False:
                self.bad8111Exit.set()
                break
            # if state.Ny is None:
            #     breakpoint()

            # sep = sepderi.update(
            #     calcEnerge(state.H.value, state.TAS.value), time.perf_counter()
            # )
            g = state.Ny.value
            # aoa = state.AoA.value

            index = g
            index = oolfi.update(index)
            # allow negative error to clear intergraled error
            # ctrl, an = controller.update(self.lim - index, ps4pid.time())
            ctrl = controller.update(self.lim - index, ps4pid.time())
            ctrl = oolfc.update(ctrl)
            ps4pid.clear().start()
            # ctrl in negative, since its pushing.
            if ctrl < -1:
                # max pushing rate is 1.
                self.ratio.value = GPush.full
            elif ctrl > 0:
                # and i dont want pulling.
                self.ratio.value = GPush.disabled
            else:
                # smooth controlling
                self.ratio.value = abs(ctrl)
        #     dc.append(
        #         copy.deepcopy(
        #             (
        #                 ps4dctime.time(),
        #                 -index / 10,
        #                 ctrl,
        #                 an.partp,
        #                 an.parti,
        #                 an.partd,
        #                 an.error,
        #                 an.integral,
        #                 an.derivative,
        #             )
        #         )
        #     )
        # save_list_to_xls(
        #     [
        #         (
        #             "t",
        #             "index",
        #             "ctrl",
        #             "partP",
        #             "partI",
        #             "partD",
        #             "error",
        #             "integral",
        #             "derivative",
        #         )
        #     ]
        #     + dc,
        #     f"glock_dc_{GetTimeString()}.xlsx",
        # )


class GLock:
    def __init__(self):
        self.sharedRatio = multiprocessing.Value("d", 0.0)
        self.bad8111Exit = multiprocessing.Event()
        self.pusher: GPush = GPush(ratio=self.sharedRatio, bad8111Exit=self.bad8111Exit)
        self.sampler: Sampler = Sampler(
            ratio=self.sharedRatio, bad8111Exit=self.bad8111Exit, lim=glim
        )

    def setOn(self):
        self.bad8111Exit.clear()
        self.pusher.go()
        self.sampler.go()

    def setOff(self):
        self.pusher.stop()
        self.sampler.stop()

    def isRunning(self):
        return self.pusher.isRunning() and self.sampler.isRunning()


class Puller(StoppableProcess):
    def __init__(self) -> None:
        super().__init__(
            strategy_runonrunning=StoppableSomewhat.StrategyRunOnRunning.skip_and_return,
        )

    def foo(self):
        ratio = 0.5
        period = 0.1
        while not self.timeToStop():
            ontime = ratio * period
            offtime = (1 - ratio) * period
            gameinput.hold(ord("W"), ontime)
            PreciseSleep(offtime)
