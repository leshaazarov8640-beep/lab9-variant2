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
fn fibonacci_iterative(n: u32) -> PyResult<u64> {
    match n {
        0 => Ok(0),
        1 => Ok(1),
        _ => {
            let mut a: u64 = 0;
            let mut b: u64 = 1;
            for _ in 2..=n {
                match a.checked_add(b) {
                    Some(sum) => {
                        a = b;
                        b = sum;
                    }
                    None => {
                        return Err(pyo3::exceptions::PyOverflowError::new_err(
                            format!("Fibonacci({}) exceeds 64-bit limit", n)
                        ));
                    }
                }
            }
            Ok(b)
        }
    }
}

#[pyfunction]
fn fibonacci_safe(n: u32) -> Option<u64> {
    match n {
        0 => Some(0),
        1 => Some(1),
        _ => {
            let mut a: u64 = 0;
            let mut b: u64 = 1;
            for _ in 2..=n {
                match a.checked_add(b) {
                    Some(sum) => {
                        a = b;
                        b = sum;
                    }
                    None => return None,
                }
            }
            Some(b)
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
    
    fn get(&mut self, n: u32) -> PyResult<u64> {
        if let Some(&result) = self.cache.get(&n) {
            return Ok(result);
        }
        
        match fibonacci_safe(n) {
            Some(result) => {
                self.cache.insert(n, result);
                Ok(result)
            }
            None => {
                Err(pyo3::exceptions::PyOverflowError::new_err(
                    format!("Fibonacci({}) exceeds 64-bit limit", n)
                ))
            }
        }
    }
    
    fn size(&self) -> usize {
        self.cache.len()
    }
}

#[pymodule]
fn rust_math(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fibonacci_recursive, m)?)?;
    m.add_function(wrap_pyfunction!(fibonacci_iterative, m)?)?;
    m.add_function(wrap_pyfunction!(fibonacci_safe, m)?)?;
    m.add_class::<FibonacciCache>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fibonacci_recursive() {
        assert_eq!(fibonacci_recursive(0), 0);
        assert_eq!(fibonacci_recursive(1), 1);
        assert_eq!(fibonacci_recursive(10), 55);
    }

    #[test]
    fn test_fibonacci_iterative() {
        assert_eq!(fibonacci_iterative(0).unwrap(), 0);
        assert_eq!(fibonacci_iterative(1).unwrap(), 1);
        assert_eq!(fibonacci_iterative(10).unwrap(), 55);
    }

    #[test]
    fn test_fibonacci_safe() {
        assert_eq!(fibonacci_safe(0), Some(0));
        assert_eq!(fibonacci_safe(1), Some(1));
        assert_eq!(fibonacci_safe(10), Some(55));
        assert_eq!(fibonacci_safe(93), Some(12200160415121876738));
        assert_eq!(fibonacci_safe(94), None);
    }
}