import logging
import os

import nibabel as nib
import numpy as np
import pydicom


def load_nifti(file_path):
    images = nib.load(file_path)
    return None, images

def load_exam(dir_path):
    patient = _load_scan(dir_path)
    images = _get_pixels_hu(patient)
    return patient, images


def _load_scan(path):
    slices = [pydicom.dcmread(path + "/" + s) for s in os.listdir(path)]
    slices.sort(key=lambda x: int(x.InstanceNumber))
    if not slices:
        raise ValueError("DICOM folder {} seems to be empty, aborting".format(path))

    try:
        slice_thickness = np.abs(
            slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2]
        )
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices


def _get_pixels_hu(scans):
    if not scans:
        return None
    image = np.stack([s.pixel_array for s in scans])
    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 1
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0

    # Convert to Hounsfield units (HU)
    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope

    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)

    image += np.int16(intercept)

    return np.array(image, dtype=np.int16)
