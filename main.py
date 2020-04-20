import math

import bs4
import requests


class Thinkpad:
    name = None
    sku = None
    price = None
    processor = None
    graphics = None
    memory = None
    battery = None
    storage = None

    def __init__(self, name, sku, price, processor, graphics, memory, battery, storage):
        self.name = name
        self.sku = sku
        self.price = price
        self.processor = processor
        self.graphics = graphics
        self.memory = memory
        self.battery = battery
        self.storage = storage


def main():
    thinkpads = parseSite()
    for thinkpad in thinkpads:
        print("==========")
        print(f"{thinkpad.name} ({thinkpad.sku})")
        print(thinkpad.price)
        print(thinkpad.processor)
        print(thinkpad.memory)
        print(thinkpad.graphics)
        print(thinkpad.battery)
        print(thinkpad.storage)


def parseSite():
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0"}
    )
    page = session.get("https://www.lenovo.com/us/en/outletus/laptops/thinkpad/c/22TP")

    if page.status_code != 200:
        print(f"Received non-OK status code: {page.status_code}")
        exit(1)

    attributes = {"class": "facetedResults-item only-allow-small-pricingSummary"}

    bs = bs4.BeautifulSoup(page.content, "html.parser")

    resultCount = bs.find("div", {"class": "totalResults"}).contents[2].strip().split(" ")[0]
    pages = math.ceil(int(resultCount) / 8)
    print(f"Results:{resultCount} - Pages:{pages}")

    tps = []
    for i in range(0, pages):
        page = session.get(f"https://www.lenovo.com/us/en/outletus/laptops/thinkpad/c/22TP?q=%3Aprice-asc&page={i}")
        bs = bs4.BeautifulSoup(page.content, "html.parser")
        resultList = bs.find(id="resultsList")
        results = resultList.find_all("div", attributes)
        for res in results:
            tps.append(parseThinkpad(res))

    return tps


def parseThinkpad(tpdiv):
    search = ["Processor", "Graphics", "Memory", "Hard Drive", "Operating System", "Battery"]
    data = {}
    name = tpdiv.find("h3", {"class": "facetedResults-title"}).find("a", {"class": "facetedResults-cta"}).contents[0]
    sku = tpdiv.find("div", {"class": "facetedResults-feature-list"}).find("dd").contents[0]
    price: bs4.element.Tag = tpdiv.find("dd", {"class": "pricingSummary-details-final-price"}).contents[0].strip()
    for t in search:
        try:
            data[t] = tpdiv.find("dt", {"data-term": t}).parent.find("dd").contents[0].strip()
        except:
            print(f"Failed to parse '{t} for {name}'")
            data[t] = None

    return Thinkpad(name, sku, price, data["Processor"], data["Graphics"], data["Memory"], data["Battery"],
                    data["Hard Drive"])


main()
