from utilitypack.util_solid import StoppableThread
from utilitypack.cold.util_solid import StoppableProcess
from utilitypack.util_wt import *
from utilitypack.util_winkey import *
from .glock_config import *
from shared.globalsys import *
import queue
import pandas as pd


@dataclasses.dataclass
class PwmWithPid:
    pool: futures.ThreadPoolExecutor
    dutyCycle: float
    pidCycle: float
    pid: PIDController
    onPwmOn: typing.Callable[[], None]
    onPwmOff: typing.Callable[[], None]
    ratio: float = dataclasses.field(init=False, default=0)
    tmPwm: SingleSectionedTimer = dataclasses.field(
        init=False, default_factory=SingleSectionedTimer
    )
    tmPid: SingleSectionedTimer = dataclasses.field(
        init=False, default_factory=SingleSectionedTimer
    )
    swEnable: Switch = dataclasses.field(init=False, default=None)
    swPwm: Switch = dataclasses.field(init=False, default=None)
    swPush: Switch = dataclasses.field(init=False, default=None)
    updateRatioFuture: futures.Future = dataclasses.field(init=False, default=None)

    def getError(self): ...

    def _asyncUpdateRatio(self):
        err = self.getError()
        dt = self.tmPid.getAndRestart()
        ratio = self.pid.update(err, dt)
        self.ratio = ratio

    def __post_init__(self):

        self.swPush = Switch(
            onSetOn=self.onPwmOn,
            onSetOff=self.onPwmOff,
        )

        self.swEnable = Switch()
        self.swPwm = Switch()
        self.tmPwm.start()

        self.tmPid.start()

    def update(self):
        """
        module control_logic (
            input wire pidUpdatable,
            input wire swPwm,
            input wire swEnable,
            output reg swPush,
            output reg pidUpdate
        );
            always @(*) begin
                swPush = swPwm & swEnable;
                pidUpdate = pidUpdatable & swEnable;
            end
        endmodule
        """
        pidUpdatable = self.pidUpdatable()
        self.updatePwm()
        self.swPush.setTo(self.swPwm() and self.swEnable())
        pidUpdate = pidUpdatable & self.swEnable()

        if pidUpdate:
            self.updateRatioFuture = self.pool.submit(self._asyncUpdateRatio)

    def pidUpdatable(self):
        return self.tmPid.get() >= self.pidCycle and (
            self.updateRatioFuture is None or not self.updateRatioFuture.running()
        )

    def updatePwm(self):
        if abs((self.ratio if self.swPwm() else (1 - self.ratio)) - 1) <= EPS:
            # full in entire period
            pass
        else:
            if self.tmPwm.get() >= (
                self.dutyCycle * (self.ratio if self.swPwm() else (1 - self.ratio))
            ):
                self.swPwm.switch()
                self.tmPwm.start()

    def __del__(self):
        self.swEnable.off()
        self.swPwm.off()
        self.swPush.off()


class Glock(PwmWithPid):
    k_glock = [win32conComp.VK_OEM_3]

    def __init__(self, pool: futures.ThreadPoolExecutor, dutyCycle: float):
        super().__init__(
            pool=pool,
            dutyCycle=dutyCycle,
            pidCycle=g3QueryInterval,
            pid=PIDController(
                g3PP,
                g3PI,
                0,
                integralLimitMin=g3RatioMin / g3PI,
                integralLimitMax=g3RatioMax / g3PI,
            ),
            onPwmOn=lambda: Keyboard.KeyDown(ord("S")),
            onPwmOff=lambda: Keyboard.KeyUp(ord("S")),
        )

    def getError(self):
        g = (
            Port8111Cache()
            .get(Port8111.QueryType.state, newest=True)
            .expectValid()
            .Ny.value
        )
        return g - gLimit


class AileronTrim:
    k_autoAileronTrim = [
        win32conComp.VK_CONTROL,
        win32conComp.VK_MENU,
        win32conComp.VK_A,
    ]
    k_autoAileronTrim = [
        win32conComp.VK_CONTROL,
        win32conComp.VK_MENU,
        win32conComp.VK_A,
    ]

    def __init__(self, pool: futures.ThreadPoolExecutor, dutyCycle: float):
        super().__init__(
            pool=pool,
            dutyCycle=dutyCycle,
            pidCycle=g3QueryInterval,
            pid=PIDController(
                g3PP,
                g3PI,
                0,
                integralLimitMin=g3RatioMin / g3PI,
                integralLimitMax=g3RatioMax / g3PI,
            ),
            onPwmOn=lambda: Keyboard.KeyDown(ord("S")),
            onPwmOff=lambda: Keyboard.KeyUp(ord("S")),
        )
        self.swPidUpdate = Switch()

    def getError(self):
        g = (
            Port8111Cache()
            .get(Port8111.QueryType.state, newest=True)
            .expectValid()
            .Ny.value
        )
        return g - gLimit
