from chpath import *

# import engineman.engineman as engineman
from engineman.enginemanimpl import *


def try8111(foo):
    try:
        return foo()
    except Port8111.FetchFailure:
        return None


def main():
    UNSUP = "UNSUPPORTED"
    print(f"vehicleName")
    try:
        print(VehicleName().get())
    except AxisUnsupported as err:
        print(UNSUP)

    print(f"withOilRadiator")
    try:
        print(OilRadiator().get())
    except AxisUnsupported as err:
        print(UNSUP)

    os.system("pause")


main()
