from copy import deepcopy
from logging import exception

from matplotlib import image
from utilitypack import *
from gameinput import *
from autofreshmap_config import *
import re

assetroot = './asset/autofreshmap/'


def signName2Path(name):
    return r'statesign/{}.png'.format(name)


if resolution == 'm1920x1080r1920x1080':
    # res1920x1080,uiscale75%
    stateDetectorInfo = {
        'hanger': {
            'path': signName2Path('hanger'),
            'lt': [863, 15],
        },
        'MissionCanceled': {
            'path': signName2Path('MissionCanceled'),
            'lt': [877, 952],
        },
        'LoadingMap': {
            'path': signName2Path('LoadingMap'),
            'lt': [1030, 203],
        },
        'OK': {
            'path': signName2Path('OK'),  #有时有色差，很奇怪。可能按钮是alfa很高的半透明的？
            'lt': [896, 553],  #不过使用z函数处理后色差不再是问题了
        }
    }
    standardMapLeftTopPoint = [286, 216]
    pointtemplatezoomrate = 1.0

elif resolution == 'm1920x1080r1366x768':
    # 1366x768,75%
    stateDetectorInfo = {
        'hanger': {
            'path': signName2Path('hanger'),
            'lt': [863, 21],
        },
        'MissionCanceled': {
            'path': signName2Path('MissionCanceled'),
            'lt': [877, 943],
        },
        'LoadingMap': {
            'path': signName2Path('LoadingMap'),
            'lt': [1030, 203],
        },
        'OK': {
            'path': signName2Path('OK'),
            'lt': [896, 553],
        }
    }
    standardMapLeftTopPoint = [294, 221]
    pointtemplatezoomrate = 1.4  #1920/1366
elif resolution == 'm1920x1080r1280x720':
    # 1280x720,75%
    stateDetectorInfo = {
        'hanger': {
            'path': signName2Path('hanger'),
            'lt': [863, 22],
        },
        'MissionCanceled': {
            'path': signName2Path('MissionCanceled'),
            'lt': [876, 941],
        },
        'LoadingMap': {
            'path': signName2Path('LoadingMap'),
            'lt': [1030, 209],
        },
        'OK': {
            'path': signName2Path('OK'),
            'lt': [896, 554],
        }
    }
    standardMapLeftTopPoint = [292, 218]
    pointtemplatezoomrate = 1.5  #1920/1366

if log2file:
    logg = logger(
        os.path.join(
            assetroot,
            rf'log\{ time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}.log'
        ))

    def allchanneloutput(s):
        logg(s)
        print(s)
else:
    logg = None

    def allchanneloutput(s):
        print(s)


class networkOperationImplementationSuite:

    @staticmethod
    def setoffwifi():
        pass

    @staticmethod
    def setonwifi():
        pass


class networkOperationImplementation_ipconfigrelease(
        networkOperationImplementationSuite):

    @staticmethod
    def setoffwifi():
        os.system('ipconfig /release "WLAN"')

    @staticmethod
    def setonwifi():
        os.system('ipconfig /renew "WLAN"')


class networkOperationImplementation_netshinterfacesetinterfacedisable(
        networkOperationImplementationSuite):

    @staticmethod
    def setoffwifi():
        os.system(
            f'netsh interface set interface name="{wlanname4netshinterface}" admin=disable'
        )

    @staticmethod
    def setonwifi():
        os.system(
            f'netsh interface set interface name="{wlanname4netshinterface}" admin=enable'
        )


class networkOperationImplementation_netshwlandisconnect(
        networkOperationImplementationSuite):

    @staticmethod
    def setoffwifi():
        os.system(f'netsh wlan disconnect')

    @staticmethod
    def setonwifi():
        os.system(f'netsh wlan connect name="{wlanname4netshwlan}"')
        os.system(
            f'netsh wlan set profileparameter name="{wlanname4netshwlan}" connectionMode=auto'
        )
        #set auto so it will be auto connected the next time u boot


networkOperationImplementationAvailableList = [
    'ipconfigrelease',
    'netshinterfacesetinterfacedisable',
    'netshwlandisconnect',
]

networkOperationImplementationName = networkOperationImplementationAvailableList[
    2]


