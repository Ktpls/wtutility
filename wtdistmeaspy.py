
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
            # ret=SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}/'.format(
            #         time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime())
            #         ))
            if didSolveMapSucceed(ret):
                state,playerpos,playererr,ympos,ymerr,gridave,griderr,plottingscale=ret
                
                #calc
                ympos=np.array(ympos)
                playerpos=np.array(playerpos)
                distingrid=np.sqrt(((ympos-playerpos)**2).sum())/gridave #using unit in grid
                #something going wrong, either not found or digits lost, if less than 140 or more than 350
                dist=distingrid*plottingscale  if plottingscale>100 and plottingscale<400 else None
                
                refresult=['%3d: %5d'%(r, int(distingrid*r+0.5)) for r in reflist]
                
                prompt=''
                prompt+='%s\n'%(state)
                if dist is not None:
                    prompt+='dist=%d\n'%(dist)
                def strictErrCheck():
                    return playererr>4 or ymerr<0.7 or griderr>4 or dist is None
                if strictErrCheck():
                    prompt+='Not recommended to use for err sake, \nbetter remeas again, dbglog will be done\n'
                    needdbglog=True
                prompt+='{}'.format('\n'.join(refresult))
                prompt+='\n'
                prompt+='dg=%5f,pe=%4d,pe=%5.3f,ye=%5.3f,ge=%5.3f\n'%\
                        (distingrid,plottingscale,playererr,ymerr,griderr)
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
    scr=cv.imread(r"C:\Program Files\WarThunder\wtequ\Opdar\asset\wtdistmeaspy\log\2022-11-12-01-45-04\unnamed.png")
    ret=SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}/'.format(
        time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime())
        ))
    print(ret)

main()