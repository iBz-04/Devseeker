use ignore::WalkBuilder;
use pyo3::prelude::*;

#[pyfunction]
fn scan_repo_files(root: &str, ignore_hidden: bool) -> PyResult<Vec<String>> {
    let mut builder = WalkBuilder::new(root);
    builder.hidden(ignore_hidden);
    builder.git_ignore(true);
    builder.git_global(true);
    builder.git_exclude(true);

    let mut results: Vec<String> = Vec::new();
    for entry in builder.build() {
        let entry = entry.map_err(|err| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(err.to_string()))?;
        if !entry.file_type().map(|kind| kind.is_file()).unwrap_or(false) {
            continue;
        }
        let path = entry.path();
        let relative = path
            .strip_prefix(root)
            .map_err(|err| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(err.to_string()))?;
        results.push(relative.to_string_lossy().to_string());
    }
    Ok(results)
}

#[pyfunction]
fn chunk_text(text: &str, max_chars: usize, overlap: usize) -> PyResult<Vec<String>> {
    if max_chars == 0 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("max_chars must be positive"));
    }
    if overlap >= max_chars {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("overlap must be smaller than max_chars"));
    }

    let mut chunks: Vec<String> = Vec::new();
    let step = max_chars - overlap;
    let chars: Vec<char> = text.chars().collect();
    let mut start = 0;

    while start < chars.len() {
        let end = std::cmp::min(start + max_chars, chars.len());
        chunks.push(chars[start..end].iter().collect());
        start += step;
    }

    Ok(chunks)
}

#[pymodule]
fn devseeker_native(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(scan_repo_files, module)?)?;
    module.add_function(wrap_pyfunction!(chunk_text, module)?)?;
    Ok(())
}
