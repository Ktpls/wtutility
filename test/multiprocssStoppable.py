import multiprocessing
import time

from utilref import *


# Example of an inherited class
class MyChildProcess(StoppableProcess):
    def foo(self, para):
        while not self.timeToStop():
            # Your custom logic here
            print(f'foo running, param{para}')
            time.sleep(1)
        print('foo dont want to leave')
        time.sleep(1)
        print('foo going to leave')


if __name__ == "__main__":
    my_process = MyChildProcess()
    my_process.go(para='111')

    # Run for 5 seconds and then stop the process
    time.sleep(5)
    
    print('foo stop calls')
    my_process.stop()
    print('foo done')
