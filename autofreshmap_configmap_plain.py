
desireds=[
    'AralSea',
    'FieldsOfPoland',
    'FireArc',
    'MaginotLineDomination#2',
    'Pradesh',
    'RedDesert',
    'SandsOfSinai',
    'SandsOfTunisia',
    #'SecondBattleOfElAlameinDomination#1',
    'SecondBattleOfElAlameinDomination#2',
    'Sinai',
    'Berlin',
]


halfdesired=[
    'AshRiver', #not great with high br
    'FrozenPass',
    'Karelia',
    'Japan',
    'Poland',
    'Poland(winter)',
    'Finland',
    'Tunisia',
    'MaginotLineDomination#1',
    'EuropeanProvince',
]

whitelistedmap=desireds+halfdesired

specialmapdetectors={
    "Sinai":{
        "mapreq":"Sinai",
        #B, or battle mode at any side
        "foo":'ret(detectMapShape() and (selectPoint(ppos=[272, 294]) or selectPoint("blueA") or selectPoint("blueB") ) )'
    },
    "FrozenPass":{
        "mapreq":"FrozenPass",
        "foo":'ret(detectMapShape() and spawnAround([474,477]))'
    },
    "EasternEurope":{
        "mapreq":"EasternEurope",
        "foo":'ret(detectMapShape() and spawnAround([109,456]))'
    },
    "Karelia":{
        "mapreq":"Karelia",
        "foo":'ret(detectMapShape() and spawnAround([316, 160]))'
    },
    "Japan":{
        "mapreq":"Japan",
        # b point
        "foo":'ret(detectMapShape() and spawnAround([233, 572]) and selectPoint(ppos=[325, 310]))'
    },
    "Normandy":{
        "mapreq":"Normandy",
        "foo":'ret(detectMapShape() and spawnAround([536, 164]))'
    },
    "Poland":{
        "mapreq":"Poland",
        "foo":'ret(detectMapShape() and spawnAround([86, 313]) and selectPoint("A"))' # includes domination and conquest, not battle
    },
    "Poland(winter)":{
        "mapreq":"Poland(winter)",
        "foo":'ret(detectMapShape() and spawnAround([86, 313]) and selectPoint("A"))'
    },
    "Jungle":{
        "mapreq":"Jungle",
        "foo":'ret(detectMapShape() and spawnAround([130, 352]))'
    },
    "FieldsOfNormandy":{
        "mapreq":"FieldsOfNormandy",
        "foo":'ret(detectMapShape() and spawnAround([ 88, 294]))'
    },
    "AshRiver":{
        "mapreq":"AshRiver",
        "foo":'ret(detectMapShape() and spawnAround([ 87, 359]))'
    },
    "Finland":{
        "mapreq":"Finland",
        #c point
        "foo":'ret(detectMapShape() and spawnAround([355,526]) and selectPoint(ppos=[492, 289]))'
    },
    # "SandsOfSinai":{
        # "mapreq":"SandsOfSinai",
        # "foo":'ret(detectMapShape() and spawnAround([334, 61]))'
    # },
    "AralSea":{
        "mapreq":"AralSea",
        "foo":'ret(detectMapShape() and spawnAround([502, 300]))'
    },
    "FieldsOfPoland":{
        "mapreq":"FieldsOfPoland",
        "foo":'ret(detectMapShape())'
    },
    "Tunisia":{
        "mapreq":"Tunisia",
        # A point
        "foo":'ret(detectMapShape() and spawnAround([424, 564]) and selectPoint(ppos=[79, 357]))'
    },
    "MaginotLineDomination#1":{
        "mapreq":"MaginotLineDomination#1",
        "foo":'ret(detectMapShape() and spawnAround([290, 65]))'
    },
    "EuropeanProvince":{
        "mapreq":"EuropeanProvince",
        "foo":'ret(detectMapShape() and spawnAround([476, 303]))'
    }
    
}
