import argparse
import os

import nibabel as nib
import numpy as np

from copd.loader import load_exam
from copd.segmentation_watershed import segment


def run():
    # call example
    # python rename.py --dir /data/example-dir
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--dir", help="Starting directory")
    parser.add_argument("-o","--output", help="Output directory")

    args = parser.parse_args()

    if not (args.dir and args.output):
        print("--dir or --output parameter missing, exiting")
        exit(1)

    patient, imgs = load_exam(args.dir)
    segmentation = segment(imgs)
    stacked = np.stack(segmentation, axis=-1)
    nifti_image = nib.Nifti2Image(stacked, affine=np.eye(4))
    nib.save(nifti_image, os.path.join(args.output, "lung_mask.nii.gz"))
    exit(0)

run()
