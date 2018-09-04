from redis import Redis
from rq import Queue, job
import os
import luigi
import json
import glob

from copd.task import COPD
from rima.work import key

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
        for j in jobs:
            job_id = str(j["job_id"])
            download_job = queue.fetch_job(job_id)
            if download_job.get_status() == job.JobStatus.FINISHED:
                print("Download task with id {} finised, starting COPD processing".format(job_id))
                yield COPD(j, key(j))
            else:
                print("Job with id {} is still in queue".format(job_id))


if __name__ == "__main__":
    luigi.run()

