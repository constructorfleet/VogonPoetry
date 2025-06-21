use rust_tag_matcher::match_tags;
use serde::{Deserialize, Serialize};
use std::io::{self, Read};

#[derive(Deserialize)]
struct MatchInput {
    patterns: Vec<String>,
    texts: Vec<String>,
}

#[derive(Serialize)]
struct MatchOutput {
    results: Vec<Vec<String>>,
}

fn main() -> anyhow::Result<()> {
    let mut buffer = String::new();
    io::stdin().read_to_string(&mut buffer)?;
    let input: MatchInput = serde_json::from_str(&buffer)?;

    let results = input
        .texts
        .iter()
        .map(|text| match_tags(text, &input.patterns))
        .collect();

    let output = MatchOutput { results };
    println!("{}", serde_json::to_string(&output)?);
    Ok(())
}