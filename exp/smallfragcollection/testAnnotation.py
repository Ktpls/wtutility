from utilref import *


# %%
@AnnotationUtil.AnnotationClass
class ToPrint:
    def __init__(self, info):
        self.info = info

    def intercept(self):
        print(self.info)


@ToPrint("foo")
def foo():
    print("calling foo()")


def callFooWithAnnotation(f):
    anno = AnnotationUtil.getAnnotationDict(f).get(ToPrint)
    if anno is not None:
        anno.intercept()
        f()


callFooWithAnnotation(foo)
