#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"${ROOT_DIR}/scripts/install_dinero.sh"

D4_DIR="${ROOT_DIR}/dineroIV_src"
D4_BIN="${D4_DIR}/dineroIV"

if [[ ! -x "${D4_BIN}" ]]; then
  echo "ERROR: DineroIV binary not found at ${D4_BIN}"
  exit 1
fi

VENV_DIR="${ROOT_DIR}/.venv"
if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[run_sims] Creating Python virtualenv at ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

echo "[run_sims] Installing Python dependencies (pandas, matplotlib)..."
pip install --quiet --upgrade pip
pip install --quiet pandas matplotlib

echo "[run_sims] Generating synthetic traces..."
python "${ROOT_DIR}/analysis/generate_traces.py"

TRACES_DIR="${ROOT_DIR}/traces"
RESULTS_DIR="${ROOT_DIR}/results"
mkdir -p "${RESULTS_DIR}"

INFMT="-informat D"
L1_BASE="-l1-dsize 32k -l1-dassoc 4 -l1-drepl l -l1-dfetch d -l1-dwalloc a -l1-dwback a"
L2_BASE="-l2-usize 256k -l2-uassoc 8 -l2-urepl l -l2-ufetch d -l2-uwalloc a -l2-uwback a"

WORKLOADS=(sequential strided random)
LINES=(32 128)

for wl in "${WORKLOADS[@]}"; do
  TRACE="${TRACES_DIR}/${wl}.din"
  if [[ ! -f "${TRACE}" ]]; then
    echo "ERROR: Missing trace ${TRACE}"
    exit 1
  fi

  for line in "${LINES[@]}"; do
    OUT="${RESULTS_DIR}/${wl}_${line}B.txt"
    echo "[run_sims] Running workload='${wl}', line=${line}B"

    L1_CFG="${L1_BASE} -l1-dbsize ${line}"
    L2_CFG="${L2_BASE} -l2-ubsize ${line}"

    "${D4_BIN}" ${INFMT} ${L1_CFG} ${L2_CFG} < "${TRACE}" > "${OUT}"
  done
done

echo "[run_sims] All runs complete. Parsing + plotting..."
python "${ROOT_DIR}/analysis/analyze_results.py"
