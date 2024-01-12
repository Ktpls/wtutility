from utilref import *


@StoppableSomewhat.EasyUse(strategy_runonrunning=StoppableSomewhat.StrategyRunOnRunning.stop_and_rerun)
def foo(self:StoppableSomewhat, id):
    def say(msg):
        print(f'{id:<10}{msg}')
    say('start')
    for i in range(10):
        if self.timeToStop():
            break
        say(i)
        time.sleep(1)
    say('end')

count_main=0
foo(1)
time.sleep(5)
foo(2)

time.sleep(20)