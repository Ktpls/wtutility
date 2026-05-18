from utilref import *
from utilitypack.util_app import *
from utilitypack.util_windows import *
from utilitypack.util_winkey import *
import keyshortcut.keyshortcutimpl as keyshortcut
from time import sleep
import traceback
import win32process


def mainloop(fps, hotkeyactionlist=list(), businesslist=list()):
    fps = FpsManager(fps)
    # main loop
    hkm = HotkeyManager(hotkeyactionlist)

    while True:
        fps.WaitUntilNextFrame()
        decideresult = hkm.decideAllHotKey()
        try:
            hkm.doAllDecidedKey(decideresult, True, False)
        except SystemExit as e:
            raise e
        except Exception as e:
            Rhythms.Error.play()
            print("#" * 10)
            traceback.print_exc()
            print("#" * 10)

        for bus in businesslist:
            try:
                bus()
            except Exception as e:
                Rhythms.Error.play()
                print("#" * 10)
                traceback.print_exc()
                print("#" * 10)


def AllTheWayOnErr(msg):
    Rhythms.Error.play()
    print(msg)
    os.system("pause")
    exit()


class ExecutableCommand:
    def __init__(self, ptr, cmd, hproc) -> None:
        self.ptr = ptr
        self.cmd = cmd
        self.hproc = hproc

    def __del__(self):
        if self.TestNop():
            self.SetCmd()

    @staticmethod
    def from_ptr_len(ptr, len, hproc):
        return ExecutableCommand(
            ptr, win32process.ReadProcessMemory(hproc, ptr, len), hproc
        )

    def TestNop(self):
        buf = win32process.ReadProcessMemory(self.hproc, self.ptr, len(self.cmd))
        return all([b == 0x90 for b in buf])

    def SetNop(self):
        windll.kernel32.WriteProcessMemory(
            ctypes.c_uint64(self.hproc.handle),
            ctypes.c_uint64(self.ptr),
            ctypes.c_buffer(b"\x90" * len(self.cmd)),
            ctypes.c_uint64(len(self.cmd)),
            ctypes.c_uint64(0),
        )

    def SetCmd(self):
        windll.kernel32.WriteProcessMemory(
            ctypes.c_uint64(self.hproc.handle),
            ctypes.c_uint64(self.ptr),
            ctypes.c_buffer(self.cmd),
            ctypes.c_uint64(len(self.cmd)),
            ctypes.c_uint64(0),
        )

    def autoSwitch(self):
        if self.TestNop():
            self.SetCmd()
            Rhythms.Cancel.play()
        else:
            self.SetNop()
            Rhythms.GoodNotify.play()


class ActionRepeater(StoppableThread):
    def __init__(self, period) -> None:
        super().__init__()
        self.peroid = period

    def action(self):
        raise NotImplementedError()

    def foo(self):
        while self.isRunning():
            self.action()
            time.sleep(self.peroid)

    def autoSwitch(self):
        if not self.isRunning():
            self.go()
            Rhythms.GoodNotify.play()
        else:
            self.stop()
            Rhythms.Cancel.play()


class MousePressRepeater(ActionRepeater):
    def __init__(self, key, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.key = key

    def action(self):
        mouse.click(self.key)


class KeyPressRepeater(ActionRepeater):
    def __init__(self, key, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.key = key

    def action(self):
        Keyboard.KeyPress(self.key)


class MacroApp(BulletinApp):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.hotkeySwitch = Switch(
            onSetOn=lambda: self.bulletin.putup(BulletinBoard.Poster("hkmEnabled")),
            onSetOff=lambda: self.bulletin.putup(BulletinBoard.Poster("hkmDisabled")),
            value=True,
        )
        self.bhhk = self.BindHotkeyHoldKeyboard(self)

    class BindHotkeyHoldKeyboard:
        registered_holdings = set()

        def __init__(self, app: "MacroApp"):
            self.app = app

        def bind_cleanning(self):
            @self.app.Hotkey(f"Clear all holding", [win32con.VK_LMENU, ord("C")])
            @self.app.WithHotkeySwitch()
            def foo(*_):
                self.app.bulletin.putup(BulletinBoard.Poster(f"Clear all holding", 1))
                for key in self.registered_holdings:
                    Keyboard.KeyUp(key)

        def bind(self, name, key):
            self.registered_holdings.add(key)

            @self.app.Hotkey(f"Hold {name}", [win32con.VK_LMENU, key])
            @self.app.WithHotkeySwitch()
            @self.app.Async()
            def foo(*_):
                self.app.bulletin.putup(BulletinBoard.Poster(f"waiting {name}", 1))
                Keyboard.KeyUp(key)
                for i in range(3):
                    time.sleep(0.1)
                Keyboard.KeyDown(key)
                self.app.bulletin.putup(BulletinBoard.Poster(f"holding {name}", 1))

    def bind_hold_mouse_left(app):
        @app.Hotkey("HoldLeft", [win32con.VK_RCONTROL, win32con.VK_F10])
        @app.WithHotkeySwitch()
        def holdLeft():
            mouse.down(0)
            app.bulletin.putup(BulletinBoard.Poster("leftHolding", 1))

    def BasicHotkey(app):

        for key, dire, name in [
            [
                win32con.VK_UP,
                keyshortcut.MoveMouseDirection.up,
                "Up",
            ],
            [
                win32con.VK_LEFT,
                keyshortcut.MoveMouseDirection.left,
                "Left",
            ],
            [
                win32con.VK_DOWN,
                keyshortcut.MoveMouseDirection.down,
                "Down",
            ],
            [
                win32con.VK_RIGHT,
                keyshortcut.MoveMouseDirection.right,
                "Right",
            ],
        ]:
            app.HotkeyFullFunction(
                f"MoveMouse{name}",
                [win32con.VK_LCONTROL, key],
                onKeyPress=app.WithHotkeySwitch()(
                    functools.partial(keyshortcut.move_mouse, dire)
                ),
            )

        @app.Hotkey(
            "Reboot", [win32con.VK_RCONTROL, win32con.VK_RSHIFT, win32con.VK_F12]
        )
        @app.WithHotkeySwitch()
        def rebootfoo():
            app.hud.stop()
            bootAsAdmin(__file__)
            Rhythms.Reboot.play()
            sys.exit()

        @app.Hotkey(
            "HKDisable", [win32con.VK_RCONTROL, win32con.VK_RSHIFT, win32con.VK_F11]
        )
        def taskSwitch():
            app.hotkeySwitch.switch()

    @EasyWrapper
    def WithHotkeySwitch(f, app: "MacroApp"):
        def foo(*arg, **kw):
            if app.hotkeySwitch():
                f(*arg, **kw)
            else:
                app.bulletin.putup(BulletinBoard.Poster("hotkey disabled", 1))

        return foo
