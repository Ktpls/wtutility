import requests
from utilref import *
import json


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
        sells = self.MarketProxyGaijinNetWeb("cln_books_brief", itemName)["response"][
            "SELL"
        ]
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
    inventory = [
        MyItem("id50230_ct_cv_105hp_sweden", 3),
        MyItem("id50212_bf_109_f_4_italy", 1),
        MyItem("items_F2G-1+Super+Corsair+(USA)", 1),
        MyItem("items_ITP+(M-1)+(USSR)", 1),
        MyItem("id50239_losat_usa", 5),
        MyItem("items_Т-10А+(USSR)", 1),
        MyItem("id50236_ki_48_ii_otsu_japan", 4),
        MyItem("id50226_b7a2_homare_23_japan", 2),
        MyItem("items_Matilda+Hedgehog+(Britain)", 1),
    ]

    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjM4MTQ3NiIsInR5cCI6IkpXVCJ9.eyJhdXRoIjoibG9naW4iLCJjbnRyeSI6IkNOIiwiZXhwIjoxNzEyMzg3OTcxLCJmYWMiOiI5MGMyMWY5YjhjNzRmZGIzMjc3ZGQyN2VjYmUzMjNjMTJiM2RmZDAyNTczYjE0M2Y1MGFiMTY4N2FkYWI0N2I2IiwiaWF0IjoxNzA5Nzk1OTcxLCJpc3MiOiIxIiwia2lkIjoiMzgxNDc2IiwibG5nIjoiZW4iLCJsb2MiOiJlYjg2ZmQ0MDM1MjcyNjRmYjNjYjhlMzkxMjBmZWUyMmIwNmVmMGQwNTkxNTMyYzU1ZGUxYTIwNjEyYTg0ODY5IiwibmljayI6IlNlbGVuYWJ1bm55Iiwic2x0IjoiZUx5SFpJSWgiLCJ0Z3MiOiIyc3RlcCwyc3RlcF90b3RwLGN1c3RvbWVyLGN1c3RvbWVyX3d0LGRpZmZjdXJyLGVtYWlsX2RlbGl2ZXJlZCxlbWFpbF92ZXJpZmllZCxsYW5nX2VuLHBhcnRuZXJfc3RlYW0scGF5X2NueSxwaG9uZV92ZXJpZmllZCxwbGF5ZXJfZWwscGxheWVyX3d0LHNzb19hbGxvd2VkX3Bvc3Qsc3RlYW0sc3RlYW1nZW4sd3RfZW4sd3RfZmlyc3RfbG9naW4sd3RfcXVpel9zdWNjZXNzIiwidWlkIjoiODMzMjI5MDQifQ.aBLb_SCVZk2esaFqL3z3fIJnuKdNADViPUGmU5J8bT7hHZD0xfL8fWtSoEEFeiJsrT8lyzq-ypTBGYkak3z9H3aiqQk7W6gWBaDg-e3LXjTqA29L0L3uweKGEeDh0DJ-90ZfLLHvOUHFofcmAoyXsHf-opeZvUB9FCJ7GYY3GILB0bGjgE2bUE7EpmlPU394-JzC66-4v70FNSLg-Xer3YGw_uTjm0qRUxSElDt8V4I7HKnEbbQb_uOixrJ0dAnXZKinJ8V1Mp_KeuOyY9rHYlWhYoU_r_e5ZH21DuyvEOLHRJePcjUodmf8kALV0kfeNC7Op-uf2rRyqarXGdbr7Q"
    tgn = TradeGaijinNet(token)
    for i in inventory:
        print(i.itemCode)
        i.price = tgn.getSellPrice(i.itemCode)

    total = np.sum([i.price * i.amount for i in inventory]) + 49.2
    line = [GetTimeString(), int(time.time()), total]
    line = [str(c) for c in line]
    AppendFile("asset/statistics/inventoryAccount.csv", ",".join(line) + "\n")
    print(total)
    os.system("pause")


main()
