use rust_embedder::embed;
use serde::{Deserialize, Serialize};
use std::env;
use std::io::{self, Read};

#[derive(Deserialize)]
struct EmbedInput {
    inputs: Vec<String>,
}

#[derive(Serialize)]
struct EmbedOutput {
    embeddings: Vec<Vec<f32>>,
}

fn main() -> anyhow::Result<()> {
    let mut buffer = String::new();
    io::stdin().read_to_string(&mut buffer)?;
    let input: EmbedInput = serde_json::from_str(&buffer)?;

    let model_path = env::args().nth(2).expect("Model path not provided");
    let embeddings = embed(&model_path, &input.inputs)?;
    let output = EmbedOutput { embeddings };

    println!("{}", serde_json::to_string(&output)?);
    Ok(())
} 
