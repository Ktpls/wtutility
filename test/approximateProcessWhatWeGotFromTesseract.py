import re
from dataclasses import dataclass


class ApproximateStandardizationGuide:
    @dataclass
    class GuideItem:
        pattern: str | re.Pattern
        replacement: str

        def do(self, s: str) -> str:
            """
            Perform the replacement operation on the given string.

            Args:
                s (str): The input string to be modified.

            Returns:
                str: The modified string after performing the replacement.
            """
            return re.sub(self.pattern, self.replacement, s)

    def __init__(self, guideSourceCode: str):
        """
        Initialize the ApproximateStandardizationGuide with the given guide source code.

        Args:
            guideSourceCode (str): The source code of the guide.
        """
        self.guideSourceCode = guideSourceCode
        guideitem = []
        for g in guideSourceCode.split("\n"):
            if len(g) == 0:
                continue
            if g.startswith("//"):
                continue
            spliter = "->"
            splitpos = g.find(spliter)
            if splitpos < 0:
                continue

            guideitem.append(
                ApproximateStandardizationGuide.GuideItem(
                    re.compile(g[:splitpos], re.MULTILINE), g[splitpos + len(spliter) :]
                )
            )
        self.guideitem = guideitem

    def do(self, s: str) -> str:
        """
        Perform the standardization process on the given string.

        Args:
            s (str): The input string to be standardized.

        Returns:
            str: The standardized string.
        """
        for g in self.guideitem:
            s = g.do(s)
        return s


asg = ApproximateStandardizationGuide(
    r"""
//confused
[A4]->A
[Ss5]->S
[0Oo]->O
[Cc]->C
[Ili1]->I
[Jj]->J
[Kk]->K
[Mm]->M
[Pp]->P
[UuVv]->U
[Ww]->W
[Xx]->X
[Zz]->Z
//unexpected
[^A-Za-z0-9\(\)\n]->
//nation marks
^O->
"""[
        1:-1
    ]
)

IDontWannaSeeThem = """
MiG21SMT
Su17M2
MiG21MF
A-10ALate
A-5C
"""[
    1:-1
]


@dataclass
class VehicleInfo:
    name: str
    pattern: re.Pattern


IDontWannaSeeThem = [
    VehicleInfo(t, re.compile(f".*{asg.do(t)}.*"))
    for t in IDontWannaSeeThem.split("\n")
]

# raw from real tesseract result
players = """
ASC
ASC
MiG-21SMT
Milan
Jaguar E
OMiG-21MF
Hunter F58
MiG-215 (R-13-300)
Milan
2
Milan
OMiG-19S
MiG-215 (R-13-300)
#MiG-21 SPS-K

MiG-21SMT
"""[
    1:-1
]

players = [asg.do(t) for t in players.split("\n")]

for l, p in enumerate(players):
    for v in IDontWannaSeeThem:
        if re.match(v.pattern, p) is not None:
            print(f"found {v.name} at line {l}")
