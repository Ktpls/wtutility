
from copy import deepcopy
from logging import exception

from matplotlib import image
from utility import*
from gameinput import *
from autofreshmap_config import*

assetroot='./asset/autofreshmap/'

if log2file:
    logg=logger(os.path.join(assetroot,r'log\{}.log'.format(
        time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime())
    )))
    def allchanneloutput(s):
        logg(s)
        print(s)
else:
    logg=None
    def allchanneloutput(s):
        print(s)

class networkOperationImplementationSuite:
    @staticmethod
    def setoffwifi():
        pass
    @staticmethod
    def setonwifi():
        pass

class networkOperationImplementation_ipconfigrelease(networkOperationImplementationSuite):
    @staticmethod
    def setoffwifi():
        os.system('ipconfig /release "WLAN"')
    @staticmethod
    def setonwifi():
        os.system('ipconfig /renew "WLAN"')

class networkOperationImplementation_netshinterfacesetinterfacedisable(networkOperationImplementationSuite):
    @staticmethod
    def setoffwifi():
        os.system('netsh interface set interface name="WLAN" admin=disable')
    @staticmethod
    def setonwifi():
        os.system('netsh interface set interface name="WLAN" admin=enable')

networkOperationImplementationAvailableList=[
    'ipconfigrelease',
    'netshinterfacesetinterfacedisable',
]

networkOperationImplementationName=networkOperationImplementationAvailableList[1]

def setoffwifi():
    exec('networkOperationImplementation_{}.setoffwifi()'.format(networkOperationImplementationName))

def setonwifi():
    exec('networkOperationImplementation_{}.setonwifi()'.format(networkOperationImplementationName))

#pass in __file__
def setadmin(file):
    import sys
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    if not is_admin():
        quotedpy='"'+file+'"'
        if sys.version_info[0] == 3:
            ret=ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, quotedpy, None, 1)
        else:#in python2.x
            ret=ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(quotedpy), None, 1)
        exit()


#singleChanneled
def picNorm(m):
    return (np.sqrt((m.astype('float')**2).sum())+0.01)


def fc(x):#foo contribution
    return np.log(1+x)

'''
info like:{
    "path":path
    "mask":mask,
    "lt":[x,y],
    "thresh":123
}
'''

class matcher:
    @staticmethod
    def imagepreprocess(m,mask=None):
        #all preprocess defined in config done here
        if mask is not None:
            m=m*mask
        if subsampleddetection:
            #this would set [x,y,1] back to [x,y], so do it first
            m=cv.resize(m,None,fx=subsampleddetectionrate,fy=subsampleddetectionrate,interpolation=cv.INTER_AREA)
        if singlechanneleddetection:
            #cvtColor cant process float output by subsampling
            m=m.astype('uint8')
            m=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
            m=m.reshape(m.shape+tuple([1])) #in accordance to multi channeled
        return m.astype('float') #for matching

    def __init__(self,info:Dict):
        path=os.path.join(assetroot,info['path'])
        m=cv.imread(path)
        if m.size==0:
            raise BaseException('loading matcher failed in {}'.format(path))
        self.pointlt=np.array(info['lt'])
        self.pointrd=self.pointlt+np.flip(m.shape[:2])
        self.m=matcher.imagepreprocess(m)
        self.thresh=info['thresh']
        
        #for dbg output
        self.path=info['path']

        if info['mask'] is not None:
            m=os.path.join(assetroot,info['mask'])
            m=cv.imread(m)
            self.mask=m
        else:
            self.mask=None

    #not using
    def matchSign_SQDIFF_NORMED(self,mscr):
        mscr=mscr[self.pointlt[1]:self.pointrd[1],self.pointlt[0]:self.pointrd[0]]
        result=cv.matchTemplate(mscr, self.m, cv.TM_SQDIFF_NORMED)
        minValue, maxValue, minLoc, maxLoc = cv.minMaxLoc(result)
        return minValue

    def cutroi(self,m):
        return m[self.pointlt[1]:self.pointrd[1],self.pointlt[0]:self.pointrd[0],:]

    '''
    channel can NOT be ignored in mscr.shape, that is like [x,y,c], where c can be 1
    depressing big error in few position
    '''
    def matchSign_LOGSQDIFF_NORMED(self,mscr):
        mscr=self.cutroi(mscr)
        mscr=matcher.imagepreprocess(mscr)
        return (
            (fc((self.m-mscr)**2).sum(axis=(0,1)))
            /
            (np.sqrt(0.01+fc(self.m**2).sum(axis=(0,1)))*np.sqrt(0.01+fc(mscr**2).sum(axis=(0,1))))
            ).mean()

    def detect(self,mscr):
        s=self.matchSign_LOGSQDIFF_NORMED(mscr)
        if dbglog:
            allchanneloutput("{} detecting: s={}".format(self.path,s))
        return s<self.thresh

    def getsignpointlt(self):
        return self.pointlt

    def getsignpointrd(self):
        return self.pointrd

    def getsigncenter(self):
        return 0.5*(self.pointlt+self.pointrd)


