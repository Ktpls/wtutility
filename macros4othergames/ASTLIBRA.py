from macroutility import *
import functools
import win32gui, win32api, win32process, win32con, pywintypes
import ctypes
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

    @staticmethod
    def from_ptr_len(self, ptr, len, hproc):
        return ExecutableCommand(
            ptr, win32process.ReadProcessMemory(hproc, ptr, len), hproc)

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

    hotkeyaction = []

    # no falling
    withNoVelocity = False

    def switchVerticalVelocityLock():
        nonlocal withNoVelocity
        ptr = moduleBase + 0x37A301
        length = 4
        nop = b'\x90\x90\x90\x90'
        cmd = b'\xf3\x0f\x58\xf8'
        withNoVelocity = not withNoVelocity
        if withNoVelocity:
            windll.kernel32.WriteProcessMemory(c_uint64(hproc.handle),
                                               c_uint64(ptr), c_buffer((nop)),
                                               c_uint64(length), c_uint64(0))
            BeepOk()
        else:
            windll.kernel32.WriteProcessMemory(c_uint64(hproc.handle),
                                               c_uint64(ptr), c_buffer(cmd),
                                               c_uint64(length), c_uint64(0))
            BeepCancel()

    hotkeyaction.append(
        hotkeymanager.hotkeytask(key=win32con.VK_F1,
                                 foo=switchVerticalVelocityLock))

    # keep rushing
    def KeepRushing():
        BeepOk()
        key_down(keycode.key_P)

    hotkeyaction.append(
        hotkeymanager.hotkeytask(key=win32con.VK_F2, foo=KeepRushing))

    # keep pressing x
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

    xpress = KeyPressRepeater(keycode.key_X, 0.2)

    def switchXPress():
        if not xpress.getRunning():
            xpress.go()
            BeepOk()
        else:
            xpress.stop()
            BeepCancel()

    hotkeyaction.append(
        hotkeymanager.hotkeytask(key=win32con.VK_F3, foo=switchXPress))

    cpress = KeyPressRepeater(keycode.key_C, 1)

    def switchCPress():
        if not cpress.getRunning():
            cpress.go()
            BeepOk()
        else:
            cpress.stop()
            BeepCancel()

    hotkeyaction.append(
        hotkeymanager.hotkeytask(key=win32con.VK_F4, foo=switchCPress))

    print('init finished')
    print(f'hwnd={hwnd:X}')
    print(f'hproc={pid:X}')
    print(f'module={moduleBase:X}')
    BeepOk()
    mainloop(10, hotkeyaction)
    win32api.CloseHandle(hproc)


main()