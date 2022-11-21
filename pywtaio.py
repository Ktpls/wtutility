
from turtle import goto
from typing import Callable
from wtdistmeaspy_implementation import *
from autofreshmap_implementation import *
class activity:
    def __init__(self):
        pass
    def update(self):
        pass
    def mainroutine(self):
        pass

class autofreshmapactivity(activity):
    def __init__(self):
        self.running=False
    
    def update(self):
        pass
    
    def mainroutine(self):
        def freshMapProcess():
            def checkstop():
                return not self.running
            def freshMapProcess_exit_cleanup():
                setonwifi()
            def shot():
                return ss.shotbgr()
            #foo: bool(*foo)(Mat& screen), with return of if detected
            #ret: if resume freshmap process
            def keepdetecting(foo:Callable[[np.ndarray], bool])->bool:
                while(True):
                    scr=shot()
                    if foo(scr):
                        return True
                    if checkstop():
                        freshMapProcess_exit_cleanup()
                        return False
                    sleep(0.3)

            #init
            loadAssetsNeeded4FreshAMap()
            
            activeWindow(getWTHwnd())
            ss=screenshoter(0)
            
            while(True):
                def detectToBattle(scr):
                    if stateDetector['hanger'].detect(scr):
                        click(stateDetector['hanger'].getsigncenter())
                        moveto(stateDetector['hanger'].getsignpointrd()+[10,10])
                        #move after click for not blocking next time detection
                        return True
                    if stateDetector['MissionCanceled'].detect(scr):
                        click(stateDetector['MissionCanceled'].getsigncenter())
                        moveto(stateDetector['MissionCanceled'].getsignpointrd()+[10,10])
                        return True
                    return False
                if not keepdetecting(detectToBattle):
                    return
                win32api.Beep(500,100)
                allchanneloutput('matching')

                #detect loading map
                def detectLoadingMap(scr):
                    if stateDetector['LoadingMap'].detect(scr):
                        return True
                    return False
                if not keepdetecting(detectLoadingMap):
                    return
                
                win32api.Beep(500,100)
                allchanneloutput('loading map')

                #determine if map desired
                #ret=[ismapdesired, match details]
                
                scr=shot()
                ret= np.array([d.detect(scr) for d in whitelistedmapdetector.values()]).any()

                allchanneloutput(str(ret))
                if ret:
                    #enter game
                    win32api.Beep(1000,100)
                    win32api.Beep(500,100)
                    win32api.Beep(1000,100)
                    allchanneloutput('good map')
                    break

                #detected banned map
                setoffwifi()
                win32api.Beep(500,100)
                allchanneloutput('bad map')

                #detect game canceled, which is not in loading map scence
                def detectGameCanceled(scr):
                    if not stateDetector['LoadingMap'].detect(scr):
                        return True
                    return False
                if not keepdetecting(detectGameCanceled):
                    return

                setonwifi()
                win32api.Beep(500,100)
                allchanneloutput('canceled')
                #for not enter game too soon after wifi on
                wifonitime=time.time()
                sleepuntil(lambda :time.time()-wifonitime> setonwifirecoverthresh,1)
        '''
        todo:
        set self.running=True
        call freshMapProcess() in new thread
        set self.running=False when cancel called
        '''


def main():
    hud=fullScrHUD()
    hud.setcontent(np.zeros([h,w,3],np.uint8))
    hud.setup()
    screen=screenshoter(0)
    fps=fpsmanager(10)
    hotkey=hotkeymanager([
        win32con.VK_F12
    ])

    idleprompt="(-.-)"
    prompt=idleprompt
    contentlefttime=time.perf_counter()
    def setcontentlefttime():
        nonlocal contentlefttime
        contentlefttime=time.perf_counter()+10
    while(True):
        fps.next()
        keys=hotkey.getkeys()
        if keys[win32con.VK_F12]:
            sleep(0.5) #for network delay
            scr=screen.shotbgr()
            #scr=cv.imread(r'./asset/wtdistmeaspy/shot.png')
            scr=cutBottomRightMap(scr)
            needdbglog=False
            ret=SolveMap_BottomRightSmallMap(scr)
            if didSolveMapSucceed(ret):
                state,playerpos,playererr,ympos,ymerr,gridave,griderr=ret
                def strictErrCheck():
                    return playererr>4 or ymerr<0.6 or griderr>4
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
        hud.setcontent(m)
        hud.update()


def testground():
    pass

main()