from .autofreshmap_configmap_importref import *

mapAcceptorParam = MapAcceptorParam(
    whitelistedmap=["3PointMap"],
    specialmapdetectors={
        "3PointMap": MapDetector(
            foo='ret(selectPoint(ptype="A") and selectPoint(ptype="B") and selectPoint(ptype="C"))'
        ),
    }
)