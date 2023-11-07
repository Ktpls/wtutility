from .util_solid import *
from .util_np import *
from .util_ocv import *

"""
windows
"""

from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
import win32api
import win32con
import win32gui
import win32ui


def getWTHwnd():
    ret = win32gui.FindWindow("DagorWClass", None)
    if ret == win32con.NULL:
        raise Exception("FindWindow() failed")
    return ret


class screenshoter:
    # reconstructed with no mfc

    def __init__(self, hwnd=0):
        self.wthwnd = hwnd
        # r = RECT()
        # windll.user32.GetClientRect(self.hwnd, byref(r))
        # self.res=[r.right,r.bottom]
        self.res = [1920, 1080]
        self.wtdc = windll.user32.GetDC(self.wthwnd)
        self.mydc = windll.gdi32.CreateCompatibleDC(self.wtdc)
        self.mybitmap = windll.gdi32.CreateCompatibleBitmap(
            self.wtdc, self.res[0], self.res[1]
        )
        windll.gdi32.SelectObject(self.mydc, self.mybitmap)

    def __del__(self):
        windll.gdi32.DeleteObject(self.mybitmap)
        windll.gdi32.DeleteObject(self.mydc)
        windll.user32.ReleaseDC(self.wthwnd, self.wtdc)

    def shot(self):
        if (
            windll.gdi32.BitBlt(
                self.mydc,
                0,
                0,
                self.res[0],
                self.res[1],
                self.wtdc,
                0,
                0,
                win32con.SRCCOPY,
            )
            == 0
        ):
            raise BaseException("bad shot, {}".format(windll.kernel32.GetLastError()))
        # 截图是BGRA排列，因此总元素个数需要乘以4
        total_bytes = self.res[0] * self.res[1] * 4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte * total_bytes
        windll.gdi32.GetBitmapBits(
            self.mybitmap, total_bytes, byte_array.from_buffer(buffer)
        )
        return np.frombuffer(buffer, dtype=np.uint8).reshape(
            self.res[1], self.res[0], 4
        )

    def shotbgr(self):
        return self.shot()[:, :, :3]

    def shotgray(self):
        return cv.cvtColor(self.shot(), cv.COLOR_BGRA2GRAY)


def activeWindow(hwnd):  # 窗口置顶
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOP,
        0,
        0,
        0,
        0,
        win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW,
    )
    win32gui.SetForegroundWindow(hwnd)


def bootAsAdmin(file):
    # pass in __file__
    quotedpy = '"' + file + '"'
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, quotedpy, None, 1
    )


def setadmin(file):
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        bootAsAdmin(file)
        exit()


