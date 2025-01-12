import requests
from datetime import datetime
import os
from urllib.parse import urljoin

STEP = 100
da_url = os.environ.get("DATA_ACCESS_URL")
token = os.environ.get("OA_TOKEN")


def publish(endpoint, body):
    return requests.post(
        urljoin(da_url, endpoint), json=body, headers={"OA-Token": token.strip()}
    )


def publish_data(dataset, data, r):
    for i in range(0, len(data), STEP):
        to_push = data[i : i + STEP]
        resp = publish(f"/datasets/{dataset}", to_push)
        if resp.status_code != 200:
            r.errors.append(
                {
                    "message": f"publishing: {resp.status_code}",
                    "message_ext": f"publishing: {resp.json()}",
                }
            )
    return


def report(dataset, errors):
    errors_out = [
        {
            "url": da_url + f"/datasets/{dataset}",
            "occurred_at": e["datetime"],
            "message": f"scrape_service: {e['message']}",
            "message_ext": f"scrape_service: {e['message_ext']}",
        }
        for e in errors
    ]
    for i in range(0, len(errors_out), STEP):
        to_push = errors_out[i : i + STEP]
        publish("/errors", to_push)


def get_latest_datum(dataset):
    resp = requests.get(urljoin(da_url, f"datasets/{dataset}?sort=_id,desc&_incognito"))
    return resp.json()["data"][0]


def log_scrape_job(
    dataset, started_at, ended_at, data_count, data_errors, total_errors
):
    resp = publish(
        "/scrape_jobs",
        [
            {
                "dataset": dataset,
                "started_at": started_at,
                "ended_at": ended_at,
                "data_count": data_errors,
                "total_errors": total_errors,
            }
        ],
    )
