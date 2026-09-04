use pyo3::prelude::*;

#[pyclass]
pub struct RustInitialBalanceEngine {}

#[pymethods]
impl RustInitialBalanceEngine {
    #[new]
    pub fn new() -> Self { Self {} }
}
