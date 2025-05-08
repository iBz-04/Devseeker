# Building Documentation

This guide explains how to build and preview the DevSeeker documentation locally using Sphinx.

## Prerequisites

Ensure you have:
- Python 3.10 or higher
- Poetry

## Install Dependencies

Install core and documentation dependencies:

```bash
poetry install --extras doc
```

Activate the virtual environment:

```bash
poetry shell
```

## Generate API Reference

Regenerate the API reference from project docstrings:

```bash
cd docs
python create_api_rst.py
```

## Build HTML Documentation

From the docs directory, run:

```bash
make html
```

The site will be generated in `docs/_build/html`. Open `docs/_build/html/index.html` in your browser.

## Live Reload

For automatic rebuilds on file changes and live reload:

```bash
cd docs
sphinx-autobuild . _build/html
```

Then open http://127.0.0.1:8000 in your browser.

## Publish on Read the Docs

Documentation is published on Read the Docs. To customize the build, add or update `.readthedocs.yaml` at the project root. For configuration details, see:
https://docs.readthedocs.io/en/stable/config-file/v2.html

## See Also

- [Sphinx Quickstart](https://www.sphinx-doc.org/en/master/usage/quickstart.html)
- [Documentation Index](index.rst)
