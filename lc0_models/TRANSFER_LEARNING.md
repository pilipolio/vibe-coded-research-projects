# Lc0 Networks for Transfer Learning and Explainability

This guide explains how to use Lc0 neural network features for transfer learning, concept extraction, and explainability tasks.

## Last Shared Layer: The Feature Extraction Point

Lc0 neural networks consist of:
1. **Input embedding** - Converts board representation to feature space
2. **Backbone network** - Encoder layers (Transformer) or residual blocks (CNN)
3. **Task-specific heads** - Policy head (move selection) and Value head (position evaluation)

The **last shared layer** (output of the final backbone layer, before the heads) provides rich, chess-specific features that can be used for:
- Explainability and interpretability
- Concept extraction
- Transfer learning to related tasks
- Attention visualization

## Architecture-Specific Details

### Transformer-based Networks (e.g., T1-256x10)

**Network:** T1-256x10-distilled-swa-2432500

**Last Shared Layer:** `encoder_layer_9_output`

**Dimensions:**
- **Embedding dimension:** 256
- **Output shape:** `[batch_size, 64, 256]`
  - 64 = 8×8 chess board positions (one vector per square)
  - 256 = feature dimension per position
- **FFN hidden dim:** 1024 (4× expansion)

**Feature Characteristics:**
- **Position-aware:** Each of the 64 positions has its own 256-dimensional feature vector
- **Context-integrated:** Features incorporate information from across the board via self-attention
- **Semantically rich:** Encodes piece positions, threats, tactical patterns, strategic concepts

**Example extraction code:**
```python
import onnx
from onnx import helper, numpy_helper

# Load the Lc0 network
model = onnx.load("lc0_network.onnx")

# Modify to output intermediate layer
# Find the node corresponding to encoder_layer_9
# Add it as an additional output

# Or use ONNX Runtime to extract activations
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession("lc0_network.onnx")

# Get intermediate layer activations
# (requires model modification to expose intermediate outputs)
```

### CNN-based Networks (e.g., ResNet)

**Last Shared Layer:** `residual_block_{N-1}_output`

**Dimensions:**
- **Feature channels:** Typically 256-512
- **Output shape:** `[batch_size, channels, 8, 8]`
  - 8×8 = spatial dimensions of chess board
  - channels = feature channels (e.g., 256, 384, 512)

**Feature Characteristics:**
- **Spatially organized:** Preserves board topology
- **Hierarchical patterns:** Captures local patterns (pieces) to global patterns (board structure)
- **Translation-equivariant:** Similar patterns detected regardless of board location

## Transfer Learning Use Cases

### 1. Chess Position Understanding

**Task:** Classify positions by strategic concepts (open game, closed game, endgame type)

**Approach:**
```python
# Extract features from last shared layer
features = extract_lc0_features(position)  # Shape: [64, 256] for T1

# Train a lightweight classifier on top
classifier = nn.Linear(256, num_concepts)
concept_logits = classifier(features.mean(dim=0))  # Global pooling
```

**Benefits:**
- Lc0 features already encode chess knowledge
- Requires much less training data
- Better generalization

### 2. Tactical Motif Detection

**Task:** Identify specific tactical patterns (pins, forks, skewers, discovered attacks)

**Approach:**
```python
# Use position-specific features
features_per_square = extract_lc0_features(position)  # [64, 256]

# Detect patterns using attention
pattern_detector = TacticalMotifClassifier(input_dim=256)
motifs = pattern_detector(features_per_square)  # [64, num_motifs]
```

**Benefits:**
- Position-aware features capture spatial relationships
- Transformer attention already models piece interactions

### 3. Move Explanation

**Task:** Explain why a move is good/bad in human-understandable terms

**Approach:**
```python
# Compare features before and after move
features_before = extract_lc0_features(position_before)
features_after = extract_lc0_features(position_after)

# Analyze feature changes
feature_diff = features_after - features_before

# Map to concepts
concept_changes = concept_decoder(feature_diff)
# e.g., "Increases king safety", "Improves piece activity"
```

### 4. Concept Probing

**Task:** Understand what concepts are encoded in Lc0 features

**Linear Probes:**
```python
# Train linear classifiers to predict specific concepts
probe_piece_color = nn.Linear(256, 2)  # White/Black piece
probe_piece_type = nn.Linear(256, 6)   # Pawn/Knight/Bishop/Rook/Queen/King
probe_is_attacked = nn.Linear(256, 1)  # Is square attacked?

# For each square's feature vector
for square_idx in range(64):
    square_features = features[square_idx]  # [256]

    piece_color = probe_piece_color(square_features)
    piece_type = probe_piece_type(square_features)
    is_attacked = probe_is_attacked(square_features)
```

**Analysis:**
- High probe accuracy → concept is well-encoded
- Low accuracy → concept is not directly represented

### 5. Cross-Game Transfer

**Task:** Apply chess knowledge to variant games (Chess960, other board sizes)

**Approach:**
```python
# Use Lc0 features as input to variant-specific head
lc0_features = extract_lc0_features(position)  # [64, 256]

# Adapt to variant
variant_adapter = VariantAdapter(input_dim=256)
adapted_features = variant_adapter(lc0_features)

# Variant-specific head
variant_policy = VariantPolicyHead(adapted_features)
```

