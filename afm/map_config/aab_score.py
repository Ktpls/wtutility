from .map_config_header import *


mapAcceptorParam = MapAcceptorParam(
    blacklistedmap=[
        "AirDomination",
        "Domination",
        "air/[Ground Strike]Ruhr",
        "air/[Ground Strike]Korsun",
        "air/[Air Domination]Malta",
    ],
    specialmapdetectors={
        "AirDomination": MapDetector(foo='ret(selectPoint(ptype="roundA"))'),
        "Domination": MapDetector(foo='ret(selectPoint(ptype="A"))'),
    },
    onnodetectorhit=MapAcceptorParam.BehaviorOnNoDetectorHit.Accept,
)
