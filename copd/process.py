import logging
import numpy as np

from copd.segmentation_watershed import segment
from copd.loader import load_exam


def analyze(exam_path):
    patient, imgs = load_exam(exam_path)

    logging.info("Finished loading image on folder: {}".format(exam_path))
    masked_lung, _ = segment(imgs)

    MAX_HU_LUNG = -380
    MIN_HU_LUNG = -1500
    lung_voxels = sum(
        [
            np.count_nonzero(i * ((i >= MIN_HU_LUNG) & (i <= MAX_HU_LUNG)))
            for i in masked_lung
        ]
    )
    logging.info("Lung voxel count is: {}".format(lung_voxels))

    x, y, z = (
        patient[0].PixelSpacing[0],
        patient[0].PixelSpacing[1],
        patient[0].SliceThickness,
    )
    voxel_volume = x * y * z
    logging.info("Voxel volume is {}".format(voxel_volume))

    lung_volume = lung_voxels * voxel_volume
    volume = round(lung_volume / 1000.0) / 1000.0
    logging.info("Lung volume is {}L".format(volume))

    stacked = np.stack(
        [i * ((i >= MIN_HU_LUNG) & (i <= MAX_HU_LUNG)) for i in masked_lung]
    )
    hu_values = stacked.ravel()[np.flatnonzero(stacked)]

    percentile = 15
    rank = int(len(hu_values) * percentile / 100)

    pd15 = int(hu_values[rank])

    result = {}
    result["pd15"] = pd15
    LAAS = [-950, -900, -850]
    for i in LAAS:
        count = len(hu_values[hu_values <= i])
        logging.info(str(i), "{:,}".format(count).replace(",", "'"), count * voxel_volume)
        key = "LAA" + str(i)
        result[key] = count * voxel_volume

    return result
