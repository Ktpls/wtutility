import locale
from threading import local


def proc():
    var=1
    def proc2():
        nonlocal var
        var=2
    proc2()
    print(var)
    pass

proc()