from utilref import *
from opdar_implementation import *

# setup
hud = fullScrHUD()
hud.setup()


def beepOnErr():
    Rhythms.Error.play()


throwErrorInHotkey = True


def main():
    tr = tracker()
    tracking = False
    lastT = time.perf_counter()

    hklist = []

    def trackswitch():
        nonlocal tracking
        if not tracking:
            tr.setup(lockpoint_default)
            tracking = True
        else:
            tracking = False
            Rhythms.Notify.play()

    hklist.append(HotkeyManager.hotkeytask([win32con.VK_F10], trackswitch))

    # key shortcuts
    import keyshortcut.keyshortcut as keyshortcut

    def holdCAndTell():
        keyshortcut.holdC()
        Rhythms.Notify.play()

    hklist.append(HotkeyManager.hotkeytask(key=win32con.VK_F11, foo=holdCAndTell))
    hkm = HotkeyManager(hklist)

    while True:
        sleepuntil(lambda: time.perf_counter() - lastT > 1.0 / fps, dt=0.25 * 1 / fps)
        nowtime = time.perf_counter()
        frametime = nowtime - lastT
        lastT = nowtime
        decideresult = hkm.decideAllHotKey()
        for i in range(len(decideresult)):
            if decideresult[i]:
                try:
                    hkm.hktl[i].foo()
                except Exception as e:
                    beepOnErr()
                    if throwErrorInHotkey:
                        raise e
                    traceback.print_exc()

        output = np.zeros([h, w, 3], np.uint8)

        def drawsearchrange(output, p):
            # range it self
            output = cv.circle(
                output,
                p.astype("int32"),
                searchrange,
                lockcirclecolor,
                lockcirclethickness,
            )
            # inner shadow
            output = cv.circle(
                output,
                p.astype("int32"),
                searchrange - (2 * (lockcirclethickness - 1) + 1),
                lockcirclecolorinner,
                lockcirclethickness,
            )
            # outter shadow
            output = cv.circle(
                output,
                p.astype("int32"),
                searchrange + (2 * (lockcirclethickness - 1) + 1),
                lockcirclecoloroutter,
                lockcirclethickness,
            )
            return output

        if tracking:
            # track
            trkret = tr.track()
            (
                ponshot,
                pomega,
                plastinthisframe,
                wingspan,
                cm,
                trackingpoints,
                planemap,
                pul,
                thetabypix,
            ) = (
                trkret.ponshot,
                trkret.pomega,
                trkret.plastinthisframe,
                trkret.wingspan,
                trkret.cm,
                trkret.trackingpoints,
                trkret.planemap,
                trkret.pul,
                trkret.thetabypix,
            )

            distance = targetwingspan / (thetabypix * wingspan + epsilon)

            te = distance / vbullet
            # the compensation of calculation delay from shot time
            pcompensation = (time.perf_counter() - tr.lastshottime) * pomega
            pest = te * pomega
            pverticaltargeting = [
                0,
                0.5 * np.arcsin(9.8e-3 * distance / vbullet**2) / thetabypix,
            ]
            estimed = ponshot + pcompensation + pest + pverticaltargeting
            pnow = ponshot + pcompensation

            output = drawsearchrange(output, pnow)

            # plane pos
            output = cv.circle(
                output,
                pnow.astype("int32"),
                planecircleradius,
                planecirclecolor,
                firecontrolseriesthickness,
            )
            # speed vector
            output = cv.line(
                output,
                pnow.astype("int32"),
                (estimed).astype("int32"),
                speedvectorcolor,
                firecontrolseriesthickness,
            )
            # estimated point
            output = cv.circle(
                output,
                (estimed).astype("int32"),
                10,
                firecontrolcirclecolor,
                firecontrolseriesthickness,
            )

            # info
            infoline = 0

            def outputoneline():
                nonlocal infoline, output
                cv.putText(
                    output,
                    info,
                    pnow.astype("int32")
                    + [0, searchrange + 3 * lockcirclethickness + lineheight]
                    + [0, infoline * lineheight],
                    cv.FONT_HERSHEY_SIMPLEX,
                    1,
                    textcolor,
                )
                infoline += 1

            info = "%4.2fkm, %4.2fs" % (distance, te)
            outputoneline()
            info = "(%4.2f,%4.2f)" % (pomega[0], pomega[1])
            outputoneline()

            # plane tracker's view
            planemap = cv.threshold(planemap, 0, 1, cv.THRESH_BINARY)[1]
            planemap = 255 * planemap
            planemap = planemap.astype("uint8").reshape(
                np.concatenate((planemap.shape, [1]))
            )
            planemap = np.concatenate((planemap, planemap, planemap), 2)
            # bigplanemap = cv.copyMakeBorder(
            #     planemap, pul[1], output.shape[0] - planemap.shape[0] - pul[1],
            #     pul[0], output.shape[1] - planemap.shape[1] - pul[0],
            #     cv.BORDER_CONSTANT)
            # output += bigplanemap

            # pul is in [x,y], originated from screensize = np.array([w, h], np.int32)
            output[
                pul[1] : pul[1] + planemap.shape[0],
                pul[0] : pul[0] + planemap.shape[1],
                :,
            ] += planemap

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

    Rhythms.Cancel.play()
    # for i,ps in enumerate(perfst):
    #   print(ps.read_ave_t())


main()
