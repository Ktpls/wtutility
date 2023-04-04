
import sys
from time import sleep
sys.path.append('.')
from utility import *

#estimate cammotion from full screen
def achievement1():
    cap = cv.VideoCapture(r"D:\output\pycammot\wtplane.avi")
    n_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH)) 
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    fps = 5
    out = cv.VideoWriter(r"D:\output\pycammot\f_marked.avi", fourcc, fps, (w, h), False)
    uimask=cv.imread(r"D:\output\pycammot\UIMASK.png")
    uimask=cv.cvtColor(uimask, cv.COLOR_BGR2GRAY)
    uimask=1/255*uimask.astype('float')
    #uimask=np.ones_like(uimask)

    # Read first frame
    prev = cap.read()[1]
    prev_gray=(uimask*cv.cvtColor(prev, cv.COLOR_BGR2GRAY)).astype('uint8')
    p0=np.array([568,194])
    for i in range(n_frames-2):
        curr = cap.read()[1]
        curr_gray = (uimask*cv.cvtColor(curr, cv.COLOR_BGR2GRAY)).astype('uint8')
        trackingpoints,cm=cameramotion(prev_gray,curr_gray)
        p0_totranform=np.concatenate((p0,[1]))
        p0inthisframe=cm@p0_totranform
        cm_transition=[cm[0,2],cm[1,2]]
        pnew=planetracker(curr_gray,p0inthisframe,100)
        pv=pnew-p0inthisframe

        #orgpoint=np.array([w/2,h/2],np.int32)

        #delta plane
        output_gray=cv.line(
            curr_gray,
            p0inthisframe.astype('int32'),
            pnew.astype('int32'),
            127)
        #plane
        output_gray=cv.circle(
            output_gray,
            pnew.astype('int32'),
            20,
            255)
        #transformed old plane
        output_gray=cv.circle(
            output_gray,
            p0inthisframe.astype('int32'),
            20,
            127)
        #old plane
        output_gray=cv.circle(
            output_gray,
            p0.astype('int32'),
            20,
            0)

        #draw cam motion
        output_gray=cv.line(
            curr_gray,
            np.array([w/2,h/2],np.int32),
            (np.array([w/2,h/2])+cm_transition).astype('int32'),
            127)

        #draw good points
        for p in trackingpoints:
            output_gray=cv.circle(
                output_gray,
                p[0].astype('int32'),
                3,
                255)
        out.write(output_gray)

        print("Frame: {}/{}, \n{}\n{},{}".format(
            str(i),
            str(n_frames),
            np.floor(100*cm)/100,
            np.array(pv,np.int32),
            np.array(pnew,np.int32)
            ))

        p0=pnew
        prev_gray = curr_gray
    out.release()
    win32api.Beep(1000,1000)
achievement1()