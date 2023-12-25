import dataclasses, typing


@dataclasses.dataclass
class SpecialMapDetector:
    mapreq: typing.Union[typing.List[str], str, None] = None
    foo: str = "ret(detectMapShape())"
