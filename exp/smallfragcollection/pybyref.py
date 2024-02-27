class Container:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return self.val.__str__()

    def __repr__(self):
        return self.val.__repr__()

    def __hash__(self):
        return self.val.__hash__()

    def __bool__(self):
        return self.val.__bool__()

    def __len__(self):
        return self.val.__len__()

    def __getitem__(self, key):
        return self.val.__getitem__(key)

    def __setitem__(self, key, value):
        return self.val.__setitem__(key, value)

    def __delitem__(self, key):
        return self.val.__delitem__(key)

    def __iter__(self):
        return self.val.__iter__()

    def __contains__(self, item):
        return self.val.__contains__(item)

    def __lt__(self, other):
        return self.val.__lt__(other)

    def __le__(self, other):
        return self.val.__le__(other)

    def __gt__(self, other):
        return self.val.__gt__(other)

    def __ge__(self, other):
        return self.val.__ge__(other)

    def __add__(self, other):
        return self.val.__add__(other)

    def __sub__(self, other):
        return self.val.__sub__(other)

    def __mul__(self, other):
        return self.val.__mul__(other)

    def __matmul__(self, other):
        return self.val.__matmul__(other)

    def __truediv__(self, other):
        return self.val.__truediv__(other)

    def __floordiv__(self, other):
        return self.val.__floordiv__(other)

    def __mod__(self, other):
        return self.val.__mod__(other)

    def __divmod__(self, other):
        return self.val.__divmod__(other)

    def __pow__(self, other, modulo=None):
        return self.val.__pow__(other, modulo)

    def __lshift__(self, other):
        return self.val.__lshift__(other)

    def __rshift__(self, other):
        return self.val.__rshift__(other)

    def __and__(self, other):
        return self.val.__and__(other)

    def __xor__(self, other):
        return self.val.__xor__(other)

    def __or__(self, other):
        return self.val.__or__(other)

    def __radd__(self, other):
        return self.val.__radd__(other)

    def __rsub__(self, other):
        return self.val.__rsub__(other)

    def __rmul__(self, other):
        return self.val.__rmul__(other)

    def __rmatmul__(self, other):
        return self.val.__rmatmul__(other)

    def __rtruediv__(self, other):
        return self.val.__rtruediv__(other)

    def __rfloordiv__(self, other):
        return self.val.__rfloordiv__(other)

    def __rmod__(self, other):
        return self.val.__rmod__(other)

    def __rdivmod__(self, other):
        return self.val.__rdivmod__(other)

    def __rpow__(self, other, modulo=None):
        return self.val.__rpow__(other, modulo)

    def __rlshift__(self, other):
        return self.val.__rlshift__(other)

    def __rrshift__(self, other):
        return self.val.__rrshift__(other)

    def __rand__(self, other):
        return self.val.__rand__(other)

    def __rxor__(self, other):
        return self.val.__rxor__(other)

    def __ror__(self, other):
        return self.val.__ror__(other)

    def __iadd__(self, other):
        return self.val.__iadd__(other)

    def __isub__(self, other):
        return self.val.__isub__(other)

    def __imul__(self, other):
        return self.val.__imul__(other)

    def __imatmul__(self, other):
        return self.val.__imatmul__(other)

    def __itruediv__(self, other):
        return self.val.__itruediv__(other)

    def __ifloordiv__(self, other):
        return self.val.__ifloordiv__(other)

    def __imod__(self, other):
        return self.val.__imod__(other)

    def __ipow__(self, other, modulo=None):
        return self.val.__ipow__(other, modulo)

    def __ilshift__(self, other):
        return self.val.__ilshift__(other)

    def __irshift__(self, other):
        return self.val.__irshift__(other)

    def __iand__(self, other):
        return self.val.__iand__(other)

    def __ixor__(self, other):
        return self.val.__ixor__(other)

    def __ior__(self, other):
        return self.val.__ior__(other)

    def __neg__(self):
        return self.val.__neg__()

    def __pos__(self):
        return self.val.__pos__()

    def __abs__(self):
        return self.val.__abs__()

    def __invert__(self):
        return self.val.__invert__()

    def __complex__(self):
        return self.val.__complex__()

    def __int__(self):
        return self.val.__int__()

    def __float__(self):
        return self.val.__float__()

    def __round__(self, n=None):
        return self.val.__round__(n)

    def __trunc__(self):
        return self.val.__trunc__()

    def __floor__(self):
        return self.val.__floor__()

    def __ceil__(self):
        return self.val.__ceil__()

    def __enter__(self):
        return self.val.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        return self.val.__exit__(exc_type, exc_value, traceback)

    def __await__(self):
        return self.val.__await__()

    def __aiter__(self):
        return self.val.__aiter__()

    def __anext__(self):
        return self.val.__anext__()

    def __aenter__(self):
        return self.val.__aenter__()

    def __aexit__(self, exc_type, exc_value, traceback):
        return self.val.__aexit__(exc_type, exc_value, traceback)

    def __getattribute__(self, name):
        if name == "val":
            return object.__getattribute__(self, name)
        return self.val.__getattribute__(name)

    def __setattr__(self, name, value):
        if name == "val":
            return object.__setattr__(self, name, value)
        return self.val.__setattr__(name, value)

    def __delattr__(self, name):
        return self.val.__delattr__(name)

    def __dir__(self):
        return self.val.__dir__()

    def __class__(self):
        return self.val.__class__()

    def __instancecheck__(self, instance):
        return self.val.__instancecheck__(instance)

    def __subclasscheck__(self, subclass):
        return self.val.__subclasscheck__(subclass)

    def __subclasshook__(self, subclass):
        return self.val.__subclasshook__(subclass)

    def __call__(self, *args, **kwargs):
        return self.val.__call__(*args, **kwargs)

    def __copy__(self):
        return self.val.__copy__()

    def __deepcopy__(self, memo):
        return self.val.__deepcopy__(memo)

    def __sizeof__(self):
        return self.val.__sizeof__()


def modify(x):
    x += 1

# not working actually
x = Container(1)
modify(x)
print(x)