def setoffwifi():
    exec('networkOperationImplementation_{}.setoffwifi()'.format(
        networkOperationImplementationName))


def setonwifi():
    exec('networkOperationImplementation_{}.setonwifi()'.format(
        networkOperationImplementationName))


# singleChanneled
def picNorm(m):
    return (np.sqrt((m.astype('float')**2).sum()) + 0.01)


'''
info like:{
    "path":path
    "mask":mask,
    "lt":[x,y],
    "thresh":123
}
'''


def assetpath2realpath(ap):
    return os.path.join(assetroot, ap)


class matcher:

    @staticmethod
    def imagepreprocess(m, mask=None):
        # all preprocess defined in config done here
        if mask is not None:
            m = m * mask
        if subsampleddetection:
            # this would set [x,y,1] back to [x,y], so do it first
            m = cv.resize(m,
                          None,
                          fx=subsampleddetectionrate,
                          fy=subsampleddetectionrate,
                          interpolation=cv.INTER_AREA)
        if singlechanneleddetection:
            # cvtColor cant process float output by subsampling
            m = m.astype('uint8')
            m = cv.cvtColor(m, cv.COLOR_BGR2GRAY)
            m = m.reshape(m.shape +
                          tuple([1]))  # in accordance to multi channeled
        return m.astype('float')  # for matching

    def __init__(self, info: Dict):
        path = assetpath2realpath(info['path'])
        m = cv.imread(path)
        if m.size == 0:
            raise BaseException('loading matcher failed in {}'.format(path))
        self.pointlt = np.array(info['lt'])
        self.pointrd = self.pointlt + np.flip(m.shape[:2])
        self.m = matcher.imagepreprocess(m)
        self.thresh = info.get(
            'thresh', None)  #optional thresh, for dynamic specified, if needed

        # for dbg output
        self.path = info['path']

        if info['mask'] is not None:
            m = assetpath2realpath(info['mask'])
            m = cv.imread(m)
            self.mask = m
        else:
            self.mask = None

    def cutroi(self, m):
        return m[self.pointlt[1]:self.pointrd[1],
                 self.pointlt[0]:self.pointrd[0], :]

    '''
    channel can NOT be ignored in mscr.shape, that is like [x,y,c], where c can be 1
    depressing big error in few position
    '''

    def matchSign_Z_ABSDIFF_NORMED(self, mscr):

        def fcerr(x):  # foo contribution
            l = 3 * (10**2)
            u = 3 * (20**2)
            x[x < l] = l
            x[x > u] = u
            x -= l
            x /= (u - l)
            return x

        mscr = matcher.imagepreprocess(mscr)

        numerator = fcerr(np.square(self.m - mscr).sum(axis=(2, )))\
            .sum(axis=(0, 1))
        denominator = np.prod(self.m.shape)
        return numerator / denominator

    def detect(self, mscr, specifiedThresh=None, cutRequired=True):
        if cutRequired:
            mscr = self.cutroi(mscr)
        s = self.matchSign_Z_ABSDIFF_NORMED(mscr)
        if dbglog:
            allchanneloutput(f"{self.path} detecting: s={s}")
        return s < self.thresh if specifiedThresh is None else s < specifiedThresh

    def getsignpointlt(self):
        return self.pointlt

    def getsignpointrd(self):
        return self.pointrd

    def getsigncenter(self):
        return 0.5 * (self.pointlt + self.pointrd)


class detector:

    def __init__(self, para):
        pass

    def detect(self, mscr):
        pass


class defaultdetector(detector):
    #para is matcherinfo
    def __init__(self, para):
        self.mtc = matcher(para)

    def detect(self, mscr):
        return self.mtc.detect(mscr)


class signdetector(detector):
    #para: {"path":path,"lt":lt}
    def __init__(self, para: dict):
        para = deepcopy(para)
        para.setdefault('thresh', standardMatchThreshold)
        para.setdefault('mask', None)
        self.mtc = matcher(para)

    def detect(self, mscr: np.ndarray):
        return self.mtc.detect(mscr)

    def getsigncenter(self):
        return self.mtc.getsigncenter()

    def getsignpointrd(self):
        return self.mtc.getsignpointrd()


