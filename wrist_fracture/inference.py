import os

import requests


def infer(image, resized, data):
    print("\nSending image file", image)
    image_file = {"image": open(image, "rb")}
    image_resized_file = {"image": open(resized, "rb")}
    headers = {"Content-type": "multipart/form-data"}
    v = requests.post("http://localhost:5555/inference/wrist/view", files=image_file)
    v_result = {**data, **v.json()}
    del v_result["images_dir"]
    del v_result["job_id"]
    f = requests.post("http://localhost:5555/inference/wrist/fracture", files=image_resized_file, data=v_result)
    return f.json()


def load_image(image):
    image = load_img(image)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    return image
