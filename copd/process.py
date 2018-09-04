
import logging
import timeit

import numpy as np
from skimage import measure, morphology
from skimage.transform import resize
from sklearn.cluster import KMeans

from copd.loader import load_exam


def make_lungmask(img):
    row_size = img.shape[0]
    col_size = img.shape[1]
    orig_img = img.copy()
    mean = np.mean(img)
    std = np.std(img)
    img = img - mean
    img = img / std
    # Find the average pixel value near the lungs
    # to renormalize washed out images
    middle = img[
        int(col_size / 5) : int(col_size / 5 * 4),
        int(row_size / 5) : int(row_size / 5 * 4),
    ]
    mean = np.mean(middle)
    max = np.max(img)
    min = np.min(img)
    # To improve threshold finding, I'm moving the
    # underflow and overflow on the pixel spectrum
    img[img == max] = mean
    img[img == min] = mean
    #
    # Using Kmeans to separate foreground (soft tissue / bone) and background (lung/air)
    #
    kmeans = KMeans(n_clusters=2).fit(np.reshape(middle, [np.prod(middle.shape), 1]))
    centers = sorted(kmeans.cluster_centers_.flatten())
    threshold = np.mean(centers)
    thresh_img = np.where(img < threshold, 1.0, 0.0)  # threshold the image

    # First erode away the finer elements, then dilate to include some of the pixels surrounding the lung.
    # We don't want to accidentally clip the lung.

    eroded = morphology.erosion(thresh_img, np.ones([3, 3]))
    dilation = morphology.dilation(eroded, np.ones([8, 8]))

    labels = measure.label(
        dilation
    )  # Different labels are displayed in different colors
    label_vals = np.unique(labels)
    regions = measure.regionprops(labels)
    good_labels = []
    for prop in regions:
        B = prop.bbox
        if (
            B[2] - B[0] < row_size / 10 * 9
            and B[3] - B[1] < col_size / 10 * 9
            and B[0] > row_size / 5
            and B[2] < col_size / 5 * 4
        ):
            good_labels.append(prop.label)
    mask = np.ndarray([row_size, col_size], dtype=np.int8)
    mask[:] = 0

    #
    #  After just the lungs are left, we do another large dilation
    #  in order to fill in and out the lung mask
    #
    for N in good_labels:
        mask = mask + np.where(labels == N, 1, 0)
    mask = morphology.dilation(mask, np.ones([1, 1]))  # one last dilation

    # change to original implementation,
    # we want hu field values back in the returned images
    return mask * orig_img


def analyze(exam_path):
    patient, imgs = load_exam(exam_path)

    logging.info("Finised loading image on folder: {}".format(exam_path))
    masked_lung = []

    logging.info("Start lung segmentation")
    start = timeit.default_timer()
    for img in imgs:
        masked_lung.append(make_lungmask(img))
    stop = timeit.default_timer()
    logging.info("Finised lung segmentation, took {}s".format(stop - start))

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
