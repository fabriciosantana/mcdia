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

# Configure Docker to use vfs in Codespaces/devcontainers, where overlayfs
# may fail with "invalid argument" on container startup.
#sudo mkdir -p /etc/docker
#cat <<'EOF' | sudo tee /etc/docker/daemon.json >/dev/null
#{
#  "storage-driver": "vfs"
#}
#EOF
