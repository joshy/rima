import glob
import json
import os

import luigi
import nibabel as nib
import numpy as np

from copd.process import load_exam, segment
from copd.tasks.dicom2nifti import D2N


class Lung(luigi.Task):
    data = luigi.DictParameter()
    key = luigi.Parameter()

    def requires(self):
        return D2N(self.data, self.key)

    def run(self):
        __, imgs = load_exam(self.data["images_dir"])
        masked_lung, mask = segment(imgs)

        nifti_mask = self.create_nifti(mask)
        nifti_masked_lung = self.create_nifti(masked_lung)

        work_dir = self.workdir()
        nib.save(nifti_mask, work_dir + '/lung_mask.nii.gz')
        nib.save(nifti_masked_lung, work_dir + "/masked_lung.nii.gz" )
        with self.output().open("w") as outfile:
            outfile.write("segmentation done")


    def output(self):
        return luigi.LocalTarget("work/results/%s/%s/segmentation.txt" % (self.data["patient_id"], self.data["accession_number"]))


    def workdir(self):
        work_dir = "work/results/%s/%s" % (self.data["patient_id"], self.data["accession_number"])
        return work_dir

    def create_nifti(self, mask):
        workdir = self.workdir()
        converted_dicom = nib.load(glob.glob(workdir + "/*.nii.gz")[0])

        stacked = np.stack(mask, -1).astype(np.uint16)
        stacked = stacked[:,:,::-1]
        stacked = np.swapaxes(stacked, 0, 1)
        stacked = stacked[:,::-1,:]
        return nib.Nifti1Image(stacked, header=converted_dicom.header, affine=converted_dicom.affine)
