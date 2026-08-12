# Custom kernel boundary

The custom Metal operation is intentionally unselected.

Issue [#37](https://github.com/skcache/miniserve/issues/37) requires profiling or explicit runtime evidence before choosing a candidate. Issue [#39](https://github.com/skcache/miniserve/issues/39) owns exactly one Metal implementation after the readable reference and MLX C++ paths agree.

No kernel source belongs here until that evidence exists. A valid result may be slower than MLX.
