#!/bin/bash
# Script to build Lc0 Docker image and convert network to ONNX

set -e

NETWORK_FILE="t1-256x10-distilled-swa-2432500.pb.gz"
OUTPUT_FILE="t1-256x10-distilled-swa-2432500.onnx"

echo "======================================================================"
echo "Lc0 ONNX Conversion Script"
echo "======================================================================"
echo ""

# Check if network file exists
if [ ! -f "$NETWORK_FILE" ]; then
    echo "Error: Network file '$NETWORK_FILE' not found!"
    echo "Please download it first:"
    echo "  wget https://storage.lczero.org/files/networks-contrib/$NETWORK_FILE"
    exit 1
fi

echo "Network file: $NETWORK_FILE"
echo "Output file: $OUTPUT_FILE"
echo ""

# Build Docker image
echo "Step 1: Building Lc0 Docker image..."
echo "----------------------------------------------------------------------"
docker build -t lc0-onnx:latest .

echo ""
echo "Step 2: Converting network to ONNX..."
echo "----------------------------------------------------------------------"

# Run conversion in Docker container
# Mount current directory to /workspace
docker run --rm \
    -v "$(pwd):/workspace" \
    lc0-onnx:latest \
    leela2onnx \
    --input="/workspace/$NETWORK_FILE" \
    --output="/workspace/$OUTPUT_FILE" \
    --onnx-batch-size=1 \
    --onnx-data-type=float32 \
    --value-head=winner \
    --policy-head=vanilla

echo ""
echo "Step 3: Verifying output..."
echo "----------------------------------------------------------------------"

if [ -f "$OUTPUT_FILE" ]; then
    OUTPUT_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
    echo "✓ Conversion successful!"
    echo "  Output file: $OUTPUT_FILE"
    echo "  Size: $OUTPUT_SIZE"
    echo ""

    # Compress the ONNX file
    echo "Step 4: Compressing ONNX file..."
    echo "----------------------------------------------------------------------"
    zip "${OUTPUT_FILE%.onnx}.onnx.zip" "$OUTPUT_FILE"
    ZIP_SIZE=$(ls -lh "${OUTPUT_FILE%.onnx}.onnx.zip" | awk '{print $5}')
    echo "✓ Compression complete!"
    echo "  Zip file: ${OUTPUT_FILE%.onnx}.onnx.zip"
    echo "  Size: $ZIP_SIZE"
else
    echo "✗ Conversion failed - output file not found"
    exit 1
fi

echo ""
echo "======================================================================"
echo "Conversion complete!"
echo "======================================================================"
echo ""
echo "Files created:"
echo "  - $OUTPUT_FILE (ONNX model)"
echo "  - ${OUTPUT_FILE%.onnx}.onnx.zip (compressed)"
echo ""
echo "You can now use the ONNX model with ONNX Runtime or other tools."
