from pathlib import Path

import imageio
import pydicom

import numpy as np
from skimage.transform import resize


def _convert(arr, crop=True):
    y, x = arr.shape

    if crop:
        startx = x // 2 - (512 // 2)
        starty = y // 2 - (1024 // 2)
        arr = arr[starty : starty + 1024, startx : startx + 512]

    # Rescaling grey scale between 0-255
    image_2d_scaled = (np.maximum(arr, 0) / arr.max()) * 255.0

    # Convert to uint
    image_2d_scaled = np.uint8(image_2d_scaled)
    return image_2d_scaled


def convert_dicom(file, output_dir):
    ds = pydicom.dcmread(str(file))
    img = _convert(np.copy(ds.pixel_array), crop=False)
    img_cropped = _convert(np.copy(ds.pixel_array), crop=True)
    img_cropped_resized = resize(img_cropped, (224, 224))
    output_full_dir = Path(output_dir, file.name + file.suffix).with_suffix(".png")

    c = "Cropped_" + file.name + file.suffix
    output_cropped_dir = Path(output_dir, c).with_suffix(".png")

    rc = "Resized_Cropped_" + file.name + file.suffix
    output_resized_cropped_dir = Path(output_dir, rc).with_suffix(".png")

    imageio.imwrite(output_full_dir, img)
    imageio.imwrite(output_cropped_dir, img_cropped)
    imageio.imwrite(output_resized_cropped_dir, img_cropped_resized)

    return output_full_dir, output_cropped_dir, output_resized_cropped_dir
