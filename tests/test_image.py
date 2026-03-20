import pytest
import image_processor
import numpy as np
import requests
import os
from PIL import Image
import io

@pytest.fixture
def sample_image():
    """Загружает тестовое изображение"""
    urls = [
        "https://www.w3schools.com/w3images/forest.jpg",
        "https://www.w3schools.com/w3images/lights.jpg"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Проверяем, что это изображение
                Image.open(io.BytesIO(response.content))
                return response.content
        except:
            continue
    
    # Создаем тестовое изображение
    img = Image.new('RGB', (256, 256), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def test_load_image(sample_image):
    img = image_processor.load_image_from_bytes(sample_image)
    assert isinstance(img, np.ndarray)
    assert len(img.shape) == 3
    assert img.shape[2] == 3

def test_resize_image(sample_image):
    resized = image_processor.resize_image(sample_image, 128, 128)
    assert resized.shape == (128, 128, 3)

def test_grayscale(sample_image):
    gray = image_processor.to_grayscale(sample_image)
    assert len(gray.shape) == 2

def test_rotate(sample_image):
    rotated = image_processor.rotate_image(sample_image, 90)
    assert len(rotated.shape) == 3

def test_save(sample_image, tmp_path):
    img = image_processor.load_image_from_bytes(sample_image)
    save_path = str(tmp_path / "test.jpg")
    image_processor.save_image(img, save_path)
    assert os.path.exists(save_path)