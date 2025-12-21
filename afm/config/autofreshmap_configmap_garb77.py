from .autofreshmap_configmap_importref import *

whitelistedmap = [
    "AshRiver",
    "FrozenPass",
    "Jungle",
    "Karelia",
    "Kurban",
    "Stalingrad",
]
mapAcceptorParam = MapAcceptorParam(
    whitelistedmap=whitelistedmap,
    specialmapdetectors={
        m: MapDetector(
            map=m,
            foo='ret(detectMapShape() and selectPoint(ptype="A") and selectPoint(ptype="B") and selectPoint(ptype="C"))',
        )
        for m in whitelistedmap
    }
)