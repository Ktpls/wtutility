from macroutility import *
import functools
import win32gui, win32api, win32process, win32con, pywintypes
from ctypes import *
import os
from utilref import StoppableThread



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
        ExecutableCommand.from_ptr_len(moduleBase + 0x36DBD6, 2, hproc),  #decDoubleJumpAndWrite
        ExecutableCommand.from_ptr_len(moduleBase + 0x40CA8E, 4, hproc),  #subStamineAndWrite
        ExecutableCommand.from_ptr_len(moduleBase + 0x4103F7, 4, hproc),  #setAttackUpperLimit
        ExecutableCommand.from_ptr_len(moduleBase + 0x414542, 6, hproc),  #poisonCountingDown
        ExecutableCommand.from_ptr_len(moduleBase + 0x4182D8, 4, hproc),  #consumingStamine
    ]
    [bcc.SetNop() for bcc in basicCmdControl]

    hotkeyaction = []

    # no falling
    nofalling = ExecutableCommand.from_ptr_len(moduleBase + 0x37A301, 4, hproc)
    hotkeyaction.append(
        HotkeyManager.hotkeytask(key=win32con.VK_F1,
                                 foo=functools.partial(
                                     ExecutableCommand.autoSwitch, nofalling)))

    # keep rushing
    def KeepRushing():
        Rhythms.Notify()
        Keyboard.KeyDownDelay(ord("P"))

    hotkeyaction.append(
        HotkeyManager.hotkeytask(key=win32con.VK_F2, foo=KeepRushing))

    # keep pressing x, c

    xpress = Keyboard.KeyPressRepeater(ord("X"), 0.2)
    hotkeyaction.append(
        HotkeyManager.hotkeytask(key=win32con.VK_F3,
                                 foo=functools.partial(
                                     Keyboard.KeyPressRepeater.autoSwitch, xpress)))

    cpress = Keyboard.KeyPressRepeater(ord("C"), 1)
    hotkeyaction.append(
        HotkeyManager.hotkeytask(key=win32con.VK_F4,
                                 foo=functools.partial(
                                     Keyboard.KeyPressRepeater.autoSwitch, cpress)))

    def beepexit():
        win32api.Beep(1000, 300)
        win32api.Beep(1000, 300)
        win32api.Beep(1000, 300)
        exit()

    hotkeyaction.append(
        HotkeyManager.hotkeytask(key=win32con.VK_F12, foo=beepexit))

    print('init finished')
    print(f'hwnd={hwnd:X}')
    print(f'hproc={pid:X}')
    print(f'module={moduleBase:X}')
    Rhythms.Success()
    mainloop(10, hotkeyaction)
    win32api.CloseHandle(hproc)


main()