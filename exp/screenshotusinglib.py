import sys
import time
import numpy
from utilref import *
import pyautogui

import time


def main():
    ps = perf_statistic(True)
    for i in range(100):
        ret=pyautogui.screenshot()
        ps.countcycle()
        if i % 10 == 0:
            print(i)
    ps.stop()
    print(ps.read_ave_t())


if __name__ == "__main__":
    main()
