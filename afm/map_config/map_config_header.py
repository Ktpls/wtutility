import dataclasses, typing, enum


@dataclasses.dataclass
class MapDetector:
    # TODO: rename as ComplexMapDetectorParam
    map: typing.Union[list[str], str, None] = None
    foo: str = "ret(detectMapShape())"


@dataclasses.dataclass
class MapAcceptorParam:
    class BehaviorOnNoDetectorHit(enum.Enum):
        Accept = "Accept"
        Reject = "Reject"

    specialmapdetectors: dict[str, MapDetector] = dataclasses.field(
        default_factory=dict
    )
    whitelistedmap: list[str] = dataclasses.field(default_factory=list)
    blacklistedmap: list[str] = dataclasses.field(default_factory=list)
    onnodetectorhit: BehaviorOnNoDetectorHit = BehaviorOnNoDetectorHit.Reject
