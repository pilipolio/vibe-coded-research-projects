#!/usr/bin/env python3
"""
Lc0 Network Inspector and ONNX Conversion Helper

This script reads Lc0 neural network weight files (.pb.gz format) and provides:
1. Detailed network architecture information
2. Layer dimensions and parameter counts
3. Guidance for ONNX conversion

Usage:
    python lc0_network_inspector.py <network_file.pb.gz>

Example:
    python lc0_network_inspector.py t1-256x10-distilled-swa-2432500.pb.gz
"""

import gzip
import sys
import argparse
from pathlib import Path

# Import the generated protobuf module
import net_pb2


def decode_layer_params(layer):
    """Decode layer parameters based on encoding type."""
    if not layer.HasField('params'):
        return None

    encoding = layer.encoding if layer.HasField('encoding') else net_pb2.Weights.Layer.LINEAR16

    # Get raw bytes
    params_bytes = layer.params

    # Calculate expected size based on dims
    total_size = 1
    for dim in layer.dims:
        total_size *= dim

    encoding_names = {
        net_pb2.Weights.Layer.LINEAR16: "LINEAR16",
        net_pb2.Weights.Layer.FLOAT16: "FLOAT16",
        net_pb2.Weights.Layer.BFLOAT16: "BFLOAT16",
        net_pb2.Weights.Layer.UNKNOWN_ENCODING: "UNKNOWN"
    }

    return {
        'encoding': encoding_names.get(encoding, "UNKNOWN"),
        'total_params': total_size,
        'dims': list(layer.dims),
        'bytes': len(params_bytes),
        'min_val': layer.min_val if layer.HasField('min_val') else None,
        'max_val': layer.max_val if layer.HasField('max_val') else None
    }


def count_params(layer):
    """Count total parameters in a layer."""
    if not layer.HasField('params'):
        return 0
    total = 1
    for dim in layer.dims:
        total *= dim
    return total


def analyze_conv_block(block, name=""):
    """Analyze a convolutional block."""
    info = {'name': name, 'total_params': 0, 'layers': {}}

    if block.HasField('weights'):
        params = decode_layer_params(block.weights)
        if params:
            info['layers']['weights'] = params
            info['total_params'] += params['total_params']

    if block.HasField('biases'):
        params = decode_layer_params(block.biases)
        if params:
            info['layers']['biases'] = params
            info['total_params'] += params['total_params']

    if block.HasField('bn_means'):
        params = decode_layer_params(block.bn_means)
        if params:
            info['layers']['bn_means'] = params
            info['total_params'] += params['total_params']

    if block.HasField('bn_stddivs'):
        params = decode_layer_params(block.bn_stddivs)
        if params:
            info['layers']['bn_stddivs'] = params
            info['total_params'] += params['total_params']

    return info


def analyze_encoder_layer(encoder, idx=0):
    """Analyze a transformer encoder layer."""
    info = {
        'index': idx,
        'total_params': 0,
        'components': {}
    }

    # Multi-head attention
    if encoder.HasField('mha'):
        mha = encoder.mha
        mha_params = 0
        for field in ['q_w', 'q_b', 'k_w', 'k_b', 'v_w', 'v_b', 'dense_w', 'dense_b']:
            if mha.HasField(field):
                layer = getattr(mha, field)
                mha_params += count_params(layer)
        info['components']['mha'] = {'params': mha_params}
        info['total_params'] += mha_params

    # Feed-forward network
    if encoder.HasField('ffn'):
        ffn = encoder.ffn
        ffn_params = 0
        for field in ['dense1_w', 'dense1_b', 'dense2_w', 'dense2_b']:
            if ffn.HasField(field):
                layer = getattr(ffn, field)
                ffn_params += count_params(layer)
        info['components']['ffn'] = {'params': ffn_params}
        info['total_params'] += ffn_params

    # Layer norms
    ln_params = 0
    for field in ['ln1_gammas', 'ln1_betas', 'ln2_gammas', 'ln2_betas']:
        if encoder.HasField(field):
            layer = getattr(encoder, field)
            ln_params += count_params(layer)
    if ln_params > 0:
        info['components']['layer_norms'] = {'params': ln_params}
        info['total_params'] += ln_params

    return info


