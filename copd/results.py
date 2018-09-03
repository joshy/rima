import glob
import json

def results(work_dir):
    result_files = glob.glob(work_dir + "/*.json")
    result = []
    for f in result_files:
        with open(f, "r") as f:
                entry = json.load(f)
                result.append(entry)
    return result