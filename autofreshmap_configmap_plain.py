
desireds=[
    'AralSea',
    'AshRiver',
    'EuropeanProvince',
    'FieldsOfPoland',
    'FireArc',
    'MaginotLineDomination#1',
    'MaginotLineDomination#2',
    'Pradesh',
    'RedDesert',
    'SandsOfSinai',
    'SandsOfTunisia',
    'SecondBattleOfElAlameinDomination#1',
    'SecondBattleOfElAlameinDomination#2',
    'Sinai',
]


halfdesired=[
    'FrozenPass',
    'Karelia',
    'Japan',
    'Poland',
    'Poland(winter)',
    #'Finland',
    'Tunisia',
]

whitelistedmap=desireds+halfdesired

specialmapdetectors={
    "Sinai":{
        "type":"mapdetector",
        "path":"Sinai",
        "point":[
            {
                "pos":[272, 294], # B
                "allowederr":20,
            },
        ],
    },
    "FrozenPass":{
        "type":"mapdetector",
        "path":"FrozenPass",
        "spawncenter":[474,477],
        "allowederrrange":100,
    },
    "EasternEurope":{
        "type":"mapdetector",
        "path":"EasternEurope",
        "spawncenter":[109,456],
        "allowederrrange":100,
    },
    "Karelia":{
        "type":"mapdetector",
        "path":"Karelia",
        "spawncenter":[316, 160],
        "allowederrrange":100,
    },
    "Japan":{
        "type":"mapdetector",
        "path":"Japan",
        "spawncenter":[233, 572],
        "allowederrrange":100,
        "point":[
            {
                "pos":[325, 310], # B point
                "allowederr":20,
            },
        ],
    },
    "Normandy":{
        "type":"mapdetector",
        "path":"Normandy",
        "spawncenter":[536, 164],
        "allowederrrange":100,
    },
    "Poland":{
        "type":"mapdetector",
        "path":"Poland",
        "spawncenter":[86, 313],
        "allowederrrange":100,
    },
    "Poland(winter)":{
        "type":"mapdetector",
        "path":"Poland(winter)",
        "spawncenter":[86, 313],
        "allowederrrange":100,
    },
    "Jungle":{
        "type":"mapdetector",
        "path":"Jungle",
        "spawncenter":[130, 352],
        "allowederrrange":100,
    },
    "FieldsOfNormandy":{
        "type":"mapdetector",
        "path":"FieldsOfNormandy",
        "spawncenter":[ 88, 294],
        "allowederrrange":100,
    },
    "AshRiver":{
        "type":"mapdetector",
        "path":"AshRiver",
        "spawncenter":[ 87, 359],
        "allowederrrange":100,
    },
    "Finland":{
        "type":"mapdetector",
        "path":"Finland",
        "spawncenter":[355,526],
        "allowederrrange":100,
        "point":[
            {
                "pos":[492, 289], # C
                "allowederr":20,
            },
        ],
    },
    "SandsOfSinai":{
        "type":"mapdetector",
        "path":"SandsOfSinai",
        "spawncenter":[334, 61],
        "allowederrrange":100,
    },
    "AralSea":{
        "type":"mapdetector",
        "path":"AralSea",
        "point":[
            {
                "pos":[502, 300], # point in desert
                "allowederr":20,
            },
        ],
    },
    'FieldsOfPoland':{
        "type":"mapdetector",
        "path":"FieldsOfPoland",
        "thresh":0.09
    },
    "Tunisia":{
        "type":"mapdetector",
        "path":"Tunisia",
        "spawncenter":[424, 564],
        "allowederrrange":100,
        "point":[
            {
                "pos":[79, 357], # A point
                "allowederr":20,
            },
        ],
    },
}
