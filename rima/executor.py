import json
import os

from copd.process import analyze
from rima.work import key


def copd(work):
    print("Running analyze on folder: {}".format(work))
    result = analyze(work)
    print("Finished analyze on folder: {}".format(work))
    return result


def process(image_base_dir, workjson):
    dir = workjson["dir"]
    type = workjson["queue"]
    items = []
    for entry in workjson["data"]:
        pid = entry["patient_id"]
        accession_nr = entry["accession_number"]
        series_nr = entry["series_number"]
        entry["images_dir"] = os.path.join(
            image_base_dir, dir, pid, accession_nr, series_nr
        )
        entry["key"] = key(entry)
        entry["type"] = type
        items.append(entry)
    return items
