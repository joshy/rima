import datetime
import time

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset


def write_dicom(
    pixel_array,  # type: np.ndarray
    filename,
    idx=None,
    wsd_header=False,
    mode="uint16",
    **kwargs
):
    """
    Create a dicom from a 2d numpy array
    :param pixel_array: 2D numpy ndarray.  If pixel_array is larger than 2D, errors.
    :param filename: string name for the output file.
    :param idx: index to use for the file (a random one is generate if it is not given), should be the same for all images in a stack
    :param wsd_header: use the WSD header (for some synthetic images it is better)
    :param mode: the output image type
    :param kwargs: DICOM tags and values to add
    :return: dicom.Dataset object
    """
    if idx is None:
        idx = np.random.choice(range(100000))
    ## This code block was taken from the output of a MATLAB secondary
    ## capture.  I do not know what the long dotted UIDs mean, but
    ## this code works.
    if wsd_header:
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = "Secondary Capture Image Storage"
        file_meta.MediaStorageSOPInstanceUID = (
            "1.3.6.1.4.1.9590.100.1.1.111165684411017669021768385720736873780"
        )
        file_meta.ImplementationClassUID = "1.3.6.1.4.1.9590.100.1.0.100.4.%d" % (idx)
    else:
        # Populate required values for file meta information
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = (
            "1.2.840.10008.5.1.4.1.1.2"
        )  # CT Image Storage
        file_meta.MediaStorageSOPInstanceUID = (
            "1.2.3"
        )  # !! Need valid UID here for real work
        file_meta.ImplementationClassUID = "1.2.3.4"  # !!! Need valid UIDs here

    file_meta.TransferSyntaxUID = "1.2.840.10008.1.2"
    ds = FileDataset(filename, {}, file_meta=file_meta, preamble=b"\0" * 128)
    # ds.Modality = 'WSD'
    ds.ContentDate = str(datetime.date.today()).replace("-", "")
    ds.ContentTime = str(time.time())  # milliseconds since the epoch

    ds.StudyInstanceUID = "1.3.6.1.4.1.9590.100.1.1.%039d" % (idx + 1)
    ds.SeriesInstanceUID = "1.3.6.1.4.1.9590.100.1.1.%039d" % (idx + 2)
    ds.SOPInstanceUID = "1.3.6.1.4.1.9590.100.1.1.%039d" % (idx + 3)
    if wsd_header:
        ds.SOPClassUID = "Secondary Capture Image Storage"

    ds.SecondaryCaptureDeviceManufctur = "LungStage 0.1"

    ## These are the necessary imaging components of the FileDataset object.
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"

    if mode == "uint16":
        ds.PixelRepresentation = 0
        ds.HighBit = 15
        ds.BitsStored = 16
        ds.BitsAllocated = 16

        if pixel_array.dtype != np.uint16:
            im_range = pixel_array.max() - pixel_array.min()
            max_uint_val = np.iinfo(np.uint16).max
            offset = pixel_array.min()
            slope = max_uint_val / im_range
            if slope < 100:
                slope = 1
            ds.RescaleSlope = 1 / slope
            ds.RescaleIntercept = offset

            pixel_array = (
                ((pixel_array - offset) * slope).clip(0, 65535).astype(np.uint16)
            )

    elif mode == "float32":
        raise NotImplementedError(
            "Float32 is not officially supported yet and so has very bad results"
        )
        ds.PixelRepresentation = 0
        ds.BitsStored = 32
        ds.BitsAllocated = 32
        if pixel_array.dtype != np.float32:
            pixel_array = pixel_array.astype(np.float32)
    else:
        raise NotImplementedError(
            "The mode {} has not been implemented only uint16 and float32".format(mode)
        )

    ds.Columns = pixel_array.shape[1]
    ds.Rows = pixel_array.shape[0]

    # add the tags from the keyword argumnets
    for k_arg, v_arg in kwargs.items():
        ds.__setattr__(k_arg, v_arg)

    ds.PixelData = pixel_array.tostring()
    ds.save_as(filename)

    return ds
