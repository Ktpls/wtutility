from .wtdistmeaspy_implementation import *


@dataclasses.dataclass
class WtdmpMainLogicResult:
    prompt: str
    succeed: bool


class wtdistmeaspy:
    """
    TODO
    reconstruct logic to make it of specificity
    """

    caliOperator = loadCalibrationOperator()

    lastDistMeasResultStaged = ElementsOfMap(None, None, None, None, None)

    psLocked = False

    smallMapCollector = DataCollector(r"./asset/wtdistmeaspy/smallMapCollection")

    def solveMapMainLogic(self):
        sleep(measdelay)  # for network delay

        # solve as successfully as possible
        for i in range(retryOnFailure):
            scr = screenshoter().shotbgr()
            scr = cutBottomRightMap(scr)
            # scr=cv.imread(r"C:\file\code\wtutility\asset\wtdistmeaspy\log\2023-11-05-00-46-33_NormalTrace\unnamed.png")

            # keep collecting
            if keepEveryMeasInRecord:
                ret = SolveMap_BottomRightSmallMap(
                    scr,
                    dbg=True,
                    dbglogpath=r"./asset/wtdistmeaspy/log/{}_NormalTrace/".format(
                        GetTimeString(),
                    ),
                    dontGetPlottingScale=self.psLocked,
                )
            else:
                ret = SolveMap_BottomRightSmallMap(
                    scr,
                    dontGetPlottingScale=self.psLocked,
                )
            # not found
            if ret.ym.state.smetype == SMException.SolveMapResultType.NO_ERR:
                break
            sleep(retryDelay)

        def exceptionlist2str(el, spliter=None):
            if spliter is None:
                spliter = "\n"
            return spliter.join([e.__repr__() for e in el])

        exception: List[SMException] = []
        prompt = ""

        # check if fall back to last result
        def CheckAndReplaceIfNeeded(
            resultitem: SolveMapResultItem,
            val2replace: Any,
            exceptionOnReplace: SMException,
        ):
            if resultitem.state.smetype != SMException.SolveMapResultType.NO_ERR:
                if val2replace is not None:
                    resultitem.result = val2replace
                    resultitem.err = 0
                    exception.append(exceptionOnReplace)
                else:
                    exception.append(resultitem.state)

        # ym is special, dont use staged one
        if ret.ym.state.smetype != SMException.SolveMapResultType.NO_ERR:
            exception.append(ret.ym.state)
        CheckAndReplaceIfNeeded(
            ret.playerpos,
            self.lastDistMeasResultStaged.playerpos,
            SMException(SMException.SolveMapResultType.using_last_playerpos),
        )
        CheckAndReplaceIfNeeded(
            ret.grid,
            self.lastDistMeasResultStaged.gridave,
            SMException(SMException.SolveMapResultType.using_last_grid),
        )
        # lock is priored than normally check and replace
        if self.psLocked:
            if self.lastDistMeasResultStaged.plottingscale is not None:
                ret.plottingscale.result = self.lastDistMeasResultStaged.plottingscale
                ret.plottingscale.err = 0
                # hint in exception will be done in secure check
            else:
                raise Exception("ps locked but no last ps")
        else:
            CheckAndReplaceIfNeeded(
                ret.plottingscale,
                self.lastDistMeasResultStaged.plottingscale,
                SMException(SMException.SolveMapResultType.using_last_ps),
            )

        if all([e.IsExceptionSafeToPass() for e in exception]):
            # able to go on

            # u wont need to strictly check if anything fatal, will u?
            def strictErrCheck():
                err = []

                if ret.playerpos.err > plerrreqstrict:
                    err.append(SMException(SMException.SolveMapResultType.SEC_PE))
                else:
                    self.lastDistMeasResultStaged.playerpos = ret.playerpos.result

                if ret.ym.err < ymerrreqstrict:
                    err.append(SMException(SMException.SolveMapResultType.SEC_YE))
                else:
                    self.lastDistMeasResultStaged.ympos = ret.ym.result

                if ret.grid.err > griderrreqstrict:
                    err.append(SMException(SMException.SolveMapResultType.SEC_GE))
                else:
                    self.lastDistMeasResultStaged.gridave = ret.grid.result

                if self.psLocked:
                    err.append(SMException(SMException.SolveMapResultType.SEC_PSLOCK))
                else:
                    if (
                        ret.plottingscale.result < plottingscalestrictlower
                        or ret.plottingscale.result > plottingscalestrictupper
                    ):
                        # something going wrong, either not found or digits lost,
                        # if less than 100 or more than 500
                        err.append(SMException(SMException.SolveMapResultType.SEC_PS))
                    else:
                        self.lastDistMeasResultStaged.plottingscale = (
                            ret.plottingscale.result
                        )

                return err  # keep dbglog unneeded

            exception += strictErrCheck()

            # calc
            ympos = np.array(ret.ym.result)
            playerpos = np.array(ret.playerpos.result)
            gridave = ret.grid.result
            plottingscale = ret.plottingscale.result
            distingrid = (
                np.sqrt(((ympos - playerpos) ** 2).sum()) / gridave
            )  # using unit in grid
            dist = distingrid * plottingscale

            refresult = ["%3d: %5d" % (r, int(distingrid * r + 0.5)) for r in reflist]

            prompt += "OK, dist=%.2f\n" % (dist)
            if len(exception) != 0:
                prompt += exceptionlist2str(exception, ",") + "\n"

            # got here anyway avoiding all the fatal ones
            # commit result
            self.lastDistMeasResultStaged.result = dist

            # todo: considering if i should automaticly calibrate

            i = 0
            while i < len(refresult):
                for j in range(3):
                    prompt += refresult[i] + ", "
                    i += 1
                    if i >= len(refresult):
                        break
                prompt += "\n"
            prompt += "dg=%.2f,ps=%d,pe=%.2f,ye=%.2f,ge=%.2f" % (
                distingrid,
                plottingscale,
                ret.playerpos.err,
                ret.ym.err,
                ret.grid.err,
            )
            solveSummary = True
        else:
            # fatal happended
            prompt += "Failed\n"
            prompt += exceptionlist2str(exception) + "\n"

            if collectFailDebugOutput:
                # resolve with debug config
                ret = SolveMap_BottomRightSmallMap(
                    scr,
                    dbg=True,
                    dbglogpath=r"./asset/wtdistmeaspy/log/{}_On{}/".format(
                        GetTimeString(),
                        exceptionlist2str(exception, ", "),
                    ),
                )
            solveSummary = False

        if collectingSmallMap:
            self.smallMapCollector.save(scr)
        return WtdmpMainLogicResult(prompt, solveSummary)
