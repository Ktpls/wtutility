from utilref import *

# import engineman.engineman as engineman
from engineman.engineman import *


def try8111(foo):
    try:
        return foo()
    except Port8111.FetchFailure:
        return None


def main():

    print(f"vehicleName")
    print(VehicleName().get())

    print(f"withOilRadiator")
    print(OilRadiator().get())
    os.system("pause")


main()
