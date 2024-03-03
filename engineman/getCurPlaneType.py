from utilitypack.utility import *
from engineman.engineman import *


def try8111(foo):
    try:
        return foo()
    except Port8111.FetchFailure:
        return None


print(f"vehicleName")
print(
    try8111(
        lambda: Port8111.get(Port8111.QueryType.indicator)
        .expectValid()
        .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
        .type
    )
)

print(f"withOilRadiator")
print(OilRadiator().get())
os.system("pause")
