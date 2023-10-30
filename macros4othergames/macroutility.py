from utilref import fpsmanager, HotkeyManager, deduplicate
from gameinput import *
from time import sleep
import traceback


def mainloop(fps, hotkeyactionlist):
    fps = fpsmanager(fps)
    #main loop
    hkm = HotkeyManager(hotkeyactionlist)

    while (True):
        fps.WaitUntilNextFrame()
        hkm.doAllDecidedKey(hkm.decideAllHotKey(), throwonerr=True)



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