import json

from pathlib import Path

import luigi

from wrist_fracture.convert import convert_dicom
from wrist_fracture.inference import infer


class WristFracture(luigi.Task):
    data = luigi.DictParameter()
    key = luigi.Parameter()

    def run(self):
        files = [x for x in Path(self.data["images_dir"]).glob("**/*") if x.is_file()]
        for f in files:
            print(f"\nProcessing file: {f}\n")
            image, cropped, resized = convert_dicom(f, self.workdir())
            result = infer(image, resized, self.data)
        with self.output().open("w") as outfile:
            json.dump(result, outfile)

    def output(self):
        return luigi.LocalTarget("work/results/%s.json" % self.key)

    def workdir(self):
        work_dir = (
            f"work/results/{self.data['patient_id']}/{self.data['accession_number']}"
        )
        Path(work_dir).mkdir(parents=True, exist_ok=True)
        return work_dir
