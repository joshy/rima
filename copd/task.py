import luigi
import json

from copd.process import analyze

class COPD(luigi.Task):
    data = luigi.DictParameter()
    key = ""

    def run(self):
        pid = self.data["patient_id"]
        accession_nr = self.data["accession_number"]
        series_nr = self.data["series_number"]
        self.key = pid + "_" + accession_nr + "_" + series_nr
        result = analyze(self.data['images_dir'])
        #for key, value in result.items():
        #    print(type(value))
        to_save = self.data.get_wrapped().copy()
        to_save['copd'] = result
        with self.output().open('w') as outfile:
            json.dump(to_save, outfile)

    def output(self):
        return luigi.LocalTarget('work/results/%s.json' % self.key)
