import image_processor
import numpy as np
import requests
import os
from PIL import Image
import io
import tempfile

# Глобальная переменная для тестового изображения
TEST_IMAGE_BYTES = None

def get_sample_image():
    """Возвращает тестовое изображение из глобальной переменной"""
    global TEST_IMAGE_BYTES
    if TEST_IMAGE_BYTES is None:
        # Если вдруг не загрузили, создаем
        img = Image.new('RGB', (256, 256), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        TEST_IMAGE_BYTES = img_byte_arr.getvalue()
    return TEST_IMAGE_BYTES

def test_load_image():
    """Тест загрузки изображения"""
    try:
        img_bytes = get_sample_image()
        img = image_processor.load_image_from_bytes(img_bytes)
        assert isinstance(img, np.ndarray)
        assert len(img.shape) == 3
        assert img.shape[2] == 3
        print("✅ Load image test passed")
        return True
    except Exception as e:
        print(f"❌ Load image test failed: {e}")
        return False

def test_resize_image():
    """Тест изменения размера"""
    try:
        img_bytes = get_sample_image()
        # Показываем информацию об изображении
        img_pil = Image.open(io.BytesIO(img_bytes))
        print(f"   Исходный размер: {img_pil.size}")
        
        resized = image_processor.resize_image(img_bytes, 128, 128)
        print(f"   После resize - shape: {resized.shape}")
        
        assert resized.shape == (128, 128, 3)
        print("✅ Resize image test passed")
        return True
    except Exception as e:
        print(f"❌ Resize test failed: {e}")
        return False

def test_grayscale():
    """Тест конвертации в grayscale"""
    try:
        img_bytes = get_sample_image()
        gray = image_processor.to_grayscale(img_bytes)
        assert len(gray.shape) == 2
        print("✅ Grayscale test passed")
        return True
    except Exception as e:
        print(f"❌ Grayscale test failed: {e}")
        return False

def test_rotate():
    """Тест поворота изображения"""
    try:
        img_bytes = get_sample_image()
        rotated = image_processor.rotate_image(img_bytes, 90)
        assert len(rotated.shape) == 3
        print("✅ Rotate test passed")
        return True
    except Exception as e:
        print(f"❌ Rotate test failed: {e}")
        return False

def test_save(tmp_path):
    """Тест сохранения изображения"""
    try:
        img_bytes = get_sample_image()
        img = image_processor.load_image_from_bytes(img_bytes)
        save_path = os.path.join(str(tmp_path), "test.jpg")
        image_processor.save_image(img, save_path)
        assert os.path.exists(save_path)
        print("✅ Save test passed")
        return True
    except Exception as e:
        print(f"❌ Save test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ RUST МОДУЛЯ ОБРАБОТКИ ИЗОБРАЖЕНИЙ")
    print("=" * 50)
    
    tmp_dir = tempfile.mkdtemp()
    
    # Загружаем тестовое изображение
    print("Загрузка тестового изображения...")
    
    urls = [
        "https://www.w3schools.com/w3images/forest.jpg",
        "https://www.w3schools.com/w3images/lights.jpg",
        "https://www.w3schools.com/w3images/flowers.jpg"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                Image.open(io.BytesIO(response.content))  # Проверка
                TEST_IMAGE_BYTES = response.content
                print(f"✅ Изображение загружено из: {url}")
                break
        except:
            continue
    
    if TEST_IMAGE_BYTES is None:
        print("Создаю тестовое изображение...")
        img = Image.new('RGB', (256, 256), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        TEST_IMAGE_BYTES = img_byte_arr.getvalue()
        print("✅ Тестовое изображение создано")
    
    # Запускаем тесты
    tests = [
        test_load_image,
        test_resize_image,
        test_grayscale,
        test_rotate,
        lambda: test_save(tmp_dir)
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print("-" * 40)
    
    print(f"\nРезультат: {passed}/{len(tests)} тестов пройдено")
    if passed == len(tests):
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ")