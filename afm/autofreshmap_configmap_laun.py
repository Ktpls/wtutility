from .autofreshmap_configmap_importref import *

whitelistedmap = ["3PointMap"]

specialmapdetectors = {
    "3PointMap": SpecialMapDetector(
        foo='ret(selectPoint(ptype="A") and selectPoint(ptype="B") and selectPoint(ptype="C"))'
    ),
}
