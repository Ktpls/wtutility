from .engineConfigInclude import *
from .utilref import *

"""
in game control setting
radiator, oilRadiator, propPitch
    Relative control step = 0%
    Sensitivity = 50%
"""


@HostedEngineConfig
class G55S(EasyEngineConfig):
    planeName = "g_55s"
    PP = 0.95
    RAD = 0.80
    OILRAD = EasyEngineConfig.ORAD_MAX


@HostedEngineConfig
class Yak3(EasyEngineConfig):
    planeName = ["yak-3_france", "yak-9t", "yak-3_eremin", "yak-1b"]
    PP = 1.00
    RAD = 0.25
    ALTSC = [[None, 1], [2350, 2]]


@HostedEngineConfig
class Raiden(EasyEngineConfig):
    planeName = "j2m5_30mm"
    PP = 0.95
    RAD = 0.35
    ALTSC = [[None, 1], [2400, 2]]


@HostedEngineConfig
class I29(EasyEngineConfig):
    planeName = "i_29"
    PP = 0.97
    RAD = 0.60
    ALTSC = [[None, 1], [3500, 2]]


@HostedEngineConfig
class P63A5(EasyEngineConfig):
    planeName = ["p-63a-5_ussr", "p-63a-10"]
    RAD = 0.4


@HostedEngineConfig
class SaabJ21A(EasyEngineConfig):
    planeName = "saab_j21a_1"
    PP = 0.75
    RAD = 1.0
    OILRAD = 1.0


@HostedEngineConfig
class Il8(EasyEngineConfig):
    planeName = "il_8_1944"
    PP = 0.95
    RAD = 0.5


@HostedEngineConfig
class Be6(EasyEngineConfig):
    planeName = "be_6"
    ALTSC = [[None, 0.93], [2000, 1.0]]
    RAD = 1.0


@HostedEngineConfig
class Itp(EasyEngineConfig):
    planeName = "itp_m1"
    RAD = 1.0
    OILRAD = 1.0

    class HeatingLevel(LambdaAxis):
        def __init__(self, gauges: Gauges):
            super().__init__(
                lambda: (
                    1
                    if gauges.oilTemp.get() < 85
                    else (2 if gauges.oilTemp.get() < 87 else 3)
                )
            )

    # def check(self, gauges: Gauges):
    #     MappingAxis(
    #     gauges.altitude,
    #     gauges.propPitch,
    #     [
    #     [None, 0.52],
    #     [4000, 0.60],
    #     [6000, 0.65],
    #     ],
    #     )
    #     super().check()


@HostedEngineConfig
class P47D(EasyEngineConfig):
    planeName = "p-47d_ussr"
    RAD = 0.45
    OILRAD = 0.45


@HostedEngineConfig
class M82Fn(EasyEngineConfig):
    planeName = ["la-7b-20", "la-5fn", "i_185_m82"]
    PP = 0.95
    RAD = 1.0
    OILRAD = EasyEngineConfig.ORAD_MAX
    ALTSC = [
        [None, 1],
        [3000, 2],
    ]


@HostedEngineConfig
class P51C(EasyEngineConfig):
    planeName = ["p-51d-20-na_j26", "p-51c-10-nt", "p-51c-10_france"]
    PP = 1.0
    RAD = 1.0
    OILRAD = EasyEngineConfig.ORAD_MAX


@HostedEngineConfig
class Hampden(EasyEngineConfig):
    planeName = "hp52_hampden_tbmk1_ussr_utk1"
    PP = 0.95
    RAD = 1.0
    ALTSC = [
        [None, 1],
        [2400, 2],
    ]


@HostedEngineConfig
class TB3(EasyEngineConfig):
    planeName = "tb_3_m17_32"
    RAD = 1.0


@HostedEngineConfig
class I153(EasyEngineConfig):
    planeName = "i-153_m62_zhukovskiy"
    RAD = 1.0
    OILRAD = EasyEngineConfig.ORAD_MAX
    ALTSC = [
        [None, 1],
        [1700, 2],
    ]

    def check(self, gauges: Gauges):
        super().check()
        MappingAxis(
            gauges.supercharger,
            gauges.propPitch,
            [
                [None, 0.95],
                [2, 0.9],
            ],
        )


@HostedEngineConfig
class I16ShvetsovM25(EngineConfig):
    planeName = ["i-16_type10"]
    RAD = 1.0


@HostedEngineConfig
class I16ShvetsovM62(I153):
    planeName = ["i-16_type27"]


@HostedEngineConfig
class Il2(EasyEngineConfig):
    planeName = ["il_2_37_1943"]
    PP = 1.0
    RAD = 1.0
    OILRAD = EasyEngineConfig.ORAD_MAX


@HostedEngineConfig
class Brigand(EasyEngineConfig):
    planeName = ["brigand_b1"]
    PP = 1.0
    RAD = 1.0
    OILRAD = 1.0


@HostedEngineConfig
class HurricaneMk1(EasyEngineConfig):
    planeName = ["hurricane_mk1_late_ep"]
    PP = 0.95
    RAD = 1.0


@HostedEngineConfig
class HurricaneMk1B(EasyEngineConfig):
    planeName = ["hurricane_mk1b"]
    PP = 0.8
    RAD = 1.0


@HostedEngineConfig
class TyphoonMk1A(EasyEngineConfig):
    planeName = ["typhoon_mk1a"]
    PP = 0.95
    RAD = 1.0
    ALTSC = [
        [None, 1],
        [3700, 2],
    ]


@HostedEngineConfig
class MB5(EasyEngineConfig):
    planeName = ["mb_5"]
    PP = 0.95
    RAD = 1.0
    ALTSC = [
        [None, 1],
        [2700, 2],
    ]


@HostedEngineConfig
class SpitfireMk1(EasyEngineConfig):
    planeName = ["spitfire_mk1"]
    PP = 0.75
    RAD = 1.0


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
