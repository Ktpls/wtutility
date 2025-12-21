from .autofreshmap_configmap_importref import *


mapAcceptorParam = MapAcceptorParam(
    blacklistedmap=[
        "air/[Ground Strike]Ruhr",
        "air/[Ground Strike]Korsun",
        "WithPoint",
    ],
    specialmapdetectors={
        "WithPoint": MapDetector(foo='ret(selectPoint(ptype="A"))'),
    },
    onnodetectorhit=MapAcceptorParam.BehaviorOnNoDetectorHit.Reject,
)
