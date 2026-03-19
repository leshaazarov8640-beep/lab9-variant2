import subprocess
import requests
import rust_fibonacci
import time
import struct
import json
import pytest

class TestGoServer:
    """Тесты для Go HTTP сервера"""
    
    def test_go_process_binary(self):
        """Тест отправки бинарных данных в Go сервер"""
        test_data = bytes([10, 20, 30, 40, 50])
        
        try:
            response = requests.post(
                "http://localhost:8080/process",
                data=test_data,
                headers={"Content-Type": "application/octet-stream"},
                timeout=5
            )
            
            assert response.status_code == 202
            task_id = struct.unpack("<Q", response.content)[0]
            assert task_id > 0
            
            time.sleep(3)
            
            result = requests.get(f"http://localhost:8080/result?id={task_id}", timeout=5)
            assert result.status_code == 200
            assert result.content != test_data
            print("Go HTTP test passed")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Go server is not running. Start it with: cd go-server && go run main.go")

class TestRustModule:
    """Тесты для Rust модуля с числами Фибоначчи"""
    
    def test_fibonacci_recursive(self):
        """Тест рекурсивного Фибоначчи"""
        assert rust_fibonacci.fibonacci_recursive(0) == 0
        assert rust_fibonacci.fibonacci_recursive(1) == 1
        assert rust_fibonacci.fibonacci_recursive(10) == 55
        print("Recursive Fibonacci test passed")
    
    def test_fibonacci_iterative(self):
        """Тест итеративного Фибоначчи"""
        assert rust_fibonacci.fibonacci_iterative(0) == 0
        assert rust_fibonacci.fibonacci_iterative(1) == 1
        assert rust_fibonacci.fibonacci_iterative(20) == 6765
        print("Iterative Fibonacci test passed")
    
    def test_fibonacci_cache(self):
        """Тест класса с кэшем - вариант 1 (под нашу реализацию)"""
        cache = rust_fibonacci.FibonacciCache()
        
        # Проверяем начальные значения
        assert cache.get(0) == 0
        assert cache.get(1) == 1
        print("Начальные значения верны")
        
        # Запрашиваем 10 - в кэш добавляются все числа от 2 до 10
        assert cache.get(10) == 55
        print("get(10) работает")
        
        # Проверяем, что 5 тоже доступно (должно быть в кэше от вычисления 10)
        assert cache.get(5) == 5
        print("get(5) работает (из кэша)")
        
        # Очищаем кэш
        cache.clear()
        print("Кэш очищен")
        
        # Проверяем после очистки
        assert cache.get(0) == 0
        assert cache.get(1) == 1
        print("После очистки базовые значения работают")
        
        print("Fibonacci cache test passed")

class TestGoSubprocess:
    """Тест вызова Go бинаря как подпроцесса"""
    
    def test_go_subprocess_json(self):
        """Запуск Go программы как подпроцесса с JSON"""
        import os
        go_exe = os.path.abspath("../go-server/go-server.exe")
        
        proc = subprocess.Popen(
            [go_exe],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        input_data = json.dumps({"numbers": [1, 2, 3, 4, 5]}).encode()
        output, error = proc.communicate(input_data)

        if error:
            print(f"Go error: {error.decode()}")

        result = json.loads(output)
        assert result["sum"] == 55  # 1+4+9+16+25 = 55
        print("Go subprocess test passed")

if __name__ == "__main__":
    print("=== Testing Go Subprocess ===")
    test = TestGoSubprocess()
    test.test_go_subprocess_json()
    
    print("\n=== Testing Rust Module ===")
    test = TestRustModule()
    test.test_fibonacci_recursive()
    test.test_fibonacci_iterative()
    test.test_fibonacci_cache()