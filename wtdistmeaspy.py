
from wtdistmeaspy_achievement import *
class toast:
    messagelist=[]
    def sendmessage(self,content, peroid):
        self.messagelist.append({
            'ctt':content,
            'st':time.perf_counter(),
            'per':peroid
        })
    
    def updatemsglist(self):
        nowtime=time.perf_counter()
        def filterfoo(m):
            return m['per']>m['ctt']-nowtime
        messagelist=[m for m in messagelist if filterfoo(m)]
        msgs=[m['ctt'] for m in messagelist]
    
    def getallmsg(self):
        self.updatemsglist()
        return '\n'.join(self.messagelist)

#new msg covers the lasts
class bulletinBoard:
    def __init__(self, idlecontent):
        self.idlecontent=idlecontent
        self.content=''
        self.overduetime=time.perf_counter()
    
    def putup(self,content,peroid):
        self.content=content
        self.overduetime=time.perf_counter()+peroid
    
    def read(self):
        if time.perf_counter()<self.overduetime:
            return self.content
        else:
            return self.idlecontent


def main():
    hud=fullScrHUD()
    hud.setcontent(np.zeros([h,w,3],np.uint8))
    hud.setup()
    screen=screenshoter(0)
    fps=fpsmanager(3)
    hotkey=hotkeymanager([
        192
    ])

    idlebulletincontents=[
        ['(=v=)',70],
        ['(-.-)',29],
        ['(>^<)',1],
    ]
    bulletin=bulletinBoard(
        idlebulletincontents[
            summonCard(
                integralProb(
                    [c[1] for c in idlebulletincontents]
                )
            )
        ][0]
    )
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
            dbglogreason=None
            ret=SolveMap_BottomRightSmallMap(scr)

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
                    if playererr>4:
                        return 'SEC_PE'
                    if  ymerr<0.5:
                        return 'SEC_YE'
                    if griderr>4:
                        return 'SEC_GE'
                    if dist is None:
                        return 'SEC_DN'
                    return None #keep dbglog unneeded
                dbglogreason=strictErrCheck()
                if dbglogreason is not None:
                    prompt+='Not recommended to use for err sake, \nbetter remeas again, dbglog will be done\n'
                prompt+='{}'.format('\n'.join(refresult))
                prompt+='\n'
                prompt+='dg=%5f,ps=%4d,pe=%5.3f,ye=%5.3f,ge=%5.3f\n'%\
                        (distingrid,plottingscale,playererr,ymerr,griderr)
            else:
                #really failed
                prompt=ret[0]
                dbglogreason=ret[0]
            if dbglogreason is not None:
                ret=SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}_On{}/'.format(
                    time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime()),
                    dbglogreason
                    ))
            bulletin.putup(prompt,10)
        m=np.zeros([h,w,3],np.uint8)
        m=outputlines2mat(m,np.array(outputpos),bulletin.read())
        m=addShadow2HUD(m)
        hud.setcontent(m)
        hud.update()


def testground():
    scr=cv.imread(
    r"C:\Program Files\WarThunder\wtequ\Opdar\asset\wtdistmeaspy\log\2022-11-15-18-40-09_OnSEC_DN\unnamed.png")
    ret=SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}/'.format(
        time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime())
        ))
    print(ret)

main()