import json
import os

from copd.process import analyze


def copd(work):
    print("Running analyze on folder: {}".format(work))
    result = analyze(work)
    print("Finished analyze on folder: {}".format(work))
    return result


def enrich_workpaths(image_base_dir, workjson):
    dir = workjson["dir"]

    for entry in workjson["data"]:
        pid = entry["patient_id"]
        accession_nr = entry["accession_number"]
        series_nr = entry["series_number"]
        entry["images_dir"] = os.path.join(
            image_base_dir, dir, pid, accession_nr, series_nr
        )
    return workjson
