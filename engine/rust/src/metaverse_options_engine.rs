use pyo3::prelude::*;

#[pyclass]
pub struct RustMetaverseOptionsEngine {}

#[pymethods]
impl RustMetaverseOptionsEngine {
    #[new]
    pub fn new() -> Self { Self {} }
}
