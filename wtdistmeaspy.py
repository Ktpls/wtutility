from wtdistmeaspy_implementation import *

caliOperator = loadCalibrationOperator()

lastDistMeasResultStaged = ElementsOfMap(None, None, None, None, None)


def mainlogic():
    sleep(measdelay)  # for network delay

    # solve as successfully as possible
    for i in range(retryOnFailure):
        scr = screenshoter().shotbgr()
        scr = cutBottomRightMap(scr)

        # keep collecting
        if keepEveryMeasInRecord:
            ret = SolveMap_BottomRightSmallMap(
                scr,
                lastDistMeasResultStaged,
                dbg=True,
                dbglogpath=r"./asset/wtdistmeaspy/log/{}_NormalTrace/".format(
                    time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()),
                ),
            )
        else:
            ret = SolveMap_BottomRightSmallMap(scr, lastDistMeasResultStaged)

        if didSolveMapSucceed(ret):
            break
        sleep(retryDelay)

    def exception2str(exc, spliter=None):
        if spliter is None:
            spliter = "\n"
        return spliter.join([e.__repr__() for e in exc])

    exception: List[SMException] = []
    prompt = ""
    if not didSolveMapSucceed(ret):
        # still failed
        # break with fatal exception
        exception = ret[1]
        prompt += "Failed\n"
        prompt += exception2str(exception)
    else:
        (
            state,
            playerpos,
            playererr,
            ympos,
            ymerr,
            gridave,
            griderr,
            plottingscale,
            msgExtra,
        ) = ret
        exception.extend(msgExtra)

        # calc
        ympos = np.array(ympos)
        playerpos = np.array(playerpos)
        distingrid = (
            np.sqrt(((ympos - playerpos) ** 2).sum()) / gridave
        )  # using unit in grid
        dist = distingrid * plottingscale

        refresult = ["%3d: %5d" % (r, int(distingrid * r + 0.5)) for r in reflist]

        prompt = ""
        prompt += (
            "%s\n" % (state)
            + exception2str(exception)
            + ("\n" if len(exception) > 0 else "")
        )
        prompt += "dist=%.2f\n" % (dist)

        def strictErrCheck():
            err = []

            if playererr > plerrreqstrict:
                err.append(SMException(SMException.SMEType.SEC_PE))
            else:
                lastDistMeasResultStaged.playerpos = playerpos

            if ymerr < ymerrreqstrict:
                err.append(SMException(SMException.SMEType.SEC_YE))
            else:
                lastDistMeasResultStaged.ympos = ympos

            if griderr > griderrreqstrict:
                err.append(SMException(SMException.SMEType.SEC_GE))
            else:
                lastDistMeasResultStaged.gridave = gridave

            if (
                plottingscale < plottingscalestrictlower
                or plottingscale > plottingscalestrictupper
            ):
                # something going wrong, either not found or digits lost,
                # if less than 100 or more than 500
                err.append(SMException(SMException.SMEType.SEC_PS))
            else:
                lastDistMeasResultStaged.plottingscale = plottingscale

            return err  # keep dbglog unneeded

        exception += strictErrCheck()
        if len(exception) > 0:
            # not usable
            prompt += "but {}. \n".format(exception2str(exception))
            prompt += "Not recommended to use, better try again\n"
        # got here anyway avoiding all the fatal ones
        # commit result
        lastDistMeasResultStaged.result = dist

        # todo: considering if i should automaticly calibrate

        i = 0
        while i < len(refresult):
            for j in range(3):
                prompt += refresult[i] + ", "
                i += 1
                if i >= len(refresult):
                    break
            prompt += "\n"
        prompt += "dg=%.2f,ps=%d,pe=%.2f,ye=%.2f,ge=%.2f\n" % (
            distingrid,
            plottingscale,
            playererr,
            ymerr,
            griderr,
        )
    if len(exception) > 0 and collectFailDebugOutput:
        # resolve with debug config
        ret = SolveMap_BottomRightSmallMap(
            scr,
            dbg=True,
            dbglogpath=r"./asset/wtdistmeaspy/log/{}_On{}/".format(
                time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()),
                exception2str(exception, ", "),
            ),
        )

    return prompt
