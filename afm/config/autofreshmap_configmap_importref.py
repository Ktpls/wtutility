import dataclasses, typing



@dataclasses.dataclass
class MapDetector:
    # TODO: rename as ComplexMapDetectorParam
    map: typing.Union[list[str], str, None] = None
    foo: str = "ret(detectMapShape())"


whitelistedmap = list()
blacklistedmap = list()
specialmapdetectors = dict()
