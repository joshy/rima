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


def load_result(work_dir, key):
    result_file = glob.glob(work_dir + "/{}.json".format(key))
    if result_file:
        with open(result_file[0], "r") as r:
            data = json.load(r)
        return data
    return None
