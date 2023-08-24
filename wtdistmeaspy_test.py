from wtdistmeaspy import *
def testground():
    scr=cv.imread(
    r"C:\prog\wtutility\asset\wtdistmeaspy\log\2023-08-24-18-23-04_NormalTrace\unnamed.png")
    ret=SolveMap_BottomRightSmallMap(scr,dbg=True,dbglogpath=r'./asset/wtdistmeaspy/log/{}/'.format(
        time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime())
        ))
    print(ret)
testground()