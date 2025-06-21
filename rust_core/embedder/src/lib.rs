use anyhow::Result;

pub fn embed(model_path: &str, inputs: &[String]) -> Result<Vec<Vec<f32>>> {
    // Placeholder: Load model and embed inputs
    Ok(inputs
        .iter()
        .map(|s| vec![s.len() as f32, 0.0, 1.0]) // fake embedding
        .collect())
}
