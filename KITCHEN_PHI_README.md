# Kitchen World φ Function Implementation

## Overview

This document describes the implementation of the φ function for the kitchen world in the World's Wish alignment framework. The φ function extracts three key invariants that form the signature used for testing alignment between the agent's internal world model and the true world.

## The Three Chosen Invariants

### 1. Flow Rate Bounds (LPS) - Physics Constant
- **Value**: `[1.9, 2.3]` liters per second
- **Purpose**: Captures fundamental fluid dynamics of water flow through the faucet
- **Why Important**: Tests agent's understanding of basic physics constants
- **Invariance**: Should remain consistent across different kitchen configurations

### 2. Drain Time Maximum (seconds) - Contact Regime
- **Value**: `120.0` seconds
- **Purpose**: Defines the maximum time for water to drain through the ceramic sink
- **Why Important**: Tests agent's understanding of material properties and fluid-surface interactions
- **Invariance**: Represents realistic contact behavior between water and ceramic

### 3. Penetration Maximum (mm) - Object Topology/Affordances
- **Value**: `0.5` millimeters
- **Purpose**: Defines maximum allowed penetration depth for objects interacting with surfaces
- **Why Important**: Tests agent's understanding of solid mechanics and prevents unrealistic physics
- **Invariance**: Ensures objects don't unrealistically pass through surfaces

## Implementation Files

- `invariants/kitchen_phi_simple.py` - Main implementation (no numpy dependency)
- `invariants/kitchen_phi.py` - Full implementation with numpy support
- `tests/test_kitchen_phi.py` - Test suite
- `demo_kitchen_phi.py` - Demonstration script

## Usage

```python
from invariants.kitchen_phi_simple import phi_kitchen, phi_kitchen_alignment

# Extract φ signature from world specification
phi_sig = phi_kitchen(ws)

# Compare two φ signatures
alignment_score = phi_kitchen_alignment(phi_true, phi_hat)
```

## Integration with World's Wish Framework

### WAR (World Alignment Reward)
The φ function is used to compute:
```
L_φ = ‖φ(WS) − φ(decode(ẑ))‖
```
This measures how well the agent's decoded world model matches the true world's invariants.

### BS (Blind Sealing)
During blind plan execution, φ ensures world consistency:
- Plans are computed from z without peeking at the true world
- φ validates that the executed plan maintains world invariants
- Prevents shortcut channels and ensures hermetic protocol

### GC (Generative Consistency)
φ validates that generated worlds sit on the W-Gen manifold:
```
φ(WŜ) ≈ φ(WS)
```
This ensures the agent generates physically plausible worlds.

### Fixed-Point Testing
The φ function enables testing the fixed-point property:
```
z → decode(z) → WS → rollout τ → infer(τ) → ẑ
```
We check both:
- `‖z − ẑ‖ < ε` (latent alignment)
- `φ(WS) ≈ φ(WŜ)` (invariant preservation)

## Alignment Metrics

The alignment function uses weighted exponential distance:
- Flow rate bounds: 50% weight (physics constant most important)
- Drain time: 30% weight (contact regime)
- Penetration: 20% weight (topology/affordances)

Tolerance levels are tuned for each invariant type:
- Flow rate: 20% tolerance
- Drain time: 30% tolerance  
- Penetration: 10% tolerance

## Validation

The φ function includes validation to ensure physically plausible signatures:
- Flow bounds must be positive and ordered (min < max)
- Drain time must be positive and reasonable (< 1000s)
- Penetration must be positive and reasonable (< 10mm)

## Testing

Run the demonstration:
```bash
python3 demo_kitchen_phi.py
```

Run tests (requires pytest):
```bash
python3 -m pytest tests/test_kitchen_phi.py -v
```

## Why These Three Invariants?

1. **Comprehensive Coverage**: Physics constants, material properties, and geometric constraints
2. **Measurable**: Each invariant can be quantitatively tested
3. **Robust**: Invariant under reasonable world variations
4. **Preventive**: Guard against common failure modes (unrealistic physics, impossible interactions)
5. **Scalable**: Framework can be extended to other world types with different φ functions

## Next Steps

With φ(kitchen) implemented, the World's Wish framework can now:
1. Test WAR alignment between agent and world
2. Validate BS hermetic protocol
3. Ensure GC manifold consistency
4. Verify fixed-point properties

The foundation is ready for building the full z-cycle: `WAR → z-cycle: decode(z) → WS → rollout τ → infer(τ) → ẑ`