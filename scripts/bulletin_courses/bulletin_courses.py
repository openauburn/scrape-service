from selenium import webdriver
from selenium.webdriver.common.by import By
import util.safety_format as safety_format
from tqdm import tqdm
import json


def scrape(latest, r):
    records = []

    url = "https://bulletin.auburn.edu/coursesofinstruction/"

    driver = webdriver.Chrome()
    driver.get(url)

    # All relevant tables
    table = driver.find_elements(By.TAG_NAME, "tbody")[0]

    links = table.find_elements(By.TAG_NAME, "a")

    subjectLinks = []

    for link in links:
        subjectLinks.append(link.get_attribute("href"))

    for subjectLink_i in tqdm(range(len(subjectLinks))):
        subjectLink = subjectLinks[subjectLink_i]
        driver.get(subjectLink)

        titleSplit = driver.find_element(By.CLASS_NAME, "page-title").text.split("-")
        subject = safety_format.string_format(titleSplit[0], r)
        subjectCode = safety_format.string_format(titleSplit[1], r)

        courses = driver.find_elements(By.CLASS_NAME, "courseblock")

        for course in courses:
            bold_title = course.find_elements(By.TAG_NAME, "strong")[0]
            code = " ".join(bold_title.text.strip().split(" ")[:2]).strip()
            course_code, course_number = code.split(" ")
            title_w_cred = " ".join(bold_title.text.strip().split(" ")[2:]).strip()
            title_w_cred_split = title_w_cred.split("(")
            title = title_w_cred_split[0].strip()
            cred = None
            if len(title_w_cred_split) > 1:
                cred = str(title_w_cred_split[1].replace(")", "").strip())

            description = course.text.replace(bold_title.text, "").strip()

            records.append(
                {
                    "subject": subject,
                    "subject_code": subjectCode,
                    "course": title,
                    "course_number": course_number.strip(),
                    "credits": cred,
                    "description": description,
                }
            )

    driver.close()
    driver.quit()

    return records
