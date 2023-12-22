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
        period = 0.5
        while not self.ifTimeToStop():
            ratio = self.ratio
            if ratio == GPush.disabled:
                PreciseSleep(period)
                continue
            if ratio > 1:
                ratio = 1
            topush = ratio * period
            torelax = (1 - ratio) * period
            gameinput.hold(gameinput.keycode.key_S, topush)
            PreciseSleep(torelax)

    def config(self, ratio):
        self.ratio = ratio


class Sampler(StoppableThread):
    g: float
    aoa: float
    sep: float

    def __init__(self, pool: ThreadPoolExecutor = None) -> None:
        super().__init__(
            StoppableThread.Strategy_RunOnRunning.stop_and_rerun,
            StoppableThread.Strategy_Error.ignore,
            pool,
        )

    def foo(self):
        pass
    
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


class GLock:
    def __calcEnerge(self, h, tas):
        return h * 9.8 + 0.5 * tas**2

    def __init__(self, lim, pool=None):
        state = Port8111.get(Port8111.QueryType.state)
        if state is None or state.valid is False:
            self.lastEnergy = 0
        else:
            self.lastEnergy = self.__calcEnerge(state.H.value, state.TAS.value)
        self.lastFreshTime = time.perf_counter()
        self.oolf = OneOrderLinearFilter(3, 0)
        self.lim = lim
        self.controller = PIDController(kp=0.15, ki=0, kd=0.0)
        self.pusher: GPush = GPush(pool=pool).go()

    def business(self):
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

        index = g
        index = self.oolf.update(index)

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
