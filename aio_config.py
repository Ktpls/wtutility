import enum


class GameMode(enum.Enum):
    arb = 0
    garb = 1
    grb = 2


gm = GameMode.arb


def getByMode(d: dict):
    return d.get(gm, None)


usingwtdistmeaspy = getByMode(
    {GameMode.arb: False, GameMode.garb: False, GameMode.grb: True}
)
usingtelescope = getByMode(
    {GameMode.arb: False, GameMode.garb: True, GameMode.grb: True}
)
usingtelescope=True
usingkeyshortcut = False
usingeagleeye = False
usingglock = False
usingengineman = False

throwErrorInBus = False
throwErrorInHotkey = False

aiofps = 10
