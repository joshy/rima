import json
import logging
import os
from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, request
from flask_assets import Bundle, Environment
from redis import Redis
from requests import post
from rq import Queue

from copd.results import results
from rima.executor import copd, enrich_workpaths

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.cfg", silent=True)

MOVA_DASHBOARD_URL = app.config["MOVA_DASHBOARD_URL"]
MOVA_DOWNLOAD_URL = app.config["MOVA_DOWNLOAD_URL"]
MOVA_TRANSFER_URL = app.config["MOVA_TRANSFER_URL"]

IMAGE_FOLDER = app.config["IMAGE_FOLDER"]

version = app.config["VERSION"] = "0.0.1"

assets = Environment(app)
js = Bundle(
    "js/jquery-3.3.1.min.js", "js/script.js", filters="jsmin", output="gen/packed.js"
)
assets.register("js_all", js)


WORK_INBOX_DIR = "work/inbox"
WORK_RESULTS_DIR = "work/results"

@app.route("/")
def main():
    queue = Queue("copd", connection=Redis())
    jobs = [x.id for x in queue.get_jobs()]
    copd_results = results(WORK_RESULTS_DIR)
    return render_template("index.html", jobs=jobs, results=copd_results, version=version)


@app.route("/receive", methods=["POST"])
def transfer():
    """ Receive jobs and process them """
    data = request.get_json(force=True)
    id = data.get("id")
    data = enrich_workpaths(IMAGE_FOLDER, data)
    with open(os.path.join(WORK_INBOX_DIR, (str(id) + ".json")), "w") as workfile:
        json.dump(data, workfile)
    headers = {"content-type": "application/json"}
    response = post(MOVA_DOWNLOAD_URL, json=data, headers=headers)
    return jsonify({"status": "success"})


@app.route("/analyze")
def analyze():
    worklist = list(WORK_INBOX_DIR)
    print("Number of exams to process: {}".format(len(worklist)))
    for w in worklist:
        copd(os.path.join(IMAGE_FOLDER, w))
    return jsonify({"status": "ok"})
