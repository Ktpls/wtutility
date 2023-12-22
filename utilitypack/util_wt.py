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
        valid: bool
        army: str
        type: str
        speed: float
        pedals1: float
        pedals2: float
        stick_elevator: float
        stick_ailerons: float
        vario: float
        altitude_hour: float
        altitude_min: float
        aviahorizon_roll: float
        aviahorizon_pitch: float
        bank: float
        bank1: float
        bank2: float
        turn: float
        compass: float
        compass1: float
        clock_hour: float
        clock_sec: float
        manifold_pressure: float
        manifold_pressure1: float
        rpm_min: float
        rpm1_min: float
        rpm_hour: float
        rpm1_hour: float
        oil_pressure: float
        oil_pressure1: float
        oil_temperature: float
        oil_temperature1: float
        oil_temperature2: float
        oil_temperature3: float
        mixture: float
        mixture1: float
        carb_temperature: float
        carb_temperature1: float
        fuel: float
        fuel_pressure: float
        fuel_pressure1: float
        gears: float
        gears1: float
        flaps: float
        trimmer: float
        throttle: float
        throttle1: float
        weapon1: float
        prop_pitch: float
        prop_pitch1: float
        supercharger: float
        radiator: float

    @dataclasses.dataclass
    class BeanIndicatorTank:
        valid: bool
        army: str
        type: str
        stabilizer: float
        gear: float
        gear_neutral: float
        speed: float
        has_speed_warning: float
        rpm: float
        driving_direction_mode: float
        cruise_control: float
        lws: float
        ircm: float
        roll_indicators_is_available: float
        first_stage_ammo: float
        crew_total: float
        crew_current: float
        crew_distance: float
        gunner_state: float
        driver_state: float

    @dataclasses.dataclass
    class BeanMapInfo:
        grid_size: List[float]
        grid_steps: List[float]
        grid_zero: List[float]
        hud_type: int
        map_generation: int
        map_max: List[float]
        map_min: List[float]
        valid: bool

    @dataclasses.dataclass
    class BeanState:
        @dataclasses.dataclass
        class UnitValue:
            unit: str
            value: typing.Union[float, typing.List[float]]

        @dataclasses.dataclass
        class Engine:
            throttle: "Port8111.BeanState.UnitValue"
            RPM_throttle: "Port8111.BeanState.UnitValue"
            mixture: "Port8111.BeanState.UnitValue"
            radiator: "Port8111.BeanState.UnitValue"
            compressor_stage: "Port8111.BeanState.UnitValue"
            magneto: "Port8111.BeanState.UnitValue"
            power: "Port8111.BeanState.UnitValue"
            RPM: "Port8111.BeanState.UnitValue"
            manifold_pressure: "Port8111.BeanState.UnitValue"
            oil_temp: "Port8111.BeanState.UnitValue"
            pitch: "Port8111.BeanState.UnitValue"
            thrust: "Port8111.BeanState.UnitValue"
            efficiency: "Port8111.BeanState.UnitValue"

        valid: bool
        aileron: UnitValue
        elevator: UnitValue
        rudder: UnitValue
        flaps: UnitValue
        gear: UnitValue
        H: UnitValue
        TAS: UnitValue
        IAS: UnitValue
        M: UnitValue
        AoA: UnitValue
        AoS: UnitValue
        Ny: UnitValue
        Vy: UnitValue
        Wx: UnitValue
        Mfuel: UnitValue
        Mfuel0: UnitValue
        engine: Engine

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
                    aileron=None,
                    elevator=None,
                    rudder=None,
                    flaps=None,
                    gear=None,
                    H=None,
                    TAS=None,
                    IAS=None,
                    M=None,
                    AoA=None,
                    AoS=None,
                    Ny=None,
                    Vy=None,
                    Wx=None,
                    Mfuel=None,
                    Mfuel0=None,
                    engine=None,
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

        def parseJson(self, json_data):
            json_obj = json.loads(json_data)
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
    def get_raw_json(queryType: "Port8111.QueryType"):
        response = requests.get("http://localhost:8111/" + queryType.getPath())
        json_data = response.json()
        return json_data

    @staticmethod
    def get(queryType: "Port8111.QueryType"):
        json_data = Port8111.get_raw_json(queryType)
        return queryType.parseJson(json_data)