class fullScrHUD:
    """
    #init
    hud=fullScrHUD()
    hud.setup()
    ...
    #main loop
    #preparing to show
    hud.clear
    #init m1
    m1=hud.getblankscreen()
    #draw sth on m1
    #then add m1 to hud
    hud.addcontent(m1)
    #or overwrite directly
    hud.writecontent(m1)
    #do the same for m2...
    ...
    #ask hud to show
    hud.update()
    ...
    #on exit
    hud.stop()
    """

    def __init__(self) -> None:
        self.resolution = [1080, 1920]
        self.terminate = False
        self.hwnd = 0
        self.m2show = self.getblankscreenwithalfa()
        self.m2draw = self.getblankscreenwithalfa()
        # set m2draw

    def setup(self):
        def WndProc(hwnd, msg, wParam, lParam):
            if msg == win32con.WM_PAINT:
                rect = win32gui.GetClientRect(hwnd)
                hdc, ps = win32gui.BeginPaint(hwnd)
                # background
                # hbr=win32gui.CreateSolidBrush(0x0000000)
                # win32gui.FillRect(hdc,rect,hbr)
                # win32gui.DeleteObject(hbr)

                w = self.resolution[1]
                h = self.resolution[0]
                mfcDC = win32ui.CreateDCFromHandle(hdc)
                hcdc = mfcDC.CreateCompatibleDC()
                BitMap = win32ui.CreateBitmap()
                BitMap.CreateCompatibleBitmap(mfcDC, w, h)
                ctypes.WinDLL("gdi32.dll").SetBitmapBits(
                    BitMap.GetHandle(), w * h * 4, self.m2show.tobytes()
                )
                hcdc.SelectObject(BitMap)
                # myblendfunc=(win32con.AC_SRC_OVER,0,255,win32con.AC_SRC_ALPHA)
                # win32gui.AlphaBlend(hdc,0,0,w, h , hcdc.GetHandleAttrib(), 0,0,w, h,myblendfunc)
                win32gui.BitBlt(
                    hdc, 0, 0, w, h, hcdc.GetHandleAttrib(), 0, 0, win32con.SRCCOPY
                )
                win32gui.DeleteObject(BitMap.GetHandle())
                hcdc.DeleteDC()
                win32gui.EndPaint(hwnd, ps)
            elif msg == win32con.WM_SIZE:
                win32gui.InvalidateRect(hwnd, None, True)
            elif msg == win32con.WM_DESTROY:
                win32gui.PostQuitMessage(0)
            if self.terminate:
                win32gui.PostQuitMessage(0)
            return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

        def mainloop():
            wc = win32gui.WNDCLASS()
            hbrush = win32gui.CreateSolidBrush(0)
            wc.hbrBackground = hbrush
            wc.lpszClassName = "Python on Windows"
            wc.lpfnWndProc = WndProc
            reg = win32gui.RegisterClass(wc)

            hwnd = win32gui.CreateWindow(
                reg,
                "Python",
                win32con.WS_POPUP,
                0,
                0,
                self.resolution[1],
                self.resolution[0],
                0,
                0,
                0,
                None,
            )
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
            win32gui.UpdateWindow(hwnd)

            win32gui.SetWindowLong(
                hwnd,
                win32con.GWL_EXSTYLE,
                win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                + win32con.WS_EX_LAYERED
                + win32con.WS_EX_NOACTIVATE,
            )
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 0, win32con.LWA_COLORKEY)
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOPMOST,
                0,
                0,
                0,
                0,
                win32con.SWP_SHOWWINDOW + win32con.SWP_NOSIZE + win32con.SWP_NOMOVE,
            )
            windll.user32.SetWindowDisplayAffinity(
                hwnd, 0x11
            )  # WDA_EXCLUDEDFROMCAPUTURE
            # can not use WDA_MONITOR, or get totally black screen

            self.hwnd = hwnd
            win32gui.PumpMessages()

        t1 = threading.Thread(target=mainloop, args=())
        t1.start()
        time.sleep(1)

    def writecontent(self, lt, content):
        self.m2draw[
            lt[0] : lt[0] + content.shape[0],
            lt[1] : lt[1] + content.shape[1],
            : content.shape[2],
        ] = content

    def clear(self):
        self.m2draw[:, :, :] = 0

    def getblankscreen(self):
        return np.zeros(
            self.resolution
            + [
                3,
            ],
            np.uint8,
        )

    def getblankscreenwithalfa(self):
        return np.zeros(
            self.resolution
            + [
                4,
            ],
            np.uint8,
        )

    def addcontentwithalfa(self, m):
        self.m2draw += m

    def addcontent(self, m):
        alp = 255 * np.ones_like(m[:, :, 0:1])
        self.m2draw += np.concatenate((m, alp), 2)

    def update(self):
        # swap
        tmp = self.m2show
        self.m2show = self.m2draw
        self.m2draw = tmp

        # needless to clear cuz entire screen will be set
        win32gui.InvalidateRect(self.hwnd, None, False)

    def stop(self):
        self.terminate = True
        self.update()

    @staticmethod
    def reverseMat2FitWindowsCoor(m):
        return np.flip(m, axis=0)


def isKBDown(k):
    return bool(win32api.GetAsyncKeyState(k) and 0x1)


def isKBDownNow(k):
    return win32api.GetAsyncKeyState(k) and 0x8000


