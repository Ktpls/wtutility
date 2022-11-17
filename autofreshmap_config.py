
citymap=[
    'AbandonedFactory',
    'AbandonedTown',
    'AdvanceToTheRhine',
    'Alaska',
    'AmericanDesert',
    'Berlin',
    'Breslau',
    'Campania',
    'CargoPort',
    'MiddleEast',
    'PortNovorossiysk',
    'PortNovorossiyskBattle',
    'Stalingrad',
    'SunCity',
    'Sweden',
    'Normandy',
]

notliked=[
    'Kurban',
    'Mozdok#2',
    'Mozdok#1',
    'Tunisia',
]

flatplain=[
]

toughforlowmovability=[
]

toughforbadlowerpitchangle=[
]

snowemap=[
    'SurroundingsOfVolokolamsk',
    'Volokolamsk',
]

notincluded=[
    'Serversk-13',
    'EasternEurope',
    'Carpathians',
]

desireds=[
    'AshRiver',
    'Sinai',
    'Poland',
    'FieldsOfNormandy',
    'Jungle',
    'FireArc',
    'AralSea',
    'Finland',
    'Pradesh',
    'BattleOfHurtgenForestDomination#1',
    'BattleOfHurtgenForestConquest#1',
    'AralSea',
]


halfdesired=[
    'FrozenPass',
    'Karelia',
    'Japan',
]

alldesired=desireds+halfdesired

secondary=[
]

whitelistedmap= alldesired

singlechanneleddetection=False
subsampleddetection=True
subsampleddetectionrate=0.1

log2file=False
dbglog=False

standardMatchThreshold=0.15
standardMapLeftTopPoint=[286,216]

setonwifirecoverthresh=13

specialmapdetectors={
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
        "spawncenter":[86, 312],
        "allowederrrange":100,
    },
    "Jungle":{
        "type":"mapdetector",
        "path":"Jungle",
        "spawncenter":[130, 352],
        "allowederrrange":100,
    },
}