.PHONY: help install dev build test lint format clean docs release bench

help:
	@echo "Available commands:"
	@echo "  install    : Install the package"
	@echo "  dev        : Install the package in editable mode with dev dependencies"
	@echo "  build      : Build the project (Rust and Python)"
	@echo "  test       : Run tests"
	@echo "  bench      : Run benchmarks (Rust and Python)"
	@echo "  lint       : Run linting (ruff, mypy)"
	@echo "  format     : Format code (ruff, cargo fmt)"
	@echo "  clean      : Clean build artifacts"
	@echo "  docs       : Build documentation"
	@echo "  release    : Prepare a new release"

install:
	pip install .

dev:
	pip install -e ".[dev]"
	maturin develop

build:
	maturin build --release

test:
	pytest tests/

bench:
	pytest tests/test_benchmarking.py
	cd rust_core && cargo bench


lint:
	ruff check .
	mypy piranha/

format:
	ruff format .
	cd rust_core && cargo fmt

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache
	cd rust_core && cargo clean

docs:
	mkdocs build

release:
	@echo "Follow the instructions in RELEASE.md to prepare a release."
