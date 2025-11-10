#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
D4_DIR="${ROOT_DIR}/dineroIV_src"

if [[ -x "${D4_DIR}/dineroIV" ]]; then
  echo "DineroIV already built at ${D4_DIR}/dineroIV"
  exit 0
fi

for cmd in git make cc; do
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "ERROR: Required tool '${cmd}' is not available."
    echo "Install Xcode Command Line Tools with:"
    echo "  xcode-select --install"
    exit 1
  fi
done

echo "[install_dinero] Cloning DineroIV sources..."
git clone https://github.com/atos-tools/dineroIV.git "${D4_DIR}"

cd "${D4_DIR}"
echo "[install_dinero] Running ./configure ..."
./configure
echo "[install_dinero] Building with make ..."
make
echo "[install_dinero] Done. Binary at ${D4_DIR}/dineroIV"
