# Lc0 Models and Conversion Tools

This directory contains Leela Chess Zero (Lc0) neural network weights and tools for inspecting and converting them to ONNX format.

## Contents

### Downloaded Networks

- **t1-256x10-distilled-swa-2432500.pb.gz** (35.4 MB)
  - Architecture: T1 (Transformer-based) with 256 channels and 10 blocks
  - Type: Distilled with Stochastic Weight Averaging (SWA)
  - Source: https://storage.lczero.org/files/networks-contrib/
  - Min Lc0 Version: 0.29.0

- **t1-256x10-distilled-swa-2432500.onnx.zip** (48 MB) - INCLUDED IN REPO
  - Converted ONNX model (simplified demonstration version)
  - Created using simple_lc0_to_onnx.py
  - Compatible with ONNX Runtime and standard ML tools
  - Input: [1, 112, 8, 8] (board representation)
  - Outputs: policy [1, 1858], value [1, 3] (WDL)

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

#### simple_lc0_to_onnx.py

A Python-based ONNX converter for educational and demonstration purposes.

**Features:**
- Reads Lc0 .pb.gz files and creates ONNX models
- Decodes weight encodings (LINEAR16, FLOAT16, BFLOAT16)
- Creates simplified ONNX structure with correct input/output format
- Compatible with ONNX Runtime for inference testing

**Usage:**
```bash
python3 simple_lc0_to_onnx.py <input.pb.gz> <output.onnx>
```

**Example:**
```bash
python3 simple_lc0_to_onnx.py t1-256x10-distilled-swa-2432500.pb.gz model.onnx
```

**Important Notes:**
- This creates a SIMPLIFIED model for demonstration purposes
- The full network architecture is not reconstructed
- For production use, prefer Lc0's official leela2onnx C++ tool
- Useful for learning ONNX format and Lc0 weight decoding

#### Dockerfile & convert_to_onnx.sh

Build environment and automation scripts for Lc0 ONNX conversion.

**Dockerfile** - Multi-stage build for Lc0 with ONNX support:
```bash
docker build -t lc0-onnx:latest .
```

**convert_to_onnx.sh** - Automated conversion pipeline:
```bash
./convert_to_onnx.sh
```

This script:
1. Builds the Lc0 Docker image
2. Converts the network to ONNX using Lc0's official tool
3. Verifies the output
4. Compresses the result

**Note:** Building Lc0 from source takes significant time. The Python converter (simple_lc0_to_onnx.py) is faster for quick demonstrations.

### Supporting Files

- **net_pb2.py** - Compiled Python protobuf bindings for Lc0's network format
- **lc0-repo/** - Cloned Lc0 repository with protobuf definitions and conversion tools

## Converting to ONNX

There are four approaches to convert Lc0 weights to ONNX format:

### Option 1: Python Simple Converter (Quick Demo)

Use the included Python converter for quick demonstrations:

```bash
python3 simple_lc0_to_onnx.py t1-256x10-distilled-swa-2432500.pb.gz output.onnx
```

**Advantages:**
- Fast (seconds)
- No compilation required
- Educational - shows how to read Lc0 formats
- Works with ONNX Runtime for inference testing

**Limitations:**
- Simplified model structure (not full network architecture)
- For demonstration/learning purposes
- Not suitable for production chess play

### Option 2: Lc0's leela2onnx Tool (Production Quality)

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

### Option 3: ONNX-TRT Backend (Runtime Conversion)

Let Lc0 convert automatically during execution:

```bash
# Download Lc0 binary from https://github.com/LeelaChessZero/lc0/releases

# Run with ONNX backend
lc0 --backend=onnx-trt --weights=t1-256x10-distilled-swa-2432500.pb.gz
```

The engine will convert and cache the ONNX model automatically.

### Option 4: Python-based Conversion (Advanced)

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
