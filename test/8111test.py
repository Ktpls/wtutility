from utilref import *

def benchMark():
    ps = perf_statistic()

    ps.start()
    for i in range(1000):
        obj = Port8111.get(Port8111.QueryType.map_info)
        ps.countcycle()
    ps.stop()
    print(f"{ps.aveTime()=}")
pass
