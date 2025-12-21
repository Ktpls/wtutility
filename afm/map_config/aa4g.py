from .map_config_header import *
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
	'GoldenQuarry',
]

city_and_plain_combined=[
    'AralSea',
    'BattleOfHurtgenForestConquest#1',
    'BattleOfHurtgenForestDomination#1',
    'Poland',
    # 'Serversk-13',
    #'Tunisia',
    'EasternEurope',
]

whitelistedmap=citymap+city_and_plain_combined

mapAcceptorParam=MapAcceptorParam(whitelistedmap=citymap+city_and_plain_combined)