## Attention Visualization

For Transformer-based networks (T1), attention weights provide insights into what the network focuses on.

**Extracting Attention:**
```python
# Requires model modification to output attention weights
# Typically shape: [num_layers, num_heads, 64, 64]
# Where 64×64 is the attention matrix (from_square × to_square)

attention_weights = extract_attention(position)

# Visualize attention from a specific square
from_square = 28  # e4 (algebraic notation)
attention_from_e4 = attention_weights[-1, :, from_square, :]  # Last layer

# Average across heads
avg_attention = attention_from_e4.mean(dim=0)  # [64]

# Visualize on chess board
visualize_attention_on_board(avg_attention)
```

**Interpretation:**
- High attention to specific squares → network considers them important
- Attention patterns often correspond to tactical relationships (attacks, defenses)

## Feature Extraction Best Practices

### 1. Normalization

Lc0 features may benefit from normalization:
```python
features = extract_lc0_features(position)

# Layer normalization (common in transformers)
features = F.layer_norm(features, normalized_shape=[256])

# Or standardization
features = (features - features.mean()) / (features.std() + 1e-8)
```

### 2. Pooling Strategies

For global position features:
```python
# Mean pooling across positions
global_features = features.mean(dim=0)  # [256]

# Max pooling
global_features = features.max(dim=0)[0]  # [256]

# Weighted pooling (e.g., by piece importance)
weights = get_piece_importance_weights()  # [64]
global_features = (features * weights.unsqueeze(-1)).sum(dim=0)  # [256]

# Attention-based pooling
attention_weights = attention_pooling(features)  # [64]
global_features = (features * attention_weights.unsqueeze(-1)).sum(dim=0)
```

### 3. Fine-tuning vs. Frozen Features

**Frozen (Feature Extraction):**
```python
# Don't update Lc0 weights
lc0_model.eval()
with torch.no_grad():
    features = lc0_model.extract_features(position)

# Train only the task-specific head
task_head.train()
output = task_head(features)
```

**Fine-tuning:**
```python
# Update Lc0 weights with small learning rate
optimizer = Adam([
    {'params': lc0_model.parameters(), 'lr': 1e-5},
    {'params': task_head.parameters(), 'lr': 1e-3}
])
```

**Recommendation:** Start with frozen features, fine-tune if needed and data is sufficient.

## Example: Full Pipeline for Concept Extraction

```python
import onnxruntime as ort
import numpy as np
from sklearn.linear_model import LogisticRegression

# 1. Load Lc0 model
session = ort.InferenceSession("t1-256x10-distilled-swa-2432500.onnx")

# 2. Prepare dataset
positions = load_chess_positions()  # List of FEN strings
labels = load_labels()  # e.g., "has_passed_pawn": [0, 1, 1, 0, ...]

# 3. Extract features
all_features = []
for position in positions:
    board_tensor = fen_to_lc0_input(position)  # [1, 112, 8, 8]
    # Run through model to get last encoder output
    # (requires modified ONNX model that outputs intermediate layer)
    features = session.run(['encoder_layer_9_output'], {'input': board_tensor})[0]
    # features shape: [1, 64, 256]

    # Global pooling
    global_features = features.mean(axis=1).squeeze()  # [256]
    all_features.append(global_features)

all_features = np.stack(all_features)  # [num_positions, 256]

# 4. Train concept probe
probe = LogisticRegression()
probe.fit(all_features, labels['has_passed_pawn'])

# 5. Evaluate
accuracy = probe.score(all_features, labels['has_passed_pawn'])
print(f"Passed pawn detection accuracy: {accuracy:.2%}")

# 6. Interpret
important_features = np.abs(probe.coef_[0]).argsort()[-10:][::-1]
print(f"Most important feature dimensions: {important_features}")
```

## ONNX Model Modifications for Feature Extraction

To extract intermediate layers from the ONNX model:

```python
import onnx

# Load model
model = onnx.load("lc0_network.onnx")

# Find the intermediate layer node
target_layer = "encoder_layer_9_output"

# Add as additional output
for node in model.graph.node:
    if target_layer in node.output:
        # Add this output to the model's output list
        intermediate_output = onnx.helper.make_tensor_value_info(
            target_layer,
            onnx.TensorProto.FLOAT,
            [1, 64, 256]  # Known shape
        )
        model.graph.output.append(intermediate_output)
        break

# Save modified model
onnx.save(model, "lc0_network_with_features.onnx")
```

Now inference returns both the original outputs AND the intermediate features:
```python
outputs = session.run(
    ['policy', 'value', 'encoder_layer_9_output'],
    {'input': board_tensor}
)
policy, value, features = outputs
```

## Resources

- **Lc0 Architecture:** https://lczero.org/dev/wiki/technical-explanation-of-leela-chess-zero/
- **Transformer Interpretability:** https://arxiv.org/abs/1706.03762
- **Chess Concept Learning:** Research on learning chess concepts from game data
- **Network Inspector Tool:** `lc0_network_inspector.py` in this repository

## References

For more information on the conversion process and ONNX usage:
- [LC0_ONNX_CONVERSION.md](../docs/LC0_ONNX_CONVERSION.md) - Comprehensive conversion guide
- [README.md](README.md) - Tool documentation
