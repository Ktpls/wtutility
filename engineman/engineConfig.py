from .engineConfigInclude import *
from .utilref import *

"""
in game control setting

radiator, oilRadiator, propPitch
    Relative control step = 0%
    Sensitivity = 50%
"""


@HostedEngineConfig(planeName="g_55s")
class G55S(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(0.80)
        gauges.oilRadiator.setToMaxAnyway()


@HostedEngineConfig(planeName=["yak-3_france", "yak-9t", "yak-3_eremin", "yak-1b"])
class Yak3(EngineConfig):
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


@HostedEngineConfig(planeName="j2m5_30mm")
class Raiden(EngineConfig):
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


@HostedEngineConfig(planeName="i_29")
class I29(EngineConfig):
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


@HostedEngineConfig(planeName=["p-63a-5_ussr", "p-63a-10"])
class P63A5(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(0.4)


@HostedEngineConfig(planeName="saab_j21a_1")
class SaabJ21A(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.75)
        gauges.oilRadiator.set(1.0)
        gauges.radiator.set(1.0)


@HostedEngineConfig(planeName="il_8_1944")
class Il8(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(0.5)


@HostedEngineConfig(planeName="be_6")
class Be6(EngineConfig):
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


@HostedEngineConfig(planeName="itp_m1")
class Itp(EngineConfig):
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


@HostedEngineConfig(planeName="p-47d_ussr")
class P47D(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(0.45)
        gauges.oilRadiator.set(0.45)


@HostedEngineConfig(planeName=["la-7b-20", "la-5fn", "i_185_m82"])
class M82Fn(EngineConfig):
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


@HostedEngineConfig(planeName=["p-51d-20-na_j26", "p-51c-10-nt", "p-51c-10_france"])
class P51C(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(1.0)
        gauges.radiator.set(1.0)
        gauges.oilRadiator.setToMaxAnyway()


@HostedEngineConfig(planeName="hp52_hampden_tbmk1_ussr_utk1")
class Hampden(EngineConfig):
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


@HostedEngineConfig(planeName="tb_3_m17_32")
class TB3(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(1.0)


@HostedEngineConfig(planeName="i-153_m62_zhukovskiy")
class I153(EngineConfig):
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


@HostedEngineConfig(planeName=["i-16_type10"])
class I16ShvetsovM25(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.radiator.set(1.0)


@HostedEngineConfig(planeName=["i-16_type27"])
class I16ShvetsovM62(I153): ...


@HostedEngineConfig(planeName=["il_2_37_1943"])
class Il2(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(1.0)
        gauges.radiator.set(1.0)
        gauges.oilRadiator.setToMaxAnyway()


@HostedEngineConfig(planeName=["brigand_b1"])
class Brigand(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(1.0)
        gauges.radiator.set(1.0)
        gauges.oilRadiator.set(1.0)


@HostedEngineConfig(planeName=["hurricane_mk1_late_ep"])
class HurricaneMk1(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.95)
        gauges.radiator.set(1.0)


@HostedEngineConfig(planeName=["hurricane_mk1b"])
class HurricaneMk1B(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.8)
        gauges.radiator.set(1.0)


@HostedEngineConfig(planeName=["typhoon_mk1a"])
class TyphoonMk1A(EngineConfig):
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


@HostedEngineConfig(planeName=["mb_5"])
class MB5(EngineConfig):
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


@HostedEngineConfig(planeName=["spitfire_mk1"])
class SpitfireMk1(EngineConfig):
    def check(self, gauges: Gauges):
        gauges.propPitch.set(0.75)
        gauges.radiator.set(1.0)


@HostedEngineConfig(planeName=["spitfire_f24"])
class SpitfireMk24(EasyEngineConfig):
    PP = 0.95
    RAD = 1.0
    ALTSC = [
        [None, 1],
        [3750, 2],
    ]


@HostedEngineConfig(planeName=["vg_33"])
class Vg33(EasyEngineConfig):
    PP = 0.95
    RAD = 1.0
    ORAD = EasyEngineConfig.SET_TO_MAX_ANYWAY


@HostedEngineConfig(planeName=["d_510"])
class D510(EasyEngineConfig):
    RAD = 1.0


@HostedEngineConfig(planeName=["ki_44_2_hei_china"])
class Ki44(EasyEngineConfig):
    PP = 0.95
    ALTSC = [
        [None, 1],
        [2000, 2],
    ]


@HostedEngineConfig(planeName=["j9_early"])
class J9(EasyEngineConfig):
    PP = 0.95
    RAD = 0.25


@HostedEngineConfig(planeName=["bf-109e-3_japan"])
class Bf109E(EasyEngineConfig):
    RAD = 1.0
    ORAD = EasyEngineConfig.SET_TO_MAX_ANYWAY



@HostedEngineConfig(planeName=["a6m2_zero_usa"])
class A6M(EasyEngineConfig):
    RAD = 0.3
    ORAD = 0.3
    PP = 1.0
