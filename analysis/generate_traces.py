#!/usr/bin/env python3
import random
from pathlib import Path

BASE_ADDR = 0x10000000
ELEMENT_SIZE = 4
N_SEQUENTIAL = 100_000
N_STRIDED = 25_000
STRIDE_BYTES = 1024

ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "traces"
TRACE_DIR.mkdir(exist_ok=True)


def write_line(f, addr: int, size: int = ELEMENT_SIZE):
    f.write(f"r 0x{addr:x} 0x{size:x}\n")


def generate_sequential(filename: Path):
    with filename.open("w") as f:
        for i in range(N_SEQUENTIAL):
            addr = BASE_ADDR + i * ELEMENT_SIZE
            write_line(f, addr)


def generate_strided(filename: Path):
    with filename.open("w") as f:
        for i in range(N_STRIDED):
            addr = BASE_ADDR + i * STRIDE_BYTES
            write_line(f, addr)


def generate_random(filename: Path):
    indices = list(range(N_SEQUENTIAL))
    random.shuffle(indices)
    with filename.open("w") as f:
        for idx in indices:
            addr = BASE_ADDR + idx * ELEMENT_SIZE
            write_line(f, addr)


def main():
    generate_sequential(TRACE_DIR / "sequential.din")
    generate_strided(TRACE_DIR / "strided.din")
    generate_random(TRACE_DIR / "random.din")


if __name__ == "__main__":
    main()
