from utilitypack.util_solid import StoppableThread
from utilitypack.cold.util_solid import StoppableProcess
from utilitypack.util_wt import *
from utilitypack.util_winkey import *
from .glock_config import *
from shared.globalsys import *
import queue
import pandas as pd


@dataclasses.dataclass
class Glock2:
    ratio: float
    dutyCycle: float = g2DutyCycle
    ps: perf_statistic = dataclasses.field(init=False, default_factory=perf_statistic)
    swEnable: Switch = dataclasses.field(init=False, default=None)
    swPwm: Switch = dataclasses.field(init=False, default=None)
    swPush: Switch = dataclasses.field(init=False, default=None)
    k_glock = [win32conComp.VK_OEM_3]

    def __post_init__(self):
        self.onTime = self.dutyCycle * self.ratio
        self.offTime = self.dutyCycle * (1 - self.ratio)

        def pushOn():
            Keyboard.KeyDown(ord("S"))
            # print('s down')

        def pushOff():
            Keyboard.KeyUp(ord("S"))
            # print('s up')

        self.swPush = Switch(
            onSetOn=pushOn,
            onSetOff=pushOff,
        )

        self.swEnable = Switch()
        self.swPwm = Switch()
        self.ps.start()

    def update(self):
        if self.swPwm():
            if self.ps.time() >= self.onTime:
                self.swPwm.off()
                self.ps.start()
        else:
            if self.ps.time() >= self.offTime:
                self.swPwm.on()
                self.ps.start()
        if self.swEnable() and self.swPwm():
            self.swPush.on()
        else:
            self.swPush.off()

    def __del__(self):
        self.swEnable.off()
        self.swPwm.off()
        self.swPush.off()


class AnalizeLog:
    @dataclasses.dataclass
    class frame:
        dt: float
        g: float
        ratio: float

    def __init__(self):
        self.data = pd.DataFrame(
            columns=[n for n in AnalizeLog.frame.__annotations__.keys()]
        )
        self.planeName = "M4K"

    def log_data(self, frame: "AnalizeLog.frame"):
        # 创建一个新的行数据
        new_row = pd.DataFrame([BeanUtil.toMap(frame)])

        # 将新行追加到DataFrame
        self.data = pd.concat([self.data, new_row], ignore_index=True)

        # 保存数据到CSV文件
        self.data.to_csv(f"{self.planeName}.csv", index=False)


al = AnalizeLog()


@dataclasses.dataclass
class Glock3:
    """
    works for most of planes
    but mirage 4000 got oscilation
    """

    ratio: float
    pool: futures.ThreadPoolExecutor
    dutyCycle: float = g2DutyCycle
    tmPwm: SingleSectionedTimer = dataclasses.field(
        init=False, default_factory=SingleSectionedTimer
    )
    tmPid: SingleSectionedTimer = dataclasses.field(
        init=False, default_factory=SingleSectionedTimer
    )
    swEnable: Switch = dataclasses.field(init=False, default=None)
    swPwm: Switch = dataclasses.field(init=False, default=None)
    swPush: Switch = dataclasses.field(init=False, default=None)
    pid: PIDController = dataclasses.field(init=False, default=None)
    k_glock = [win32conComp.VK_OEM_3]
    asyncGetRatioRunning: bool = dataclasses.field(init=False, default=False)

    def asyncGetRatio(self):
        g = Port8111.get(Port8111.QueryType.state).expectValid().Ny.value
        dt = self.tmPid.get()
        self.tmPid.start()
        ratio = self.pid.update(g - gLimit, dt)
        self.ratio = ratio
        self.asyncGetRatioRunning = False
        # al.log_data(AnalizeLog.frame(dt, 0.1 * g, ratio))

    def __post_init__(self):
        def pushOn():
            Keyboard.KeyDown(ord("S"))

        def pushOff():
            Keyboard.KeyUp(ord("S"))

        self.swPush = Switch(
            onSetOn=pushOn,
            onSetOff=pushOff,
        )

        def enable():
            self.tmPid.start()

        def disable():
            self.tmPid.clear()

        self.swEnable = Switch(onSetOn=enable, onSetOff=disable)
        self.swPwm = Switch()
        self.tmPwm.start()

        self.pid = PIDController(
            g3PP,
            g3PI,
            0,
            integralLimitMin=g3RatioMin / g3PI,
            integralLimitMax=g3RatioMax / g3PI,
        )
        self.tmPid.start()

    def update(self):
        if self.swPwm():
            if self.tmPwm.get() >= self.dutyCycle * self.ratio:
                self.swPwm.off()
                self.tmPwm.start()
        else:
            if self.tmPwm.get() >= self.dutyCycle * (1 - self.ratio):
                self.swPwm.on()
                self.tmPwm.start()
        if self.swEnable() and self.swPwm():
            self.swPush.on()
        else:
            self.swPush.off()
        if (
            self.swEnable()
            and self.tmPid.get() >= g3QueryInterval
            and not self.asyncGetRatioRunning
        ):
            self.pool.submit(Glock3.asyncGetRatio, self)

    def __del__(self):
        self.swEnable.off()
        self.swPwm.off()
        self.swPush.off()
