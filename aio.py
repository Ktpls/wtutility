from utilitypack.utility import *
from aio_config import *
import traceback
import hashlib
import functools

bulletinoutputpos = (100, 500)
telescopepos = (100, 100)


def beepOnErr():
    win32api.Beep(1000, 1000)
    win32api.Beep(500, 1000)


@dataclasses.dataclass
class InputSession:
    @dataclasses.dataclass
    class SessionInstance:
        class SessionEndType(Enum):
            UNSPECIFIED = 0
            OK = 1
            CANCEL = 2

        content: str = ""
        sessionEndType: SessionEndType = SessionEndType.UNSPECIFIED

        def append(self, extraContent: str):
            self.content += extraContent

        def backSpace(self):
            self.content = self.content[:-1]

        def putup(self, bulletin: bulletinBoard):
            bulletin.putup(self.content)

    # foo that sets hkm and returns older hkm
    FooSwapHKM: Callable[[HotkeyManager], HotkeyManager]
    bulletin: bulletinBoard
    RunningSessionInstance: SessionInstance = dataclasses.field(
        default_factory=SessionInstance
    )
    hotkeymanagerStack: List[HotkeyManager] = dataclasses.field(default_factory=list)
    FooSessionDoneCallback: Callable[[SessionInstance], None] = dataclasses.field(
        init=False
    )

    def __GetHotkeyReg(self):
        @dataclasses.dataclass
        class KeyMapping:
            char: str
            key: int

        AllKeyMapping = [KeyMapping(k, 48 + i) for i, k in enumerate("0123456789")]
        KeyIndexed = {k.key: k.char for k in AllKeyMapping}

        def procKey(k):
            self.RunningSessionInstance.append(KeyIndexed.get(k, "?"))
            self.RunningSessionInstance.putup(self.bulletin)

        HotkeyReg = [
            HotkeyManager.hotkeytask(key=[k.key], foo=functools.partial(procKey, k.key))
            for k in AllKeyMapping
        ]

        def backSpace():
            self.RunningSessionInstance.backSpace()
            self.RunningSessionInstance.putup(self.bulletin)

        HotkeyReg.append(
            HotkeyManager.hotkeytask(
                key=[win32con.VK_BACK],
                foo=backSpace,
            )
        )

        def OutFromSession(endType: InputSession.SessionInstance.SessionEndType):
            self.RunningSessionInstance.sessionEndType = endType
            self.FooSessionDoneCallback(self.RunningSessionInstance)
            old = self.hotkeymanagerStack.pop()
            inputer = self.FooSwapHKM(old)

        HotkeyReg.extend(
            [
                HotkeyManager.hotkeytask(
                    key=[win32con.VK_ESCAPE],
                    foo=functools.partial(
                        OutFromSession,
                        InputSession.SessionInstance.SessionEndType.CANCEL,
                    ),
                ),
                HotkeyManager.hotkeytask(
                    key=[win32con.VK_RETURN],
                    foo=functools.partial(
                        OutFromSession, InputSession.SessionInstance.SessionEndType.OK
                    ),
                ),
            ]
        )

        return HotkeyReg

    def IntoSession(self, callback):
        self.RunningSessionInstance=InputSession.SessionInstance()
        self.FooSessionDoneCallback = callback
        inputer = HotkeyManager(self.__GetHotkeyReg())
        old = self.FooSwapHKM(inputer)
        self.hotkeymanagerStack.append(old)

    def GetContent(self):
        return self.content


