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


def main():

    # 告示板
    idlebulletincontents = [
        ['(=w=)', 66],
        ['(>^<)', 30],
        ['(0v0)', 1],
        ['($w$)', 1],
        ['(0w<)', 1],
        ['(@~@)', 1],
    ]
    # 每天固定一种

    seed = time.strftime('%Y-%m-%d', time.localtime()).encode('utf-8')
    seed = hashlib.md5(seed).digest()
    seed = int.from_bytes(seed[:8], 'big')
    bulletin = bulletinBoard(idlebulletincontents[summonCard(
        [c[1] for c in idlebulletincontents],
        np.random.Generator(np.random.PCG64(seed)))][0])

    # 日常运作的业务
    business = []
    # 热键
    hotkeyaction = []

    # wtdistmeas
    if usingwtdistmeaspy:

        import wtdistmeaspy

        def hkcallWTDistMeas():
            bulletin.putup(wtdistmeaspy.mainlogic(), 10)

        '''
        VK_OEM_3=0xC0
        Used for miscellaneous characters; it can vary by keyboard.
        For the US standard keyboard, the '`~' key
        '''
        hotkeyaction.append(
            hotkeymanager.hotkeytask(key=0xc0, foo=hkcallWTDistMeas))

        def startCali():
            lastStaged = wtdistmeaspy.lastDistMeasResultStaged.result
            if lastStaged is None:
                bulletin.putup("no staged dist result", 10)
                return
            wtdistmeaspy.caliOperator.start(lastStaged)
            bulletin.putup(f"caliberating to {lastStaged}", 10)

        hotkeyaction.append(
            hotkeymanager.hotkeytask(key=[win32con.VK_CONTROL, 0xc0],
                                     foo=startCali))

        def stopCali():
            wtdistmeaspy.caliOperator.stop()
            bulletin.putup(f"stopped", 10)

        hotkeyaction.append(
            hotkeymanager.hotkeytask(key=[win32con.VK_SHIFT, 0xc0],
                                     foo=stopCali))

    # telescope
    if usingtelescope:
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
            hotkeymanager.hotkeytask(key=win32con.VK_F12, foo=switchtele))

    # key shortcuts
    if usingkeyshortcut:

        import keyshortcut

        def holdLeftAndTell():
            keyshortcut.holdMouseLeft()
            bulletin.putup('LeftHolding', 1)

        hotkeyaction.append(
            hotkeymanager.hotkeytask(key=win32con.VK_F10, foo=holdLeftAndTell))

        def holdCAndTell():
            keyshortcut.holdC()
            bulletin.putup('CHolding', 1)

        hotkeyaction.append(
            hotkeymanager.hotkeytask(key=win32con.VK_F11, foo=holdCAndTell))

        keylist = [
            win32con.VK_UP, win32con.VK_LEFT, win32con.VK_DOWN,
            win32con.VK_RIGHT
        ]
        direction = ['up', 'left', 'down', 'right']
        kd = zip(keylist, direction)
        for pair in kd:
            hotkeyaction.append(
                hotkeymanager.hotkeytask(key=[win32con.VK_CONTROL, pair[0]],
                                         foo=functools.partial(
                                             keyshortcut.move_mouse, pair[1])))

    # eagle eye
    if usingeagleeye:
        import eagleeye
        eedcstate = False

        def eedcswitch():
            nonlocal eedcstate
            if eedcstate:
                eagleeye.cachedShots = []
                eedcstate = False
                bulletin.putup('eedc off', 1)
            else:
                eedcstate = True
                bulletin.putup('eedc on', 1)

        hotkeyaction.append(
            hotkeymanager.hotkeytask(key=win32con.VK_F8, foo=eedcswitch))

        def eedcOnClickWithSwitch():
            if eedcstate:
                eagleeye.onClick()

        hotkeyaction.append(
            hotkeymanager.hotkeytask(key=win32con.VK_LBUTTON,
                                     foo=eedcOnClickWithSwitch))
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
        hotkeymanager.hotkeytask(
            key=[win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_F12],
            foo=rebootfoo))

    # main loop
    hud = fullScrHUD()
    hud.setup()
    fps = fpsmanager(aiofps)
    hkm = hotkeymanager(hotkeyaction)

    while (True):
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
                    if throwErrorInHotkey:
                        raise e
                    traceback.print_exc()

        for bus in business:

            try:
                bus()
            except Exception as e:
                beepOnErr()
                traceback.print_exc()
                if throwErrorInBus:
                    raise e

        # show bulletin
        hud.writecontent(np.flip(bulletinoutputpos),
                         aPicWithText(bulletin.read(), maxsize=[400, 700]))

        hud.update()


main()