def getMapSpawnCenter(m, spawntype='blue'):

    def spawnfilter_red(m):
        return cv.inRange(m, hsv2opencv8bithsv([0, 70, 40]),
                          hsv2opencv8bithsv([10, 100, 100]))

    def spawnfilter_blue(m):
        return cv.inRange(m, hsv2opencv8bithsv([220, 70, 40]),
                          hsv2opencv8bithsv([230, 100, 100]))

    spawnfilter = {'red': spawnfilter_red, 'blue': spawnfilter_blue}
    m = cv.cvtColor(m, cv.COLOR_BGR2HSV)
    m = spawnfilter[spawntype](m)
    X = np.arange(m.shape[1])
    Y = np.arange(m.shape[0])
    XY = np.meshgrid(X, Y)
    center = [(C * m).sum() / m.sum() for C in XY]
    return np.array(center)


def mapname2assetpath(mapname):
    return 'map/' + mapname + '.png'


def threshedmatchtemplate(src, temp, mask, simu):
    matchresult = cv.matchTemplate(src, temp, cv.TM_SQDIFF_NORMED, mask=mask)
    minval, maxval, minloc, maxloc = cv.minMaxLoc(matchresult)
    # print(minval)
    if dbglog:
        allchanneloutput(
            f'threshedmatchtemplate(): minval={minval}, simuthresh={simu}')
    return minloc if minval <= simu else None


def cutmap(m):
    pointlt = np.array(standardMapLeftTopPoint)
    pointrd = pointlt + [648, 648]
    mm = m[pointlt[1]:pointrd[1], pointlt[0]:pointrd[0]]
    return mm


def zoompointimg(m):
    mattr = np.array(
        [[pointtemplatezoomrate, 0, 0], [0, pointtemplatezoomrate, 0]],
        dtype=np.float32)
    return cv.warpAffine(
        m, mattr,
        np.round(np.flip(m.shape[:2]) * pointtemplatezoomrate).astype(
            np.int32))


Asset4PointDetection_Template = {
    t: zoompointimg(cv.imread(assetpath2realpath(signName2Path(t))))
    for t in ['A', 'B', 'C']
}
Asset4PointDetection_Pointmask = zoompointimg(
    cv.imread(assetpath2realpath(signName2Path('zonemask'))))[:, :, 0]


class mapdetector(detector):
    '''
    para: {
        "mapreq":path,
        "foo":str
    }
    the so called path is actually map name, by which mapname2assetpath is needed
    after that assetpath2realpath will be done in matcher
    '''

    def __init__(self, para: dict):
        para = deepcopy(para)

        if 'mapreq' in para:
            bean4dmtc = {
                'mask': None,
                'lt': standardMapLeftTopPoint,
                'thresh': standardMatchThreshold,
                'path': mapname2assetpath(para["mapreq"])
            }
            self.mtc = matcher(bean4dmtc)
        else:
            self.mtc = None

        self.foo = para['foo']

    def detect(self, mscr):

        mapcut = cutmap(mscr)

        def detectMapShape(specialThresh=None):
            return self.mtc.detect(mscr, specialThresh)

        def distance(a, b):
            err = np.sqrt(((a - b)**2).sum())
            return err

        def detectSpawn():
            center = getMapSpawnCenter(mapcut)
            return center

        def spawnAround(point, err=None):
            if err is None:
                err = standardSpawnCenterError
            return distance(detectSpawn(), point) < err

        def selectPoint(ptype=None, ppos=None, err=None):
            if ptype is None:
                # fall back to all
                ptype = [k for k in Asset4PointDetection_Template.keys()]
            if type(ptype) is str:
                ptype = [ptype]
            result = [
                threshedmatchtemplate(mapcut, Asset4PointDetection_Template[t],
                                      Asset4PointDetection_Pointmask,
                                      detectpointsimilarity)
                for t in ptype
            ]
            result = [r for r in result if r is not None]

            if ppos is not None:
                if err is None:
                    err = standardPointSelectorError
                result = [r for r in result if distance(np.array(r), np.array(ppos)) < err]

            return len(result) != 0

        retVal = None

        def ret(val):
            nonlocal retVal
            retVal = val

        try:
            exec(self.foo)
            return retVal
        except BaseException as e:
            traceback.print_exc()
            raise e