def main():
    # 告示板
    idlebulletincontents = [
        ["(=w=)", 67],
        ["(>^<)", 30],
        ["($w$)", 1],
        ["(0w<)", 1],
        ["(0v0)", 1],
    ]

    # 每天固定一种
    seed = time.strftime("%Y-%m-%d", time.localtime()).encode("utf-8")
    seed = hashlib.md5(seed).digest()
    seed = int.from_bytes(seed[:8], "big")
    bulletin = bulletinBoard(
        idlebulletincontents[
            summonCard(
                [c[1] for c in idlebulletincontents],
                np.random.Generator(np.random.PCG64(seed)),
            )
        ][0]
    )

    # 日常运作的业务
    business = []
    # 热键
    hotkeyaction = []

    # wtdistmeas
    if usingwtdistmeaspy:
        print("wtdistmeaspy activated")
        import wtdistmeaspy

        wtdmp = wtdistmeaspy.wtdistmeaspy()
        """
        VK_OEM_3=0xC0
        Used for miscellaneous characters; it can vary by keyboard.
        For the US standard keyboard, the '`~' key
        """
        OEM3 = 0xC0

        def SwitchPlottingScaleLock():
            wtdmp.psLocked = not wtdmp.psLocked
            if wtdmp.psLocked:
                bulletin.putup("plotting scale locked")
            else:
                bulletin.putup("plotting scale unlocked")

        hotkeyaction.append(
            HotkeyManager.hotkeytask(
                key=[win32con.VK_SHIFT, OEM3], foo=SwitchPlottingScaleLock
            )
        )

        def hkcallWTDistMeas():
            bulletin.putup(wtdmp.solveMapMainLogic())

        hotkeyaction.append(HotkeyManager.hotkeytask(key=OEM3, foo=hkcallWTDistMeas))

        def startCali():
            lastStaged = wtdmp.lastDistMeasResultStaged.result
            if lastStaged is None:
                bulletin.putup("no staged dist result")
                return
            wtdmp.caliOperator.start(lastStaged)
            bulletin.putup(f"caliberating to {lastStaged}")

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=[win32con.VK_CONTROL, OEM3], foo=startCali)
        )

        def stopCali():
            wtdmp.caliOperator.stop()
            bulletin.putup(f"cali stopped")

        # not used that much. normally just switch out from snip mode
        # hotkeyaction.append(
        #     hotkeymanager.hotkeytask(key=[win32con.VK_SHIFT, OEM3], foo=stopCali)
        # )

        def SetPlottingScale():
            nonlocal inputSession
            bulletin.putup("input plotting scale")

            def SetPlottingScaleLock(session: InputSession.SessionInstance):
                if (
                    session.sessionEndType
                    == InputSession.SessionInstance.SessionEndType.OK
                ):
                    nonlocal wtdmp
                    wtdmp.psLocked = True
                    wtdmp.lastDistMeasResultStaged.plottingscale = int(session.content)
                    bulletin.putup(f"plotting scale locked at {session.content}")
                elif (
                    session.sessionEndType
                    == InputSession.SessionInstance.SessionEndType.CANCEL
                ):
                    bulletin.putup("plotting scale canceled")

            inputSession.IntoSession(SetPlottingScaleLock)

        hotkeyaction.append(
            HotkeyManager.hotkeytask(
                key=[win32con.VK_CONTROL, win32con.VK_SHIFT, OEM3],
                foo=SetPlottingScale,
            )
        )

    # telescope
    if usingtelescope:
        print("telescope activated")
        import telescope

        tele = telescope.telescope()

        def telemain():
            scope = tele.mainlooplogic()
            if scope is None:
                return
            hud.writecontent(np.flip(telescopepos), scope)

        business.append(telemain)

        def switchtele():
            tele.enabled = not tele.enabled

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=win32con.VK_F12, foo=switchtele)
        )

    # key shortcuts
    if usingkeyshortcut:
        print("keyshortcut activated")
        import keyshortcut

        def holdLeftAndTell():
            keyshortcut.holdMouseLeft()
            bulletin.putup("LeftHolding", 1)

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=win32con.VK_F10, foo=holdLeftAndTell)
        )

        def holdCAndTell():
            keyshortcut.holdC()
            bulletin.putup("CHolding", 1)

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=win32con.VK_F11, foo=holdCAndTell)
        )

        keylist = [
            win32con.VK_UP,
            win32con.VK_LEFT,
            win32con.VK_DOWN,
            win32con.VK_RIGHT,
        ]
        direction = ["up", "left", "down", "right"]
        kd = zip(keylist, direction)
        for pair in kd:
            hotkeyaction.append(
                HotkeyManager.hotkeytask(
                    key=[win32con.VK_CONTROL, pair[0]],
                    foo=functools.partial(keyshortcut.move_mouse, pair[1]),
                )
            )

    # eagle eye
    if usingeagleeye:
        import eagleeye

        eedcstate = False

        def eedcswitch():
            nonlocal eedcstate
            if eedcstate:
                eagleeye.cachedShots = []
                eedcstate = False
                bulletin.putup("eedc off", 1)
            else:
                eedcstate = True
                bulletin.putup("eedc on", 1)

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=win32con.VK_F8, foo=eedcswitch)
        )

        def eedcOnClickWithSwitch():
            if eedcstate:
                eagleeye.onClick()

        hotkeyaction.append(
            HotkeyManager.hotkeytask(key=win32con.VK_LBUTTON, foo=eedcOnClickWithSwitch)
        )
        business.append(eagleeye.onFrame)

    # reboot, not working on exit

    def rebootfoo():
        hud.stop()
        bootAsAdmin(__file__)
        dur = 100
        freqseq = [500, 750, 400]
        [win32api.Beep(f, dur) for f in freqseq]
        sys.exit()

    hotkeyaction.append(
        HotkeyManager.hotkeytask(
            key=[win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F12], foo=rebootfoo
        )
    )

    def TestInput():
        def callback(content, sessionType):
            print(sessionType)
            print(content)

        nonlocal inputSession
        inputSession.IntoSession(callback)

    hotkeyaction.append(
        HotkeyManager.hotkeytask(
            key=[win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F11], foo=TestInput
        )
    )

    hud = fullScrHUD()
    hud.setup()
    fps = fpsmanager(aiofps)
    hkm = HotkeyManager(hotkeyaction)

    def swapHKM(newHkm):
        nonlocal hkm
        old = hkm
        hkm = newHkm
        return old

    inputSession = InputSession(swapHKM, bulletin)

    # main loop
    while True:
        fps.WaitUntilNextFrame()
        hud.clear()

        decideresult = hkm.decideAllHotKey()
        for i in range(len(decideresult)):
            if decideresult[i]:
                try:
                    hkm.hktl[i].foo()
                except SystemExit as e:
                    raise e
                except Exception as e:
                    beepOnErr()
                    print("#" * 10)
                    traceback.print_exc()
                    print("#" * 10)
                    if throwErrorInHotkey:
                        raise e

        for bus in business:
            try:
                bus()
            except Exception as e:
                beepOnErr()
                print("#" * 10)
                traceback.print_exc()
                print("#" * 10)
                if throwErrorInBus:
                    raise e

        # show bulletin
        hud.writecontent(
            np.flip(bulletinoutputpos),
            aPicWithText(bulletin.read(), maxsize=[400, 700]),
        )

        hud.update()


main()
