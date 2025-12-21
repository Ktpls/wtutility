import requests
from chpath import *
import json
from utilitypack.util_solid import *
from utilitypack.util_np import *

@dataclasses.dataclass
class TradeGaijinNet:
    token: str
    header: dict = None
    appid: str = "1067"

    def __post_init__(self):
        if self.header is None:
            self.header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://trade.gaijin.net",
                "Connection": "keep-alive",
                "Referer": "https://trade.gaijin.net/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "TE": "trailers",
            }

    def MarketProxyGaijinNetWeb(self, action, itemName):
        body = (
            "action={action}&token={token}&appid={appid}&market_name={itemName}".format(
                **{
                    "action": action,
                    "token": self.token,
                    "appid": self.appid,
                    "itemName": itemName,
                }
            )
        )
        result = requests.post(
            url="https://market-proxy.gaijin.net/web",
            headers=self.header,
            data=body.encode(),
        )
        result = json.loads(result.text.encode())
        return result

    def getSellPrice(self, itemName):
        resp = self.MarketProxyGaijinNetWeb("cln_books_brief", itemName)["response"]
        sells = resp["SELL"]
        if len(sells) == 0:
            return 0
        list.sort(sells, key=lambda x: x[0])
        time.sleep(0.1)
        return (sells[0][0]) / 10000


@dataclasses.dataclass
class MyItem:
    itemCode: str
    amount: int
    price: float = 0


def main():
    money = 121.63
    inventory = [
        MyItem("id50230_ct_cv_105hp_sweden", 3),
        MyItem("id50212_bf_109_f_4_italy", 1),
        MyItem("items_F2G-1+Super+Corsair+(USA)", 1),
        MyItem("id50226_b7a2_homare_23_japan", 2),
        MyItem("id50244_strikemaster_mk_88_great_britain", 4),
    ]

    token = ReadTextFile("smalls/trade.ignored")
    tgn = TradeGaijinNet(token)
    for i in inventory:
        print(i.itemCode)
        i.price = tgn.getSellPrice(i.itemCode)

    total = np.sum([i.price * i.amount for i in inventory]) * 0.85 + money
    line = [GetTimeString(), int(time.time()), total]
    line = [str(c) for c in line]
    AppendFile("asset/statistics/inventoryAccount.csv", ",".join(line) + "\n")
    print(total)
    os.system("pause")


main()
