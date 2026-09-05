.PHONY: setup hardware oracle benchmark test lint cpp-configure cpp-build cpp-test cpp-configure-mlx cpp-build-mlx cpp-test-mlx phase0

setup:
	uv sync

hardware:
	uv run python tools/hardware_report.py

oracle:
	uv run python tools/reference_tokens.py --suite --output results/golden_tokens.json

benchmark: hardware
	uv run python -m tools.reference_benchmark

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

cpp-configure-mlx:
	cmake -S cpp -B cpp/build-mlx \
		-DCMAKE_BUILD_TYPE=Debug \
		-DMINISERVE_ENABLE_MLX=ON \
		-DMLX_CPP_ROOT="$(shell uv run python -m mlx --cmake-dir)"

cpp-build-mlx: cpp-configure-mlx
	cmake --build cpp/build-mlx

cpp-test-mlx: cpp-build-mlx
	ctest --test-dir cpp/build-mlx --output-on-failure

phase0: test cpp-test oracle benchmark
