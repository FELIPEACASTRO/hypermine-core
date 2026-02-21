#!/bin/bash
# HyperMine Core — NUMA Optimization Setup
# Configures NUMA-aware memory allocation for optimal mining performance

set -e

echo "=== HyperMine Core — NUMA Setup ==="

# Check NUMA availability
if ! command -v numactl &> /dev/null; then
    echo "Installing numactl..."
    sudo apt-get install -y numactl
fi

# Display NUMA topology
echo "NUMA Topology:"
numactl --hardware

# Set NUMA interleave policy for mining processes
echo "Setting NUMA memory policy..."
echo "Use: numactl --interleave=all ./hypermine-core --config config.toml"
echo "Or for specific NUMA node: numactl --cpunodebind=0 --membind=0 ./hypermine-core"

echo "=== NUMA Setup Complete ==="
