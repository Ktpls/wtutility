from macroutility import *
import functools
import win32gui, win32api, win32process, win32con, pywintypes
from ctypes import *
import os
from utilref import StoppableThread


def BeepErr():
    win32api.Beep(1000, 2000)


def BeepOk():
    win32api.Beep(1000, 500)


def BeepCancel():
    win32api.Beep(500, 500)


def AllTheWayOnErr(msg):
    BeepErr()
    print(msg)
    os.system('pause')
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
            ptr, win32process.ReadProcessMemory(hproc, ptr, len), hproc)

    def TestNop(self):
        buf = win32process.ReadProcessMemory(self.hproc, self.ptr,
                                             len(self.cmd))
        return all([b == 0x90 for b in buf])

    def SetNop(self):
        windll.kernel32.WriteProcessMemory(c_uint64(self.hproc.handle),
                                           c_uint64(self.ptr),
                                           c_buffer(b'\x90' * len(self.cmd)),
                                           c_uint64(len(self.cmd)),
                                           c_uint64(0))

    def SetCmd(self):
        windll.kernel32.WriteProcessMemory(c_uint64(self.hproc.handle),
                                           c_uint64(self.ptr),
                                           c_buffer(self.cmd),
                                           c_uint64(len(self.cmd)),
                                           c_uint64(0))

    def autoSwitch(self):
        if self.TestNop():
            self.SetCmd()
            BeepCancel()
        else:
            self.SetNop()
            BeepOk()


class KeyPressRepeater(StoppableThread):

    def __init__(self, key, peroid) -> None:
        super().__init__()
        self.key = key
        self.peroid = peroid

    def foo(self):
        while (self.getRunning()):
            key_down(self.key)
            time.sleep(0.01)
            key_up(self.key)
            time.sleep(self.peroid)

    def autoSwitch(self):
        if not self.getRunning():
            self.go()
            BeepOk()
        else:
            self.stop()
            BeepCancel()


def main():
    # hacking preparation
    hwnd = win32gui.FindWindow("ASTLIBRA Revision", "ASTLIBRA Revision")
    if hwnd == win32con.NULL:
        AllTheWayOnErr("bad window")
    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    if pid == win32con.NULL:
        AllTheWayOnErr("bad process")

    hproc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
    moduleBase = win32process.EnumProcessModules(hproc)
    moduleBase = moduleBase[0]

    basicCmdControl = [
        ExecutableCommand.from_ptr_len(moduleBase + 0x3593E0, 4, hproc),  #subVitAndWrite
        ExecutableCommand.from_ptr_len(moduleBase + 0x40CA8E, 4, hproc),  #subStamineAndWrite
        ExecutableCommand.from_ptr_len(moduleBase + 0x4103F7, 4, hproc),  #setAttackUpperLimit
        ExecutableCommand.from_ptr_len(moduleBase + 0x4182D8, 4, hproc),  #consumingStamine
        ExecutableCommand.from_ptr_len(moduleBase + 0x414542, 6, hproc),  #poisonCountingDown
        ExecutableCommand.from_ptr_len(moduleBase + 0x36DBD6, 2, hproc),  #decDoubleJumpAndWrite
    ]
    [bcc.SetNop() for bcc in basicCmdControl]

    hotkeyaction = []

    # no falling
    nofalling = ExecutableCommand.from_ptr_len(moduleBase + 0x37A301, 4, hproc)
    hotkeyaction.append(
        hotkeymanager.hotkeytask(key=win32con.VK_F1,
                                 foo=functools.partial(
                                     ExecutableCommand.autoSwitch, nofalling)))

    # keep rushing
    def KeepRushing():
        BeepOk()
        key_down(keycode.key_P)

    hotkeyaction.append(
        hotkeymanager.hotkeytask(key=win32con.VK_F2, foo=KeepRushing))

    # keep pressing x, c

    xpress = KeyPressRepeater(keycode.key_X, 0.2)
    hotkeyaction.append(
        hotkeymanager.hotkeytask(key=win32con.VK_F3,
                                 foo=functools.partial(
                                     KeyPressRepeater.autoSwitch, xpress)))

    cpress = KeyPressRepeater(keycode.key_C, 1)
    hotkeyaction.append(
        hotkeymanager.hotkeytask(key=win32con.VK_F4,
                                 foo=functools.partial(
                                     KeyPressRepeater.autoSwitch, cpress)))

    def beepexit():
        win32api.Beep(1000, 300)
        win32api.Beep(1000, 300)
        win32api.Beep(1000, 300)
        exit()

    hotkeyaction.append(
        hotkeymanager.hotkeytask(key=win32con.VK_F12, foo=beepexit))

    print('init finished')
    print(f'hwnd={hwnd:X}')
    print(f'hproc={pid:X}')
    print(f'module={moduleBase:X}')
    BeepOk()
    mainloop(10, hotkeyaction)
    win32api.CloseHandle(hproc)


main()