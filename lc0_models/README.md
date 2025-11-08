# Lc0 Models and Conversion Tools

This directory contains Leela Chess Zero (Lc0) neural network weights and tools for inspecting and converting them to ONNX format.

## Contents

### Downloaded Networks

- **t1-256x10-distilled-swa-2432500.pb.gz** (35.4 MB)
  - Architecture: T1 (Transformer-based) with 256 channels and 10 blocks
  - Type: Distilled with Stochastic Weight Averaging (SWA)
  - Source: https://storage.lczero.org/files/networks-contrib/
  - Min Lc0 Version: 0.29.0

### Tools

#### lc0_network_inspector.py

A Python script for inspecting Lc0 network files and providing ONNX conversion guidance.

**Features:**
- Reads and parses Lc0 .pb.gz weight files
- Displays network architecture information
- Shows layer dimensions and parameter counts
- Provides step-by-step ONNX conversion instructions

**Usage:**
```bash
python3 lc0_network_inspector.py <network_file.pb.gz>
```

**Example:**
```bash
python3 lc0_network_inspector.py t1-256x10-distilled-swa-2432500.pb.gz
```

**Output includes:**
- Network format and version information
- Architecture type (Residual CNN vs Transformer)
- Encoder/residual block counts
- Policy, value, and MLH head information
- Total parameter count and memory estimates
- Detailed ONNX conversion guidance

### Supporting Files

- **net_pb2.py** - Compiled Python protobuf bindings for Lc0's network format
- **lc0-repo/** - Cloned Lc0 repository with protobuf definitions and conversion tools

## Converting to ONNX

There are three main approaches to convert Lc0 weights to ONNX format:

### Option 1: Lc0's leela2onnx Tool (Recommended)

Build and use Lc0's official conversion tool:

```bash
# Clone and build Lc0
git clone https://github.com/LeelaChessZero/lc0.git
cd lc0
./build.sh

# Convert to ONNX
./build/lc0 leela2onnx \
    --input=t1-256x10-distilled-swa-2432500.pb.gz \
    --output=t1-256x10-distilled.onnx \
    --onnx-batch-size=1 \
    --onnx-data-type=float32 \
    --onnx-opset=14
```

### Option 2: ONNX-TRT Backend (Runtime Conversion)

Let Lc0 convert automatically during execution:

```bash
# Download Lc0 binary from https://github.com/LeelaChessZero/lc0/releases

# Run with ONNX backend
lc0 --backend=onnx-trt --weights=t1-256x10-distilled-swa-2432500.pb.gz
```

The engine will convert and cache the ONNX model automatically.

### Option 3: Python-based Conversion (Advanced)

For custom conversion logic, you can extend `lc0_network_inspector.py` to build ONNX graphs using the `onnx` Python library. This requires deep understanding of both Lc0 and ONNX formats.

Reference implementation: `lc0-repo/src/neural/onnx/converter.cc`

## Using Converted ONNX Models

### Python with ONNX Runtime

```python
import onnxruntime as ort
import numpy as np

# Load ONNX model
session = ort.InferenceSession("t1-256x10-distilled.onnx")

# Display model information
for inp in session.get_inputs():
    print(f"Input: {inp.name}, Shape: {inp.shape}, Type: {inp.type}")

for out in session.get_outputs():
    print(f"Output: {out.name}, Shape: {out.shape}, Type: {out.type}")

# Run inference
input_name = session.get_inputs()[0].name
input_data = np.random.randn(1, 112, 8, 8).astype(np.float32)
outputs = session.run(None, {input_name: input_data})

print(f"Policy output shape: {outputs[0].shape}")
print(f"Value output shape: {outputs[1].shape}")
```

### TensorRT Optimization (NVIDIA GPUs)

```bash
# Convert ONNX to TensorRT engine for optimized inference
trtexec --onnx=t1-256x10-distilled.onnx \
        --saveEngine=t1-256x10-distilled.trt \
        --fp16
```

## Network Architecture: T1-256x10

The T1 architecture is a Transformer-based neural network designed for chess:

**Key Features:**
- **Transformer encoders**: Uses attention mechanisms instead of traditional CNNs
- **256 channels**: Feature dimension for internal representations
- **10 blocks**: Number of transformer encoder layers
- **Distilled**: Trained to match stronger networks with fewer parameters
- **SWA (Stochastic Weight Averaging)**: Improves generalization and stability

**Advantages:**
- More memory-efficient than larger CNN-based networks
- Better at capturing long-range dependencies on the chess board
- Good balance between playing strength and inference speed
- Suitable for resource-constrained environments

## Requirements

- Python 3.8+
- protobuf
- onnx
- numpy

Install dependencies:
```bash
pip install protobuf onnx numpy
```

For running ONNX models:
```bash
pip install onnxruntime
```

## References

- **Lc0 Official Website**: https://lczero.org/
- **Lc0 GitHub**: https://github.com/LeelaChessZero/lc0
- **Best Networks**: https://lczero.org/play/networks/bestnets/
- **Training Networks**: http://training.lczero.org/networks
- **ONNX Documentation**: https://onnx.ai/
- **Comprehensive Guide**: See `../docs/LC0_ONNX_CONVERSION.md`

## License

The Lc0 networks and tools are licensed under GPL v3. See the Lc0 repository for full license information.
