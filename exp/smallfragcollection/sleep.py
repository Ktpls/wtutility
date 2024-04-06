from utilref import *

ps = perf_statistic()
for i in range(10):
    ps.start()
    Rhythms.Success.play()
    ps.stop().countcycle()
print(ps.aveTime())
