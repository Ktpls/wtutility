from concurrent.futures import ThreadPoolExecutor
from re import T

from flask.scaffold import F
from utilitypack.util_solid import StoppableThread
from utilitypack.util_wt import *
import keyshortcut.gameinput as gameinput


class GPush(StoppableThread):
    def __init__(self, pool: ThreadPoolExecutor = None) -> None:
        super().__init__(
            strategy_runonrunning=StoppableThread.Strategy_RunOnRunning.stop_and_rerun,
            pool=pool,
        )

    def foo(self, ctrl):
        gameinput.hold(ord("w"), ctrl)


class ArbGLock:
    def __calcEnerge(self, h, tas):
        return h * 9.8 + 0.5 * tas**2

    def __init__(self, lim, pool=None):
        state = Port8111.get(Port8111.QueryType.state)
        self.lastEnergy = self.__calcEnerge(state.H, state.TAS)
        self.lastFreshTime = time.perf_counter()
        self.oolf = OneOrderLinearFilter(10, 0)
        self.lim = lim
        self.controller = PIDController(kP=0.1, kI=0.0, kD=0.0)
        self.pusher = GPush(pool=pool)

    def business(self):
        state = Port8111.get(Port8111.QueryType.state)
        timeNow = time.perf_counter()
        g = state.Ny
        aoa = state.AoA
        energyNow = self.__calcEnerge(state.H, state.TAS)
        sep = (energyNow - self.lastEnergy) / (timeNow - self.lastFreshTime)
        self.lastEnergy = energyNow
        self.lastFreshTime = timeNow

        index = g
        index = self.oolf.update(index)

        err = ReLU(index - self.lim)
        ctrl = self.controller.update(err)
        if err > 0:
            # push negative g
            self.pusher.go(ctrl)
            return True, ctrl
        return False, 0
