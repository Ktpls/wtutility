from utilref import *


@AllOptionalInit
@dataclasses.dataclass
class clz1:
    a: int
    b: int


@AllOptionalInit
@dataclasses.dataclass
class clz2:
    a: int
    b: str


i1 = clz1(b=2)
i2 = BeanUtil.BeanCopy(i1, clz2)
i3 = clz2()
BeanUtil.BeanCopy(i1, i3)
print(f'{i1=}, {i2=}, {i3=}')
pass
