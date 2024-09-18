from utilitypack.util_app import *
from utilitypack.util_winkey import *
from utilitypack.util_wt import *

k_exit = HotkeyManager.Key(win32conComp.VK_F12)
k_glock = HotkeyManager.Key(win32conComp.VK_OEM_3)


@dataclasses.dataclass
class Glock2:
    ratio: float
    dutyCycle: float = 0.5
    ps: perf_statistic = dataclasses.field(init=False, default_factory=perf_statistic)
    swEnable: Switch = dataclasses.field(init=False, default=None)
    swPwm: Switch = dataclasses.field(init=False, default=None)
    swPush: Switch = dataclasses.field(init=False, default=None)

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
                self.ps.clear().start()
        else:
            if self.ps.time() >= self.offTime:
                self.swPwm.on()
                self.ps.clear().start()
        if self.swEnable() and self.swPwm():
            self.swPush.on()
        else:
            self.swPush.off()


fpsm = FpsManager(60)
gl = Glock2(0.4, 0.5)
while True:
    fpsm.WaitUntilNextFrame()
    if k_exit.GetKeyDown():
        Rhythms.GoodNotify.asyncPlay()
        break
    if k_glock.GetKeyDown():
        gl.swEnable.on()
    else:
        gl.swEnable.off()
    gl.update()
