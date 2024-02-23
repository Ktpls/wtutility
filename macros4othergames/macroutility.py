from utilref import *
from keyshortcut.gameinput import *
from time import sleep
import traceback
import win32process


def mainloop(fps, hotkeyactionlist=list(), businesslist=list()):
    fps = fpsmanager(fps)
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
            Rythm.RythmError.play()
            print("#" * 10)
            traceback.print_exc()
            print("#" * 10)

        for bus in businesslist:
            try:
                bus()
            except Exception as e:
                Rythm.RythmError.play()
                print("#" * 10)
                traceback.print_exc()
                print("#" * 10)


def AllTheWayOnErr(msg):
    Rythm.RythmError.play()
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
            Rythm.RythmCancel.play()
        else:
            self.SetNop()
            Rythm.RythmGoodNotify.play()


class KeyPressRepeater(StoppableThread):
    def __init__(self, key, peroid) -> None:
        super().__init__()
        self.key = key
        self.peroid = peroid

    def foo(self):
        while self.getRunning():
            key_down(self.key)
            time.sleep(0.01)
            key_up(self.key)
            time.sleep(self.peroid)

    def autoSwitch(self):
        if not self.getRunning():
            self.go()
            Rythm.RythmGoodNotify.play()
        else:
            self.stop()
            Rythm.RythmCancel.play()
