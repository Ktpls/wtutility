from sympy import false
from .util_windows import *
import requests

import json


def GetWtHwnd():
    ret = win32gui.FindWindow("DagorWClass", None)
    if ret == win32con.NULL:
        raise Exception("FindWindow() failed")
    return ret


class Port8111:
    @dataclasses.dataclass
    class BeanIndicatorAir:
        valid: bool = None
        army: str = None
        type: str = None
        speed: float = None
        pedals1: float = None
        pedals2: float = None
        stick_elevator: float = None
        stick_ailerons: float = None
        vario: float = None
        altitude_hour: float = None
        altitude_min: float = None
        aviahorizon_roll: float = None
        aviahorizon_pitch: float = None
        bank: float = None
        bank1: float = None
        bank2: float = None
        turn: float = None
        compass: float = None
        compass1: float = None
        clock_hour: float = None
        clock_sec: float = None
        manifold_pressure: float = None
        manifold_pressure1: float = None
        rpm_min: float = None
        rpm1_min: float = None
        rpm_hour: float = None
        rpm1_hour: float = None
        oil_pressure: float = None
        oil_pressure1: float = None
        oil_temperature: float = None
        oil_temperature1: float = None
        oil_temperature2: float = None
        oil_temperature3: float = None
        mixture: float = None
        mixture1: float = None
        carb_temperature: float = None
        carb_temperature1: float = None
        fuel: float = None
        fuel_pressure: float = None
        fuel_pressure1: float = None
        gears: float = None
        gears1: float = None
        flaps: float = None
        trimmer: float = None
        throttle: float = None
        throttle1: float = None
        weapon1: float = None
        prop_pitch: float = None
        prop_pitch1: float = None
        supercharger: float = None
        radiator: float = None

    @dataclasses.dataclass
    class BeanIndicatorTank:
        valid: bool = None
        army: str = None
        type: str = None
        stabilizer: float = None
        gear: float = None
        gear_neutral: float = None
        speed: float = None
        has_speed_warning: float = None
        rpm: float = None
        driving_direction_mode: float = None
        cruise_control: float = None
        lws: float = None
        ircm: float = None
        roll_indicators_is_available: float = None
        first_stage_ammo: float = None
        crew_total: float = None
        crew_current: float = None
        crew_distance: float = None
        gunner_state: float = None
        driver_state: float = None

    @dataclasses.dataclass
    class BeanMapInfo:
        grid_size: typing.List[float] = None
        grid_steps: typing.List[float] = None
        grid_zero: typing.List[float] = None
        hud_type: int = None
        map_generation: int = None
        map_max: typing.List[float] = None
        map_min: typing.List[float] = None
        valid: bool = None

    @dataclasses.dataclass
    class BeanState:
        @dataclasses.dataclass
        class UnitValue:
            unit: str
            value: typing.Union[float, typing.List[float]]

        @dataclasses.dataclass
        class Engine:
            throttle: "Port8111.BeanState.UnitValue" = None
            RPM_throttle: "Port8111.BeanState.UnitValue" = None
            mixture: "Port8111.BeanState.UnitValue" = None
            radiator: "Port8111.BeanState.UnitValue" = None
            compressor_stage: "Port8111.BeanState.UnitValue" = None
            magneto: "Port8111.BeanState.UnitValue" = None
            power: "Port8111.BeanState.UnitValue" = None
            RPM: "Port8111.BeanState.UnitValue" = None
            manifold_pressure: "Port8111.BeanState.UnitValue" = None
            oil_temp: "Port8111.BeanState.UnitValue" = None
            pitch: "Port8111.BeanState.UnitValue" = None
            thrust: "Port8111.BeanState.UnitValue" = None
            efficiency: "Port8111.BeanState.UnitValue" = None

        valid: bool = None
        aileron: UnitValue = None
        elevator: UnitValue = None
        rudder: UnitValue = None
        flaps: UnitValue = None
        gear: UnitValue = None
        H: UnitValue = None
        TAS: UnitValue = None
        IAS: UnitValue = None
        M: UnitValue = None
        AoA: UnitValue = None
        AoS: UnitValue = None
        Ny: UnitValue = None
        Vy: UnitValue = None
        Wx: UnitValue = None
        Mfuel: UnitValue = None
        Mfuel0: UnitValue = None
        engine: Engine = None

        @staticmethod
        def fromDict(data_dict: typing.Dict[str, float]) -> "Port8111.BeanState":
            @dataclasses.dataclass
            class keyFormat:
                name: str
                index: int
                unit: str
                originalKey: str

                @staticmethod
                def parse_key_format(key: str):
                    if ", " in key:
                        nameindex, unit = key.split(", ")
                    else:
                        nameindex = key
                        unit = None
                    if " " in nameindex:
                        namesindex = nameindex.split(" ")
                        if namesindex[-1].isdigit():
                            name = nameindex[
                                : -(len(namesindex[-1]) + 1)
                            ]  # +1 for space
                            index = int(namesindex[-1])
                        else:
                            name = " ".join(namesindex)
                            index = None
                    else:
                        name = nameindex
                        index = None
                    return keyFormat(name, index, unit, key)

            valid = data_dict.get("valid", False)
            aircraft_fields = {"valid": valid}
            if valid:
                keys = [
                    keyFormat.parse_key_format(k)
                    for k in data_dict.keys()
                    if k != "valid"
                ]
                keys.sort(key=lambda x: x.name)
                grouped_keys = {
                    key: list(_) for key, _ in itertools.groupby(keys, lambda k: k.name)
                }

                # Initialize corresponding fields in Aircraft
                for name, keys in grouped_keys.items():
                    # Assuming all units are the same for each key in the same group
                    unit = keys[0].unit
                    values = (
                        [data_dict[key.originalKey] for key in keys]
                        if len(keys) != 1
                        else data_dict[keys[0].originalKey]
                    )
                    aircraft_fields[name] = Port8111.BeanState.UnitValue(unit, values)

                # Create Engine instance
                engine = Port8111.BeanState.Engine(
                    throttle=aircraft_fields.get("throttle", None),
                    RPM_throttle=aircraft_fields.get("RPM throttle", None),
                    mixture=aircraft_fields.get("mixture", None),
                    radiator=aircraft_fields.get("radiator", None),
                    compressor_stage=aircraft_fields.get("compressor stage", None),
                    magneto=aircraft_fields.get("magneto", None),
                    power=aircraft_fields.get("power", None),
                    RPM=aircraft_fields.get("RPM", None),
                    manifold_pressure=aircraft_fields.get("manifold pressure", None),
                    oil_temp=aircraft_fields.get("oil temp", None),
                    pitch=aircraft_fields.get("pitch", None),
                    thrust=aircraft_fields.get("thrust", None),
                    efficiency=aircraft_fields.get("efficiency", None),
                )

                # Create Aircraft instance
                aircraft = Port8111.BeanState(
                    valid=aircraft_fields.get("valid", None),
                    aileron=aircraft_fields.get("aileron", None),
                    elevator=aircraft_fields.get("elevator", None),
                    rudder=aircraft_fields.get("rudder", None),
                    flaps=aircraft_fields.get("flaps", None),
                    gear=aircraft_fields.get("gear", None),
                    H=aircraft_fields.get("H", None),
                    TAS=aircraft_fields.get("TAS", None),
                    IAS=aircraft_fields.get("IAS", None),
                    M=aircraft_fields.get("M", None),
                    AoA=aircraft_fields.get("AoA", None),
                    AoS=aircraft_fields.get("AoS", None),
                    Ny=aircraft_fields.get("Ny", None),
                    Vy=aircraft_fields.get("Vy", None),
                    Wx=aircraft_fields.get("Wx", None),
                    Mfuel=aircraft_fields.get("Mfuel", None),
                    Mfuel0=aircraft_fields.get("Mfuel0", None),
                    engine=engine,
                )
            else:
                aircraft = Port8111.BeanState(
                    valid=valid,
                )
            return aircraft

    class QueryType(enum.Enum):
        indicator = 0
        map_info = 1
        state = 2

        @staticmethod
        def __throwEnumNotFound():
            raise Exception("enum not found")

        def getPath(self):
            if self == self.indicator:
                return "indicator"
            elif self == self.map_info:
                return "map_info.json"
            elif self == self.state:
                return "state"
            Port8111.QueryType.__throwEnumNotFound()
            return ""

        def parseJson(self, json_obj):
            if self == self.indicator:
                army = json_obj["army"]
                if army == "air":
                    return Port8111.BeanIndicatorAir(**json_obj)
                elif army == "tank":
                    return Port8111.BeanIndicatorTank(**json_obj)
                Port8111.QueryType.__throwEnumNotFound()
            elif self == self.map_info:
                return Port8111.BeanMapInfo(**json_obj)
            elif self == self.state:
                return Port8111.BeanState.fromDict(json_obj)
            Port8111.QueryType.__throwEnumNotFound()

    @staticmethod
    def get_raw_json(queryType: "Port8111.QueryType", timeout=None):
        try:
            response = requests.get(
                "http://localhost:8111/" + queryType.getPath(),
                timeout=timeout if timeout is not None else 1,
            )
        except (requests.ConnectionError, requests.ReadTimeout):
            return None
        json_data = response.json()
        return json_data

    @staticmethod
    def get(queryType: "Port8111.QueryType", timeout=None):
        json_data = Port8111.get_raw_json(queryType, timeout=timeout)
        if json_data is None:
            return None
        return queryType.parseJson(json_data)
