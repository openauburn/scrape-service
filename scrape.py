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
    for arg in args:
        arg = arg.strip()
        if arg.lower().endswith("-all"):
            scripts.append({'script': arg[:-4], 'is_all': True})
        else:
            scripts.append({'script': arg, 'is_all': False})

    for script_obj in scripts:
        script_name = script_obj['script']
        is_all = script_obj['is_all']

        latest = None
        r = Report()

        script_func = importlib.import_module("scripts." + script_name + "." + script_name)
        scrape_results = script_func.scrape(latest, r)
        data_access.publish_data(script_name, scrape_results, r)
        
        with open('report_{}.json'.format(script_name + str(datetime.now())), 'w', encoding='utf-8') as f:
            json.dump(r.errors, f, ensure_ascii=False, indent=4)

        with open('data_{}.json'.format(script_name + str(datetime.now())), 'w', encoding='utf-8') as f:
            json.dump(scrape_results, f, ensure_ascii=False, indent=4)

    
    return 0

if __name__ == "__main__":
    main()