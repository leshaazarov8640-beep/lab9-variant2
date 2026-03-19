import subprocess
import requests
import rust_fibonacci
import time
import struct
import json
import pytest

class TestGoServer:
    def test_go_process_binary(self):
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
            pytest.skip("Go server is not running")

class TestRustModule:
    def test_fibonacci_recursive(self):
        assert rust_fibonacci.fibonacci_recursive(0) == 0
        assert rust_fibonacci.fibonacci_recursive(1) == 1
        assert rust_fibonacci.fibonacci_recursive(10) == 55
        print("Recursive Fibonacci test passed")
    
    def test_fibonacci_iterative(self):
        assert rust_fibonacci.fibonacci_iterative(0) == 0
        assert rust_fibonacci.fibonacci_iterative(1) == 1
        assert rust_fibonacci.fibonacci_iterative(20) == 6765
        print("Iterative Fibonacci test passed")
    
    def test_fibonacci_cache(self):
        cache = rust_fibonacci.FibonacciCache()
        assert cache.size() == 2
        
        assert cache.get(10) == 55
        assert cache.size() == 3
        
        assert cache.get(5) == 5
        assert cache.size() == 4
        
        assert cache.get(10) == 55
        assert cache.size() == 4
        print("Fibonacci cache test passed")

class TestGoSubprocess:
    def test_go_subprocess_json(self):
        proc = subprocess.Popen(
            ["C:\\Users\\User\\lab9-variant2\\go-server\\go-server.exe"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        input_data = json.dumps({"numbers": [1, 2, 3, 4, 5]}).encode()
        output, error = proc.communicate(input_data)

        if error:
            print(f"Go error: {error.decode()}")

        result = json.loads(output)
        assert result["sum"] == 55
        print("Go subprocess test passed")