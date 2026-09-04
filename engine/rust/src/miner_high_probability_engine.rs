use pyo3::prelude::*;

#[pyclass]
pub struct RustMinerHighProbabilityEngine {}

#[pymethods]
impl RustMinerHighProbabilityEngine {
    #[new]
    pub fn new() -> Self { Self {} }
    
    pub fn batch_position_sizing(&self, capital: f64, entries: Vec<f64>, stops: Vec<f64>) -> Vec<i32> {
        let max_risk = capital * 0.03;
        entries.iter().zip(stops.iter()).map(|(e, s)| {
            let risk = (e - s).abs();
            if risk > 0.0 { (max_risk / risk) as i32 } else { 0 }
        }).collect()
    }
}