class detector:
    def __init__(self,para):
        pass
    def detect(self,mscr):
        pass

class defaultdetector(detector):
    #para is matcherinfo
    def __init__(self,para):
        self.mtc=matcher(para)
    def detect(self,mscr):
        return self.mtc.detect(mscr)

class signdetector(detector):
    #para: {"path":path,"lt":lt}
    def __init__(self,para:dict):
        para=deepcopy(para)
        para.setdefault('thresh',standardMatchThreshold)
        para.setdefault('mask',None)
        self.mtc=matcher(para)
    def detect(self,mscr:np.ndarray):
        return self.mtc.detect(mscr)
    def getsigncenter(self):
        return self.mtc.getsigncenter()
    def getsignpointrd(self):
        return self.mtc.getsignpointrd()

def getMapSpawnCenter(m):
    m=cv.cvtColor(m,cv.COLOR_BGR2HSV)
    m=cv.inRange(m,hsv2opencv8bithsv([220,60,65]),hsv2opencv8bithsv([230,90,100]))
    X=np.arange(m.shape[1])
    Y=np.arange(m.shape[0])
    XY=np.meshgrid(X,Y)
    center=[(C*m).sum()/m.sum() for C in XY]
    return np.array(center)

def mapname2path(mapname):
    return 'map/'+mapname+'.png'
class mapdetector(detector):
    #para: {"path":path}
    #the so called path is actually map name, by which mapname2path is needed
    def __init__(self,para:dict):
        para=deepcopy(para)
        para.setdefault('mask',None)
        para.setdefault('lt',standardMapLeftTopPoint)
        para.setdefault('thresh',standardMatchThreshold)
        para["path"]=mapname2path(para["path"])
        self.mtc=matcher(para)
        
        self.detectspawn='spawncenter' in para
        self.spawncenter:np.ndarray=para.get('spawncenter',[0,0])
        self.allowederrrange:int=para.get('allowederrrange',0)
        
    def detect(self,mscr):
        ismapright=self.mtc.detect(mscr)
        if self.detectspawn:
            m=self.mtc.cutroi(mscr)
            center=getMapSpawnCenter(m)
            err=np.sqrt(((center-self.spawncenter)**2).sum())
            isspawnright=err<self.allowederrrange
        else:
            isspawnright=True
        return ismapright and isspawnright

def getdetector(info):
    src='{}(info)'.format(info['type'])
    try:
        obj=eval(src)
        return obj
    except BaseException as err:
        allchanneloutput('err in getdetector(), {}'.format(err))



def maplist2detectorlist(ml):
    ml=deduplicate(ml)
    dl={
        m:getdetector(
            specialmapdetectors[m] if m in specialmapdetectors else
            {
                "type":"mapdetector",
                "path":m
            }
        )
        for m in ml
    }
    return dl



