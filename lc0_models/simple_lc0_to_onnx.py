#!/usr/bin/env python3
"""
Simple Lc0 to ONNX Converter

This script creates a simplified ONNX representation of an Lc0 network.
Note: This creates a structural representation but may not include all operational details.
For production use, prefer Lc0's official leela2onnx C++ tool.

Usage:
    python3 simple_lc0_to_onnx.py <input.pb.gz> <output.onnx>
"""

import gzip
import sys
import argparse
from pathlib import Path
import struct

import onnx
from onnx import helper, TensorProto
import numpy as np
import net_pb2


def decode_layer_to_numpy(layer):
    """Decode an Lc0 layer to numpy array."""
    if not layer.HasField('params'):
        return None

    params_bytes = layer.params
    dims = list(layer.dims)

    if len(dims) == 0:
        return None

    total_size = 1
    for dim in dims:
        total_size *= dim

    encoding = layer.encoding if layer.HasField('encoding') else net_pb2.Weights.Layer.LINEAR16

    # Decode based on encoding type
    if encoding == net_pb2.Weights.Layer.LINEAR16:
        # LINEAR16: quantized 16-bit values
        min_val = layer.min_val if layer.HasField('min_val') else -1.0
        max_val = layer.max_val if layer.HasField('max_val') else 1.0

        # Read as uint16
        values = np.frombuffer(params_bytes, dtype=np.uint16)

        # Dequantize: map [0, 65535] to [min_val, max_val]
        values = values.astype(np.float32)
        values = min_val + (values / 65535.0) * (max_val - min_val)

    elif encoding == net_pb2.Weights.Layer.FLOAT16:
        # Direct FP16
        values = np.frombuffer(params_bytes, dtype=np.float16).astype(np.float32)

    elif encoding == net_pb2.Weights.Layer.BFLOAT16:
        # BF16 - need special handling
        values = np.frombuffer(params_bytes, dtype=np.uint16)
        # BF16 to FP32: shift left by 16 bits
        fp32_bits = values.astype(np.uint32) << 16
        values = fp32_bits.view(np.float32)
    else:
        print(f"Warning: Unknown encoding {encoding}, treating as float16")
        values = np.frombuffer(params_bytes, dtype=np.float16).astype(np.float32)

    # Reshape to specified dimensions
    try:
        return values[:total_size].reshape(dims)
    except:
        print(f"Warning: Could not reshape {len(values)} values to {dims}")
        return values[:total_size]


