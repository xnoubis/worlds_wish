"""
Tests for the kitchen world φ function implementation.
"""

import json
import pathlib
import numpy as np
import pytest
from invariants.kitchen_phi import (
    phi_kitchen, 
    phi_kitchen_alignment, 
    phi_kitchen_validation,
    compute_kitchen_phi
)

def load_kitchen_ws():
    """Load the kitchen world specification"""
    p = pathlib.Path("ws_ir/examples/kitchen.json")
    return json.loads(p.read_text())

def test_phi_kitchen_extraction():
    """Test that φ correctly extracts the three invariants from kitchen world"""
    ws = load_kitchen_ws()
    phi_sig = phi_kitchen(ws)
    
    # Check all three invariants are present
    assert "flow_rate_bounds" in phi_sig
    assert "drain_time_max" in phi_sig
    assert "penetration_max" in phi_sig
    
    # Check flow rate bounds
    flow_bounds = phi_sig["flow_rate_bounds"]
    assert isinstance(flow_bounds, np.ndarray)
    assert flow_bounds.shape == (2,)
    assert flow_bounds[0] == 1.9
    assert flow_bounds[1] == 2.3
    
    # Check drain time
    drain_time = phi_sig["drain_time_max"]
    assert isinstance(drain_time, np.ndarray)
    assert drain_time.shape == (1,)
    assert drain_time[0] == 120.0
    
    # Check penetration
    penetration = phi_sig["penetration_max"]
    assert isinstance(penetration, np.ndarray)
    assert penetration.shape == (1,)
    assert penetration[0] == 0.5

def test_phi_kitchen_validation():
    """Test validation of kitchen φ signatures"""
    # Valid signature
    valid_phi = {
        "flow_rate_bounds": np.array([1.9, 2.3]),
        "drain_time_max": np.array([120.0]),
        "penetration_max": np.array([0.5])
    }
    assert phi_kitchen_validation(valid_phi) == True
    
    # Invalid: flow bounds not ordered
    invalid_phi1 = {
        "flow_rate_bounds": np.array([2.3, 1.9]),  # wrong order
        "drain_time_max": np.array([120.0]),
        "penetration_max": np.array([0.5])
    }
    assert phi_kitchen_validation(invalid_phi1) == False
    
    # Invalid: negative drain time
    invalid_phi2 = {
        "flow_rate_bounds": np.array([1.9, 2.3]),
        "drain_time_max": np.array([-10.0]),  # negative
        "penetration_max": np.array([0.5])
    }
    assert phi_kitchen_validation(invalid_phi2) == False
    
    # Invalid: too large penetration
    invalid_phi3 = {
        "flow_rate_bounds": np.array([1.9, 2.3]),
        "drain_time_max": np.array([120.0]),
        "penetration_max": np.array([20.0])  # too large
    }
    assert phi_kitchen_validation(invalid_phi3) == False

def test_phi_kitchen_alignment():
    """Test alignment metric between φ signatures"""
    phi_true = {
        "flow_rate_bounds": np.array([1.9, 2.3]),
        "drain_time_max": np.array([120.0]),
        "penetration_max": np.array([0.5])
    }
    
    # Perfect alignment
    phi_perfect = phi_true.copy()
    align_perfect = phi_kitchen_alignment(phi_true, phi_perfect)
    assert align_perfect == pytest.approx(1.0, abs=1e-6)
    
    # Slight deviation
    phi_slight = {
        "flow_rate_bounds": np.array([1.95, 2.25]),  # small change
        "drain_time_max": np.array([115.0]),  # small change
        "penetration_max": np.array([0.52])  # small change
    }
    align_slight = phi_kitchen_alignment(phi_true, phi_slight)
    assert 0.5 < align_slight < 1.0  # should be good but not perfect
    
    # Large deviation
    phi_large = {
        "flow_rate_bounds": np.array([0.5, 1.0]),  # large change
        "drain_time_max": np.array([50.0]),  # large change
        "penetration_max": np.array([5.0])  # large change
    }
    align_large = phi_kitchen_alignment(phi_true, phi_large)
    assert 0.0 < align_large < 0.5  # should be poor

def test_compute_kitchen_phi():
    """Test the convenience function"""
    ws = load_kitchen_ws()
    phi_sig, validation_score = compute_kitchen_phi(ws)
    
    # Should be valid
    assert validation_score == 1.0
    
    # Should have correct structure
    assert isinstance(phi_sig, dict)
    assert len(phi_sig) == 3
    assert all(key in phi_sig for key in ["flow_rate_bounds", "drain_time_max", "penetration_max"])

def test_phi_robustness_to_missing_invariants():
    """Test that φ handles missing invariants gracefully"""
    ws = load_kitchen_ws()
    # Remove invariants
    ws_no_invariants = {k: v for k, v in ws.items() if k != "invariants"}
    
    phi_sig = phi_kitchen(ws_no_invariants)
    
    # Should use defaults
    assert phi_sig["flow_rate_bounds"][0] == 1.9
    assert phi_sig["flow_rate_bounds"][1] == 2.3
    assert phi_sig["drain_time_max"][0] == 120.0
    assert phi_sig["penetration_max"][0] == 0.5