
from wtdistmeaspy_achievement import *


def main():
    hud=fullScrHUD()
    hud.setcontent(np.zeros([h,w,3],np.uint8))
    hud.setup()
    screen=screenshoter(0)
    fps=fpsmanager(10)
    hotkey=hotkeymanager([
        192
    ])

    idleprompt="(=w=)"
    prompt=idleprompt
    contentlefttime=time.perf_counter()
    def setcontentlefttime():
        nonlocal contentlefttime
        contentlefttime=time.perf_counter()+10
    while(True):
        fps.next()
        keys=hotkey.getkeys()
        if keys[192]: 
            '''
            VK_OEM_3=0xC0
            Used for miscellaneous characters; it can vary by keyboard.
            For the US standard keyboard, the '`~' key
            '''
            sleep(0.5) #for network delay
            scr=screen.shotbgr()
            #scr=cv.imread(r'./asset/wtdistmeaspy/shot.png')
            scr=cutBottomRightMap(scr)
            
            #keep collecting
            needdbglog=False
            ret=SolveMap_BottomRightSmallMap(scr)
            if didSolveMapSucceed(ret):
                state,playerpos,playererr,ympos,ymerr,gridave,griderr=ret
                def strictErrCheck():
                    return playererr>4 or ymerr<0.7 or griderr>4
                ympos=np.array(ympos)
                playerpos=np.array(playerpos)
                dist=np.sqrt(((ympos-playerpos)**2).sum())/gridave
                refresult=['%3d: %5d'%(r, int(dist*r+0.5)) for r in reflist]
                prompt=''
                prompt+='%s\n'%(state)
                if strictErrCheck():
                    prompt+='Not recommended to use for err sake, dbglog will be done\n'
                    needdbglog=True
                prompt+='dist=%5f\n'%(dist)
                prompt+='pe=%5.3f,ye=%5.3f,ge=%5.3f\n'%(playererr,ymerr,griderr)
                prompt+='{}'.format('\n'.join(refresult))
            else:
                #really failed
                prompt=ret[0]
                needdbglog=True
            if needdbglog:
                ret=SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}/'.format(
                    time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime())
                    ))
            setcontentlefttime()

        if time.perf_counter()>contentlefttime:
            prompt=idleprompt
        m=np.zeros([h,w,3],np.uint8)
        m=outputlines2mat(m,np.array(outputpos),prompt)
        m=addShadow2HUD(m)
        hud.setcontent(m)
        hud.update()


def testground():
    pass

main()