def create_simple_onnx_model(net_file, output_file, batch_size=1):
    """
    Create a simplified ONNX model from Lc0 network.
    This creates a mock structure for demonstration purposes.
    """
    print(f"Reading network from {net_file}...")

    # Read the network file
    with gzip.open(net_file, 'rb') as f:
        net_data = f.read()

    net = net_pb2.Net()
    net.ParseFromString(net_data)

    if not net.HasField('weights'):
        print("Error: No weights in network file!")
        return False

    weights = net.weights

    print(f"Creating ONNX model...")
    print(f"  Batch size: {batch_size}")

    # Create input tensor (standard Lc0 input: 112 planes, 8x8 board)
    input_shape = [batch_size, 112, 8, 8]
    input_tensor = helper.make_tensor_value_info('input', TensorProto.FLOAT, input_shape)

    # Create output tensors
    # Policy: 1858 possible moves in chess
    policy_shape = [batch_size, 1858]
    policy_output = helper.make_tensor_value_info('policy', TensorProto.FLOAT, policy_shape)

    # Value: WDL (Win/Draw/Loss) - 3 values
    value_shape = [batch_size, 3]
    value_output = helper.make_tensor_value_info('value', TensorProto.FLOAT, value_shape)

    # Create a simple identity-like graph for demonstration
    # In a real conversion, this would build the full network architecture

    nodes = []
    initializers = []

    # Add a simple placeholder convolution to demonstrate weight extraction
    if weights.HasField('input') and weights.input.HasField('weights'):
        print("  Extracting input embedding weights...")
        input_weights_np = decode_layer_to_numpy(weights.input.weights)
        if input_weights_np is not None:
            print(f"    Input weights shape: {input_weights_np.shape}")
            # Store as constant
            input_weights_tensor = helper.make_tensor(
                name='input_weights',
                data_type=TensorProto.FLOAT,
                dims=input_weights_np.shape,
                vals=input_weights_np.flatten().tolist()
            )
            initializers.append(input_weights_tensor)

    # Add placeholder nodes (simplified network)
    # Note: This is a mock structure - real conversion needs full architecture

    # Flatten input for demonstration
    flatten_node = helper.make_node(
        'Flatten',
        inputs=['input'],
        outputs=['flattened'],
        axis=1
    )
    nodes.append(flatten_node)

    # Create dummy weight matrices for policy and value heads
    input_size = 112 * 8 * 8  # 7168

    # Policy head: simple linear projection
    policy_weights = np.random.randn(1858, input_size).astype(np.float32) * 0.01
    policy_weights_tensor = helper.make_tensor(
        name='policy_weights',
        data_type=TensorProto.FLOAT,
        dims=[1858, input_size],
        vals=policy_weights.flatten().tolist()
    )
    initializers.append(policy_weights_tensor)

    # Transpose policy weights to match flattened input
    policy_weights_transposed = policy_weights.T  # Now [input_size, 1858]

    policy_weights_tensor = helper.make_tensor(
        name='policy_weights',
        data_type=TensorProto.FLOAT,
        dims=list(policy_weights_transposed.shape),
        vals=policy_weights_transposed.flatten().tolist()
    )
    # Update initializer
    initializers[-1] = policy_weights_tensor

    policy_matmul = helper.make_node(
        'MatMul',
        inputs=['flattened', 'policy_weights'],
        outputs=['policy']
    )
    nodes.append(policy_matmul)

    # Value head: simple linear projection
    value_weights = np.random.randn(3, input_size).astype(np.float32) * 0.01
    value_weights_transposed = value_weights.T  # Now [input_size, 3]

    value_weights_tensor = helper.make_tensor(
        name='value_weights',
        data_type=TensorProto.FLOAT,
        dims=list(value_weights_transposed.shape),
        vals=value_weights_transposed.flatten().tolist()
    )
    initializers.append(value_weights_tensor)

    value_matmul = helper.make_node(
        'MatMul',
        inputs=['flattened', 'value_weights'],
        outputs=['value']
    )
    nodes.append(value_matmul)

    # Create the graph
    graph_def = helper.make_graph(
        nodes,
        'lc0-simplified',
        [input_tensor],
        [policy_output, value_output],
        initializer=initializers
    )

    # Create the model (using IR version 8 for better compatibility)
    model_def = helper.make_model(
        graph_def,
        producer_name='lc0-simple-converter',
        opset_imports=[helper.make_opsetid("", 13)]
    )

    # Set IR version to 8 for compatibility with older ONNX Runtime
    model_def.ir_version = 8

    # Add metadata
    model_def.doc_string = f"Simplified ONNX model from Lc0 network: {Path(net_file).name}"

    # Check the model
    try:
        onnx.checker.check_model(model_def)
        print("  Model validation: OK")
    except Exception as e:
        print(f"  Model validation warning: {e}")

    # Save the model
    print(f"Saving ONNX model to {output_file}...")
    onnx.save(model_def, output_file)

    output_size = Path(output_file).stat().st_size
    print(f"  Output size: {output_size / (1024*1024):.2f} MB")

    print("\n" + "="*80)
    print("IMPORTANT NOTE")
    print("="*80)
    print("This is a SIMPLIFIED/MOCK ONNX model for demonstration purposes.")
    print("It extracts some weights but does not recreate the full network architecture.")
    print("")
    print("For production use, please use Lc0's official leela2onnx tool:")
    print("  https://github.com/LeelaChessZero/lc0")
    print("")
    print("This simplified model demonstrates:")
    print("  ✓ How to read Lc0 .pb.gz files")
    print("  ✓ How to decode weight encodings (LINEAR16, FLOAT16, BFLOAT16)")
    print("  ✓ Basic ONNX model structure")
    print("  ✓ Input/output tensor formats")
    print("="*80 + "\n")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Simple Lc0 to ONNX converter (demonstration/educational)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('input', type=str, help='Input Lc0 network file (.pb.gz)')
    parser.add_argument('output', type=str, help='Output ONNX file (.onnx)')
    parser.add_argument('--batch-size', type=int, default=1,
                        help='Batch size for ONNX model (default: 1)')

    args = parser.parse_args()

    input_file = Path(args.input)
    output_file = Path(args.output)

    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found!")
        sys.exit(1)

    try:
        success = create_simple_onnx_model(input_file, output_file, args.batch_size)
        if success:
            print("Conversion completed successfully!")
            sys.exit(0)
        else:
            print("Conversion failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
