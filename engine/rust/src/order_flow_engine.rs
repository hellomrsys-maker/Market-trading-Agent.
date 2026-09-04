use pyo3::prelude::*;

#[pyclass]
pub struct RustOrderFlowEngine {}

#[pymethods]
impl RustOrderFlowEngine {
    #[new]
    pub fn new() -> Self { Self {} }
}
