from .autofreshmap_configmap_importref import *

# friendly for turrentless tank destroyers
highSurvivablity = [
    "AralSea",
    # "Berlin",
    "EasternEurope",
    "EuropeanProvince",
    "FieldsOfNormandy",
    "FieldsOfPoland",
    # "Finland",
    #'FireArc',
    "Flanders",
    "FrozenPass",
    "Karelia",
    "MaginotLineDomination#1",
    "MaginotLineDomination#2",
    "Mozdok#2",
    "Poland",
    "PortNovorossiysk",
    "Pradesh",
    "RedDesert",
    "Sinai",
    "SandsOfSinai",
    "SandsOfTunisia",
    "SecondBattleOfElAlamein",
    "Tunisia",
    "AshRiver",
    # "Carpathians",
    "Jungle",
    "MiddleEast",
]


whitelistedmap = highSurvivablity
specialmapdetectors = {
    "Sinai": MapDetector(
        map="Sinai",
        # B, or C or battle mode at any side
        # ignoring point type
        # have no shelter in battle mode with spawn at bottom
        foo="ret(detectMapShape() and not (singlePoint([102, 293]) and spawnAround([244, 542])))",
    ),
    "FrozenPass": MapDetector(
        map="FrozenPass",
        # A or B, not single C in village
        foo="ret(detectMapShape() and spawnAround([474,477]) and (not singlePoint([528, 99])))",
    ),
    "EasternEurope": MapDetector(
        map="EasternEurope",
        foo="ret(detectMapShape() and spawnAround([109,456]))",
    ),
    "Karelia": MapDetector(
        map="Karelia",
        foo="ret(detectMapShape() and spawnAround([316, 160]))",
    ),
    "Japan": MapDetector(
        map="Japan",
        # b point
        foo="ret(detectMapShape() and spawnAround([233, 572]) and selectPoint(ppos=[325, 310]))",
    ),
    "Normandy": MapDetector(
        map="Normandy",
        foo="ret(detectMapShape() and spawnAround([536, 164]))",
    ),
    "Poland": MapDetector(
        map=["Poland", "Poland(winter)"],
        # includes domination and conquest, not battle
        foo='ret((detectMapShape(mtcid=0) or detectMapShape(mtcid=1)) and spawnAround([86, 313]) and selectPoint("A"))',
    ),
    "Jungle": MapDetector(
        map="Jungle",
        foo="ret(detectMapShape() and spawnAround([130, 352]))",
    ),
    "FieldsOfNormandy": MapDetector(
        map="FieldsOfNormandy",
        foo="ret(detectMapShape() and spawnAround([ 88, 294]) and singlePoint([359, 98]))",  # single point at top
    ),
    "AshRiver": MapDetector(
        map="AshRiver",
        foo="ret(detectMapShape() and spawnAround([ 87, 359]))",
    ),
    "Finland": MapDetector(
        map="Finland",
        # c point
        foo="ret(detectMapShape() and spawnAround([355,526]) and not singlePoint([178, 308]))",  # not single point at left
    ),
    # "SandsOfSinai": MapDetector(
    # map="SandsOfSinai",
    # # better survivability at upper, less likely to be killed by flankers
    # foo="ret(detectMapShape() and spawnAround([334, 61]))",
    # ),
    "FieldsOfPoland": MapDetector(
        map="FieldsOfPoland",
        foo="ret(detectMapShape())",
    ),
    "Tunisia": MapDetector(
        map="Tunisia",
        # A point
        foo="ret(detectMapShape() and spawnAround([424, 564]) and selectPoint(ppos=[79, 357]))",
    ),
    "MaginotLine#1": MapDetector(
        map=["MaginotLine#1", "MaginotLine#1(Winter)"],
        # born at upper, highland between two spawns
        foo="ret((detectMapShape(mtcid=0) or detectMapShape(mtcid=1)) and spawnAround([290, 65]))",
    ),
    "MaginotLine#2": MapDetector(
        map=["MaginotLine#2", "MaginotLine#2(Winter)"],
        foo="ret(detectMapShape(mtcid=0) or detectMapShape(mtcid=1))",
    ),
    "EuropeanProvince": MapDetector(
        map="EuropeanProvince",
        # at bottom right spawn, good vision at this highland
        foo="ret(detectMapShape() and spawnAround([476, 303]))",
    ),
    "Berlin": MapDetector(
        map="Berlin",
        # good vision at bottom right spawn or upper right
        foo="ret(detectMapShape())",
    ),
    "PortNovorossiysk": MapDetector(
        map="PortNovorossiysk",
        # upper spawn
        # born at upper, good vision between buildings through river and survivability for river
        foo="ret(detectMapShape() and spawnAround([550, 88]))",
    ),
    "SecondBattleOfElAlamein": MapDetector(
        map=[
            "SecondBattleOfElAlameinConquest#1",
            "SecondBattleOfElAlameinDomination#2",
        ],
        # born at upper, better vision around up right spawn
        foo="ret((detectMapShape(mtcid=0) or detectMapShape(mtcid=1)) and spawnAround([219, 87]))",
    ),
    "Carpathians": MapDetector(
        map="Carpathians",
        # born at lower, better vision around A on mount
        foo="ret(detectMapShape() and spawnAround([222, 529]))",
    ),
    "MiddleEast": MapDetector(
        map="MiddleEast",
        # born at lower, better vision around A on mount
        foo="ret(detectMapShape() and spawnAround([508, 346]))",
    ),
    "Flanders": MapDetector(
        map="Flanders",
        # born at lower, better vision around A on mount
        foo="ret(detectMapShape() and spawnAround([326, 618]))",
    ),
}