def inspect_network(pb_file_path):
    """Inspect an Lc0 network file and return detailed information."""

    print(f"\n{'='*80}")
    print(f"Lc0 Network Inspector")
    print(f"{'='*80}\n")

    # Read the gzipped protobuf file
    with gzip.open(pb_file_path, 'rb') as f:
        net_data = f.read()

    # Parse the protobuf (top-level is Net, not Weights)
    net = net_pb2.Net()
    net.ParseFromString(net_data)

    # Check magic number
    if net.HasField('magic'):
        expected_magic = 0x1c0  # Lc0 magic number
        if net.magic != expected_magic:
            print(f"Warning: Unexpected magic number: {hex(net.magic)} (expected {hex(expected_magic)})")

    # Get weights from Net message
    if not net.HasField('weights'):
        print("Error: No weights found in network file!")
        if net.HasField('onnx_model'):
            print("This file contains an ONNX model, not native weights!")
        return {}

    weights = net.weights

    print(f"Network File: {pb_file_path}")
    print(f"File Size: {Path(pb_file_path).stat().st_size / (1024*1024):.2f} MB")

    # License information
    if net.HasField('license'):
        print(f"\nLicense: {net.license[:50]}..." if len(net.license) > 50 else f"\nLicense: {net.license}")

    # Version information
    if net.HasField('min_version'):
        print(f"Min Lc0 Version: {net.min_version.major}.{net.min_version.minor}.{net.min_version.patch}")

    # Format information
    if net.HasField('format'):
        format_info = net.format
        if format_info.HasField('network_format'):
            network_format = format_info.network_format
            if hasattr(network_format, 'network_structure'):
                network_structure = network_format.network_structure
                print(f"\nNetwork Structure: {network_structure.name}")

                # Determine architecture type
                arch_type = "Unknown"
                if 'RESIDUAL' in str(network_structure.name):
                    arch_type = "Residual CNN"
                elif 'ATTENTION' in str(network_structure.name) or 'TRANSFORMER' in str(network_format.input):
                    arch_type = "Transformer/Attention"

                print(f"Architecture Type: {arch_type}")

        if format_info.HasField('network_format'):
            nf = format_info.network_format
            if hasattr(nf, 'input'):
                print(f"Input Format: {nf.input}")
            if hasattr(nf, 'output'):
                print(f"Output Format: {nf.output}")

    # Count total parameters
    total_params = 0

    # Input embedding
    if weights.HasField('input'):
        input_params = 0
        if weights.input.HasField('weights'):
            input_params += count_params(weights.input.weights)
        if input_params > 0:
            print(f"\n{'='*80}")
            print("Input Embedding:")
            print(f"  Parameters: {input_params:,}")
            total_params += input_params

    # Residual blocks (for CNN architectures)
    residual_channels = None
    last_residual_output_dim = None

    if len(weights.residual) > 0:
        print(f"\n{'='*80}")
        print(f"Residual Tower: {len(weights.residual)} blocks")
        residual_params = 0

        # Try to infer channel count from first residual block
        first_block = weights.residual[0]
        if first_block.HasField('conv1') and first_block.conv1.HasField('weights'):
            conv_dims = list(first_block.conv1.weights.dims)
            if len(conv_dims) >= 1:
                residual_channels = conv_dims[0]  # Output channels
                print(f"  Residual channels: {residual_channels}")

        for i, res_block in enumerate(weights.residual):
            block_params = 0
            if res_block.HasField('conv1'):
                for layer in [res_block.conv1.weights, res_block.conv1.biases]:
                    if layer.ByteSize() > 0:
                        block_params += count_params(layer)
            if res_block.HasField('conv2'):
                for layer in [res_block.conv2.weights, res_block.conv2.biases]:
                    if layer.ByteSize() > 0:
                        block_params += count_params(layer)
            if res_block.HasField('se'):
                for layer in [res_block.se.w1, res_block.se.b1, res_block.se.w2, res_block.se.b2]:
                    if layer.ByteSize() > 0:
                        block_params += count_params(layer)
            residual_params += block_params

        print(f"  Total Parameters: {residual_params:,}")
        print(f"  Avg per block: {residual_params // len(weights.residual):,}")

        # The last residual block output is the feature representation
        last_residual_output_dim = residual_channels

        print(f"\n  {'='*76}")
        print(f"  TRANSFER LEARNING INTERFACE")
        print(f"  {'='*76}")
        print(f"  Last Shared Layer: residual_block_{len(weights.residual)-1}_output")
        print(f"  Feature Channels: {last_residual_output_dim if last_residual_output_dim else 'N/A'}")
        print(f"  Output Shape: [batch_size, {last_residual_output_dim if last_residual_output_dim else '?'}, 8, 8]")
        print(f"                (8x8 = chess board spatial dimensions)")
        print(f"  ")
        print(f"  Use this layer for:")
        print(f"    • Feature extraction for explainability")
        print(f"    • Concept extraction (e.g., piece positions, threats)")
        print(f"    • Transfer learning to related tasks")
        print(f"    • Spatial pattern visualization")
        print(f"  {'='*76}")

        total_params += residual_params

    # Encoder layers (for Transformer architectures)
    encoder_embedding_dim = None
    last_encoder_output_dim = None

    if len(weights.encoder) > 0:
        print(f"\n{'='*80}")
        print(f"Transformer Encoder: {len(weights.encoder)} layers")
        encoder_params = 0

        # Try to infer embedding dimension from first encoder layer
        first_encoder = weights.encoder[0]
        if first_encoder.HasField('mha') and first_encoder.mha.HasField('q_w'):
            q_w = first_encoder.mha.q_w
            q_w_dims = list(q_w.dims)

            if len(q_w_dims) >= 2 and q_w_dims[-1] > 0:
                # Dims field is populated
                encoder_embedding_dim = q_w_dims[-1]
            elif len(q_w.params) > 0:
                # Infer from parameter byte count
                # For attention, q_w is typically [d_model, d_model]
                import math
                bytes_per_param = 2  # LINEAR16, FLOAT16, BFLOAT16 all use 2 bytes
                total_params = len(q_w.params) // bytes_per_param
                encoder_embedding_dim = int(math.sqrt(total_params))

            if encoder_embedding_dim:
                print(f"  Embedding dimension: {encoder_embedding_dim}")

                # Verify with FFN if available
                if first_encoder.HasField('ffn') and first_encoder.ffn.HasField('dense1_w'):
                    ffn_w1 = first_encoder.ffn.dense1_w
                    if len(ffn_w1.params) > 0:
                        ffn_params = len(ffn_w1.params) // bytes_per_param
                        ffn_hidden = ffn_params // encoder_embedding_dim
                        print(f"  FFN expansion ratio: {ffn_hidden // encoder_embedding_dim}x (hidden dim: {ffn_hidden})")

        for i, encoder in enumerate(weights.encoder):
            enc_info = analyze_encoder_layer(encoder, i)
            encoder_params += enc_info['total_params']

            if i == 0:  # Show details for first layer
                print(f"\n  Layer 0 breakdown:")
                for comp_name, comp_info in enc_info['components'].items():
                    print(f"    {comp_name}: {comp_info['params']:,} parameters")

        print(f"\n  Total Encoder Parameters: {encoder_params:,}")
        print(f"  Avg per layer: {encoder_params // len(weights.encoder):,}")

        # The last encoder output is the feature representation before heads
        last_encoder_output_dim = encoder_embedding_dim

        print(f"\n  {'='*76}")
        print(f"  TRANSFER LEARNING INTERFACE")
        print(f"  {'='*76}")
        print(f"  Last Shared Layer: encoder_layer_{len(weights.encoder)-1}_output")
        print(f"  Feature Dimension: {last_encoder_output_dim if last_encoder_output_dim else 'N/A'}")
        print(f"  Output Shape: [batch_size, 64, {last_encoder_output_dim if last_encoder_output_dim else '?'}]")
        print(f"                (64 = 8x8 chess board positions)")
        print(f"  ")
        print(f"  Use this layer for:")
        print(f"    • Feature extraction for explainability")
        print(f"    • Concept extraction (e.g., piece positions, threats)")
        print(f"    • Transfer learning to related tasks")
        print(f"    • Attention visualization")
        print(f"  {'='*76}")

        total_params += encoder_params

    # Policy head
    if weights.HasField('policy'):
        print(f"\n{'='*80}")
        print("Policy Head:")
        policy_params = 0

        policy = weights.policy

        # Count encoder layers in policy head (attention policy)
        if len(policy.pol_encoder) > 0:
            print(f"  Policy encoders: {policy.pol_encoder}")
            for enc in policy.pol_encoder:
                enc_info = analyze_encoder_layer(enc)
                policy_params += enc_info['total_params']

        # Count regular policy layers
        for field in ['ip_pol_w', 'ip_pol_b', 'ip2_pol_w', 'ip2_pol_b',
                      'ip3_pol_w', 'ip3_pol_b', 'ip4_pol_w']:
            if policy.HasField(field):
                layer = getattr(policy, field)
                policy_params += count_params(layer)

        # Conv blocks for legacy policy
        if policy.HasField('policy1'):
            conv_info = analyze_conv_block(policy.policy1, "policy1")
            policy_params += conv_info['total_params']
        if policy.HasField('policy'):
            conv_info = analyze_conv_block(policy.policy, "policy")
            policy_params += conv_info['total_params']

        print(f"  Total Parameters: {policy_params:,}")
        total_params += policy_params

    # Value head
    if weights.HasField('value'):
        print(f"\n{'='*80}")
        print("Value Head:")
        value_params = 0

        value = weights.value
        for field in ['ip_val_w', 'ip_val_b', 'ip1_val_w', 'ip1_val_b',
                      'ip2_val_w', 'ip2_val_b']:
            if value.HasField(field):
                layer = getattr(value, field)
                value_params += count_params(layer)

        if value.HasField('value'):
            conv_info = analyze_conv_block(value.value, "value")
            value_params += conv_info['total_params']

        print(f"  Total Parameters: {value_params:,}")
        total_params += value_params

    # MLH head
    if weights.HasField('moves_left'):
        print(f"\n{'='*80}")
        print("Moves Left Head (MLH):")
        mlh_params = 0

        mlh = weights.moves_left
        for field in ['ip_mov_w', 'ip_mov_b', 'ip1_mov_w', 'ip1_mov_b',
                      'ip2_mov_w', 'ip2_mov_b']:
            if mlh.HasField(field):
                layer = getattr(mlh, field)
                mlh_params += count_params(layer)

        if mlh.HasField('moves_left'):
            conv_info = analyze_conv_block(mlh.moves_left, "moves_left")
            mlh_params += conv_info['total_params']

        print(f"  Total Parameters: {mlh_params:,}")
        total_params += mlh_params

    # Summary
    print(f"\n{'='*80}")
    print(f"TOTAL NETWORK PARAMETERS: {total_params:,}")
    print(f"Estimated memory (FP16): {total_params * 2 / (1024*1024):.2f} MB")
    print(f"Estimated memory (FP32): {total_params * 4 / (1024*1024):.2f} MB")
    print(f"{'='*80}\n")

    return {
        'total_params': total_params,
        'residual_blocks': len(weights.residual),
        'encoder_layers': len(weights.encoder),
        'has_policy': weights.HasField('policy'),
        'has_value': weights.HasField('value'),
        'has_mlh': weights.HasField('moves_left')
    }


