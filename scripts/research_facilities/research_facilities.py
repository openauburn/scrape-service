import util.geocode as geocode
from util.report import Report
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

r = Report()


def scrape(latest, r):
    records = []

    url = "https://cws.auburn.edu/ovpr/Facilities"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find_all(class_="table table-striped")[0]
    rows = table.find_all("tr")[1:]

    for row_i in tqdm(range(len(rows))):
        row = rows[row_i]
        name_col, loc_col, no_col = row.find_all("td")

        name_a = name_col.find_all("a")[0]
        name = name_a.get_text().strip()
        details_url = "https://cws.auburn.edu" + name_a.get("href")
        response2 = requests.get(details_url)
        soup2 = BeautifulSoup(response2.text, "html.parser")
        main_div = soup2.find_all(class_="content_row")[1]
        fields = main_div.find_all(class_="form-group editor-field")
        location, directors, description, facil_url = None, None, None, None
        for field in fields:
            key, value = field.find_all(class_="row")[:2]
            key = key.get_text().strip().lower()
            value = value.get_text().strip()
            match key:
                case "location":
                    location = value
                case "directors":
                    directors = value
                case "description":
                    description = value
                case "url":
                    facil_url = value
                case _:
                    continue

        address, latitude, longitude = location, None, None

        if location:
            address, latitude, longitude = geocode.get_lat_long(
                location + " Alabama USA", r
            )

        records.append(
            {
                "name": name,
                "location": location,
                "url": facil_url,
                "directors": directors,
                "description": description,
                "latitude": latitude,
                "longitude": longitude,
            }
        )

    return records
