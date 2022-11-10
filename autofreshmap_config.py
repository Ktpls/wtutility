
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
    'Finland',
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
    'BattleOfHurtgenForestDomination#1',
    'EasternEurope',
]

desireds=[
    'AshRiver',
    'FireArc',
    'Sinai',
    'Jungle',
    'Poland',
    'AralSea',
    'Carpathians',
    'FieldsOfNormandy',
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
subsampleddetectionrate=0.5

log2file=False
dbglog=False

standardMatchThreshold=0.2
standardMapLeftTopPoint=[286,216]

setonwifirecoverthresh=13

def mapname2path(mapname):
    return 'map/'+mapname+'.png'

specialmapdetectors={
    "FrozenPass":{
        "type":"mapAndSpawnDetector",
        "path":mapname2path("FrozenPass"),
        "spawncenter":[474,477],
        "allowederrrange":100,
    },
    "EasternEurope":{
        "type":"mapAndSpawnDetector",
        "path":mapname2path("EasternEurope"),
        "spawncenter":[109,456],
        "allowederrrange":100,
    },
    "Karelia":{
        "type":"mapAndSpawnDetector",
        "path":mapname2path("Karelia"),
        "spawncenter":[316, 160],
        "allowederrrange":100,
    },
    "Japan":{
        "type":"mapAndSpawnDetector",
        "path":mapname2path("Japan"),
        "spawncenter":[233, 572],
        "allowederrrange":100,
    },
    "Normandy":{
        "type":"mapAndSpawnDetector",
        "path":mapname2path("Normandy"),
        "spawncenter":[536, 164],
        "allowederrrange":100,
    },
    "Poland":{
        "type":"mapAndSpawnDetector",
        "path":mapname2path("Poland"),
        "spawncenter":[86, 312],
        "allowederrrange":100,
    },
}