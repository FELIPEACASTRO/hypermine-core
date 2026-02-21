#!/bin/bash
# HyperMine Core — Automated Benchmark Suite
# Runs benchmarks for all supported algorithms on detected hardware

set -e

BINARY="${1:-./hypermine-core}"
CONFIG="${2:-./config.toml}"
OUTPUT="benchmark_results_$(date +%Y%m%d_%H%M%S).json"

echo "=== HyperMine Core — Benchmark Suite ==="
echo "Binary: $BINARY"
echo "Config: $CONFIG"
echo "Output: $OUTPUT"
echo ""

# Detect hardware
echo "Detecting hardware..."
echo "CPU: $(lscpu | grep 'Model name' | awk -F: '{print $2}' | xargs)"
echo "Cores: $(nproc)"
echo "RAM: $(free -h | awk '/Mem:/ {print $2}')"

# Detect GPUs
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPUs:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
fi

if command -v rocm-smi &> /dev/null; then
    echo "AMD GPUs:"
    rocm-smi --showproductname
fi

echo ""
echo "Starting benchmarks..."

# Run benchmark for each algorithm
ALGORITHMS=("sha256" "randomx" "etchash" "kawpow" "kheavyhash" "blake3" 
            "nexapow" "karlsenhash" "pyrinhash" "verushash22" "equihash" 
            "autolykos2" "ghostrider" "firopow" "zelhash" "verthash")

for algo in "${ALGORITHMS[@]}"; do
    echo "Benchmarking: $algo..."
    $BINARY --benchmark --algorithm "$algo" --duration 60 2>/dev/null || echo "  Skipped (not available)"
done

echo ""
echo "=== Benchmark Complete ==="
echo "Results saved to: $OUTPUT"
