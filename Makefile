.PHONY: setup hardware test lint cpp-configure cpp-build cpp-test

setup:
	uv sync

hardware:
	uv run python tools/hardware_report.py

test:
	uv run pytest

lint:
	uv run ruff check .

cpp-configure:
	cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Debug

cpp-build: cpp-configure
	cmake --build cpp/build

cpp-test: cpp-build
	ctest --test-dir cpp/build --output-on-failure
