# DineroIV Cache Lab (L1 + L2, Synthetic Traces)

This package gives you a plug-and-play way to run DineroIV cache simulations
with L1 + L2 caches on macOS (including Apple Silicon, e.g., M1–M4) and then
generate figures similar to those in your assignment write-up.

It does all of this:
- clones and builds DineroIV locally (inside this folder),
- generates synthetic traces for three workloads,
- runs DineroIV with a 2-level cache hierarchy (L1D + L2 unified),
- parses the output for L1 and L2 miss rates,
- computes AMAT, and
- produces CSV + PNG charts.

## Quick start

```bash
cd dineroiv-cache-lab
bash scripts/install_dinero.sh
bash scripts/run_sims.sh
```

After that, see `analysis/plots/` for PNG charts and `results/` for raw outputs.
