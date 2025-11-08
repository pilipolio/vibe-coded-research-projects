# Leela Chess Zero (Lc0) ONNX Conversion Guide

## Overview

This guide provides a comprehensive overview of converting Leela Chess Zero (Lc0) models from their native format to ONNX (Open Neural Network Exchange) format for use in standard machine learning tools and frameworks.

## Quick Start: Practical Example

Here's a complete walkthrough using a specific Lc0 network to get you started quickly.

### Example Network: T1-256x10-distilled-swa-2432500

This example uses the **T1-256x10** architecture, a distilled network optimized for efficiency:

**Network Details:**
- **Name:** T1-256x10-distilled-swa-2432500
- **Architecture:** T1 (Transformer-based) with 256 channels and 10 blocks
- **Type:** Distilled with Stochastic Weight Averaging (SWA)
- **Download URL:** https://storage.lczero.org/files/networks-contrib/t1-256x10-distilled-swa-2432500.pb.gz

### Step-by-Step Conversion

#### Step 1: Download the Network

```bash
# Download using wget
wget https://storage.lczero.org/files/networks-contrib/t1-256x10-distilled-swa-2432500.pb.gz

# Or using curl
curl -O https://storage.lczero.org/files/networks-contrib/t1-256x10-distilled-swa-2432500.pb.gz
```

#### Step 2: Verify the Download

```bash
# Check file size and integrity
ls -lh t1-256x10-distilled-swa-2432500.pb.gz

# Expected: File should be several hundred MB
```

#### Step 3: Convert to ONNX Using Lc0

**Option A: Using ONNX-TRT Backend (Automatic Conversion)**

```bash
# Run with ONNX backend - conversion happens automatically
lc0 --backend=onnx-trt \
    --weights=t1-256x10-distilled-swa-2432500.pb.gz \
    --backend-opts=gpu=0

# The engine will convert internally and cache the ONNX model
```

**Option B: Export ONNX Model (If Supported)**

```bash
# Some Lc0 versions support direct ONNX export
# Check your Lc0 version documentation for exact syntax

lc0 --backend=onnx-trt \
    --weights=t1-256x10-distilled-swa-2432500.pb.gz \
    --export-onnx=t1-256x10-distilled.onnx
```

#### Step 4: Use the ONNX Model

```python
import onnxruntime as ort
import numpy as np

# Load the converted or exported ONNX model
session = ort.InferenceSession("t1-256x10-distilled.onnx")

# Display model information
print("Model Inputs:")
for inp in session.get_inputs():
    print(f"  Name: {inp.name}, Shape: {inp.shape}, Type: {inp.type}")

print("\nModel Outputs:")
for out in session.get_outputs():
    print(f"  Name: {out.name}, Shape: {out.shape}, Type: {out.type}")

# Example inference (input format depends on Lc0's encoding)
# This is a placeholder - actual input encoding requires Lc0's board representation
input_name = session.get_inputs()[0].name
dummy_input = np.random.randn(1, 112, 8, 8).astype(np.float32)

# Run inference
outputs = session.run(None, {input_name: dummy_input})

print(f"\nInference complete. Output shapes:")
for i, output in enumerate(outputs):
    print(f"  Output {i}: {output.shape}")
```

### Network-Specific Considerations

**T1 Architecture:**
- Uses Transformer-based attention mechanisms
- More memory-efficient than some larger networks
- Good balance between strength and speed

**Distilled Networks:**
- Trained to match stronger networks with fewer parameters
- Faster inference times
- Slightly lower strength but excellent for resource-constrained environments

**SWA (Stochastic Weight Averaging):**
- Improves generalization
- More stable evaluations
- Better convergence properties

## Understanding Lc0 Model Formats

### Native Format

Leela Chess Zero primarily uses a **custom protobuf-based format** (`.pb.gz`) for its neural network weights. This format is optimized for:
- Efficient storage and compression
- Fast loading in the Lc0 engine
- Compatibility with Lc0's custom backends
- Best performance with latest Lc0 features

### ONNX Format

While ONNX models are not directly provided on main Lc0 download pages, the Lc0 engine includes **internal conversion capabilities** to transform native weights into ONNX format for use with backends like OnnxRuntime.

## Getting Official Lc0 Weights

### Download Sources

Official and strongest networks in native `.pb.gz` format can be obtained from:

1. **Best Networks Page** (Recommended)
   - URL: https://lczero.org/play/networks/bestnets/
   - Contains the strongest and most recommended networks
   - Networks are categorized by architecture and training generation

2. **Training Networks**
   - URL: http://training.lczero.org/networks
   - Full archive of all training runs
   - Useful for research or testing specific network versions

