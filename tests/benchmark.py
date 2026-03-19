import timeit
import rust_fibonacci

def python_fibonacci_iterative(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def python_fibonacci_recursive(n):
    if n <= 1:
        return n
    return python_fibonacci_recursive(n-1) + python_fibonacci_recursive(n-2)

if __name__ == "__main__":
    print("=" * 60)
    print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ PYTHON VS RUST")
    print("=" * 60)
    
    print("\n1. Итеративный метод (n=100000, 100 итераций):")
    python_time = timeit.timeit(lambda: python_fibonacci_iterative(100000), number=100)
    rust_time = timeit.timeit(lambda: rust_fibonacci.fibonacci_iterative(100000), number=100)
    print(f"   Python: {python_time:.4f} сек")
    print(f"   Rust:   {rust_time:.4f} сек")
    print(f"   Rust быстрее в {python_time/rust_time:.2f} раз")
    
    print("\n2. Рекурсивный метод (n=30, 10 итераций):")
    python_time = timeit.timeit(lambda: python_fibonacci_recursive(30), number=10)
    rust_time = timeit.timeit(lambda: rust_fibonacci.fibonacci_recursive(30), number=10)
    print(f"   Python: {python_time:.4f} сек")
    print(f"   Rust:   {rust_time:.4f} сек")
    print(f"   Rust быстрее в {python_time/rust_time:.2f} раз")
    
    print("\n3. Сравнение с кэшем (n=50, 1000 итераций):")
    cache = rust_fibonacci.FibonacciCache()
    python_time = timeit.timeit(lambda: python_fibonacci_iterative(50), number=1000)
    rust_time = timeit.timeit(lambda: cache.get(50), number=1000)
    print(f"   Python без кэша: {python_time:.4f} сек")
    print(f"   Rust с кэшем:    {rust_time:.4f} сек")
    print(f"   Rust быстрее в {python_time/rust_time:.2f} раз")