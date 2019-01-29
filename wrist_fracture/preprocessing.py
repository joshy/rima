import os
import pydicom


def center_crop(ds):
    arr = ds.pixel_array
    y, x = arr.shape
    startx = x//2-(512//2)
    starty = y//2-(1024//2)
    arr = arr[starty:starty+1024,startx:startx+512]


    # Rescaling grey scale between 0-255
    image_2d_scaled = (np.maximum(arr,0) / arr.max()) * 255.0

    # Convert to uint
    image_2d_scaled = np.uint8(image_2d_scaled)
    return image_2d_scaled


def convert(path):
    files = os.listdir()


def read(file):
    ds = pydicom.dcmread(file)
    pixel_array = ds.pixel_array
    return ds, pixel_array


def files(path):
    return os.listdir()