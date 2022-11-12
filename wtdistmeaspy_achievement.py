
import matplotlib as mpl
from utility import *
from wtdistmeaspy_config import *
import pytesseract.pytesseract as ptact
ptact.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
yellowmarkpath=r"./asset/wtdistmeaspy/yellowmark.png"
kernelyellowmark=cv.imread(yellowmarkpath)
def pic2kernel(p:np.ndarray):
    maque=p.copy()
    maque[maque[:,:,0]!=maque[:,:,2]]=[1,1,1]
    maque[maque[:,:,0]!=maque[:,:,1]]=[1,1,1]
    maque=maque[:,:,0]
    maque[maque[:,:]!=1]=0
    mask=1-maque
    
    p=(mask*cv.cvtColor(p,cv.COLOR_BGR2GRAY)).astype('float')
    ave=p.sum()/mask.sum()
    norm2=(p**2).sum() - mask.sum()*ave**2
    p=(p-ave)*mask #-ave will lower masked pos, which is 0, to minus
    return p/norm2
    #return p
kernelyellowmark=pic2kernel(kernelyellowmark)
#screen
w=1920
h=1080

def didSolveMapSucceed(solvemapret):
    return len(solvemapret)>1

def SolveMap_BottomRightSmallMap(isrc,dbg:bool=False,dbglogpath:str=''):
    
    if dbg:
        def dbglogsavestep(m,name=None,method='savemat'):
            nonlocal dbglogpath
            exec('{}(m,path=dbglogpath,name=name)'.format(method))
        logg=logger(os.path.join(dbglogpath,'log.log'))
        def log(s):
            logg(s)
    else:
        def dbglogsavestep(m,name=None,method='savemat'):
            pass
        logg=None
        def log(s):
            pass
    
    mcolored=isrc
    dbglogsavestep(mcolored)
    
    mgray=cv.cvtColor(mcolored,cv.COLOR_BGR2GRAY)
    dbglogsavestep(mgray)
    
    #find player
    mcolorply=cv.GaussianBlur(mcolored,[5,5],1)
    dbglogsavestep(mcolorply)
    
    mcolorply=cv.cvtColor(mcolorply,cv.COLOR_BGR2HSV)
    dbglogsavestep(mcolorply)
    
    mcolorply=cv.inRange(mcolorply,hsv2opencv8bithsv([25,15,55]),hsv2opencv8bithsv([65,60,256]))
    dbglogsavestep(mcolorply)
    
    mply=cv.adaptiveThreshold(mgray,1,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, -110)
    dbglogsavestep(255*mply)
    
    mply=mcolorply*mply
    dbglogsavestep(mply)
    
    def playerfinder_gaussiandensity_method(m):
        b=cv.GaussianBlur(m,[3,3],None)
        dbglogsavestep(b)
        
        mply=(m*(b>200)).astype('int')
        dbglogsavestep(mply)
        
        X=np.arange(mply.shape[1])
        Y=np.arange(mply.shape[0])
        X,Y=np.meshgrid(X,Y)
        mplysum=mply.sum()
        if mplysum<1:
            return [False]
        
        playerpos=[(X*mply).sum()/mplysum,(Y*mply).sum()/mplysum]
        playererr=((
            (X-playerpos[0])**2+(Y-playerpos[1])**2
            )*mply).sum()/mplysum
        log('p=(%3d,%3d),pe=%5.3f'%(playerpos[0],playerpos[1],playererr))
        return True,playerpos,playererr
    
    afterprocessresult=playerfinder_gaussiandensity_method(mply)
    if not afterprocessresult[0]:
        errormsg="PL_NOT_FOUND"
        return [errormsg]
    _,playerpos,playererr=afterprocessresult

    if playererr>plerrreq:
        errormsg="PL_2GREAT_ERR %5f"%playererr
        return [errormsg]
    #try deleting too wrong points like did in grid processing

    #find yellow mark
    mcolorym=cv.cvtColor(mcolored,cv.COLOR_BGR2HSV)
    dbglogsavestep(mcolorym)
    
    mcolorvalid=cv.inRange(mcolorym,hsv2opencv8bithsv([60-25,45,20]),hsv2opencv8bithsv([60+25,256,256]))/255
    dbglogsavestep(mcolorvalid*255)
    
    mym=mgray.copy()
    mym=mym*mcolorvalid
    dbglogsavestep(mym)
    
    mym=cv.filter2D(mym,-1,kernelyellowmark)
    dbglogsavestep(mym,method='savematn')
    ympos=[mym.max(0).argmax(),mym.max(1).argmax()]
    ymerr=mym[ympos[1],ympos[0]] #not real err. greater is better
    log('y=(%3d,%3d),ye=%5.3f'%(ympos[0],ympos[1],ymerr))

    if ymerr<ymerrreq:
        errormsg="YM_2LESS_PROD %5f"%ymerr
        return [errormsg]

    #find grid
    mgrd=255-mgray
    dbglogsavestep(mgrd)
    
    mgrd=cv.adaptiveThreshold(mgrd,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,5,-5)
    dbglogsavestep(mgrd)
    
    gridlinekernellength=201
    onepixline=np.ones([gridlinekernellength])
    kernelrow=np.array([-1*onepixline,1*onepixline,1*onepixline,-1*onepixline])
    kernelrow=kernelrow/gridlinekernellength

    mrow=cv.filter2D(mgrd,-1,kernelrow)
    dbglogsavestep(mrow)
    drow=mrow.mean(axis=1)/255

    mcol=cv.filter2D(mgrd,-1,kernelrow.T)
    dbglogsavestep(mcol)
    dcol=mcol.mean(axis=0)/255

    dbglogsavestep(cv.threshold(mcol.astype('float')+mrow.astype('float'),255,255,cv.THRESH_TRUNC)[1])

    def distribution2interval(d):
        d=d*(d>gridthresh)
        #distribution2interval
        linepos=[i for i,l in enumerate(d) if l>0]
        interval=(arrayshift(linepos,-1)-linepos)[:-1] #trim the last nan out in arrayshift
        return interval
    interval=np.concatenate([distribution2interval(dcol),distribution2interval(drow)])

    log('all intervals\n%s'%('\n'.join(['%4d'%i for i in interval])))

    #filter intervals
    interval=[i for i in interval if i >MIN_LINE_INTERVAL]
    log('degened intervals\n%s'%('\n'.join(['%4d'%i for i in interval])))

    interval=np.array(interval)
    intervaltotalnum=len(interval)
    while (True):
        if (len(interval) < 1):
            #no available interval
            errormsg = "GD_BAD_INTE";
            log(errormsg);
            return [errormsg];
        ave = interval.mean()
        errs=(interval-ave)**2;
        err = errs.sum()/len(errs)
        if (err < griderrreq):
            log("grid interval samples used %d out of %d, err=%5f\n"%(len(interval), intervaltotalnum, err));
            break;
        
        #lower err and try again
        interval=np.delete(interval,errs.argmax());

    log('used intervals\n%s'%('\n'.join(['%4d'%i for i in interval])))

    gridave=interval.sum()/len(interval)
    griderr=interval.var()

    log('g=%3f,ge=%5f.3f'%(gridave,griderr))
    
    
    #find plotting scale
    #standard: all bivalue map must be presented in [0,255] form
    psfindrange=int(2.5*gridave)
    #cut region and del the "ruler"
    mps = np.copy(mcolored[-psfindrange:-3, -psfindrange:])
    dbglogsavestep(mps)

    #filter absolute color
    mpshsv=cv.cvtColor(mps,cv.COLOR_BGR2HSV)
    darkgraypoints=cv.inRange(mpshsv,hsv2opencv8bithsv([0,0,0]),hsv2opencv8bithsv([360,50,30]))
    dbglogsavestep(darkgraypoints)

    #filter adaptive value(lightness)
    #mpsgray = cv.cvtColor(mps, cv.COLOR_BGR2GRAY)
    mpsgray=mpshsv[:,:,2]
    #enhance details in dark
    mpsgray=cv.normalize(mpsgray,None,0,255,cv.NORM_MINMAX)
    #flatten the mountain and enhance again
    #for text will never be too bright, 
    #but the contrast between shadow and nonshadow area around player to indicate the looking direction, 
    #could cause normalize trouble
    mpsgray[mpsgray>127]=127
    mpsgray*=2
    mpsgray = mpsgray.astype('float')
    relblack = cv.threshold(
        (mpsgray-(regionave(mpsgray, [5, 5])-20)), 0, 255, cv.THRESH_BINARY_INV)[1]
    dbglogsavestep(relblack)
    
    # #filter adaptive saturation
    # mpssat=mpshsv[:,:,1].astype('float')
    # relinsat = cv.threshold(
    #     (mpssat-(regionave(mpssat, [5, 5]))), 0, 255, cv.THRESH_BINARY_INV)[1]
    # dbglogsavestep(relinsat)
    
    black=np.logical_and(darkgraypoints,relblack).astype('float')*255
    #black=np.logical_and(black,relinsat).astype('float')*255
    dbglogsavestep(black)
    
    #delete grid lines
    gridlinekernellength=int(2*gridave)
    onepixline=np.ones([gridlinekernellength])
    
    kernelrow=np.array([-1*onepixline,1*onepixline,-1*onepixline])/gridlinekernellength
    kernels=[kernelrow,kernelrow.T]
    ongrid=np.zeros_like(black)*255
    for i in range(len(kernels)):
        onthisdirectiongrid=cv.filter2D(black/255,-1,kernels[i])
        dbglogsavestep(onthisdirectiongrid*255)
        onthisdirectiongrid=cv.threshold(onthisdirectiongrid,0.20,255,cv.THRESH_BINARY)[1]
        dbglogsavestep(onthisdirectiongrid)
        ongrid=np.logical_or(ongrid,onthisdirectiongrid).astype('float')*255
        dbglogsavestep(ongrid)

    black=np.logical_and(black,np.logical_not(ongrid)).astype('float')*255
    dbglogsavestep(black)
    
    #filter density to remove noise points
    for i in range(2):
        black=densityfilter(black/255,[5,5],3/25).astype('float')*255
        dbglogsavestep(black)
    
    #set the most densed pos, as the text is, to center
    dence=density(black/255,[11,11])
    dbglogsavestep(dence,method='savematflt')
    minval,maxval,minloc,maxloc=cv.minMaxLoc(dence)
    vector=np.round(np.flip(dence.shape)*0.5)-maxloc
    shiftmat=np.array([
        [1,0,vector[0]],
        [0,1,vector[1]]
    ])
    black=cv.warpAffine(black,shiftmat,np.flip(black.shape))
    dbglogsavestep(black)
    
    #assume text is at the center vertically
    textheight=15+4
    toppos=int(black.shape[0]*0.5-0.5*textheight)
    black=black[toppos:toppos+textheight,:]
    dbglogsavestep(black)

    plottingscalestr = ptact.image_to_string(black.astype('uint8'), lang='eng')
    log('plottingscale')
    log(plottingscalestr)
    plottingscale=numinstr(plottingscalestr)

    return 'OK',playerpos,playererr,ympos,ymerr,gridave,griderr,plottingscale

def outputlines2mat(m,pos,content,lineheight=25):
    m=m.copy()
    line=content.split('\n')
    for i,l in enumerate(line):
        cv.putText(
            m,
            l,
            pos.astype('int32')
            +[0,i*lineheight],
            cv.FONT_HERSHEY_SIMPLEX,
            1,
            textcolor)
    return m

def cutBottomRightMap(m):
    pa=np.array([1548, 729])
    pb=np.array([1871, 1052])
    return cv.getRectSubPix(m,pb-pa,0.5*(pa+pb))


def addShadow2HUD(m,thickness=shadowthickness):
    gray=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
    kernelshape=2*thickness+1
    edgekernel=np.ones([kernelshape,kernelshape])
    edgekernel[thickness,thickness]=-100#anchor pix must be black
    # edgekernel=np.array([
    #     [1,1,1],
    #     [1,-80,1],
    #     [1,1,1],
    # ])
    edge=cv.filter2D(gray,-1,edgekernel)
    edge=cv.threshold(edge,0,1,cv.THRESH_BINARY)[1]
    edge=edge.reshape(edge.shape+(1,))
    return m+edge*shadowcolor