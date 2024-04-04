from utilref import *


def collectingHudmsg():
    hudmsg: Port8111.BeanHudMsg = Port8111.get(
        Port8111.QueryType.hudmsg, {"lastEvt": 0, "lastDmg": 0}
    )
    AppendFile(
        r"asset\statistics\hudmsg.txt", "".join([m.msg + "\n" for m in hudmsg.damage])
    )


@Singleton
class MsgParser:

    def __init__(self):
        MstPatts = [
            r"^(.+) destroyed (?:.+)$",
            r"^(.+) set afire (.+)$",
            r"^(.+) critically damaged (.+)$",
            r"^(.+) severely damaged (.+)$",
            r"^(.+) shot down (.+)$",
            r"^(.+) has crashed\.$",
            r"^(.+) has achieved (?:.+)$",
            r"^(?:.+) has disconnected from the game\.$",
            r"^(?:.+)td! kd\?NET_PLAYER_DISCONNECT_FROM_GAME$",
            r"^(.+) has delivered the final blow!$",
        ]
        MstPatts = [re.compile(p) for p in MstPatts]
        self.MstPatts = MstPatts

        # some vehilces contains brackets inside name
        self.UnitPatt = re.compile(r"^(.+?) \((.+)\)$")

    def ExtractMsg(self, msg):
        for p in self.MstPatts:
            mtc = p.match(msg)
            if mtc:
                return mtc
        return None

    def ExtractPlayerInfo(self, msg):
        return self.UnitPatt.match(msg)

    def SummaryHudMsg(self, l: list[str]):
        players = dict()
        for m in l:
            mtc = self.ExtractMsg(m)
            # TODO change assertion to log.error
            assert mtc is not None, f"{m} cant be parsed!"
            for p in mtc.groups():
                pi = self.ExtractPlayerInfo(p)
                if pi is not None:
                    groupspi = pi.groups()
                    players[groupspi[0]] = BeanPlayer(groupspi[0], groupspi[1])
        return players


class HudMsgHost:
    def __init__(self, name, vehicle):
        self.lastDmg = 0
        self.playerInfo = dict()

    def update(self):
        # TODO how to set lastDmg back to 0?
        hudmsg: Port8111.BeanHudMsg = Port8111.get(
            Port8111.QueryType.hudmsg,
            param={"lastEvt": 0, "lastDmg": self.lastDmg},
        )
        if hudmsg is not None and len(hudmsg.damage) > 0:
            newInfo = MsgParser().SummaryHudMsg([m.msg for m in hudmsg.damage])
            self.playerInfo.update(newInfo)
            self.lastDmg = hudmsg.damage[-1].time


@dataclasses.dataclass
class BeanPlayer:
    name: str
    vehicle: str


collectingHudmsg()
'''
r = MsgParser().SummaryHudMsg(ReadTextFile(r"asset\statistics\hudmsg.txt").splitlines())
breakpoint()
pass
'''