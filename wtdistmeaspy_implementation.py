
import matplotlib as mpl
from utilitypack.utility import *
from wtdistmeaspy_config import *
yellowmarkpath = r"./asset/wtdistmeaspy/yellowmark.png"
kernelyellowmark = cv.imread(yellowmarkpath)

if ocrimpltype == 'tes':
    from wtdistmeaspy_ocrimpl import implTesseract as ocrimpl
elif ocrimpltype == 'cnn':
    from wtdistmeaspy_ocrimpl import implCNN as ocrimpl

ocrimpl.init()


def pic2kernel(p: np.ndarray):
    maque = p.copy()
    maque[maque[:, :, 0] != maque[:, :, 2]] = [1, 1, 1]
    maque[maque[:, :, 0] != maque[:, :, 1]] = [1, 1, 1]
    maque = maque[:, :, 0]
    maque[maque[:, :] != 1] = 0
    mask = 1 - maque

    p = (mask * cv.cvtColor(p, cv.COLOR_BGR2GRAY)).astype('float')
    ave = p.sum() / mask.sum()
    norm2 = (p**2).sum() - mask.sum() * ave**2
    p = (p - ave) * mask  # -ave will lower masked pos, which is 0, to minus
    return p / norm2

    # return p


kernelyellowmark = pic2kernel(kernelyellowmark)
# screen
w = 1920
h = 1080


def didSolveMapSucceed(solvemapret):
    return len(solvemapret) > 1


