#!/usr/bin/env python3
import re
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
PLOTS_DIR = ROOT / "analysis" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

WORKLOADS = {
    "sequential": "Sequential Scan (High Spatial)",
    "strided": "Strided Access (Medium Spatial)",
    "random": "Random Access (Low Locality)",
}
LINE_SIZES = [32, 128]

T_L1 = 1.0
T_L2 = 10.0
T_MEM = 100.0

MISS_RATE_RE = re.compile(r"Demand miss rate\s+([0-9.]+)")


def parse_level_miss_rates(path: Path):
    current = None
    miss = {}

    with path.open() as f:
        for raw in f:
            line = raw.strip()
            if line.startswith("l1-dcache"):
                current = "L1"
                continue
            if line.startswith("l2-ucache") or line.startswith("l2-dcache"):
                current = "L2"
                continue
            if current and line.startswith("Demand miss rate"):
                m = MISS_RATE_RE.search(line)
                if not m:
                    continue
                miss[current] = float(m.group(1))
                current = None

    if "L1" not in miss or "L2" not in miss:
        raise RuntimeError(f"Missing L1/L2 miss rate in {path}")
    return miss


def compute_amat(mr_l1: float, mr_l2: float) -> float:
    return T_L1 + mr_l1 * (T_L2 + mr_l2 * T_MEM)


def collect_results():
    rows = []
    for short, label in WORKLOADS.items():
        for line_size in LINE_SIZES:
            fname = f"{short}_{line_size}B.txt"
            path = RESULTS_DIR / fname
            if not path.exists():
                raise FileNotFoundError(path)
            miss = parse_level_miss_rates(path)
            mr_l1 = miss["L1"]
            mr_l2 = miss["L2"]
            amat = compute_amat(mr_l1, mr_l2)
            rows.append(
                {
                    "WorkloadShort": short,
                    "Workload": label,
                    "Line Size (bytes)": line_size,
                    "L1 Miss Rate": mr_l1,
                    "L1 Miss Rate (%)": mr_l1 * 100.0,
                    "L2 Miss Rate": mr_l2,
                    "L2 Miss Rate (%)": mr_l2 * 100.0,
                    "AMAT (cycles)": amat,
                }
            )
    return pd.DataFrame(rows)


def plot_miss_rates(df):
    plt.figure(figsize=(10, 5))
    labels = [f"{w}\n{ls}B" for w, ls in zip(df["Workload"], df["Line Size (bytes)"])]
    x = range(len(df))
    width = 0.4
    x1 = [xi - width / 2 for xi in x]
    x2 = [xi + width / 2 for xi in x]

    plt.bar(x1, df["L1 Miss Rate (%)"], width=width, label="L1")
    plt.bar(x2, df["L2 Miss Rate (%)"], width=width, label="L2")

    plt.xticks(list(x), labels, rotation=45, ha="right")
    plt.ylabel("Demand Miss Rate (%)")
    plt.title("L1 and L2 Demand Miss Rates")
    plt.legend()
    plt.tight_layout()
    outpath = PLOTS_DIR / "miss_rate_by_workload.png"
    plt.savefig(outpath, dpi=200)
    print(f"Saved {outpath}")


def plot_amat(df):
    plt.figure(figsize=(10, 5))
    labels = [f"{w}\n{ls}B" for w, ls in zip(df["Workload"], df["Line Size (bytes)"])]
    x = range(len(df))

    plt.bar(list(x), df["AMAT (cycles)"])
    plt.xticks(list(x), labels, rotation=45, ha="right")
    plt.ylabel("Average Memory Access Time (cycles)")
    plt.title("Average Memory Access Time by Workload and Line Size")
    plt.tight_layout()
    outpath = PLOTS_DIR / "amat_by_workload.png"
    plt.savefig(outpath, dpi=200)
    print(f"Saved {outpath}")


def main():
    df = collect_results()
    print(df.to_string(index=False))
    csv_path = PLOTS_DIR / "results_table.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved {csv_path}")
    plot_miss_rates(df)
    plot_amat(df)


if __name__ == "__main__":
    main()
