import logging
import timeit

import numpy as np
from skimage import measure, morphology
from sklearn.cluster import KMeans


def _make_lungmask(img):
    # taken from https://www.raddq.com/dicom-processing-segmentation-visualization-in-python/
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


def segment(imgs):
    masked_lung = []
    logging.info("Start lung segmentation")
    start = timeit.default_timer()
    for img in imgs:
        masked_lung.append(_make_lungmask(img))
    stop = timeit.default_timer()
    logging.info("Finished lung segmentation, took {}s".format(stop - start))
    return masked_lung