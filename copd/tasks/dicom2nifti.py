import json
import os

import dicom2nifti
import luigi


class D2N(luigi.Task):
    data = luigi.DictParameter()
    key = luigi.Parameter()

    def run(self):
        accession_number = self.data["accession_number"]
        patient_id = self.data["patient_id"]
        accession_dir = "work/results/{}/{}".format(patient_id, accession_number)
        if not os.path.exists(accession_dir):
            os.makedirs(accession_dir)
        dicom2nifti.convert_directory(self.data["images_dir"], accession_dir)
        with self.output().open("w") as outfile:
            outfile.write("Converted to nifti")


    def output(self):
        return luigi.LocalTarget("work/results/%s/%s/dicom2nifti.txt" % (self.data["patient_id"], self.data["accession_number"]))
