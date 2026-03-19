import image_processor
import numpy as np
import requests
import os

def get_sample_image():
    url = "https://upload.wikimedia.org/wikipedia/en/7/7d/Lenna_%28test_image%29.png"
    response = requests.get(url)
    return response.content

def test_load_image():
    img_bytes = get_sample_image()
    img = image_processor.load_image_from_bytes(img_bytes)
    assert isinstance(img, np.ndarray)
    assert len(img.shape) == 3
    assert img.shape[2] == 3
    print("✅ Load image test passed")

def test_resize_image():
    img_bytes = get_sample_image()
    resized = image_processor.resize_image(img_bytes, 128, 128)
    assert resized.shape == (128, 128, 3)
    print("✅ Resize image test passed")

def test_grayscale():
    img_bytes = get_sample_image()
    gray = image_processor.to_grayscale(img_bytes)
    assert len(gray.shape) == 2
    print("✅ Grayscale test passed")

def test_rotate():
    img_bytes = get_sample_image()
    rotated = image_processor.rotate_image(img_bytes, 90)
    assert len(rotated.shape) == 3
    print("✅ Rotate test passed")

if __name__ == "__main__":
    test_load_image()
    test_resize_image()
    test_grayscale()
    test_rotate()