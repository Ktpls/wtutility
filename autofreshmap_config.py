
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

city_and_plain_combined=[
    'AralSea',
    'BattleOfHurtgenForestConquest#1',
    'BattleOfHurtgenForestDomination#1',
    'Finland',
    'FrozenPass',
    'Poland',
    'Serversk-13',
    'Tunisia',
    'EasternEurope',
]

other_aaliked_except_city=[
    'AralSea',
    'BattleOfHurtgenForestConquest#1',
    'BattleOfHurtgenForestDomination#1',
    'Poland',
    'Tunisia',
]

allaaliked=citymap+other_aaliked_except_city

notliked=[
    'Kurban',
    'Carpathians',
    'Tunisia',
    "ArcticPier",
    "VietnamDomination#2",
    "VietnamDomination#1",
    "Spaceport",
    "FuldaDomination#2",
    "FuldaDomination#1",
    "ArdennesDomination#2",
    "ArdennesDomination#1",
    "38thParallel",
    "ArcticPolarBase",
    'BattleOfHurtgenForestConquest#1',
    'BattleOfHurtgenForestDomination#1',
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
    '38thParallel',
]

desireds=[
    'AralSea',
    'AshRiver',
    'EuropeanProvince',
    'FieldsOfPoland',
    'Finland',
    'FireArc',
    'MaginotLineDomination#1',
    'MaginotLineDomination#2',
    'Mozdok#1',
    'Mozdok#2',
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
    'FieldsOfNormandy',
    'Poland',
    'Poland(winter)',
    'Jungle',
]

alldesired=desireds+halfdesired

secondary=[
]

whitelistedmap=alldesired

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
        "spawncenter":[86, 313],
        "allowederrrange":200,
    },
    "Poland(winter)":{
        "type":"mapdetector",
        "path":"Poland(winter)",
        "spawncenter":[86, 313],
        "allowederrrange":200,
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
}