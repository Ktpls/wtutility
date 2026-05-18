from .map_config_header import *

mapAcceptorParam = MapAcceptorParam(
    blacklistedmap=[
        r"air\[Operation]RockyCanyon",
        r"air\[Operation]Afghanistan",
        r"air\[Operation]GolanHeights(AirSpawns)",
        r"air\[Operation]Vietnam",
        r"air\[Operation]Spain",
        r"air\[Operation]MysteriousValley(AirSpawns)",
        #r"airHq\[Operation]GolanHeights",
    ],
    onnodetectorhit=MapAcceptorParam.BehaviorOnNoDetectorHit.Accept
)