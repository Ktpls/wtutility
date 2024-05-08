class ClassNone:
    def __init__(
        self, defaultPropertyValue=None, defaultMethodValue=None, *args, **kwargs
    ):
        self.defaultMethodValue = defaultMethodValue or dict()
        self.defaultPropertyValue = defaultPropertyValue or dict()
        pass


    def __getattr__(self, name: str):
        def _func_none(*args, **kwargs):
            pass
        return _func_none



a = ClassNone()
print(a.dosomething())
