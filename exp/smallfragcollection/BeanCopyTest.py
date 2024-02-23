from utilref import *


@AllOptionalInit
@dataclasses.dataclass
class clz1:
    a: int
    b: int
    c: int


@AllOptionalInit
@dataclasses.dataclass
class clz2:
    a: int
    b: str
    c: int


@dataclasses.dataclass
class classWithArgedInitFunc:
    a: int
    b: str
    c: int

    def __init__(self, some_val_required_in_init) -> None:
        pass


dataSource = clz1(a=1,c=2)
copied = clz2()
BeanUtil.copyProperties(dataSource, copied)
copiedWithoutInit = BeanUtil.copyProperties(dataSource, clz2)
copiedWithoutInitWithArgedInitFunc=BeanUtil.copyProperties(dataSource, classWithArgedInitFunc)
print(f"{dataSource=}, {copiedWithoutInit=}, {copied=}, {copiedWithoutInitWithArgedInitFunc=}")
pass
