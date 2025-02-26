from tqdm import tqdm
import json


def scrape(latest, r):
    records = []

    file = open("scripts/salary/AUSalary.txt", "r")
    lines = file.readlines()[2:]
    file.close()

    for line in lines:
        spl = line.split(" ")
        posn = spl[0]
        name_dept_title_salary = line.replace(posn, "").strip()
        salary = name_dept_title_salary.split(" ")[-1]
        name_dept_title = name_dept_title_salary.replace(salary, "").strip()
        name = name_dept_title[0:46].strip()
        dept = name_dept_title[46 : 46 + 31].strip()
        title = name_dept_title[46 + 31 :].strip()

        records.append(
            {
                "posn": posn,
                "name": name,
                "salary": float(salary.replace("$", "").replace(",", "").strip()),
                "department": dept,
                "title": title,
            }
        )

    return records
