#!/bin/bash
# HyperMine Core — Farm Deploy Script
# Deploys or updates HyperMine Core across all mining nodes

set -e

VERSION="${1:-latest}"
INVENTORY="${2:-inventory.yml}"

echo "=== HyperMine Core — Farm Deploy ==="
echo "Version: $VERSION"
echo "Inventory: $INVENTORY"

# Check Ansible
if ! command -v ansible-playbook &> /dev/null; then
    echo "Error: Ansible is required. Install with: pip install ansible"
    exit 1
fi

# Deploy
echo "Deploying HyperMine Core v${VERSION} to all nodes..."
ansible-playbook -i "$INVENTORY" deploy_miner.yml \
    -e "hypermine_version=${VERSION}" \
    --diff

echo "=== Deploy Complete ==="
