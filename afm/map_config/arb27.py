from .map_config_header import *

smalls = [
    r"air\[Operation]Bastogne(LightVehicles)",
    r"air\[Operation]CentralTunisia(LightVehicles)",
    r"air\[Operation]Cochinchina(LightVehicles)",
    r"air\[Operation]ConsolidationOfPositionsOnSicily(LightVehicles)",
    r"air\[Operation]CounterstrikeUnderSmolensk(LightVehicles)",
    r"air\[Operation]Essen(LightVehicles)",
    r"air\[Operation]HenanProvince(LightVehicles)",
    r"air\[Operation]LakeLadoga(LightVehicles)",
    r"air\[Operation]Mozdok(LightVehicles)",
    r"air\[Operation]NearEast(LightVehicles)",
    r"air\[Operation]Honolulu(LightVehicles)",
    r"air\[Operation]PortMoresby(LightVehicles)",
    r"air\[Operation]TheLastBattleOfKhalkhynGol(LightVehicles)",
    r"air\[Operation]WakeIsland(LightVehicles)",
    r"air\[Operation]YooPassage(LightVehicles)",
    r"air\[Operation]Counteroffensive(LightVehicles)",
    # r"airHighQuality\[Operation]Bastogne(LightVehicles)",
    # r"airHighQuality\[Operation]CentralTunisia(LightVehicles)",
    # r"airHighQuality\[Operation]Cochinchina(LightVehicles)",
    # r"airHighQuality\[Operation]ConsolidationOfPositionsOnSicily(LightVehicles)",
    # r"airHighQuality\[Operation]Counteroffensive(LightVehicles)",
    # r"airHighQuality\[Operation]CounterstrikeUnderSmolensk(LightVehicles)",
    # r"airHighQuality\[Operation]Essen(LightVehicles)",
    # r"airHighQuality\[Operation]HenanProvince(LightVehicles)",
    # r"air\[Operation]Honolulu(LightVehicles)",
    # r"airHighQuality\[Operation]LakeLadoga(LightVehicles)",
    # # r"airHighQuality\[Operation]Mozdok(LightVehicles)",  # no bombable af
    # r"airHighQuality\[Operation]NearEast(LightVehicles)",
    # r"air\[Operation]PortMoresby(LightVehicles)",
    # r"air\[Operation]TheLastBattleOfKhalkhynGol(LightVehicles)",
    # r"air\[Operation]WakeIsland(LightVehicles)",
    # r"air\[Operation]YooPassage(LightVehicles)",
]

mapAcceptorParam = MapAcceptorParam(
    blacklistedmap=smalls
)