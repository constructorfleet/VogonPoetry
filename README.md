# VogonPoetry

*A Declarative, Agentic LLM Pipeline Engine – because even your thoughts require permits.*

---

## Overview

VogonPoetry is a modular, extensible engine for building LLM pipelines in Python. Its design is inspired by agentic architectures, leveraging declarative configuration, modern Python features, and strong type safety via Pydantic.

- **Modular:** Easily plug in new embedders, steps, or tags.
- **Declarative:** Pipelines are defined in YAML config files.
- **Agentic:** Pipelines can be composed, extended, and traced.
- **Extensible:** Add new pipeline steps, embedders, and tracing backends.

---

## Features

- **FastAPI API** for running pipelines and retrieving trace results.
- **Async pipeline execution** for scalable, concurrent processing.
- **Pluggable embedders** with local and remote support.
- **Tag and vector utilities** for semantic operations.
- **Traceable execution** with persistent trace storage.

---

## Installation

```bash
git clone https://github.com/constructorfleet/VogonPoetry.git
cd VogonPoetry
pip install -r requirements.txt
```

> **Note:** Python 3.10+ is recommended.

---

## Quick Start

### Run from CLI

```bash
python -m vogonpoetry [path_to_config.yaml]
```
If no config is provided, defaults to `config/example_pipeline.yaml`.

### Run the API Server

```bash
uvicorn vogonpoetry.api:app --reload
```

- POST `/run` – Run a pipeline (see API details below).
- GET `/trace/{trace_id}` – Retrieve execution trace by ID.

---

## Example Pipeline Config

```yaml
# config/example_pipeline.yaml
embedders:
  - name: "example-embedder"
    type: "remote"
    url: "http://localhost:8001/embed"
pipeline:
  id: "example-pipeline"
  description: "A sample pipeline"
  steps:
    - type: "classify"
      ...
```

---

## API

### POST `/run`

Run a pipeline with a given config and context.

**Request:**
```json
{
  "config": "config/example_pipeline.yaml",
  "context": { }
}
```

**Response:**
```json
{
  "trace_id": "uuid-string",
  "trace": [...]
}
```

### GET `/trace/{trace_id}`

Retrieve the trace for a pipeline execution.

---

## Project Structure

- `vogonpoetry/app.py` – Main application interface
- `vogonpoetry/api.py` – FastAPI routes
- `vogonpoetry/embedders/` – Embedder implementations
- `vogonpoetry/pipeline/` – Pipeline core and steps
- `vogonpoetry/tags/` – Tag and vector utilities
- `vogonpoetry/tracing/` – Trace storage and management
- `vogonpoetry/loader.py` – Config loader

---

## Development & Contribution

1. Fork this repo and create a feature branch.
2. Add or modify modules with type hints and docstrings.
3. Ensure new features include tests.
4. Open a Pull Request.

---

## License

This project is currently unlicensed. Please contact the maintainers for usage details.

---

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://docs.pydantic.dev/), and Python’s async features.

---

> _“The poetry is terrible, but the pipelines are beautiful."_ 🚀
