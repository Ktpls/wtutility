
from wtdistmeaspy_implementation import *

caliOperator=loadCalibrationOperator()
class LastDistMeasResult:
    def __init__(self):
        self.val=None
    def get(self):
        if self.val is None:
            return False
        return self.val
    def set(self,val):
        self.val=val
lastDistMeasResultStaged=LastDistMeasResult()

def mainlogic():
    sleep(measdelay)  # for network delay

    # solve as successfully as possible
    for i in range(retryOnFailure):
        scr = screenshoter().shotbgr()
        scr = cutBottomRightMap(scr)

        # keep collecting
        if keepEveryMeasInRecord:
            ret = SolveMap_BottomRightSmallMap(scr, dbg=True, dbglogpath=r'./asset/wtdistmeaspy/log/{}_NormalTrace/'.format(
                time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()),
            ))
        else:
            ret = SolveMap_BottomRightSmallMap(scr)

        if didSolveMapSucceed(ret):
            break
        sleep(retryDelay)

    if not didSolveMapSucceed(ret):
        # still failed
        prompt = ret[0]
        dbglogreason = ret[0]
    else:
        state, playerpos, playererr, ympos, ymerr, gridave, griderr, plottingscale = ret

        # calc
        ympos = np.array(ympos)
        playerpos = np.array(playerpos)
        distingrid = np.sqrt(((ympos-playerpos)**2).sum()) / \
            gridave  # using unit in grid
        dist = distingrid*plottingscale

        refresult = ['%3d: %5d' % (r, int(distingrid*r+0.5)) for r in reflist]

        prompt = ''
        prompt += '%s\n' % (state)
        prompt += 'dist=%d\n' % (dist)

        def strictErrCheck():
            if playererr > plerrreqstrict:
                return 'SEC_PE'
            if ymerr < ymerrreqstrict:
                return 'SEC_YE'
            if griderr > griderrreqstrict:
                return 'SEC_GE'
            if plottingscale < plottingscalestrictlower or plottingscale > plottingscalestrictupper:
                return 'SEC_PS'
                # something going wrong, either not found or digits lost,
                # if less than 100 or more than 500
            return None  # keep dbglog unneeded
        dbglogreason = strictErrCheck()
        if dbglogreason is not None:
            # not usable
            prompt += 'but {}. \n'.format(dbglogreason)
            prompt += 'Not recommended to use, better try again\n'
        else:
            #everything goes great.
            # stage result
            lastDistMeasResultStaged.set(dist)
            
        prompt += '{}'.format('\n'.join(refresult))
        prompt += '\n'
        prompt += 'dg=%.2f,ps=%d,pe=%.2f,ye=%.2f,ge=%.2f\n' %\
            (distingrid, plottingscale, playererr, ymerr, griderr)
    if dbglogreason is not None and collectFailDebugOutput:
        # resolve with debug config
        ret = SolveMap_BottomRightSmallMap(scr, dbg=True, dbglogpath=r'./asset/wtdistmeaspy/log/{}_On{}/'.format(
            time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()),
            dbglogreason
        ))

    return prompt