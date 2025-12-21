from .map_config_header import *


mapAcceptorParam = MapAcceptorParam(
    blacklistedmap=[
        "air/[Ground Strike]Ruhr",
        "air/[Ground Strike]Korsun",
        "WithPoint",
    ],
    specialmapdetectors={
        "WithPoint": MapDetector(foo='ret(selectPoint(ptype="A"))'),
    },
    onnodetectorhit=MapAcceptorParam.BehaviorOnNoDetectorHit.Accept,
)
