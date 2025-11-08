# Dockerfile for Lc0 ONNX Conversion
# This builds Lc0 from source with ONNX support and converts networks to ONNX format

FROM ubuntu:22.04 AS builder

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    ninja-build \
    pkg-config \
    libgtest-dev \
    protobuf-compiler \
    libprotobuf-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install meson via pip
RUN pip3 install meson

# Clone Lc0 repository
WORKDIR /opt
RUN git clone https://github.com/LeelaChessZero/lc0.git
WORKDIR /opt/lc0

# Build Lc0 with ONNX support
# Using plain backend which includes ONNX conversion tools
RUN ./build.sh -Dplain=true

# Runtime stage
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libprotobuf32 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy built Lc0 binary from builder
COPY --from=builder /opt/lc0/build/release/lc0 /usr/local/bin/lc0

# Create working directory
WORKDIR /workspace

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/lc0"]
CMD ["--help"]
