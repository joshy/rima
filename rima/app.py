import json
import logging
import os
from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, request
from flask_assets import Bundle, Environment
from redis import Redis
from requests import post
from rq import Queue

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


@app.route("/")
def main():
    queue = Queue("copd", connection=Redis())
    jobs = [x.id for x in queue.get_jobs()]
    return render_template("index.html", jobs=jobs, version=version)


@app.route("/receive", methods=["POST"])
def transfer():
    """ Receive jobs and process them """
    data = request.get_json(force=True)
    headers = {"content-type": "application/json"}
    response = post(MOVA_DOWNLOAD_URL, json=data, headers=headers)
    return jsonify({"status": "success"})


@app.route("/analyze")
def analyze():
    
    return jsonify({"status":"ok"})