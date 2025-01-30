import os
import sys
import importlib
import subprocess
import data_access
from util.report import Report

from datetime import datetime

import json


def main():
    args = sys.argv[1:]
    scripts = []
    if "".join(args).lower() == "ls":
        ls()
    else:
        for i, arg in enumerate(args):
            arg = arg.strip()
            if i < len(args) - 1 and args[i + 1].lower().endswith("-all"):
                scripts.append({"script": arg, "is_all": True})
            elif not arg.lower().endswith("-all"):
                scripts.append({"script": arg, "is_all": False})
        print(scripts)
        for script_obj in scripts:
            script_name = script_obj["script"]
            is_all = script_obj["is_all"]

            latest = None
            r = Report()

            script_func = importlib.import_module(
                "scripts." + script_name + "." + script_name
            )
            scrape_results = script_func.scrape(latest, r)
            data_access.publish_data(script_name, scrape_results, r)

            with open(
                ".log/report_{}.json".format(script_name + str(datetime.now())),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(r.errors, f, ensure_ascii=False, indent=4)

            with open(
                ".log/data_{}.json".format(script_name + str(datetime.now())),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(scrape_results, f, ensure_ascii=False, indent=4)

        return 0


def ls():
    print("Displaying available dataset scrapers:")
    for path, folders, files in os.walk("scripts"):
        for folder in folders:
            if "__" not in folder:
                print(folder)


if __name__ == "__main__":
    main()
