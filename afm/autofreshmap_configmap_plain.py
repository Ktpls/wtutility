from .autofreshmap_configmap_importref import *

# friendly for turrentless tank destroyers
highSurvivablity = [
    "AralSea",
    "Berlin",
    "EasternEurope",
    "EuropeanProvince",
    "FieldsOfNormandy",
    "FieldsOfPoland",
    "Finland",
    #'FireArc',
    "FrozenPass",
    "Karelia",
    "MaginotLineDomination#1",
    "MaginotLineDomination#2",
    "Mozdok#2",
    "Poland",
    "PortNovorossiysk",
    "Pradesh",
    "RedDesert",
    "SandsOfSinai",
    "SandsOfTunisia",
    "SecondBattleOfElAlamein",
    "Tunisia",
    "AshRiver",
    "Carpathians",
    "Jungle",
    "MiddleEast",
]


whitelistedmap = highSurvivablity

specialmapdetectors = {
    "Sinai": SpecialMapDetector(
        mapreq="Sinai",
        # B, or C or battle mode at any side
        # ignoring point type
        foo="ret(detectMapShape())",
    ),
    "FrozenPass": SpecialMapDetector(
        mapreq="FrozenPass",
        # A or B, not single C in village
        foo="ret(detectMapShape() and spawnAround([474,477]) and (not singlePoint([528, 99])))",
    ),
    "EasternEurope": SpecialMapDetector(
        mapreq="EasternEurope",
        foo="ret(detectMapShape() and spawnAround([109,456]))",
    ),
    "Karelia": SpecialMapDetector(
        mapreq="Karelia",
        foo="ret(detectMapShape() and spawnAround([316, 160]))",
    ),
    "Japan": SpecialMapDetector(
        mapreq="Japan",
        # b point
        foo="ret(detectMapShape() and spawnAround([233, 572]) and selectPoint(ppos=[325, 310]))",
    ),
    "Normandy": SpecialMapDetector(
        mapreq="Normandy",
        foo="ret(detectMapShape() and spawnAround([536, 164]))",
    ),
    "Poland": SpecialMapDetector(
        mapreq=["Poland", "Poland(winter)"],
        # includes domination and conquest, not battle
        foo='ret((detectMapShape(mtcid=0) or detectMapShape(mtcid=1)) and spawnAround([86, 313]) and selectPoint("A"))',
    ),
    "Jungle": SpecialMapDetector(
        mapreq="Jungle",
        foo="ret(detectMapShape() and spawnAround([130, 352]))",
    ),
    "FieldsOfNormandy": SpecialMapDetector(
        mapreq="FieldsOfNormandy",
        foo="ret(detectMapShape() and spawnAround([ 88, 294]) and singlePoint([359, 98]))",  # single point at top
    ),
    "AshRiver": SpecialMapDetector(
        mapreq="AshRiver",
        foo="ret(detectMapShape() and spawnAround([ 87, 359]))",
    ),
    "Finland": SpecialMapDetector(
        mapreq="Finland",
        # c point
        foo="ret(detectMapShape() and spawnAround([355,526]) and not singlePoint([178, 308]))",  # not single point at left
    ),
    "SandsOfSinai": SpecialMapDetector(
        mapreq="SandsOfSinai",
        # better survivability at upper, less likely to be killed by flankers
        foo="ret(detectMapShape() and spawnAround([334, 61]))",
    ),
    "FieldsOfPoland": SpecialMapDetector(
        mapreq="FieldsOfPoland",
        foo="ret(detectMapShape())",
    ),
    "Tunisia": SpecialMapDetector(
        mapreq="Tunisia",
        # A point
        foo="ret(detectMapShape() and spawnAround([424, 564]) and selectPoint(ppos=[79, 357]))",
    ),
    "MaginotLineDomination#1": SpecialMapDetector(
        mapreq=["MaginotLineDomination#1", "MaginotLineDomination#1Winter"],
        # born at upper, highland between two spawns
        foo="ret((detectMapShape(mtcid=0) or detectMapShape(mtcid=1)) and spawnAround([290, 65]))",
    ),
    "MaginotLineDomination#2": SpecialMapDetector(
        mapreq=["MaginotLineDomination#2", "MaginotLineDomination#2Winter"],
        foo="ret(detectMapShape(mtcid=0) or detectMapShape(mtcid=1))",
    ),
    "EuropeanProvince": SpecialMapDetector(
        mapreq="EuropeanProvince",
        # at bottom right spawn, good vision at this highland
        foo="ret(detectMapShape() and spawnAround([476, 303]))",
    ),
    "Berlin": SpecialMapDetector(
        mapreq="Berlin",
        # good vision at bottom right spawn or upper right
        foo="ret(detectMapShape())",
    ),
    "PortNovorossiysk": SpecialMapDetector(
        mapreq="PortNovorossiysk",
        # upper spawn
        # born at upper, good vision between buildings through river and survivability for river
        foo="ret(detectMapShape() and spawnAround([550, 88]))",
    ),
    "SecondBattleOfElAlamein": SpecialMapDetector(
        mapreq=[
            "SecondBattleOfElAlameinConquest#1",
            "SecondBattleOfElAlameinDomination#2",
        ],
        # born at upper, better vision around up right spawn
        foo="ret((detectMapShape(mtcid=0) or detectMapShape(mtcid=1)) and spawnAround([219, 87]))",
    ),
    "Carpathians": SpecialMapDetector(
        mapreq="Carpathians",
        # born at lower, better vision around A on mount
        foo="ret(detectMapShape() and spawnAround([222, 529]))",
    ),
    "MiddleEast": SpecialMapDetector(
        mapreq="MiddleEast",
        # born at lower, better vision around A on mount
        foo="ret(detectMapShape() and spawnAround([508, 346]))",
    ),
}
