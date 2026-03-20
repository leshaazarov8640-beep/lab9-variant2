import pytest
import rust_math as rust_fibonacci

def test_fibonacci_recursive():
    assert rust_fibonacci.fibonacci_recursive(0) == 0
    assert rust_fibonacci.fibonacci_recursive(1) == 1
    assert rust_fibonacci.fibonacci_recursive(10) == 55
    print("✅ Recursive Fibonacci test passed")

def test_fibonacci_iterative():
    assert rust_fibonacci.fibonacci_iterative(0) == 0
    assert rust_fibonacci.fibonacci_iterative(1) == 1
    assert rust_fibonacci.fibonacci_iterative(20) == 6765
    print("✅ Iterative Fibonacci test passed")

def test_fibonacci_cache():
    cache = rust_fibonacci.FibonacciCache()
    assert cache.get(0) == 0
    assert cache.get(1) == 1
    assert cache.get(10) == 55
    assert cache.get(5) == 5
    print("✅ Fibonacci cache test passed")

def test_fibonacci_overflow():
    import pytest
    with pytest.raises(Exception):
        rust_fibonacci.fibonacci_iterative(100)
    assert rust_fibonacci.fibonacci_safe(100) is None
    print("✅ Overflow handling test passed")

if __name__ == "__main__":
    test_fibonacci_recursive()
    test_fibonacci_iterative()
    test_fibonacci_cache()
    test_fibonacci_overflow()