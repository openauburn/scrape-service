from selenium import webdriver
from selenium.webdriver.common.by import By
import util.geocode as geocode
import util.safety_format as safety_format
from util.report import Report
from tqdm import tqdm
import time


r = Report()


def scrape(latest, r):
    records = []

    url = "https://www.auburn.edu/administration/facilities/webapps/buildings/index.php"

    driver = webdriver.Chrome()

    driver.get(url)

    # All relevant rows
    table = driver.find_elements(By.TAG_NAME, "tbody")[1]
    rows = table.find_elements(By.TAG_NAME, "tr")[1:]

    codes = []
    names = []
    departmentNames = []

    # Grabbing codes and shorthand names from table
    for row in rows:
        codes.append(
            safety_format.string_format(
                row.find_elements(By.TAG_NAME, "td")[1:][2].text, r
            ),
        )
        names.append(
            safety_format.string_format(
                row.find_elements(By.TAG_NAME, "td")[1:][0].text, r
            ),
        )

    baseUrl = "https://www.auburn.edu/administration/facilities/webapps/buildings/profile.php?bldg="

    for n in tqdm(range(len(codes))):
        name = names[n]
        code = codes[n]

        # Using building code to retrieve individual page
        facilityUrl = baseUrl + code
        driver.get(facilityUrl)

        # Extracting official name and description
        info = driver.find_elements(By.CLASS_NAME, "row")[-2]
        text = info.find_element(By.CLASS_NAME, "col-sm-9").text
        textSplit = text.split("About:")
        officialName = safety_format.string_format(
            textSplit[0].split("Official Name:")[1], r
        )
        description = safety_format.string_format(textSplit[-1], r)

        # Building statistics / additional information
        stats = info.find_element(By.CLASS_NAME, "col-sm-3")
        statsSplit = stats.text.split("\n\n")

        location, yearBuilt, primaryUse, sqft = None, None, None, None

        for n in range(len(statsSplit)):
            stat = statsSplit[n]
            statSplit = stat.split("\n")

            if len(statSplit) <= 1:  # Empty stat row
                continue

            if "Address" in statSplit[0]:
                location = (
                    safety_format.string_format(statSplit[1], r)
                    + " "
                    + safety_format.string_format(statSplit[2], r)
                )
            elif "Year Built" in statSplit[0]:
                yearBuilt = safety_format.integer_format(statSplit[1], r)
            elif "Primary Use" in statSplit[0]:
                primaryUse = safety_format.string_format(statSplit[1], r)
            elif "Size" in statSplit[0]:
                sqft = safety_format.integer_format(
                    statSplit[1].replace("Gross Sq. Ft.", ""), r
                )

        # Requesting department information page
        departmentURL = facilityUrl.replace("profile", "depts")
        driver.get(departmentURL)
        time.sleep(2)

        # Extracting rows of department information
        table = (
            driver.find_elements(By.CLASS_NAME, "row")[1]
            .find_element(By.CLASS_NAME, "col-sm-6")
            .find_element(By.CLASS_NAME, "objbox")
            .find_element(By.TAG_NAME, "tbody")
        )
        rows = table.find_elements(By.TAG_NAME, "tr")
        rows = rows[1:]

        deptNames, deptURLs = [], []
        for row in rows:
            deptNames.append(safety_format.string_format(row.text, r))
            if len(row.find_elements(By.TAG_NAME, "a")) > 0:
                deptURLs.append(
                    row.find_element(By.TAG_NAME, "a").get_attribute("href")
                )
            else:
                deptURLs.append(None)

        address, latitude, longitude = geocode.get_lat_long(location, r)

        record = {
            "code": code,
            "name": name,
            "official_name": officialName,
            "primary_use": primaryUse,
            "description": description,
            "website_url": facilityUrl,
            "departments": None
            if len(deptNames) == 0
            else deptNames,  # list of strings
            "department_urls": None
            if len(deptURLs) == 0
            else deptURLs,  # list of strings
            "year_built": yearBuilt,  # int
            "square_feet": sqft,  # int
            "address": location,
            "latitude": str(latitude),  # text
            "longitude": str(longitude),  # text
        }

        # Creating department object for table insertion if not already inserted
        departments = []
        n = 0
        for deptName in deptNames:
            if deptName not in departmentNames:
                departments.append(
                    {
                        "name": deptName,
                        "website_url": deptURLs[n],
                    }
                )

            n += 1

        records.append(record)

    driver.close()
    driver.quit()

    return records
