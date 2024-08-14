from .engineConfigInclude import *
from .utilref import *

"""
in game control setting

radiator, oilRadiator, propPitch
    Relative control step = 0%
    Sensitivity = 50%
"""


@HostedEngineConfig
class G55S(EngineConfig):
    planeName = "g_55s"
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(0.80)
        gauges.oilRadiator.setToMaxAnyway()


@HostedEngineConfig
class Yak3(EngineConfig):
    planeName = ["yak-3_france", "yak-9t", "yak-3_eremin", "yak-1b"]

    def check(self, gauges: Gauges):
        gauges.propPitch.set(1.00)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [2350, 2],
            ],
        )
        gauges.radiator.set(0.25)


@HostedEngineConfig
class Raiden(EngineConfig):
    planeName = "j2m5_30mm"

    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [2400, 2],
            ],
        )
        gauges.radiator.set(0.35)


@HostedEngineConfig
class I29(EngineConfig):
    planeName = "i_29"

    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.97)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [3500, 2],
            ],
        )
        gauges.radiator.set(0.60)


@HostedEngineConfig
class P63A5(EngineConfig):
    planeName = ["p-63a-5_ussr", "p-63a-10"]

    def check(self, gauges: Gauges):
        gauges.radiator.set(0.4)


@HostedEngineConfig
class SaabJ21A(EngineConfig):
    planeName = "saab_j21a_1"

    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.75)
        gauges.oilRadiator.set(1.0)
        gauges.radiator.set(1.0)


@HostedEngineConfig
class Il8(EngineConfig):
    planeName = "il_8_1944"

    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(0.5)


@HostedEngineConfig
class Be6(EngineConfig):
    planeName = "be_6"

    def check(self, gauges: Gauges):
        MappingAxis(
            gauges.altitude,
            gauges.propPitch,
            [
                [None, 0.93],
                [2000, 1.0],
            ],
        )
        gauges.radiator.set(1.0)


@HostedEngineConfig
class Itp(EngineConfig):
    planeName = "itp_m1"

    class HeatingLevel(LambdaAxis):
        def __init__(self, gauges: Gauges):
            super().__init__(
                lambda: (
                    1
                    if gauges.oilTemp.get() < 85
                    else (2 if gauges.oilTemp.get() < 87 else 3)
                )
            )

    def check(self, gauges: Gauges):
        # MappingAxis(
        # gauges.altitude,
        # gauges.propPitch,
        # [
        # [None, 0.52],
        # [4000, 0.60],
        # [6000, 0.65],
        # ],
        # )
        gauges.radiator.set(1.0)
        gauges.oilRadiator.set(1.0)


@HostedEngineConfig
class P47D(EngineConfig):
    planeName = "p-47d_ussr"

    def check(self, gauges: Gauges):
        gauges.radiator.set(0.45)
        gauges.oilRadiator.set(0.45)


@HostedEngineConfig
class M82Fn(EngineConfig):
    planeName = ["la-7b-20", "la-5fn", "i_185_m82"]

    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [3000, 2],
            ],
        )
        gauges.radiator.set(1.0)
        gauges.oilRadiator.setToMaxAnyway()


@HostedEngineConfig
class P51C(EngineConfig):
    planeName = ["p-51d-20-na_j26", "p-51c-10-nt", "p-51c-10_france"]

    def check(self, gauges: Gauges):
        gauges.propPitch.set(1.0)
        gauges.radiator.set(1.0)
        gauges.oilRadiator.setToMaxAnyway()


@HostedEngineConfig
class Hampden(EngineConfig):
    planeName = "hp52_hampden_tbmk1_ussr_utk1"

    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [2400, 2],
            ],
        )
        gauges.radiator.set(1.0)


@HostedEngineConfig
class TB3(EngineConfig):
    planeName = "tb_3_m17_32"

    def check(self, gauges: Gauges):
        gauges.radiator.set(1.0)


@HostedEngineConfig
class I153(EngineConfig):
    planeName = "i-153_m62_zhukovskiy"

    def check(self, gauges: Gauges):
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [1700, 2],
            ],
        )
        MappingAxis(
            gauges.supercharger,
            gauges.propPitch,
            [
                [None, 0.95],
                [2, 0.9],
            ],
        )
        gauges.radiator.set(1.0)
        gauges.oilRadiator.setToMaxAnyway()


@HostedEngineConfig
class I16ShvetsovM25(EngineConfig):
    planeName = ["i-16_type10"]

    def check(self, gauges: Gauges):
        gauges.radiator.set(1.0)


@HostedEngineConfig
class I16ShvetsovM62(I153):
    planeName = ["i-16_type27"]


@HostedEngineConfig
class Il2(EngineConfig):
    planeName = ["il_2_37_1943"]

    def check(self, gauges: Gauges):
        gauges.propPitch.set(1.0)
        gauges.radiator.set(1.0)
        gauges.oilRadiator.setToMaxAnyway()


@HostedEngineConfig
class Brigand(EngineConfig):
    planeName = ["brigand_b1"]

    def check(self, gauges: Gauges):
        gauges.propPitch.set(1.0)
        gauges.radiator.set(1.0)
        gauges.oilRadiator.set(1.0)


@HostedEngineConfig
class HurricaneMk1(EngineConfig):
    planeName = ["hurricane_mk1_late_ep"]

    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(1.0)


@HostedEngineConfig
class HurricaneMk1B(EngineConfig):
    planeName = ["hurricane_mk1b"]

    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.8)
        gauges.radiator.set(1.0)


@HostedEngineConfig
class TyphoonMk1A(EngineConfig):
    planeName = ["typhoon_mk1a"]

    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(1.0)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [3700, 2],
            ],
        )


@HostedEngineConfig
class MB5(EngineConfig):
    planeName = ["mb_5"]

    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(1.0)
        MappingAxis(
            gauges.altitude,
            gauges.supercharger,
            [
                [None, 1],
                [2700, 2],
            ],
        )


@HostedEngineConfig
class SpitfireMk1(EngineConfig):
    planeName = ["spitfire_mk1"]
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.75)
        gauges.radiator.set(1.0)


@HostedEngineConfig
class SpitfireMk24(EasyEngineConfig):
    planeName = ["spitfire_f24"]
    PP = 0.95
    RAD = 1.0
    ALTSC = [
        [None, 1],
        [3750, 2],
    ]


@HostedEngineConfig
class Vg33(EasyEngineConfig):
    planeName = ["vg_33"]
    PP = 0.95
    RAD = 1.0
    ORAD = EasyEngineConfig.ORAD_MAX


@HostedEngineConfig
class D510(EasyEngineConfig):
    planeName = ["d_510"]
    RAD = 1.0


@HostedEngineConfig
class Ki44(EasyEngineConfig):
    planeName = ["ki_44_2_hei_china"]
    PP = 0.95
    ALTSC = [
        [None, 1],
        [2000, 2],
    ]


@HostedEngineConfig
class J9(EasyEngineConfig):
    planeName = ["j9_early"]
    PP = 0.95
    RAD = 0.25


@HostedEngineConfig
class Bf109E(EasyEngineConfig):
    planeName = ["bf-109e-3_japan"]
    RAD = 1.0
    ORAD = EasyEngineConfig.ORAD_MAX


@HostedEngineConfig
class A6M(EasyEngineConfig):
    planeName = ["a6m2_zero_usa"]
    RAD = 0.3
    ORAD = 0.3
    PP = 1.0
