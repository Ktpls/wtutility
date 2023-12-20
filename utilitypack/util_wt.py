from .util_windows import *
import requests

import json


def getWTHwnd():
    ret = win32gui.FindWindow("DagorWClass", None)
    if ret == win32con.NULL:
        raise Exception("FindWindow() failed")
    return ret


class port8111:
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

        from dataclasses import dataclass

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

    class queryType(enum.Enum):
        indicator = 0
        map_info = 1

        @staticmethod
        def __throwEnumNotFound():
            raise Exception("enum not found")

        def getPath(self):
            if self == self.indicator:
                return "indicator"
            port8111.queryType.__throwEnumNotFound()
            return ""

        def parseJson(self, json_data):
            jo = json.loads(json_data)
            if self == self.indicator:
                army = jo["army"]
                if army == "air":
                    return port8111.BeanIndicatorAir(**jo)
                elif army == "tank":
                    return port8111.BeanIndicatorTank(**jo)
                port8111.queryType.__throwEnumNotFound()
            elif self == self.map_info:
                return port8111.BeanMapInfo(**jo)
            port8111.queryType.__throwEnumNotFound()

    @staticmethod
    def get(queryType: "port8111.queryType"):
        """
        TODO
        send get request to localhost:8111
        parse json
        return object
        """
        response = requests.get("http://localhost:8111/" + queryType.getPath())
        json_data = response.json()
        return queryType.parseJson(json_data)
