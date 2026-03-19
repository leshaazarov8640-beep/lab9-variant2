use pyo3::prelude::*;
use image::DynamicImage;

#[pyfunction]
fn load_image_from_bytes(py: Python, image_bytes: Vec<u8>) -> PyResult<PyObject> {
    let img = match image::load_from_memory(&image_bytes) {
        Ok(img) => img,
        Err(e) => return Err(pyo3::exceptions::PyIOError::new_err(e.to_string())),
    };
    
    let rgb_img = img.to_rgb8();
    let (height, width) = (rgb_img.height() as usize, rgb_img.width() as usize);
    let data = rgb_img.into_raw();
    
    Python::with_gil(|py| {
        let numpy = py.import("numpy")?;
        let array = numpy.call_method1("array", (data,))?;
        let shaped = array.call_method1("reshape", (height, width, 3))?;
        Ok(shaped.to_object(py))
    })
}

#[pyfunction]
fn resize_image(py: Python, image_bytes: Vec<u8>, width: u32, height: u32) -> PyResult<PyObject> {
    let img = match image::load_from_memory(&image_bytes) {
        Ok(img) => img,
        Err(e) => return Err(pyo3::exceptions::PyIOError::new_err(e.to_string())),
    };
    
    let resized = img.resize(width, height, image::imageops::FilterType::Lanczos3);
    let rgb_img = resized.to_rgb8();
    let data = rgb_img.into_raw();
    
    Python::with_gil(|py| {
        let numpy = py.import("numpy")?;
        let array = numpy.call_method1("array", (data,))?;
        let shaped = array.call_method1("reshape", (height as usize, width as usize, 3))?;
        Ok(shaped.to_object(py))
    })
}

#[pyfunction]
fn to_grayscale(py: Python, image_bytes: Vec<u8>) -> PyResult<PyObject> {
    let img = match image::load_from_memory(&image_bytes) {
        Ok(img) => img,
        Err(e) => return Err(pyo3::exceptions::PyIOError::new_err(e.to_string())),
    };
    
    let gray = img.grayscale();
    let gray_img = gray.to_luma8();
    let (height, width) = (gray_img.height() as usize, gray_img.width() as usize);
    let data = gray_img.into_raw();
    
    Python::with_gil(|py| {
        let numpy = py.import("numpy")?;
        let array = numpy.call_method1("array", (data,))?;
        let shaped = array.call_method1("reshape", (height, width))?;
        Ok(shaped.to_object(py))
    })
}

#[pyfunction]
fn rotate_image(py: Python, image_bytes: Vec<u8>, angle: i32) -> PyResult<PyObject> {
    let img = match image::load_from_memory(&image_bytes) {
        Ok(img) => img,
        Err(e) => return Err(pyo3::exceptions::PyIOError::new_err(e.to_string())),
    };
    
    let rotated = match angle {
        90 => img.rotate90(),
        180 => img.rotate180(),
        270 => img.rotate270(),
        _ => return Err(pyo3::exceptions::PyValueError::new_err("Angle must be 90, 180, or 270")),
    };
    
    let rgb_img = rotated.to_rgb8();
    let (height, width) = (rgb_img.height() as usize, rgb_img.width() as usize);
    let data = rgb_img.into_raw();
    
    Python::with_gil(|py| {
        let numpy = py.import("numpy")?;
        let array = numpy.call_method1("array", (data,))?;
        let shaped = array.call_method1("reshape", (height, width, 3))?;
        Ok(shaped.to_object(py))
    })
}

#[pyfunction]
fn save_image(py: Python, img_array: &PyAny, path: String) -> PyResult<()> {
    let numpy = py.import("numpy")?;
    let flat = img_array.call_method0("flatten")?;
    let bytes = flat.call_method0("tobytes")?;
    let data = bytes.extract::<Vec<u8>>()?;
    
    let shape = img_array.getattr("shape")?.extract::<Vec<usize>>()?;
    if shape.len() != 3 || shape[2] != 3 {
        return Err(pyo3::exceptions::PyValueError::new_err("Expected array shape (H, W, 3)"));
    }
    
    let (height, width) = (shape[0] as u32, shape[1] as u32);
    
    let img_buffer = image::ImageBuffer::from_raw(width, height, data)
        .ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err("Failed to create ImageBuffer"))?;
    let dyn_img = image::DynamicImage::ImageRgb8(img_buffer);
    
    dyn_img.save(&path)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    
    Ok(())
}

#[pymodule]
fn image_processor(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(load_image_from_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(resize_image, m)?)?;
    m.add_function(wrap_pyfunction!(to_grayscale, m)?)?;
    m.add_function(wrap_pyfunction!(rotate_image, m)?)?;
    m.add_function(wrap_pyfunction!(save_image, m)?)?;
    Ok(())
}