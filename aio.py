from utilitypack.utility import *
import traceback
import wtdistmeaspy
import telescope
import navalKeyHolding

bulletinoutputpos = (100, 500)
telescopepos = (100, 100)


def main():
    hud = fullScrHUD()
    hud.setup()
    fps = fpsmanager(10)

    # 告示板
    idlebulletincontents = [
        ['(=w=)', 69],
        ['(>^<)', 30],
        ['(0v0)', 1],
    ]
    # 每天固定一种
    initPyRandom(time.strftime('%Y-%m-%d', time.localtime()))
    bulletin = bulletinBoard(
        idlebulletincontents[
            summonCard(
                integralProb(
                    [c[1] for c in idlebulletincontents]
                )
            )
        ][0]
    )

    # 业务
    business = []
    hotkeyaction = []

    # wtdistmeas

    def hkcallWTDistMeas():
        bulletin.putup(wtdistmeaspy.mainlogic(), 10)
    '''
    VK_OEM_3=0xC0
    Used for miscellaneous characters; it can vary by keyboard.
    For the US standard keyboard, the '`~' key
    '''
    hotkeyaction.append(hotkeymanager.hotkeytask(
        key=0xc0,
        foo=hkcallWTDistMeas
    ))

    # telescope
    tele = telescope.telescope()

    def telemain():
        scope = tele.mainlooplogic()
        if scope is None:
            return
        hud.writesubscenceoncontent(np.flip(telescopepos), scope)
    business.append(telemain)

    def switchtele():
        tele.enabled = not tele.enabled
    hotkeyaction.append(hotkeymanager.hotkeytask(
        key=win32con.VK_F12,
        foo=switchtele
    ))

    # naval left holding

    def holdAndTell():
        navalKeyHolding.holdMouseLeft()
        bulletin.putup('LeftHolding', 1)
    hotkeyaction.append(hotkeymanager.hotkeytask(
        key=win32con.VK_F10,
        foo=holdAndTell
    ))

    def holdCAndTell():
        navalKeyHolding.holdC()
        bulletin.putup('CHolding', 1)
    hotkeyaction.append(hotkeymanager.hotkeytask(
        key=win32con.VK_F11,
        foo=holdCAndTell
    ))

    # reboot, not working on exit

    def reboot():
        bootAsAdmin(__file__)
        win32api.Beep(1000, 1000)
        exit(0)
    # hotkeyaction.append(hotkeymanager.hotkeytask(
        # key= [win32con.VK_CONTROL,win32con.VK_F11,win32con.VK_F11],
        # foo= reboot
    # ))

    # main loop
    hkm = hotkeymanager(hotkeyaction)

    while (True):
        fps.next()
        keystate = hkm.getkeys()
        hud.clear()
        try:
            [hkf.foo() for hkf in hotkeyaction if hotkeymanager.iskeycalling(
                hkf.key, keystate)]
        except SystemExit as e:
            raise e
        except BaseException as e:
            traceback.print_exc()
        try:
            [bus() for bus in business]
        except BaseException as e:
            traceback.print_exc()

        # show bulletin
        hud.writesubscenceoncontent(
            np.flip(bulletinoutputpos), aPicWithText(bulletin.read()))

        hud.update()


main()
