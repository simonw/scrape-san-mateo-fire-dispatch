from bs4 import BeautifulSoup as Soup
import httpx
import json
import datetime
import pytz

url = "http://www.firedispatch.com/iPhoneActiveIncident.asp?Agency=04100"


def scrape_page(url):
    date = str(datetime.datetime.now(pytz.timezone("America/Los_Angeles")).date())
    html = httpx.get(url).text
    bits = [
        b.strip()
        for b in html.split("</TABLE>")[0].split("<TR><TD HEIGHT=4></TD></TR>")[1:]
    ]
    events = []
    for bit in bits:
        if not bit:
            continue
        tds = Soup(bit, "html5lib").select("td")
        if not tds:
            continue
        time, id = tds[0].text.strip().replace("\xa0", " ").rsplit(None, 1)
        summary = tds[1].text.strip()
        category = tds[2].text.strip()
        location = tds[3].text.strip()
        latitude = None
        longitude = None
        # If there is a maps.google.com link get lat/lon
        map_link = tds[3].select("a[href^='https://maps.google.com']")
        if map_link:
            map_bits = map_link[0]["href"].split("q=")[1]
            latitude, longitude = map(float, map_bits.split(","))
        units = tds[4].text.strip().replace("\xa0", " ")
        events.append(
            {
                "id": id,
                "date": date,
                "time": time,
                "summary": summary,
                "category": category,
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
                "units": units,
            }
        )
    return html, events


if __name__ == "__main__":
    html, events = scrape_page(url)
    open("incidents.html", "w").write(html)
    open("incidents.json", "w").write(json.dumps(events, indent=4))