def print_conversion_guidance(network_file):
    """Print guidance for converting to ONNX format."""
    print("\n" + "="*80)
    print("ONNX CONVERSION GUIDANCE")
    print("="*80 + "\n")

    print("Option 1: Use Lc0's built-in leela2onnx tool (Recommended)")
    print("-" * 80)
    print("The Lc0 engine includes a native leela2onnx converter written in C++.")
    print("\nSteps:")
    print("1. Build Lc0 from source:")
    print("   git clone https://github.com/LeelaChessZero/lc0.git")
    print("   cd lc0")
    print("   ./build.sh  # or follow platform-specific build instructions")
    print("\n2. Run the conversion:")
    print(f"   ./build/lc0 leela2onnx --input={network_file} \\")
    print(f"                          --output={Path(network_file).stem}.onnx \\")
    print("                          --onnx-batch-size=1")
    print("\n3. Customize with additional options:")
    print("   --onnx-data-type=float32     # or float16")
    print("   --onnx-opset=14              # ONNX opset version")
    print("   --value-head=winner          # Value head type")
    print("   --policy-head=vanilla        # Policy head type")

    print("\n\nOption 2: Use ONNX-TRT Backend (Runtime Conversion)")
    print("-" * 80)
    print("Let Lc0 convert automatically at runtime:")
    print("\nSteps:")
    print("1. Download pre-built Lc0 binary from:")
    print("   https://github.com/LeelaChessZero/lc0/releases")
    print("\n2. Run with ONNX backend:")
    print(f"   lc0 --backend=onnx-trt --weights={network_file}")
    print("\n   The engine will convert and cache the ONNX model automatically.")

    print("\n\nOption 3: Python-based Conversion (Advanced)")
    print("-" * 80)
    print("For custom conversion logic, you can extend this script to:")
    print("1. Read the .pb.gz file (already implemented above)")
    print("2. Build an ONNX graph using the 'onnx' Python library")
    print("3. Map Lc0 layers to ONNX operators")
    print("\nNote: This requires deep understanding of both formats and is complex.")
    print("      Refer to lc0-repo/src/neural/onnx/converter.cc for reference.")

    print("\n\nNext Steps:")
    print("-" * 80)
    print("• For chess play: Use Lc0 with native .pb.gz format")
    print("• For ML research: Use Option 1 (leela2onnx) for best compatibility")
    print("• For deployment: Consider ONNX Runtime or TensorRT for inference")
    print("\nFor more information, see:")
    print("  https://github.com/LeelaChessZero/lc0")
    print("  ../docs/LC0_ONNX_CONVERSION.md")
    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Inspect Lc0 network files and provide ONNX conversion guidance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('network_file', type=str,
                        help='Path to Lc0 network file (.pb.gz)')
    parser.add_argument('--conversion-guide', action='store_true',
                        help='Show ONNX conversion guidance')

    args = parser.parse_args()

    network_file = Path(args.network_file)

    if not network_file.exists():
        print(f"Error: File '{network_file}' not found!")
        sys.exit(1)

    if not network_file.suffix == '.gz':
        print(f"Warning: File doesn't have .gz extension. Expected .pb.gz format.")

    try:
        # Inspect the network
        network_info = inspect_network(network_file)

        # Always show conversion guidance
        print_conversion_guidance(network_file)

    except Exception as e:
        print(f"Error inspecting network: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
