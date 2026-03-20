import timeit
import rust_math as rust_fibonacci
import image_processor
import requests
import json
import subprocess
import os
from PIL import Image
import io

print("=" * 70)
print("ПРОФИЛИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ: Python vs Rust vs Go")
print("=" * 70)

# ========== ПОДГОТОВКА ТЕСТОВОГО ИЗОБРАЖЕНИЯ ==========
print("\n1. ПОДГОТОВКА ТЕСТОВОГО ИЗОБРАЖЕНИЯ")

def get_test_image():
    """Загружает или создает тестовое изображение"""
    urls = [
        "https://www.w3schools.com/w3images/forest.jpg",
        "https://www.w3schools.com/w3images/lights.jpg",
        "https://www.w3schools.com/w3images/flowers.jpg"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Проверяем, что это изображение
                Image.open(io.BytesIO(response.content))
                print(f"   ✅ Изображение загружено из: {url}")
                return response.content
        except:
            continue
    
    # Если не удалось загрузить, создаем тестовое изображение
    print("   ⚠️ Создаю тестовое изображение...")
    img = Image.new('RGB', (512, 512), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

# Загружаем тестовое изображение
img_bytes = get_test_image()
img_pil = Image.open(io.BytesIO(img_bytes))
print(f"   Размер изображения: {img_pil.size}")
print(f"   Формат: {img_pil.format or 'JPEG'}")

# ========== ТЕСТ 1: ФИБОНАЧЧИ ==========
print("\n2. ЧИСЛА ФИБОНАЧЧИ")

def fib_python_recursive(n):
    if n <= 1:
        return n
    return fib_python_recursive(n-1) + fib_python_recursive(n-2)

print("\n   Рекурсивный метод (n=35, 5 итераций):")
# Python рекурсивно
py_time_recursive = timeit.timeit(lambda: fib_python_recursive(35), number=5)
print(f"   Python (рекурсия): {py_time_recursive:.4f} сек")

# Rust рекурсивно
rust_time_recursive = timeit.timeit(lambda: rust_fibonacci.fibonacci_recursive(35), number=5)
print(f"   Rust (рекурсия):   {rust_time_recursive:.4f} сек")
print(f"   Ускорение:         {py_time_recursive/rust_time_recursive:.2f}x")

print("\n   Итеративный метод (n=90, 10000 итераций):")
# Python итеративно
def fib_python_iterative(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

py_time_iterative = timeit.timeit(lambda: fib_python_iterative(90), number=10000)
print(f"   Python: {py_time_iterative:.4f} сек")

# Rust итеративно
rust_time_iterative = timeit.timeit(lambda: rust_fibonacci.fibonacci_iterative(90), number=10000)
print(f"   Rust:   {rust_time_iterative:.4f} сек")
print(f"   Ускорение: {py_time_iterative/rust_time_iterative:.2f}x")

# Демонстрация безопасной версии
print("\n   Безопасная версия (проверка границ):")
for n in [90, 91, 92, 93, 94, 95]:
    try:
        result = rust_fibonacci.fibonacci_iterative(n)
        print(f"   n={n}: {str(result)[:20]}... (OK)")
    except Exception as e:
        print(f"   n={n}: {e}")
        break

# ========== ТЕСТ 2: ОБРАБОТКА ИЗОБРАЖЕНИЙ ==========
print("\n3. ОБРАБОТКА ИЗОБРАЖЕНИЙ (50 итераций)")

def pil_resize():
    img = img_pil.copy()
    return img.resize((128, 128))

def rust_resize():
    return image_processor.resize_image(img_bytes, 128, 128)

def pil_grayscale():
    img = img_pil.copy()
    return img.convert('L')

def rust_grayscale():
    return image_processor.to_grayscale(img_bytes)

# Изменение размера
print("\n   Изменение размера (600x400 -> 128x128):")
print("   Примечание: Rust медленнее из-за декодирования JPEG при каждом вызове")
rust_time_resize = timeit.timeit(rust_resize, number=50)
pil_time_resize = timeit.timeit(pil_resize, number=50)
print(f"   PIL:  {pil_time_resize:.4f} сек")
print(f"   Rust: {rust_time_resize:.4f} сек")
if pil_time_resize > 0 and rust_time_resize > 0:
    print(f"   Отношение: {rust_time_resize/pil_time_resize:.2f}x (Rust медленнее)")

# Grayscale
print("\n   Конвертация в grayscale:")
rust_time_grayscale = timeit.timeit(rust_grayscale, number=50)
pil_time_grayscale = timeit.timeit(pil_grayscale, number=50)
print(f"   PIL:  {pil_time_grayscale:.4f} сек")
print(f"   Rust: {rust_time_grayscale:.4f} сек")
if pil_time_grayscale > 0 and rust_time_grayscale > 0:
    print(f"   Отношение: {rust_time_grayscale/pil_time_grayscale:.2f}x (Rust медленнее)")

# ========== ТЕСТ 3: JSON ОБРАБОТКА ==========
print("\n4. JSON ОБРАБОТКА (100 итераций)")

data = {"numbers": list(range(1000))}

# Python
def json_python():
    return json.dumps(data)

py_time_json = timeit.timeit(json_python, number=100)
print(f"   Чистый Python: {py_time_json:.4f} сек")

# Go подпроцесс
def json_go():
    # Пробуем разные возможные имена бинарника
    go_exe_candidates = [
        os.path.abspath("../go-server/calculator.exe"),
        os.path.abspath("../go-server/go-server.exe"),
        os.path.abspath("../go-server/server.exe")
    ]
    
    go_exe = None
    for candidate in go_exe_candidates:
        if os.path.exists(candidate):
            go_exe = candidate
            break
    
    if go_exe is None:
        print(f"   ⚠️ Go бинарник не найден, пропускаем тест")
        return b'{"sum":0}'
    
    test_data = json.dumps({"numbers": [1, 2, 3, 4, 5]})
    try:
        proc = subprocess.Popen(
            [go_exe],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        out, _ = proc.communicate(test_data.encode())
        return out
    except Exception as e:
        print(f"   ⚠️ Ошибка при запуске Go: {e}")
        return b'{"sum":0}'

go_time_json = timeit.timeit(json_go, number=10)
print(f"   Python+Go: {go_time_json:.4f} сек (10 итераций)")

# ========== ТЕСТ 4: ПРОСТЫЕ ЧИСЛА (Python) ==========
print("\n5. ПРОСТЫЕ ЧИСЛА (Python)")

def primes_python(limit=100000):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit+1, i):
                sieve[j] = False
    return [i for i, is_prime in enumerate(sieve) if is_prime]

py_time_primes = timeit.timeit(lambda: primes_python(100000), number=10)
print(f"   Python: {py_time_primes:.4f} сек (10 итераций)")

# ========== ДОПОЛНИТЕЛЬНО: ТЕСТ КЭША ==========
print("\n6. ТЕСТ КЭША FIBONACCI")

cache = rust_fibonacci.FibonacciCache()

def python_fib_without_cache():
    return fib_python_iterative(50)

def rust_fib_with_cache():
    return cache.get(50)

# Прогреваем кэш
try:
    cache.get(50)
except:
    pass

py_time_cache = timeit.timeit(python_fib_without_cache, number=1000)
rust_time_cache = timeit.timeit(rust_fib_with_cache, number=1000)
print(f"   Python без кэша: {py_time_cache:.4f} сек")
print(f"   Rust с кэшем:    {rust_time_cache:.4f} сек")
print(f"   Ускорение:       {py_time_cache/rust_time_cache:.2f}x")

# ========== ИТОГОВАЯ ТАБЛИЦА ==========
print("\n" + "=" * 70)
print("ИТОГОВАЯ ТАБЛИЦА ПРОИЗВОДИТЕЛЬНОСТИ")
print("=" * 70)
print("| Задача                  | Python  | Rust    | Go      |")
print("|-------------------------|---------|---------|---------|")
print(f"| Фибоначчи (рекурсия)    | {py_time_recursive:.2f}с   | {rust_time_recursive:.2f}с   | -       |")
print(f"| Фибоначчи (итеративно)  | {py_time_iterative:.2f}с   | {rust_time_iterative:.2f}с   | -       |")
print(f"| Изменение размера        | {pil_time_resize:.2f}с   | {rust_time_resize:.2f}с   | -       |")
print(f"| Grayscale                | {pil_time_grayscale:.2f}с   | {rust_time_grayscale:.2f}с   | -       |")
print(f"| JSON (100 итераций)      | {py_time_json:.2f}с   | -       | {go_time_json:.2f}с   |")
print(f"| Простые числа (100k)     | {py_time_primes:.2f}с   | -       | -       |")
print(f"| Кэш Fibonacci (n=50)     | {py_time_cache:.2f}с   | {rust_time_cache:.2f}с   | -       |")
