from utility import *
import traceback
import wtdistmeaspy
import telescope
import navalKeyHolding

bulletinoutputpos = (100, 500)
telescopepos = (100, 100)


def iskeycalling(key, keystate):
    if type(key) is int:
        key = [key]
    return all([keystate[k] for k in key])


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
    hotkeyaction.append({
        'key': 0xC0,
        'foo': hkcallWTDistMeas
    })


    #telescope
    tele = telescope.telescope()
    def telemain():
        scope = tele.mainlooplogic()
        if scope is None:
            return
        m = hud.getblankscreenwithalfa()
        m[telescopepos[0]:telescopepos[0]+scope.shape[0],
          telescopepos[1]:telescopepos[1]+scope.shape[1], :] = scope
        m[:,:,3]=100
        hud.addcontentwithalfa(m)
    business.append(telemain)

    def switchtele():
        tele.enabled = not tele.enabled
    hotkeyaction.append({
        'key': win32con.VK_F12,
        'foo': switchtele
    })


    def holdAndTell():
        navalKeyHolding.holdMouseLeft()
        bulletin.putup('LeftHolding',1)
    hotkeyaction.append({
        'key':win32con.VK_F10,
        'foo':holdAndTell
    })


    #main loop
    hkm = hotkeymanager(list(deduplicate([b['key'] for b in hotkeyaction])))

    while (True):
        fps.next()
        keystate = hkm.getkeys()
        hud.clear()
        try:
            [hkf['foo']() for hkf in hotkeyaction if iskeycalling(hkf['key'], keystate)]
        except BaseException as e:
            traceback.print_exc()
        try:
            [bus() for bus in business]
        except BaseException as e:
            traceback.print_exc()

        # show bulletin
        m = hud.getblankscreen()
        m = outputlines2mat(m, np.array(bulletinoutputpos), bulletin.read())
        m = addShadow2HUD(m)
        hud.addcontent(m)

        hud.update()


main()
