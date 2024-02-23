class StdSingleton:
    _instance = None
    val = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass


def Singleton(cls):
    cls.__singleton_instance__ = None

    def fooNew(cls):
        if cls.__singleton_instance__ is None:
            cls.__singleton_instance__ = object.__new__(cls)
        return cls.__singleton_instance__

    cls.__new__ = fooNew
    return cls


@Singleton
class Port8111Cache:
    val = 0

    def __init__(self):
        pass


a = Port8111Cache()
print(a.val)
a.val = 10
b = Port8111Cache()
print(b.val)
