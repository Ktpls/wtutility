from utilref import *
import threading
import time


class MyThread(object):
    def __init__(self):
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            # Do some work here
            print("Working...")
            time.sleep(1)

    def stop(self):
        self.stop_event.set()


class StoppableThreadState(enum.Enum):
    stopped = 1
    running = 2
    stopping = 3


class StoppableThread2(StoppableSomewhat):
    """
    derivate from it and override foo()
    """

    # TODO give option to handle error by user. thats for wtutily system to log error
    def __init__(
        self,
        strategy_runonrunning: "StoppableSomewhat.StrategyRunOnRunning" = None,
        strategy_error: "StoppableSomewhat.StrategyError" = None,
        pool: futures.ThreadPoolExecutor = None,
    ) -> None:
        super().__init__(strategy_runonrunning, strategy_error)
        self.stopsignal = threading.Event()
        self.pool: futures.ThreadPoolExecutor = Coalesce(pool, futures.ThreadPoolExecutor())
        self.future = None
        self.state = StoppableThreadState.stopped

    def foo(self, *arg, **kw) -> typing.Any:
        raise NotImplementedError("should never run without overriding foo")

    def isRunning(self) -> bool:
        return self.state == StoppableThreadState.running

    @FunctionalWrapper
    def go(self, *arg, **kw) -> None:
        if self.isRunning():
            if (
                self.strategy_runonrunning
                == StoppableThread.StrategyRunOnRunning.raise_error
            ):
                raise RuntimeError("already running")
            elif (
                self.strategy_runonrunning
                == StoppableThread.StrategyRunOnRunning.stop_and_rerun
            ):
                self.stop()
            elif (
                self.strategy_runonrunning
                == StoppableThread.StrategyRunOnRunning.skip_and_return
            ):
                return
        self.ensureStopped()
        self.stopsignal.clear()

        def call() -> None:
            """
            wrapper so can call the passed "self"'s foo
            if not, can never know which overwritten foo should be called
            check if self.stopsignal when any place to break
            """
            ret = None
            try:
                ret = self.foo(*arg, **kw)
            except Exception as e:
                if self.strategy_error == StoppableThread.StrategyError.raise_error:
                    raise e
                elif self.strategy_error == StoppableThread.StrategyError.print_error:
                    traceback.print_exc()
                elif self.strategy_error == StoppableThread.StrategyError.ignore:
                    pass
            self.state = StoppableThreadState.stopped
            self.stopsignal.clear()
            return ret

        self.future = self.pool.submit(call)
        self.state = StoppableThreadState.running

    @FunctionalWrapper
    def stop(self) -> None:
        # add critical section here
        if self.state in (StoppableThreadState.stopped, StoppableThreadState.stopping):
            return
        self.state = StoppableThreadState.stopping
        self.stopsignal.set()

    def ensureStopped(self):
        if self.future is not None:
            self.future.result()
        self.state = StoppableThreadState.stopped

    def timeToStop(self) -> bool:
        return self.stopsignal.is_set()


def main():
    t = MyThread()
    with futures.ThreadPoolExecutor() as executor:
        future = executor.submit(t.run)
        # Do some other work here
        time.sleep(5)
        # Stop the thread
        t.stop()
        # Wait for the thread to finish
        future.result()


if __name__ == "__main__":
    main()
