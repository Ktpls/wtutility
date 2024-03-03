import requests
from lxml import html
import os
from dataclasses import dataclass
from typing import *
import traceback
import time


@dataclass
class Vehicle:
    name: str
    br: list[str]


def completeUrl(leftover, base="https://wiki.warthunder.com"):
    return base + leftover


def myget(url):
    url = completeUrl(url)
    while True:
        try:
            # slow down
            time.sleep(1)
            response = requests.get(url)
            break
        except Exception as e:
            traceback.print_exc()
    return response


def CountryOfAviation(page):
    # page = "https://wiki.warthunder.com/Aviation"

    response = myget(page)
    tree = html.fromstring(response.content)

    td_elements = tree.xpath("//table[@class='wt-class-table']/tr[1]/td[1]/div/a[1]")
    ret = [td_element.get("href") for td_element in td_elements]
    return ret


def VehicleOfCountry(page):
    """
    todo
    down load html from url 'https://wiki.warthunder.com/Category:USSR_aircraft'
    use xpath to select all div elements with class equals 'tree-item', under which lays a single div, under which lays an 'a' element, select the href of 'a',
    print them all
    """
    # page = 'https://wiki.warthunder.com/Category:USSR_aircraft'

    response = myget(page)
    tree = html.fromstring(response.content)

    div_elements = tree.xpath("//div[@class='tree-item']/div/a")
    return [div_element.get("href") for div_element in div_elements]


def BrOfVehicle(page):
    # page = 'https://wiki.warthunder.com/MiG-21SMT'

    response = myget(page)
    tree = html.fromstring(response.content)

    td_elements = tree.xpath("//div[@class='general_info_br']/table/tr[2]/td")
    return [td_element.text for td_element in td_elements]


from openpyxl import Workbook

workbook = Workbook()
sheet = workbook.active


def writeList(l):
    sheet.append(l)


country = CountryOfAviation("https://wiki.warthunder.com/Aviation")
for c in country:
    line = [f"Country {c}"]
    writeList(line)
    print(",".join(line))
    vehicle = VehicleOfCountry(completeUrl(c))
    for v in vehicle:
        br = BrOfVehicle(completeUrl(v))
        line = [f"Vehicle {v}"]
        line.extend(br)
        print(",".join(line))
        writeList(line)

workbook.save("output.xlsx")
