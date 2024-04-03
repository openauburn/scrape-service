import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import util.safety_format as safety_format
import util.geocode as geocode

def scrape(latest, r):

    url = 'https://iss.auburn.edu/crimelog/index.php?_offset=0&'
    url_all = 'https://iss.auburn.edu/crimelog/index.php?_pagination_off=1&'

    driver = webdriver.Chrome()
    driver.get(url_all)

    user = os.environ.get("CLERY_AUTH_USER")
    passw = os.environ.get("CLERY_AUTH_PASS")

    user_field = driver.find_element('name','user')
    user_field.send_keys(user)

    pass_field = driver.find_element('name','pass')
    pass_field.send_keys(passw)

    submit = driver.find_element('name','submit')
    submit.click()

    view_all = driver.find_element(By.LINK_TEXT, '[show all]')
    view_all.click()

    table = driver.find_elements(By.TAG_NAME, 'tbody')[2]
    table_rows = table.find_elements(By.TAG_NAME, 'tr')[1:]

    rows = []

    if latest is not None: # full
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

        if(fields[0].text == "NA"):
            continue

        address, latitude, longitude = geocode.get_lat_long(fields[10].text + " Auburn Alabama", r)

        record = {
            "incident_id": safety_format.string_format(fields[0].text, r),
            "campus": safety_format.string_format(fields[1].text, r),
            "date_reported": safety_format.date_format(fields[2].text, r),
            "occurred_from": safety_format.datetime_format(fields[3].text,fields[4].text, r),
            "occurred_to": safety_format.datetime_format(fields[5].text,fields[6].text, r),
            "incident_type": safety_format.string_format(fields[7].text, r),
            "clery_class": safety_format.string_format(fields[8].text, r),
            "additional_info": safety_format.string_format(fields[9].text, r),
            "location": safety_format.string_format(address, r),
            "longitude": longitude,
            "latitude": latitude,
            "disposition": safety_format.string_format(fields[11].text, r),
            "date_of_supplement": safety_format.date_format(fields[12].text, r),
            "supplement_disposition": safety_format.string_format(fields[13].text, r),
            "date_of_supplement_2": safety_format.date_format(fields[14].text, r),
            "supplement_disposition_2": safety_format.string_format(fields[15].text, r)   
        }

        records.append(record)

        c += 1
        print(c)

    driver.close()
    driver.quit()

    return records