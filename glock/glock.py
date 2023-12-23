from concurrent.futures import ThreadPoolExecutor
from re import T
from tkinter import NO

from flask.scaffold import F
from utilitypack.util_solid import StoppableThread
from utilitypack.util_wt import *
import keyshortcut.gameinput as gameinput


class GPush(StoppableThread):
    ratio: float
    disabled = None

    def __init__(self, pool: ThreadPoolExecutor = None) -> None:
        self.ratio = 0
        super().__init__(
            strategy_runonrunning=StoppableThread.Strategy_RunOnRunning.stop_and_rerun,
            pool=pool,
        )

    def foo(self):
        period = 0.2
        while not self.ifTimeToStop():
            ratio = self.ratio
            if ratio == GPush.disabled:
                PreciseSleep(period)
                continue
            if ratio > 1:
                ratio = 1
            if ratio < 0:
                ratio = 0
            topush = ratio * period
            torelax = (1 - ratio) * period
            gameinput.hold(gameinput.keycode.key_S, topush)
            PreciseSleep(torelax)

    def config(self, ratio):
        self.ratio = ratio


class Sampler(StoppableThread):
    def __init__(self, pool: ThreadPoolExecutor = None) -> None:
        super().__init__(
            StoppableThread.Strategy_RunOnRunning.stop_and_rerun,
            StoppableThread.Strategy_Error.ignore,
            pool,
        )
        state = Port8111.get(Port8111.QueryType.state)
        if state is None or state.valid is False:
            self.lastEnergy = 0
        else:
            self.lastEnergy = self.__calcEnerge(state.H.value, state.TAS.value)
        self.lastFreshTime = time.perf_counter()

        self.oolf = OneOrderLinearFilter(1, 0)
        self.g = 0
        self.aoa = 0
        self.sep = 0

    def foo(self):
        period = 0.1
        while not self.ifTimeToStop():
            self.sampleNow()
            sleep(period)

    def sampleNow(self):
        state = Port8111.get(Port8111.QueryType.state)
        if state is None or state.valid is False:
            return False, 0
        timeNow = time.perf_counter()
        if state.Ny is None:
            breakpoint()
        g = state.Ny.value
        aoa = state.AoA.value
        energyNow = self.__calcEnerge(state.H.value, state.TAS.value)
        sep = (energyNow - self.lastEnergy) / (timeNow - self.lastFreshTime)
        self.lastEnergy = energyNow
        self.lastFreshTime = timeNow

        g = self.oolf.update(g)

        self.g = g
        self.aoa = aoa
        self.sep = sep

    def __calcEnerge(self, h, tas):
        return h * 9.8 + 0.5 * tas**2


class GLock:
    def __init__(self, lim, pool=None):
        self.lim = lim
        self.controller = PIDController(kp=0.9, ki=0, kd=0.0)
        self.pusher: GPush = GPush(pool=pool).go()
        self.sampler: Sampler = Sampler(pool=pool).go()

    def business(self):
        index = self.sampler.g

        err = ReLU(index - self.lim)
        ctrl = self.controller.update(err)
        if ctrl > 1:
            ctrl = 1
        if err > 0:
            # push negative g
            self.pusher.config(ctrl)
            # gameinput.hold(gameinput.keycode.key_S, ctrl)
            return True, ctrl
        else:
            self.pusher.config(GPush.disabled)
            return False, 0