def maplist2detectorlist(ml):
    ml = deduplicate(ml)
    dl = {
        m: mapdetector(specialmapdetectors[m] if m in
                           specialmapdetectors else {
                               "mapreq": m,
                               "foo": 'ret(detectMapShape())'
                           })
        for m in ml
    }
    return dl


whitelistedmapdetector = None
stateDetector = None


def loadAssetsNeeded4FreshAMap():
    global whitelistedmapdetector, stateDetector
    whitelistedmapdetector = maplist2detectorlist(whitelistedmap)
    stateDetector = {k: signdetector(v) for k, v in stateDetectorInfo.items()}
    return whitelistedmapdetector, stateDetector


def leaveButton():
    sleep(1)
    # move after click for not blocking next time detection
    moveto([0, 0])


def freshAMap():

    def shot():
        return ss.shotbgr()

    # foo: bool(*foo)(Mat& screen), with return of if detected
    # ret: if resume freshmap process
    def keepdetecting(foo: Callable[[np.ndarray], bool],
                      sleeptime=0.5) -> bool:
        while (True):
            scr = shot()
            if foo(scr):
                return True
            sleep(sleeptime)

    # init
    loadAssetsNeeded4FreshAMap()

    ss = screenshoter(0)
    while (True):

        def detectToBattle(scr):

            if stateDetector['OK'].detect(scr):
                # click(stateDetector['OK'].getsigncenter())
                press(keycode.key_Enter)
            if stateDetector['hanger'].detect(scr):
                # click(stateDetector['hanger'].getsigncenter())
                press(keycode.key_Enter)
                return True
            if stateDetector['MissionCanceled'].detect(scr):
                # click(stateDetector['MissionCanceled'].getsigncenter())
                press(keycode.key_Enter)
                return True
            return False

        if not keepdetecting(detectToBattle):
            return
        win32api.Beep(500, 100)
        allchanneloutput('matching')

        # detect loading map
        loadingscreen = None

        def detectLoadingMap(scr):
            if stateDetector['LoadingMap'].detect(scr):
                nonlocal loadingscreen
                loadingscreen = scr
                return True
            if stateDetector['hanger'].detect(scr):  # for click not succeed
                press(keycode.key_Enter)
            if stateDetector['OK'].detect(scr):
                press(keycode.key_Enter)
            if stateDetector['MissionCanceled'].detect(scr):
                press(keycode.key_Enter)
            return False

        if not keepdetecting(detectLoadingMap):
            return

        win32api.Beep(500, 100)
        allchanneloutput('loading map')

        # determine if map desired
        # ret=[ismapdesired, match details]

        #ret= np.array([d.detect(loadingscreen) for d in whitelistedmapdetector.values()]).any()
        ret = False
        # name,detector
        for n, d in whitelistedmapdetector.items():
            # done this by hand to get 2 times faster
            if d.detect(loadingscreen):
                allchanneloutput(f'{n}')
                ret = True
                break

        allchanneloutput(str(ret))
        if ret:
            # enter game
            win32api.Beep(1000, 100)
            win32api.Beep(500, 100)
            win32api.Beep(1000, 100)
            allchanneloutput('good map')
            break

        # detected banned map
        setoffwifi()
        win32api.Beep(500, 100)
        allchanneloutput('bad map')

        # detect game canceled, which is not in loading map scence
        def detectGameCanceled(scr):
            if not stateDetector['LoadingMap'].detect(scr):
                return True
            # setoffwifi()
            return False

        # detect able to enter again
        def detectGameRematchable(scr):
            if stateDetector['hanger'].detect(scr):
                return True
            if stateDetector['MissionCanceled'].detect(scr):
                return True
            return False

        # sleep at least some time
        sleep(minDelayAfterDisconnected)
        if not keepdetecting(detectGameCanceled):
            return

        setonwifi()
        win32api.Beep(500, 100)
        allchanneloutput('canceled')
        # for not enter game too soon after wifi on
        wifonitime = time.time()
        sleepuntil(lambda: time.time() - wifonitime > setonwifirecoverthresh,
                   1)


def testOneRaw():
    loadAssetsNeeded4FreshAMap()
    scr = cv.imread(
        r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Serversk-13.png"
    )
    ret = [d.detect(scr) for d in whitelistedmapdetector.values()]
    print()