def signName2Path(name):
    return r'statesign/{}.png'.format(name)
stateDetectorInfo={
    'hanger':{
        'path':signName2Path('hanger'),
        'lt':[863,15],
    },
    'MissionCanceled':{
        'path':signName2Path('MissionCanceled'),
        'lt':[877,952],
    },
    'LoadingMap':{
        'path':signName2Path('LoadingMap'),
        'lt':[1030,203],
    },
    'OK':{
        'path':signName2Path('OK'), #有时有色差，很奇怪。可能按钮不完全是不透明的？
        'lt':[896,553],
        'thresh':0.3
    }
}

whitelistedmapdetector=None
stateDetector=None

def loadAssetsNeeded4FreshAMap():
    global whitelistedmapdetector,stateDetector
    whitelistedmapdetector=maplist2detectorlist(whitelistedmap)
    stateDetector={
        k:signdetector(v)
        for k,v in stateDetectorInfo.items()
    }

def leaveButton():
    sleep(1)
    #move after click for not blocking next time detection
    moveto([0,0])


def freshAMap():
    def shot():
        return ss.shotbgr()
    #foo: bool(*foo)(Mat& screen), with return of if detected
    #ret: if resume freshmap process
    def keepdetecting(foo:Callable[[np.ndarray], bool], sleeptime=0.5)->bool:
        while(True):
            scr=shot()
            if foo(scr):
                return True
            sleep(sleeptime)

    #init
    loadAssetsNeeded4FreshAMap()
    
    activeWindow(getWTHwnd())
    ss=screenshoter(0)
    while(True):
        def detectToBattle(scr):
            if stateDetector['OK'].detect(scr):
                #click(stateDetector['OK'].getsigncenter())
                press(keycode.key_Enter)
            if stateDetector['hanger'].detect(scr):
                #click(stateDetector['hanger'].getsigncenter())
                press(keycode.key_Enter)
                return True
            if stateDetector['MissionCanceled'].detect(scr):
                #click(stateDetector['MissionCanceled'].getsigncenter())
                press(keycode.key_Enter)
                return True
            return False
        if not keepdetecting(detectToBattle):
            return
        win32api.Beep(500,100)
        allchanneloutput('matching')

        #detect loading map
        loadingscreen=None
        def detectLoadingMap(scr):
            if stateDetector['LoadingMap'].detect(scr):
                nonlocal loadingscreen
                loadingscreen=scr
                return True
            if stateDetector['hanger'].detect(scr): #for click not succeed
                #click(stateDetector['hanger'].getsigncenter())
                press(keycode.key_Enter)
            return False
        if not keepdetecting(detectLoadingMap):
            return
        
        win32api.Beep(500,100)
        allchanneloutput('loading map')

        #determine if map desired
        #ret=[ismapdesired, match details]
        
        #ret= np.array([d.detect(loadingscreen) for d in whitelistedmapdetector.values()]).any()
        ret=False
        for d in whitelistedmapdetector.values():
            #done this by hand to get 2 times faster
            if d.detect(loadingscreen):
                ret=True
                break

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
            #setoffwifi()
            return False
        #detect able to enter again
        def detectGameRematchable(scr):
            if stateDetector['hanger'].detect(scr):
                return True
            if stateDetector['MissionCanceled'].detect(scr):
                return True
            return False
        #sleep at least some time
        sleep(5)
        if not keepdetecting(detectGameCanceled):
            return

        setonwifi()
        win32api.Beep(500,100)
        allchanneloutput('canceled')
        #for not enter game too soon after wifi on
        wifonitime=time.time()
        sleepuntil(lambda :time.time()-wifonitime> setonwifirecoverthresh,1)

def testOneRaw():
    loadAssetsNeeded4FreshAMap()
    scr=cv.imread(r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Serversk-13.png")
    ret= [d.detect(scr) for d in whitelistedmapdetector.values()]
    print()
