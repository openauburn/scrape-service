from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import time
from tqdm import tqdm
import subprocess


def parse_profile(page, link):
    try:
        header = page.find_element(By.TAG_NAME, "h1")
        title = header.find_element(By.TAG_NAME, "span").text.strip()
        name = header.text.replace(title, "").strip()

        department = " / ".join(
            [
                n.text.replace("/", "").strip()
                for n in page.find_element(
                    By.CLASS_NAME, "pds-primary-affiliation"
                ).find_elements(By.TAG_NAME, "span")
            ][::-1]
        )

        profile_overview = page.find_element(By.CLASS_NAME, "profile-overview")
        sec_titles, sec_contents = (
            profile_overview.find_elements(By.CLASS_NAME, "section-title"),
            profile_overview.find_elements(By.CLASS_NAME, "section-content"),
        )

        orcid, wos, degrees, publication_total, grant_total, patent_total = (
            None,
            None,
            None,
            None,
            None,
            None,
        )

        for i in range(len(sec_titles)):
            sec_title = sec_titles[i]
            sec_content = sec_contents[i]
            match sec_title.text.strip().lower():
                case "orcid":
                    orcid = (
                        sec_content.find_elements(By.TAG_NAME, "a")[1]
                        .get_attribute("href")
                        .strip()
                    )
                case "wos researcherid":
                    wos = (
                        sec_content.find_element(By.TAG_NAME, "a")
                        .get_attribute("href")
                        .strip()
                    )
                case "degrees":
                    degrees = [
                        text.strip()
                        for text in sec_content.get_attribute("innerHTML").split("<br>")
                    ]
                case _:
                    continue

        nav_sections = [
            li.find_elements(By.TAG_NAME, "span")[-1]
            for li in page.find_element(By.CLASS_NAME, "sidebar-content").find_elements(
                By.TAG_NAME, "li"
            )[1:]
        ]

        for nav_section in nav_sections:
            nav_text = nav_section.text.strip().lower()
            if "publications" in nav_text:
                publication_total = int(
                    nav_text.replace("publications (", "").replace(")", "")
                )
            elif "grants" in nav_text:
                grant_total = int(nav_text.replace("grants (", "").replace(")", ""))
            elif "patents" in nav_text:
                patent_total = int(nav_text.replace("patents (", "").replace(")", ""))

        return {
            "name": name,
            "title": title,
            "department": department,
            "orcid": orcid,
            "wos": wos,
            "degrees": degrees,
            "publication_total": publication_total,
            "grant_total": grant_total,
            "patent_total": patent_total,
            "proquest_url": link,
        }
    except Exception as e:
        print(e.with_traceback)
        return None


def scrape(latest, r):
    records = []
    scholar_list_base_url = "https://scholars.proquest.com/gallery/auburn/results?dept=82BFAFEDC0A8000601493AB6237E1F7F"

    driver = webdriver.Chrome()
    driver.get(scholar_list_base_url)

    while "Retry later" in driver.find_element(By.TAG_NAME, "body").text:
        try:
            # Disconnect from Mullvad
            subprocess.run(["mullvad", "disconnect"], check=True)
            print("Disconnected from Mullvad.")

            # Wait a few seconds before reconnecting
            time.sleep(10)

            # Reconnect to Mullvad
            subprocess.run(["mullvad", "connect"], check=True)
            print("Reconnected to Mullvad.")

            time.sleep(10)

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

        driver.get(scholar_list_base_url)

    results = driver.find_element(By.ID, "results_main_header")
    page_desc = results.find_element(By.CLASS_NAME, "small").text
    num_pages = int(page_desc.replace("(Page 1 of ", "").replace(")", ""))

    links = []

    for page_num in range(num_pages):
        driver.get(scholar_list_base_url + f"&page={page_num + 1}")

        pds_links = driver.find_elements(By.CLASS_NAME, "pds-name-link")
        links += [pds_link.get_attribute("href").strip() for pds_link in pds_links]

    for link_i in tqdm(range(len(links))):
        link = links[link_i]
        record = None
        while record is None:
            driver.get(link)
            record = parse_profile(driver, link)
            if record is None:
                subprocess.run(["mullvad", "disconnect"], check=True)
                print("Disconnected from Mullvad.")

                # Wait a few seconds before reconnecting
                time.sleep(5)

                # Reconnect to Mullvad
                subprocess.run(["mullvad", "connect"], check=True)
                print("Reconnected to Mullvad.")

                time.sleep(5)

        records.append(record)

        # while "Retry later" in driver.find_element(By.TAG_NAME, "body").text:
        #     try:
        #         # Disconnect from Mullvad
        #         subprocess.run(["mullvad", "disconnect"], check=True)
        #         print("Disconnected from Mullvad.")

        #         # Wait a few seconds before reconnecting
        #         time.sleep(10)

        #         # Reconnect to Mullvad
        #         subprocess.run(["mullvad", "connect"], check=True)
        #         print("Reconnected to Mullvad.")

        #         time.sleep(10)

        #         driver.close()
        #         driver.quit()
        #         driver = webdriver.Chrome()
        #         driver.get(link)

        #     except subprocess.CalledProcessError as e:
        #         print(f"Error: {e}")

    with open("fac.json", "w") as f:
        json.dump(records, f)

    driver.close()
    driver.quit()

    return records