### Network Selection

When downloading networks, consider:
- **Architecture**: Different network architectures (e.g., T60, T70, T80) have varying computational requirements
- **Strength**: Higher network IDs generally indicate stronger play
- **Size**: Larger networks require more computational resources
- **Compatibility**: Ensure the network is compatible with your Lc0 version

## Conversion Methods

### Method 1: Built-in Lc0 Conversion (Recommended)

The Lc0 engine contains built-in functionality to convert native weights to ONNX format.

#### Using the ONNX-TRT Backend

The `onnx-trt` backend automatically handles conversion internally:

```bash
# Example: Run Lc0 with ONNX-TRT backend
lc0 --backend=onnx-trt --weights=path/to/network.pb.gz
```

**Key features:**
- Automatic conversion during runtime
- Optimized for NVIDIA GPUs with TensorRT
- No manual conversion steps required
- Best performance with latest Lc0 features

#### Manual Conversion (If Supported)

Check the Lc0 documentation for specific conversion utilities:

```bash
# Example syntax (verify with current Lc0 version)
lc0 --backend=onnx-trt --export-onnx=output.onnx --weights=input.pb.gz
```

**Note:** Manual conversion syntax may vary by Lc0 version. Refer to the official documentation.

### Method 2: Using Lc0's Conversion Tools

For standalone conversion without running the engine:

1. **Clone the Lc0 repository:**
   ```bash
   git clone https://github.com/LeelaChessZero/lc0.git
   cd lc0
   ```

2. **Build with ONNX support:**
   ```bash
   # Build instructions vary by platform
   # Ensure ONNX libraries are available
   meson build --backend vs2019  # Windows example
   # or
   ./build.sh  # Linux/Mac example
   ```

3. **Check for conversion utilities:**
   ```bash
   # Look for conversion scripts in scripts/ or tools/ directory
   ls scripts/
   ls tools/
   ```

### Method 3: Community Tools

Some community repositories may provide:
- Pre-converted ONNX models
- Standalone conversion scripts
- Python-based conversion utilities

**Caution:** Community tools may not support:
- Latest network architectures
- All Lc0 features
- Optimal performance configurations

## Using ONNX Models with Lc0

### Configuration

To use ONNX models with Lc0:

```bash
# Basic ONNX backend usage
lc0 --backend=onnx-trt --weights=network.pb.gz

# With additional options
lc0 --backend=onnx-trt \
    --weights=network.pb.gz \
    --backend-opts=<options>
```

### Backend Options

Common ONNX backend options:

- **GPU Device Selection:**
  ```bash
  --backend-opts=gpu=0  # Use first GPU
  ```

- **Performance Tuning:**
  ```bash
  --backend-opts=fp16=true  # Enable FP16 precision
  ```

