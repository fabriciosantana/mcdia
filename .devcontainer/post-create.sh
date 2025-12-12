#!/usr/bin/env bash
set -euo pipefail

CONDA_DIR=/opt/conda
source "${CONDA_DIR}/etc/profile.d/conda.sh"
conda activate mcdia

python -m ipykernel install --user --name mcdia --display-name "Python (mcdia)"

if [ -f ".pre-commit-config.yaml" ]; then
  pre-commit install
fi

conda env export -n mcdia > /workspaces/mcdia/environment.lock.yml
