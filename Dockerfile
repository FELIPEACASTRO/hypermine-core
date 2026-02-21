# ============================================================================
# HyperMine Core — Multi-Stage Docker Build
# ============================================================================
# Build: docker build -t hypermine-core .
# Run:   docker run --gpus all -v $(pwd)/config.toml:/etc/hypermine/config.toml hypermine-core
# ============================================================================

# Stage 1: Build environment
FROM nvidia/cuda:12.6.0-devel-ubuntu24.04 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    ninja-build \
    git \
    curl \
    pkg-config \
    libssl-dev \
    nasm \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy source code
WORKDIR /build
COPY . .

# Build with maximum optimizations
RUN mkdir -p build && cd build \
    && cmake .. \
        -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DENABLE_CUDA=ON \
        -DENABLE_OPENCL=OFF \
        -DENABLE_LTO=ON \
        -DENABLE_TESTS=OFF \
        -DENABLE_BENCH=OFF \
    && ninja -j$(nproc)

# Stage 2: Runtime environment (minimal)
FROM nvidia/cuda:12.6.0-runtime-ubuntu24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy binary and configs
COPY --from=builder /build/build/hypermine /usr/local/bin/hypermine
COPY config.toml /etc/hypermine/config.toml
COPY coins/ /etc/hypermine/coins/

# Create non-root user
RUN useradd -m -s /bin/bash hypermine
USER hypermine

WORKDIR /home/hypermine

# Expose monitoring ports
EXPOSE 8080 9090

ENTRYPOINT ["hypermine"]
CMD ["--config", "/etc/hypermine/config.toml"]
