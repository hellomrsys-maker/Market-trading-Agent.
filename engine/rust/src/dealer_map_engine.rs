use pyo3::prelude::*;

#[pyclass]
pub struct RustDealerMapEngine {}

#[pymethods]
impl RustDealerMapEngine {
    #[new]
    pub fn new() -> Self { Self {} }
}