class HotkeyManager:
    """
    to piorer ctrl+c than c
    responde no c after doing ctrl+c
    issue:
    1. ctrl+a,ctrl+a and ctrl+a,ctrl+s
        fastly press ctrl+a, and ctrl+s, could cause slightly overlap whose key state is [ctrl,a,s] physically
        that is, [ctrl,a]->[ctrl,a,s]->[ctrl,s]
        so at the second state, both [ctrl+a,ctrl+a] and [ctrl+a,ctrl+s] are triggered
        not severe problem
    """

    @dataclasses.dataclass
    class ContiniousCallHandler:
        prevState: typing.List[bool] = dataclasses.field(default_factory=list)
        countiousPressTime: int = 0
        startRepeatPeriod: int = 10
        useControlOnContiniousPress: bool = True

        @staticmethod
        def __dictEq(a: typing.Dict[int, bool], b: typing.Dict[int, bool]):
            if len(a) != len(b):
                return False
            for k in a.keys():
                if k not in b.keys():
                    return False
                if a[k] != b[k]:
                    return False
            return True

        def updateState(self, newState):
            if HotkeyManager.ContiniousCallHandler.__dictEq(self.prevState, newState):
                self.countiousPressTime += 1
                return self.countiousPressTime >= self.startRepeatPeriod
            else:
                self.countiousPressTime = 0
                self.prevState = newState
                return True

    class hotkeytask:
        key: List[List[int]]

        def __init__(
            self,
            key: int | Iterable,
            foo: Callable[[], None],
            continiousPress: bool = False,
        ) -> None:
            if not isinstance(key, Iterable):
                self.key = [[key]]
            elif not isinstance(key[0], Iterable):
                self.key = [key]
            else:
                self.key = key
            # self.key is like [keyset1=[key1, key2], keyset2=[key3, key4]]
            self.foo = foo
            self.continiousPress = continiousPress
            self.stage = 0

        def tryRespond(self, respond: bool, anyRespondingExceptThis: bool):
            if respond:
                if self.stage == len(self.key) - 1:
                    # progress completed
                    self.stage = 0
                    self.foo()
                else:
                    self.stage += 1
            elif anyRespondingExceptThis:
                self.stage = 0

        def GetNowKey(self):
            return self.key[self.stage]

    @dataclasses.dataclass
    class Key:
        code: int

        def GetKeyDown(self):
            return isKBDown(self.code)

    def __init__(self, hotkeytasklist: List[hotkeytask]):
        keyconcerned = [hka.key for hka in hotkeytasklist]
        keyconcerned = list(itertools.chain.from_iterable(keyconcerned))
        keyconcerned = list(itertools.chain.from_iterable(keyconcerned))
        keyconcerned = deduplicate(keyconcerned)
        self.kc = [HotkeyManager.Key(k) for k in keyconcerned]

        # clear all previous state
        [k.GetKeyDown() for k in self.kc]

        self.hktl = hotkeytasklist
        self.cch = HotkeyManager.ContiniousCallHandler()

    def decideAllHotKey(self) -> List[bool]:
        keystate = {k.code: k.GetKeyDown() for k in self.kc}
        cchblocked = not self.cch.updateState(keystate)

        class respondstate(enum.Enum):
            false = 0
            true = 1
            unknown = 2

        respondtable = [
            respondstate.unknown
            if not cchblocked or hk.continiousPress
            else respondstate.false
            for hk in self.hktl
        ]

        def piorered(a: HotkeyManager.hotkeytask, b: HotkeyManager.hotkeytask):
            def include(a: HotkeyManager.hotkeytask, b: HotkeyManager.hotkeytask):
                for k in b.GetNowKey():
                    if k not in a.GetNowKey():
                        return False
                return True

            # a>b and b<a, not equal
            return include(a, b) and not include(b, a)

        # costly
        piorinfo = [
            [
                aidx
                for aidx, a in enumerate(self.hktl)
                if aidx != bidx and piorered(a, b)
            ]
            for bidx, b in enumerate(self.hktl)
        ]

        def decideRespondState(i):
            # checked
            if respondtable[i] != respondstate.unknown:
                return

            # all key pressed
            if all([keystate[k] for k in self.hktl[i].GetNowKey()]):
                # didnt check piored, check it
                [
                    decideRespondState(p)
                    for p in piorinfo[i]
                    if respondtable[p] == respondstate.unknown
                ]

                # no piored responded
                if all([respondtable[p] == respondstate.false for p in piorinfo[i]]):
                    respondtable[i] = respondstate.true
                else:
                    respondtable[i] = respondstate.false
            else:
                # not respond this
                respondtable[i] = respondstate.false

        for hkidx, hk in enumerate(self.hktl):
            decideRespondState(hkidx)

        assert all([rt != respondstate.unknown for rt in respondtable])
        r = [
            respondtable[hkidx] == respondstate.true
            for hkidx, hk in enumerate(self.hktl)
        ]
        return [
            respondtable[hkidx] == respondstate.true
            for hkidx, hk in enumerate(self.hktl)
        ]

    def doAllDecidedKey(self, decideresult, throwonerr=False, printonerr=False):
        AnyRespondingExceptThis = [
            any([(rb if i != j else False) for j, rb in enumerate(decideresult)])
            for i, ra in enumerate(decideresult)
        ]
        for i in range(len(decideresult)):
            try:
                self.hktl[i].tryRespond(decideresult[i], AnyRespondingExceptThis[i])
            except Exception as e:
                if printonerr:
                    traceback.print_exc()
                if throwonerr:
                    raise e