Refer to the [Lc0 GitHub repository](https://github.com/LeelaChessZero/lc0) for complete backend option documentation.

## Integration with Standard ML Tools

### Using Converted ONNX Models

Once you have an ONNX model, you can use it with standard tools:

#### Python with ONNX Runtime

```python
import onnxruntime as ort
import numpy as np

# Load ONNX model
session = ort.InferenceSession("lc0_network.onnx")

# Prepare input (example - actual input format may vary)
input_name = session.get_inputs()[0].name
input_data = np.random.randn(1, 112, 8, 8).astype(np.float32)

# Run inference
outputs = session.run(None, {input_name: input_data})

# Process outputs
policy, value = outputs[0], outputs[1]
```

#### TensorRT Optimization

For NVIDIA GPUs, further optimize with TensorRT:

```bash
# Convert ONNX to TensorRT engine
trtexec --onnx=lc0_network.onnx \
        --saveEngine=lc0_network.trt \
        --fp16  # Enable FP16 precision
```

### Input/Output Format

Lc0 neural networks typically expect:

**Input:**
- Shape: `[batch_size, channels, 8, 8]` (for standard chess)
- Channels: Board representation (piece positions, castling rights, etc.)
- Data type: Float32

**Output:**
- **Policy head**: Move probabilities (shape varies by architecture)
- **Value head**: Position evaluation (typically scalar or 3-class WDL)

Refer to Lc0 documentation for exact specifications.

## Best Practices and Recommendations

### When to Use ONNX Format

**✅ Use ONNX when:**
- Integrating Lc0 networks into custom ML pipelines
- Using non-Lc0 inference frameworks
- Researching network architectures
- Deploying on platforms without native Lc0 support

**❌ Avoid ONNX when:**
- Running standard chess analysis (use native Lc0 engine)
- Seeking maximum performance (native format is optimized)
- Using latest Lc0 features (may not be fully compatible)

### Official vs. Community Resources

**Prefer Official Lc0:**
- ✅ Best compatibility with latest features
- ✅ Optimal performance
- ✅ Regular updates and support
- ✅ Accurate network implementations

**Community Resources:**
- ⚠️ May lag behind official releases
- ⚠️ Varying quality and maintenance
- ⚠️ Potential compatibility issues
- ✅ Can provide convenience for specific use cases

### Performance Considerations

1. **Native format is fastest** for standard Lc0 usage
2. **ONNX-TRT backend** provides good performance for ONNX workflows
3. **Manual conversion** may introduce overhead
4. **GPU acceleration** is strongly recommended for both formats

## Troubleshooting

### Common Issues

**Issue: Conversion fails with "unsupported operation"**
- Solution: Ensure Lc0 version supports your network architecture
- Check for ONNX opset compatibility

**Issue: ONNX model gives different results than native**
- Solution: Verify conversion settings (precision, optimization levels)
- Check input preprocessing matches Lc0's expectations

**Issue: Poor performance with ONNX**
- Solution: Enable hardware acceleration (CUDA, TensorRT)
- Consider using FP16 precision
- Use optimized ONNX runtime providers

## Additional Resources

### Official Documentation

- **Lc0 GitHub:** https://github.com/LeelaChessZero/lc0
- **Official Website:** https://lczero.org/
- **Network Downloads:** https://lczero.org/play/networks/bestnets/
- **Training Data:** http://training.lczero.org/networks

### Community Resources

- **Lc0 Discord:** Community support and discussions
- **GitHub Issues:** Report bugs or ask technical questions
- **Lc0 Wiki:** Additional documentation and guides

### Related Technologies

- **ONNX Runtime:** https://onnxruntime.ai/
- **TensorRT:** https://developer.nvidia.com/tensorrt
- **Protocol Buffers:** https://protobuf.dev/

## Transfer Learning and Explainability

Lc0 networks provide rich intermediate features that can be used for:
- **Explainability:** Understanding what the network "sees" in a position
- **Concept Extraction:** Training probes to detect specific chess concepts
- **Transfer Learning:** Adapting to related tasks (variants, analysis tools, teaching)
- **Attention Visualization:** Visualizing which board positions the network focuses on

### Key Feature Layer

For the **T1-256x10** network (used in this guide):

- **Last Shared Layer:** `encoder_layer_9_output`
- **Dimensions:** `[batch_size, 64, 256]`
  - 64 = 8×8 chess board positions
  - 256 = feature dimension per position
- **Use:** Extract before policy/value heads for transfer learning

### Example Use Cases

**1. Concept Probing:**
```python
# Extract features from last encoder layer
features = extract_encoder_output(position)  # [64, 256]

# Train linear probe for specific concepts
probe = LinearProbe(256, num_concepts)
concepts = probe(features)
# e.g., "has_passed_pawn", "king_safety", "piece_activity"
```

**2. Position Similarity:**
```python
# Compare positions based on Lc0 features
features_A = extract_encoder_output(position_A).mean(axis=0)  # [256]
features_B = extract_encoder_output(position_B).mean(axis=0)  # [256]

similarity = cosine_similarity(features_A, features_B)
```

**3. Tactical Motif Detection:**
```python
# Use position-specific features
features_per_square = extract_encoder_output(position)  # [64, 256]

# Train classifier to detect pins, forks, etc.
motif_classifier = TacticalClassifier(256)
motifs = motif_classifier(features_per_square)
```

For detailed examples, code, and best practices, see:
- **[lc0_models/TRANSFER_LEARNING.md](../lc0_models/TRANSFER_LEARNING.md)**
- **Network Inspector Tool:** `lc0_models/lc0_network_inspector.py`

## Conclusion

While Lc0's native `.pb.gz` format is recommended for standard usage, ONNX conversion capabilities enable integration with broader ML ecosystems. The Lc0 engine's built-in conversion features provide the most reliable path for creating ONNX models, ensuring compatibility and performance.

For the best chess-playing experience and latest features, use the official Lc0 engine with native format weights. For research, integration, or custom ML workflows, ONNX conversion provides flexibility while maintaining the power of Lc0's neural networks.

The intermediate features from Lc0 networks (particularly the last encoder output) provide a powerful foundation for explainability research, concept extraction, and transfer learning to related chess tasks.

---

*This guide is based on Lc0 project practices as of 2025. For the most current information, always refer to the official Lc0 GitHub repository and documentation.*
