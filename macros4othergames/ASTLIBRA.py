from macroutility import *
import functools
import win32gui, win32api, win32process, win32con, pywintypes
import ctypes
from ctypes import *
import os
from utilref import StoppableThread


def BeepErr():
    win32api.Beep(300, 2000)


def BeepOk():
    win32api.Beep(1000, 1000)


def BeepCancel():
    win32api.Beep(500, 1000)


def AllTheWayOnErr(msg):
    BeepErr()
    print(msg)
    os.system('pause')
    exit()


def main():
    # hacking preparation
    hwnd = win32gui.FindWindow("ASTLIBRA Revision", "ASTLIBRA Revision")
    if hwnd == win32con.NULL:
        AllTheWayOnErr("bad window")
    hproc = win32process.GetWindowThreadProcessId(hwnd)[1]
    if hproc == win32con.NULL:
        AllTheWayOnErr("bad process")

    hopenproc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, hproc)
    moduleBase = win32process.EnumProcessModules(hopenproc)
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
            windll.kernel32.WriteProcessMemory(c_uint64(hopenproc.handle),
                                               c_uint64(ptr), c_buffer((nop)),
                                               c_uint64(length), c_uint64(0))
            BeepOk()
        else:
            windll.kernel32.WriteProcessMemory(c_uint64(hopenproc.handle),
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
    class XPress(StoppableThread):

        def foo(self):
            while (self.getRunning()):
                key_down(keycode.key_X)
                time.sleep(0.01)
                key_up(keycode.key_X)
                time.sleep(0.2)

    xpress = XPress()

    def switchXPress():
        if not xpress.getRunning():
            #xpress.go(functools.partial(XPress.foo, xpress))
            xpress.go()
            BeepOk()
        else:
            xpress.stop()
            BeepCancel()

    hotkeyaction.append(
        hotkeymanager.hotkeytask(key=win32con.VK_F3, foo=switchXPress))

    print('init finished')
    print(f'hwnd={hwnd:X}')
    print(f'hproc={hproc:X}')
    print(f'module={moduleBase:X}')
    BeepOk()
    mainloop(10, hotkeyaction)
    win32api.CloseHandle(hopenproc)


main()