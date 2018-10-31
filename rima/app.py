import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from flask_assets import Bundle, Environment
from redis import Redis
from requests import post
from rq import Queue

from copd.results import load_result, results
from rima.executor import copd, process
from rima.work import work_items

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.cfg", silent=True)

MOVA_DASHBOARD_URL = app.config["MOVA_DASHBOARD_URL"]
MOVA_DOWNLOAD_URL = app.config["MOVA_DOWNLOAD_URL"]
MOVA_TRANSFER_URL = app.config["MOVA_TRANSFER_URL"]

IMAGE_FOLDER = app.config["IMAGE_FOLDER"]

version = app.config["VERSION"] = "0.0.1"

assets = Environment(app)
js = Bundle("js/script.js", filters="jsmin", output="gen/packed.js")
assets.register("js_all", js)


WORK_INBOX_DIR = "work/inbox"
WORK_RESULTS_DIR = "work/results"


@app.template_filter("to_date")
def to_date(date_as_int):
    if date_as_int:
        return datetime.strptime(str(date_as_int), "%Y%m%d").strftime("%d.%m.%Y")
    else:
        return ""


@app.route("/")
def main():
    copd_results = results(WORK_RESULTS_DIR)
    items = work_items(WORK_INBOX_DIR)
    return render_template(
        "index.html", results=copd_results, work_items=items, version=version
    )


@app.route("/analyze", methods=["POST"])
def transfer():
    """ Receive jobs and process them """
    data = request.get_json(force=True)
    process(IMAGE_FOLDER, data)
    headers = {"content-type": "application/json"}
    response = post(MOVA_DOWNLOAD_URL, json=data, headers=headers)
    if response.status_code == 200:
        for job in response.json()["jobs"]:
            with open(
                os.path.join(WORK_INBOX_DIR, (job["key"] + ".json")), "w"
            ) as workfile:
                json.dump(job, workfile)

        return jsonify(response.json()["series_length"])
    else:
        return "Post failed", 500


@app.route("/copd/show")
def details():
    key = request.args.get("key", "")
    result = load_result(WORK_RESULTS_DIR, key)
    images = os.listdir(result["images_dir"])
    # otherwise the images will be in random order
    images.sort()
    prefix = (
        "wadouri:http://localhost:9123/images/"
        + result["patient_id"]
        + "/"
        + result["accession_number"]
        + "/"
        + result["series_number"]
        + "/"
    )
    image_paths = list(map(lambda x: prefix + x, images))
    return render_template(
        "copd_result.html", result=result, image_paths=json.dumps(image_paths), version=version
    )


@app.route("/images/<path:path>")
def images(path):
    filename = os.path.join(IMAGE_FOLDER, 'copd', path)
    return send_file(filename, mimetype='application/dicom')


@app.route("/p/i/<path:path>")
def i(path):
    f = os.path.join("/home/joshy/github/rima", path)
    return send_file(f, mimetype="appliaction/dicom")


@app.route("/p/show")
def p():
    key = request.args.get("key", "")
    result = load_result(WORK_RESULTS_DIR, key)

    p = Path("work/results") / result['patient_id'] / result["accession_number"]

    s = "i" / p / "source.nii.gz"
    m = "i" / p / "lung_mask.nii.gz"

    return render_template("papaya-index.html", source_image=s, mask_image=m, result=result)
