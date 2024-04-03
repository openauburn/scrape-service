from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import util.safety_format as safety_format
import util.geocode as geocode

def scrape(latest, r):

    url = 'https://auburn.edu/administration/campus-safety/reports/fire/index.php?_search=&action=search&_csrf='

    driver = webdriver.Chrome()
    driver.get(url)

    table = driver.find_elements(By.TAG_NAME, 'tbody')[2]
    table_rows = table.find_elements(By.TAG_NAME, 'tr')[1:]

    rows = []

    if latest is not None:
        for row in table_rows:
            fields = row.find_elements(By.TAG_NAME, 'td')
            if(fields[0].text == latest.incident_id):
                break
            else:
                rows.append(row)
    else:
        rows = table_rows

    rows.reverse()

    c = 0
    records = []
    for row in rows: # For each incident

        fields = row.find_elements(By.TAG_NAME, 'td')

        if(fields[0].text == "NA" or "TEST" in fields[0].text): # Not counting entries used to test the logging system
            continue

        address, latitude, longitude = geocode.get_lat_long(fields[7].text + " Auburn Alabama", r)

        record = {
            "incident_id": safety_format.string_format(fields[0].text, r),
            "site": safety_format.string_format(fields[1].text, r),
            "occurred_at" : safety_format.datetime_format(fields[2].text, fields[3].text, r),
            "reported_at": safety_format.date_format(fields[4].text, r),
            "description": safety_format.string_format(fields[5].text, r),
            "cause": safety_format.string_format(fields[6].text, r),
            "location": address,
            "longitude": longitude,
            "latitude": latitude,
            "damage_cost": safety_format.string_format(fields[8].text, r),
            "injuries": int(fields[9].text),
            "deaths": int(fields[10].text),
        }
        records.append(record)

        c += 1
        print(c)

    driver.close()
    driver.quit()

    return records