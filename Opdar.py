
from opdar_implementation import *

# setup
hud = fullScrHUD()
hud.setup()


def main():
    tr = tracker()
    tracking = False
    lastT = time.perf_counter()

    # perfst=[
    #   perf_statistic(),
    #   perf_statistic(),
    #   perf_statistic()]

    while (True):
        sleepuntil(lambda: time.perf_counter() - lastT > 1.0 / fps,
                   dt=0.25 * 1 / fps)
        nowtime = time.perf_counter()
        frametime = nowtime - lastT
        lastT = nowtime

        if isKBDown(win32con.VK_F10):
            tr.setup(lockpoint_default)
            tracking = True
        if isKBDown(win32con.VK_F11):
            tracking = False
            win32api.Beep(500, 100)
        if isKBDown(win32con.VK_F12):
            hud.stop()
            odc=None
            break

        output = np.zeros([h, w, 3], np.uint8)

        def drawsearchrange(output, p):
            # range it self
            output = cv.circle(output, p.astype('int32'), searchrange,
                               lockcirclecolor, lockcirclethickness)
            # inner shadow
            output = cv.circle(
                output, p.astype('int32'),
                searchrange - (2 * (lockcirclethickness - 1) + 1),
                lockcirclecolorinner, lockcirclethickness)
            # outter shadow
            output = cv.circle(
                output, p.astype('int32'),
                searchrange + (2 * (lockcirclethickness - 1) + 1),
                lockcirclecoloroutter, lockcirclethickness)
            return output

        if tracking:

            # track
            ponshot, pomega, plastinthisframe, wingspanpx, cm, trackingpoints, planemap, pul, maxscore = tr.track(
            )

            distance = targetwingspan / (c_thetabypix * wingspanpx)

            te = distance / vbullet
            # the compensation of calculation delay from shot time
            pcompensation = (time.perf_counter() - tr.lastshottime) * pomega
            pest = te * pomega
            pverticaltargeting = [
                0,
                0.5 * np.arcsin(9.8e-3 * distance / vbullet**2) / c_thetabypix
            ]
            estimed = ponshot + pcompensation + pest + pverticaltargeting
            pnow = ponshot + pcompensation

            output = drawsearchrange(output, pnow)

            # plane pos
            output = cv.circle(output, pnow.astype('int32'), planecircleradius,
                               planecirclecolor, firecontrolseriesthickness)
            # speed vector
            output = cv.line(output, pnow.astype('int32'),
                             (estimed).astype('int32'), speedvectorcolor,
                             firecontrolseriesthickness)
            # estimated point
            output = cv.circle(output, (estimed).astype('int32'), 10,
                               firecontrolcirclecolor,
                               firecontrolseriesthickness)

            # info
            infoline = 0

            def outputoneline():
                nonlocal infoline, output
                cv.putText(
                    output, info,
                    pnow.astype('int32') +
                    [0, searchrange + 3 * lockcirclethickness + lineheight] +
                    [0, infoline * lineheight], cv.FONT_HERSHEY_SIMPLEX, 1,
                    textcolor)
                infoline += 1

            info = '%4.2fkm, %4.2fs' % (distance, te)
            outputoneline()
            info = '(%4.2f,%4.2f)' % (pomega[0], pomega[1])
            outputoneline()
            info = 's%4.2f' % (maxscore)
            outputoneline()

            # plane tracker's view
            planemap = cv.threshold(planemap, 0, 1, cv.THRESH_BINARY)[1]
            planemap = 255 * planemap
            planemap = planemap.astype('uint8').reshape(
                np.concatenate((planemap.shape, [1])))
            planemap = np.concatenate((planemap, planemap, planemap), 2)
            bigplanemap = cv.copyMakeBorder(
                planemap, pul[1], output.shape[0] - planemap.shape[0] - pul[1],
                pul[0], output.shape[1] - planemap.shape[1] - pul[0],
                cv.BORDER_CONSTANT)
            output += bigplanemap

            # #last pos
            # output=cv.circle(
            #   output,
            #   (plastinthisframe).astype('int32'),
            #   10,
            #   (0,0,255))

            # #draw cam motion
            # cm_transition=[cm[0,2],cm[1,2]]
            # output=cv.line(
            #   output,
            #   np.array([w/2,h/2],np.int32),
            #   (np.array([w/2,h/2])+cm_transition).astype('int32'),
            #   127)

            # #draw good points
            # for p in trackingpoints:
            #   output=cv.circle(
            #       output,
            #       p[0].astype('int32'),
            #       3,
            #       (255,255,255))

        else:
            output = drawsearchrange(output, lockpoint_default)

        hud.clear()
        hud.addcontent(output)  # cuz its full screenly overlayer
        hud.update()

    win32api.Beep(1000, 1000)
    # for i,ps in enumerate(perfst):
    #   print(ps.read_ave_t())


main()
