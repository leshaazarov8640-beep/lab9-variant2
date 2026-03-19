use pyo3::prelude::*;
use std::collections::HashMap;

#[pyfunction]
fn fibonacci_recursive(n: u32) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2),
    }
}

#[pyfunction]
fn fibonacci_iterative(n: u32) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => {
            let mut a = 0;
            let mut b = 1;
            for _ in 2..=n {
                let temp = a + b;
                a = b;
                b = temp;
            }
            b
        }
    }
}

#[pyclass]
struct FibonacciCache {
    cache: HashMap<u32, u64>,
}

#[pymethods]
impl FibonacciCache {
    #[new]
    fn new() -> Self {
        let mut cache = HashMap::new();
        cache.insert(0, 0);
        cache.insert(1, 1);
        FibonacciCache { cache }
    }
    
    fn get(&mut self, n: u32) -> u64 {
        if let Some(&result) = self.cache.get(&n) {
            return result;
        }
        
        let result = fibonacci_iterative(n);
        self.cache.insert(n, result);
        result
    }
    
    fn size(&self) -> usize {
        self.cache.len()
    }
}

#[pymodule]
fn rust_fibonacci(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fibonacci_recursive, m)?)?;
    m.add_function(wrap_pyfunction!(fibonacci_iterative, m)?)?;
    m.add_class::<FibonacciCache>()?;
    Ok(())
}