def SolveMap_BottomRightSmallMap(isrc, dbg: bool = False, dbglogpath: str = ''):

    if dbg:
        def dbglogsavestep(m, name='unnamed', method='savemat'):
            nonlocal dbglogpath
            exec('{}(m,path=dbglogpath,name=name)'.format(method))
        logg = logger(os.path.join(dbglogpath, 'log.log'))

        def log(s):
            logg(s)
    else:
        def dbglogsavestep(m, name=None, method='savemat'):
            pass
        logg = None

        def log(s):
            pass

    mcolored = isrc
    dbglogsavestep(mcolored)

    mgray = cv.cvtColor(mcolored, cv.COLOR_BGR2GRAY)
    dbglogsavestep(mgray)

    # find player

    mcolorply = cv.cvtColor(mcolored, cv.COLOR_BGR2HSV)
    dbglogsavestep(mcolorply)

    mcolorply = cv.inRange(mcolorply, hsv2opencv8bithsv(
        [25, 15, 55]), hsv2opencv8bithsv([65, 60, 256]))
    dbglogsavestep(mcolorply)

    mply = cv.adaptiveThreshold(
        mgray, 1, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, -110)
    dbglogsavestep(255*mply)

    mply = mcolorply*mply
    dbglogsavestep(mply)

    def playerfinder_gaussiandensity_method(m):
        b = cv.GaussianBlur(m, [5, 5], None)
        dbglogsavestep(b)

        mply = (m*(b > 255*5/25)).astype('int')
        dbglogsavestep(mply)

        X = np.arange(mply.shape[1])
        Y = np.arange(mply.shape[0])
        X, Y = np.meshgrid(X, Y)
        mplysum = mply.sum()
        if mplysum < 1:
            return [False]

        playerpos = [(X*mply).sum()/mplysum, (Y*mply).sum()/mplysum]
        playererr = ((
            (X-playerpos[0])**2+(Y-playerpos[1])**2
        )*mply).sum()/mplysum
        log('p=(%3d,%3d),pe=%5.3f' % (playerpos[0], playerpos[1], playererr))
        return True, playerpos, playererr

    afterprocessresult = playerfinder_gaussiandensity_method(mply)
    if not afterprocessresult[0]:
        errormsg = "PL_NOT_FOUND"
        return [errormsg]
    _, playerpos, playererr = afterprocessresult

    if playererr > plerrreq:
        errormsg = "PL_2GREAT_ERR %5f" % playererr
        return [errormsg]
    # try deleting too wrong points like did in grid processing

    # find yellow mark
    mcolorym = cv.cvtColor(mcolored, cv.COLOR_BGR2HSV)
    dbglogsavestep(mcolorym)

    mcolorvalid = cv.inRange(mcolorym, hsv2opencv8bithsv(
        [60-25, 70, 50]), hsv2opencv8bithsv([60+25, 100, 100]))/255
    dbglogsavestep(mcolorvalid*255)

    mym = mcolored.copy()
    mym = mym[:, :, 1:]
    mym = np.average(mym, axis=2)  # yellow channel
    mym = mym*mcolorvalid
    dbglogsavestep(mym)

    mym = cv.filter2D(mym, -1, kernelyellowmark)
    dbglogsavestep(mym, method='savematn')
    ympos = [mym.max(0).argmax(), mym.max(1).argmax()]
    ymerr = mym[ympos[1], ympos[0]]  # not real err. greater is better
    log('y=(%3d,%3d),ye=%5.3f' % (ympos[0], ympos[1], ymerr))

    if ymerr < ymerrreq:
        errormsg = "YM_2LESS_PROD %5f" % ymerr
        return [errormsg]

    # find grid
    mgrd = 255-mgray
    dbglogsavestep(mgrd)

    mgrd = cv.adaptiveThreshold(
        mgrd, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 5, -5)
    dbglogsavestep(mgrd)

    gridlinekernellength = 201
    onepixline = np.ones([gridlinekernellength])
    kernelrow = np.array([-1*onepixline, 1*onepixline,
                         1*onepixline, -1*onepixline])
    kernelrow = kernelrow/gridlinekernellength

    mrow = cv.filter2D(mgrd, -1, kernelrow)
    dbglogsavestep(mrow)
    drow = mrow.mean(axis=1)/255

    mcol = cv.filter2D(mgrd, -1, kernelrow.T)
    dbglogsavestep(mcol)
    dcol = mcol.mean(axis=0)/255

    dbglogsavestep(cv.threshold(mcol.astype('float') +
                   mrow.astype('float'), 255, 255, cv.THRESH_TRUNC)[1])

    def distribution2interval(d):
        d = d*(d > 0.5)
        # distribution2interval
        linepos = [i for i, l in enumerate(d) if l > 0]
        # trim the last nan out in arrayshift
        interval = (arrayshift(linepos, -1)-linepos)[:-1]
        return interval
    interval = np.concatenate(
        [distribution2interval(dcol), distribution2interval(drow)])

    log('all intervals\n%s' % ('\n'.join(['%4d' % i for i in interval])))

    MIN_LINE_INTERVAL = 20
    # filter intervals
    interval = [i for i in interval if i > MIN_LINE_INTERVAL]
    log('degened intervals\n%s' % ('\n'.join(['%4d' % i for i in interval])))

    interval = np.array(interval)
    intervaltotalnum = len(interval)
    while (True):
        if (len(interval) < 1):
            # no available interval
            errormsg = "GD_BAD_INTE"
            log(errormsg)
            return [errormsg]
        ave = interval.mean()
        errs = (interval-ave)**2
        err = errs.sum()/len(errs)
        if (err < griderrreq):
            log("grid interval samples used %d out of %d, err=%5f\n" %
                (len(interval), intervaltotalnum, err))
            break

        # lower err and try again
        interval = np.delete(interval, errs.argmax())

    log('used intervals\n%s' % ('\n'.join(['%4d' % i for i in interval])))

    gridave = interval.mean()
    griderr = interval.var()

    log('g=%3f,ge=%5f.3f' % (gridave, griderr))

    # find plotting scale
    # standard: all bivalue map must be presented in [0,255] form
    psfindrange = int(2.5*gridave)
    # cut region and del the "scale"
    # 3 is height of scale, 14 is height of text, 1 is gap between scale and text
    # text is a little bit out of range between two vertical lines,
    # so 2x interval is with slight possibility losing char pixel
    # but 2.5x interval is quite enough
    mps = np.copy(mcolored[-3-1-14:-3-1, -psfindrange:, :])
    dbglogsavestep(mps)
    # consider cut map in the last step, for using as more region info in detection as possible

    # filter absolute color
    mpshsv = cv.cvtColor(mps, cv.COLOR_BGR2HSV)
    darkgraypoints = cv.inRange(mpshsv, hsv2opencv8bithsv(
        [0, 0, 0]), hsv2opencv8bithsv([360, 50, 30]))
    dbglogsavestep(darkgraypoints)

    # filter adaptive value(lightness)
    mpsgray = mpshsv[:, :, 2]
    mpsgray = mpsgray.astype('float')
    relblack = cv.threshold(
        (mpsgray-(regionave(mpsgray, [3, 3])-5)), 0, 255, cv.THRESH_BINARY_INV)[1]
    dbglogsavestep(relblack)

    # be both really black and relatively black
    black = np.logical_and(darkgraypoints, relblack).astype('float')*255
    # black=np.logical_and(black,relinsat).astype('float')*255
    dbglogsavestep(black)

    charw, charh = 10, 20

    # padding for ease of recongnization by tesseract, at least in the past
    # but our cnn using data collected from tesseract daily using uses the standard 20x10 char pic
    black = cv.copyMakeBorder(black, 3, 3, 3, 3, cv.BORDER_CONSTANT, value=0)
    dbglogsavestep(black)
    plottingscale = ocrimpl.ocr(black)
    
    # cnn works fine even with dirty relblack pic
    # relblack = cv.copyMakeBorder(relblack, 3, 3, 3, 3, cv.BORDER_CONSTANT, value=0)
    # plottingscale = ocrimpl.ocr(black)

    # im collecting samples on dl prac
    savemat(black, f'black4CNN_{plottingscale}',
            path='./output/wtdmp_noised_scale_collection_project/')

    return 'OK', playerpos, playererr, ympos, ymerr, gridave, griderr, plottingscale


def cutBottomRightMap(m):
    pa = np.array([1548, 729])
    pb = np.array([1871, 1052])
    return cv.getRectSubPix(m, pb-pa, 0.5*(pa+pb))
