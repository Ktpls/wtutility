
import sys

sys.path.append('.')
from utility import *
textcolor=255*rgb2bgr(hsv2rgb((0,0,1)))
textshadowcolor=255*rgb2bgr(hsv2rgb((0,0,0.3)))
outputpos=[100,540]
#screen
screenshape=[1080,1920]
def outputlines2mat(m,pos,content, lineinterval=10):
    pos=np.array(pos).astype('int')
    line=content.split('\n')
    yoffset=0
    xmax=0
    fontFace=cv.FONT_HERSHEY_DUPLEX
    fontScale=1
    thickness=1
    for i,l in enumerate(line):
        size=np.array(cv.getTextSize(l, fontFace, fontScale, thickness)[0])
        yoffset+=size[1]+lineinterval if i!=0 else size[1]
        if xmax< size[0]:
            xmax=size[0]
        m=cv.putText(
            m,
            l,
            pos+[0,yoffset],
            fontFace,
            fontScale,
            textcolor,
            thickness=thickness)
    box=[pos,pos + [xmax,yoffset]]
    return m,box

def simpleAntialising(m,size=3):
    shadow=cv.GaussianBlur(m,[size,size],None)
    intersection=cv.cvtColor(m,cv.COLOR_BGR2GRAY)
    intersection=cv.threshold(m,0,1,cv.THRESH_BINARY)[1]
    return shadow*(1-intersection)+m

def putProgressClock(m,prog,pos,radius,color):
    pos=np.array(pos)
    prog=0.25-prog
    center=pos+[radius,radius]
    cv.line(
        m,
        center,
        (center+[radius*np.cos(prog*2*np.pi),-radius*np.sin(prog*2*np.pi)]).astype('int'),
        color
    )
    cv.circle(
        m,
        center,
        radius,
        color
    )
    return m

def putTimedMsg(m,msg,prog,pos,clockverticalaligncentered=False,padding=10):
    pos=np.array(pos)
    contentpos=pos+[padding,padding]
    clockpadding=5
    clockrad=30
    
    promptpos=contentpos+[2*clockpadding+2*clockrad,0]
    m,boxtext=outputlines2mat(
        m,
        promptpos,
        msg)
    
    boxrdtotal=boxtext[1]
    if boxrdtotal[1]<contentpos[1]+2*clockpadding+2*clockrad:
        boxrdtotal[1]=contentpos[1]+2*clockpadding+2*clockrad
    
    m=putProgressClock(
        m,
        prog,
        [
            contentpos[0]+clockpadding,
            int(0.5*(box[1][1]+contentpos[1]))-clockrad if clockverticalaligncentered else
                contentpos[1]+clockpadding
        ],
        clockrad,
        (255,255,255)
    )
    box=[pos,boxrdtotal+[padding,padding]]
    m=cv.rectangle(
        m,
        box[0],
        box[1],
        (255,255,255),
        thickness=2
    )
    return m,box

def bgrhud():
    hud=fullScrHUD()
    hud.setcontent(np.zeros(screenshape+[3],np.uint8))
    hud.setup()
    fps=fpsmanager(10)
    msg='123\n'
    msg+='456\n'
    msg+='789'
    starttime=time.time()
    while(True):
        fps.next()
        m=np.zeros(screenshape+[3],np.uint8)
        m,_=putTimedMsg(
            m,
            msg,
            0.1*(time.time()-starttime),
            outputpos)
        
        hud.setcontent(simpleAntialising(m))
        hud.update()

bgrhud()