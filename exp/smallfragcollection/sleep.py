from utilref import *

ps = perf_statistic()
for i in range(10):
    ps.start()
    Rythm.RythmSuccess.play()
    ps.stop().countcycle()
print(ps.aveTime())
