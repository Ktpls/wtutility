import dataclasses, typing


@dataclasses.dataclass
class MapDetector:
    map: typing.Union[list[str], str, None] = None
    foo: str = "ret(detectMapShape())"
