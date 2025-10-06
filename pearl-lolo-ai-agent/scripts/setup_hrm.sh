#!/usr/bin/env bash
set -euo pipefail

# Simple bootstrapper for fetching Sapient's HRM repository and installing dependencies.
# Usage: ./scripts/setup_hrm.sh [target_directory]

REPO_URL="https://github.com/sapientinc/HRM.git"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${1:-${PROJECT_ROOT}/external/hrm}"

mkdir -p "${TARGET_DIR%/*}"

if [ -d "${TARGET_DIR}/.git" ]; then
  echo "[setup_hrm] Existing HRM checkout detected at ${TARGET_DIR}. Pulling latest changes..."
  git -C "${TARGET_DIR}" pull --ff-only
else
  echo "[setup_hrm] Cloning HRM into ${TARGET_DIR}"
  git clone "${REPO_URL}" "${TARGET_DIR}"
fi

if [ ! -f "${TARGET_DIR}/requirements.txt" ]; then
  echo "[setup_hrm] requirements.txt not found in HRM repo. Please verify the repository structure." >&2
  exit 1
fi

echo "[setup_hrm] Installing Python dependencies for HRM"
python3 -m pip install -r "${TARGET_DIR}/requirements.txt"

echo "[setup_hrm] Downloading default checkpoints"
python3 "${TARGET_DIR}/scripts/download_models.py"

echo "[setup_hrm] HRM environment ready. Configure the service endpoint in config.yaml."
