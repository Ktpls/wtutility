desireds = [
    'AralSea',
    'FieldsOfPoland',
    'FireArc',
    'MaginotLineDomination#2',
    'Pradesh',
    'RedDesert',
    'SandsOfTunisia',
    'Sinai',
]

halfdesired = [
    #'AshRiver',  # not great with high br
    'FrozenPass',
    'Karelia',
    'Japan', # right with tail, left, and right again. be aware of falling down
    'Poland',
    'Finland',
    'Tunisia',
    'MaginotLineDomination#1',
    'EuropeanProvince',
    'EasternEurope',
    'SandsOfSinai',
    'Berlin',
    'PortNovorossiysk',
    'SecondBattleOfElAlamein',
    'FieldsOfNormandy'
]

whitelistedmap = desireds + halfdesired

specialmapdetectors = {
    "Sinai": {
        "mapreq":
        "Sinai",
        # B, or battle mode at any side
        "foo":
        'ret(detectMapShape() and (selectPoint(ppos=[272, 294]) or selectPoint("blueA") or selectPoint("blueB") ) )'
    },
    "FrozenPass": {
        "mapreq": "FrozenPass",
        "foo": 'ret(detectMapShape() and spawnAround([474,477]))'
    },
    "EasternEurope": {
        "mapreq": "EasternEurope",
        "foo": 'ret(detectMapShape() and spawnAround([109,456]))'
    },
    "Karelia": {
        "mapreq": "Karelia",
        "foo": 'ret(detectMapShape() and spawnAround([316, 160]))'
    },
    "Japan": {
        "mapreq":
        "Japan",
        # b point
        "foo":
        'ret(detectMapShape() and spawnAround([233, 572]) and selectPoint(ppos=[325, 310]))'
    },
    "Normandy": {
        "mapreq": "Normandy",
        "foo": 'ret(detectMapShape() and spawnAround([536, 164]))'
    },
    "Poland": {
        "mapreq": ["Poland", "Poland(winter)"],
        "foo":
        'ret((detectMapShape(mtcid=0) or detectMapShape(mtcid=1)) and spawnAround([86, 313]) and selectPoint("A"))'
        # includes domination and conquest, not battle
    },
    "Jungle": {
        "mapreq": "Jungle",
        "foo": 'ret(detectMapShape() and spawnAround([130, 352]))'
    },
    "FieldsOfNormandy": {
        "mapreq": "FieldsOfNormandy",
        "foo": 'ret(detectMapShape() and spawnAround([ 88, 294]) and singlePoint([359, 98]))' # single point at top
    },
    "AshRiver": {
        "mapreq": "AshRiver",
        "foo": 'ret(detectMapShape() and spawnAround([ 87, 359]))'
    },
    "Finland": {
        "mapreq":
        "Finland",
        # c point
        "foo":
        'ret(detectMapShape() and spawnAround([355,526]) and singlePoint([492, 289]))' #single point at right
    },
    "SandsOfSinai": {
        "mapreq": "SandsOfSinai",
        # better survivability at upper, less likely to be killed by flankers
        "foo": 'ret(detectMapShape() and spawnAround([334, 61]))'
    },
    "AralSea": {
        "mapreq": "AralSea",
        # actually both side are fine
        "foo": 'ret(detectMapShape() and spawnAround([502, 300]))'
    },
    "FieldsOfPoland": {
        "mapreq": "FieldsOfPoland",
        "foo": 'ret(detectMapShape())'
    },
    "Tunisia": {
        "mapreq":
        "Tunisia",
        # A point
        "foo":
        # born at bottom left, go behind the stone slightly left of the bridge above a
        'ret(detectMapShape() and spawnAround([424, 564]) and selectPoint(ppos=[79, 357]))'
    },
    "MaginotLineDomination#1": {
        "mapreq": ["MaginotLineDomination#1", "MaginotLineDomination#1Winter"],
        "foo":
        # born at upper, highland between two spawns
        'ret((detectMapShape(mtcid=0) or detectMapShape(mtcid=1)) and spawnAround([290, 65]))'
    },
    "MaginotLineDomination#2": {
        "mapreq": ["MaginotLineDomination#2", "MaginotLineDomination#2Winter"],
        "foo": 'ret(detectMapShape(mtcid=0) or detectMapShape(mtcid=1))'
    },
    "EuropeanProvince": {
        "mapreq": "EuropeanProvince",
        # at bottom right spawn, good vision at this highland
        "foo": 'ret(detectMapShape() and spawnAround([476, 303]))'
    },
    "Berlin": {
        "mapreq": "Berlin",
        # bottom spawn
        # good vision at bottom right spawn
        "foo": 'ret(detectMapShape() and spawnAround([306, 504]))'
    },
    "PortNovorossiysk": {
        "mapreq": "PortNovorossiysk",
        # upper spawn
        # born at upper, good vision between buildings through river and survivability for river
        "foo": 'ret(detectMapShape() and spawnAround([550, 88]))'
    },
    "SecondBattleOfElAlamein": {
        "mapreq": ['SecondBattleOfElAlameinConquest#1', 'SecondBattleOfElAlameinDomination#2'],
        # born at upper, better vision around up right spawn
        "foo": 'ret((detectMapShape(mtcid=0) or detectMapShape(mtcid=1)) and spawnAround([559, 464]))'
    },
}
