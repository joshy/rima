import glob
import json


def key(entry):
    pid = entry["patient_id"]
    accession_nr = entry["accession_number"]
    series_nr = entry["series_number"]
    return pid + "_" + accession_nr + "_" + series_nr


def work_items(work_dir):
    result_files = glob.glob(work_dir + "/*.json")
    result = []
    for f in result_files:
        with open(f, "r") as f:
            entry = json.load(f)
            result.append(entry)
    return result
