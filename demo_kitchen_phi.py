#!/usr/bin/env python3
"""
Demonstration of Kitchen World φ Function in World's Wish Framework

This script demonstrates how the three chosen invariants for φ(kitchen) work:
1. Flow Rate Bounds (LPS) - physics constant
2. Drain Time Maximum (seconds) - contact regime  
3. Penetration Maximum (mm) - object topology/affordances

These invariants form the signature used in:
- WAR (World Alignment Reward): comparing φ(WS) vs φ(decode(ẑ))
- GC (Generative Consistency): checking if WŜ sits on the W-Gen manifold
- Fixed-point testing: ensuring z→WŜ→τ̂→z̃ maintains φ-invariance
"""

import json
import pathlib
import sys
sys.path.append('.')

from invariants.kitchen_phi_simple import (
    phi_kitchen, 
    phi_kitchen_alignment, 
    phi_kitchen_validation,
    compute_kitchen_phi
)

def load_kitchen_world():
    """Load the kitchen world specification"""
    p = pathlib.Path("ws_ir/examples/kitchen.json")
    return json.loads(p.read_text())

def demonstrate_phi_extraction():
    """Demonstrate φ function extraction from kitchen world"""
    print("=== Kitchen World φ Function Demonstration ===\n")
    
    # Load kitchen world
    ws = load_kitchen_world()
    print("1. Kitchen World Specification:")
    print(f"   - Objects: {[obj['id'] for obj in ws['objects']]}")
    print(f"   - Physics: gravity={ws['physics']['g']}, dt={ws['physics']['dt']}")
    print(f"   - Invariants: {ws['invariants']}")
    print()
    
    # Extract φ signature
    phi_sig = phi_kitchen(ws)
    print("2. φ(WS) Signature Extraction:")
    print(f"   - Flow Rate Bounds (LPS): {phi_sig['flow_rate_bounds']} (physics constant)")
    print(f"   - Drain Time Max (s): {phi_sig['drain_time_max']} (contact regime)")
    print(f"   - Penetration Max (mm): {phi_sig['penetration_max']} (topology/affordances)")
    print()
    
    # Validate signature
    is_valid = phi_kitchen_validation(phi_sig)
    print(f"3. φ Signature Validation: {'✓ VALID' if is_valid else '✗ INVALID'}")
    print()

def demonstrate_alignment_metrics():
    """Demonstrate alignment metrics between φ signatures"""
    print("=== φ Alignment Metrics ===\n")
    
    # True signature
    ws = load_kitchen_world()
    phi_true = phi_kitchen(ws)
    
    # Test cases
    test_cases = [
        ("Perfect Match", phi_true),
        ("Slight Deviation", {
            "flow_rate_bounds": [1.95, 2.25],
            "drain_time_max": [115.0],
            "penetration_max": [0.52]
        }),
        ("Moderate Deviation", {
            "flow_rate_bounds": [1.5, 2.0],
            "drain_time_max": [80.0],
            "penetration_max": [1.0]
        }),
        ("Large Deviation", {
            "flow_rate_bounds": [0.5, 1.0],
            "drain_time_max": [50.0],
            "penetration_max": [5.0]
        }),
        ("Invalid Bounds", {
            "flow_rate_bounds": [2.3, 1.9],  # wrong order
            "drain_time_max": [120.0],
            "penetration_max": [0.5]
        })
    ]
    
    print("Alignment Scores (0.0 = poor, 1.0 = perfect):")
    print("-" * 50)
    
    for name, phi_test in test_cases:
        align_score = phi_kitchen_alignment(phi_true, phi_test)
        is_valid = phi_kitchen_validation(phi_test)
        status = "✓" if is_valid else "✗"
        print(f"{status} {name:20} | Score: {align_score:.3f}")
    
    print()

def demonstrate_worlds_wish_integration():
    """Demonstrate how φ fits into World's Wish framework"""
    print("=== World's Wish Framework Integration ===\n")
    
    ws = load_kitchen_world()
    phi_sig, validation_score = compute_kitchen_phi(ws)
    
    print("World's Wish Alignment Components:")
    print()
    
    print("1. WAR (World Alignment Reward):")
    print("   L_align = ‖z − ẑ‖²")
    print("   L_φ = ‖φ(WS) − φ(decode(ẑ))‖")
    print(f"   Current φ(WS): {phi_sig}")
    print()
    
    print("2. BS (Blind Sealing):")
    print("   - Plan computed from z (no peeking)")
    print("   - On reveal, execute without altering plan")
    print("   - φ ensures world consistency during execution")
    print()
    
    print("3. GC (Generative Consistency):")
    print("   - Check φ(WŜ) matches φ(WS)")
    print("   - Ensure WŜ sits on W-Gen manifold")
    print(f"   - Validation score: {validation_score}")
    print()
    
    print("4. Fixed-Point Testing:")
    print("   - z → decode(z) → WS → rollout τ → infer(τ) → ẑ")
    print("   - Check ‖z − ẑ‖ < ε (alignment)")
    print("   - Check φ(WS) ≈ φ(WŜ) (invariance)")
    print()

def demonstrate_invariant_importance():
    """Demonstrate why these three invariants are chosen"""
    print("=== Why These Three Invariants? ===\n")
    
    print("1. Flow Rate Bounds (LPS) - Physics Constant:")
    print("   - Fundamental fluid dynamics property")
    print("   - Invariant across different kitchen configurations")
    print("   - Tests agent's understanding of basic physics")
    print()
    
    print("2. Drain Time Maximum (seconds) - Contact Regime:")
    print("   - Defines water-ceramic sink interaction")
    print("   - Tests agent's understanding of material properties")
    print("   - Ensures realistic fluid behavior")
    print()
    
    print("3. Penetration Maximum (mm) - Object Topology/Affordances:")
    print("   - Defines maximum object-surface penetration")
    print("   - Tests agent's understanding of solid mechanics")
    print("   - Ensures objects don't unrealistically pass through surfaces")
    print()
    
    print("These invariants form a robust signature because they:")
    print("- Capture different aspects of the world (physics, materials, geometry)")
    print("- Are measurable and testable")
    print("- Are invariant under reasonable world variations")
    print("- Prevent common failure modes (unrealistic physics, impossible interactions)")

def main():
    """Run the complete demonstration"""
    demonstrate_phi_extraction()
    demonstrate_alignment_metrics()
    demonstrate_worlds_wish_integration()
    demonstrate_invariant_importance()
    
    print("=== Summary ===")
    print("✓ φ(kitchen) successfully extracts three key invariants")
    print("✓ Alignment metrics distinguish between good and poor matches")
    print("✓ Integration with World's Wish framework is ready")
    print("✓ Invariants capture physics constants, contact regimes, and topology")
    print("\nThe kitchen world φ function is ready for use in the World's Wish alignment framework!")

if __name__ == "__main__":
    main()