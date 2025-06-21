use pyo3::prelude::*;
use pyo3::types::PyList;
use aho_corasick::AhoCorasick;
use globset::{Glob, GlobSetBuilder};
use regex::Regex;

#[pyfunction]
fn match_tags(text: &str, patterns: Vec<String>) -> PyResult<Vec<String>> {
    let mut matched = Vec::new();

    let mut builder = GlobSetBuilder::new();
    for pattern in &patterns {
        let glob = Glob::new(pattern).unwrap_or_else(|_| Glob::new("*").unwrap());
        builder.add(glob);
    }
    let globset = builder.build().unwrap();

    if globset.is_match(text) {
        for pattern in &patterns {
            let glob = Glob::new(pattern).unwrap_or_else(|_| Glob::new("*").unwrap());
            let re_str = glob.regex().to_string();
            let re = Regex::new(&re_str).unwrap_or_else(|_| Regex::new(".*").unwrap());
            if re.is_match(text) {
                matched.push(pattern.clone());
            }
        }
    }

    matched.sort();
    matched.dedup();
    Ok(matched)
}

#[pymodule]
fn rust_tag_matcher(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(match_tags, m)?)?;
    Ok(())
}