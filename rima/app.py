import json
import logging
import os
from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, request, send_file
from flask_assets import Bundle, Environment
from redis import Redis
from requests import post
from rq import Queue

from copd.results import results, load_result
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


@app.route("/receive", methods=["POST"])
def transfer():
    """ Receive jobs and process them """
    data = request.get_json(force=True)
    items = process(IMAGE_FOLDER, data)
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
    images_dir = result["images_dir"]
    images = os.listdir(result["images_dir"])
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
    print(filename, "\n")
    return send_file(filename, mimetype='application/dicom')
