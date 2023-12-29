import dataclasses, typing


@dataclasses.dataclass
class MapDetector:
    map: typing.Union[typing.List[str], str, None] = None
    foo: str = "ret(detectMapShape())"
