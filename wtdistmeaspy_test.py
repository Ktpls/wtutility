from wtdistmeaspy import *
def testground():
    scr=cv.imread(
    r"C:\file\code\Opdar\asset\wtdistmeaspy\log\2022-12-15-10-47-39_OnSEC_DN\unnamed.png")
    ret=SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}/'.format(
        time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime())
        ))
    print(ret)
testground()