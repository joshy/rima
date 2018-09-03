import luigi
import json

from copd.process import analyze

class COPD(luigi.Task):
    data = luigi.DictParameter()
    key = luigi.Parameter()

    def run(self):
        result = analyze(self.data['images_dir'])
        to_save = self.data.get_wrapped().copy()
        to_save['copd'] = result
        with self.output().open('w') as outfile:
            json.dump(to_save, outfile)

    def output(self):
        return luigi.LocalTarget('work/results/%s.json' % self.key)
