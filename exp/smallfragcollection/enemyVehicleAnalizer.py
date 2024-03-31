from utilref import *

def collectingHudmsg():
    hudmsg: Port8111.BeanHudMsg = Port8111.get(
        Port8111.QueryType.hudmsg, {"lastEvt": 0, "lastDmg": 0}
    )
    AppendFile(r"asset\statistics\hudmsg.txt", "".join([m.msg+'\n' for m in hudmsg.damage]))
collectingHudmsg()
r"""
http://127.0.0.1:8111/hudmsg?lastEvt=0&lastDmg=0
{
  "events": [],
  "damage": [
    {
      "id": 1217,
      "msg": "[Wied] Zhukov2019 (F4U-4) shot down =HOMEY= 四舍五入我有两米多高 (▄P-63C)",
      "sender": "",
      "enemy": false,
      "mode": "",
      "time": 289
    },
    {
      "id": 1358,
      "msg": "=HOMEY= NIGHTFURYYYY (◐Bf 109 F) has achieved \"Terror of the Sky\"",
      "sender": "",
      "enemy": false,
      "mode": "",
      "time": 958
    },
    {
      "id": 1365,
      "msg": "purelighttd! kd?NET_PLAYER_DISCONNECT_FROM_GAME",
      "sender": "",
      "enemy": false,
      "mode": "",
      "time": 962
    }
  ]
}
"""
