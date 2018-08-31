from redis import Redis
from rq import Queue
import os
import luigi
import json
import glob

from copd.process import COPD

queue = Queue("copd", connection=Redis())


def read_work():
    work_files = glob.glob("work/inbox/*.json")
    result = []
    for w in work_files:
        with open(w, "r") as data_file:
            entry = json.load(data_file)
            result.append(entry)
    return result


class COPDWatcher(luigi.Task):
    def run(self):
        jobs = read_work()
        for job in jobs:
            job_id = str(job['id'])

            download_job = queue.fetch_job(job_id)
            if download_job is None:
                print("Job with id {} not anymore in queue".format(job_id))
                for entry in job['data']:
                    d = yield COPD(entry)
                    print(d)
            else:
                print("Job with id {} is still in queue".format(job_id))


if __name__ == "__main__":
    luigi.run()

