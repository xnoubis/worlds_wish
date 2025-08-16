"""
Simplified Kitchen World Invariant Signature φ(WS) - No numpy dependency

Implements the φ function for the kitchen world that extracts three key invariants:
1. Flow Rate Bounds (LPS) - physics constant
2. Drain Time Maximum (seconds) - contact regime  
3. Penetration Maximum (mm) - object topology/affordances
"""

from __future__ import annotations
from typing import Dict, Any, Tuple, List

def phi_kitchen(ws: Dict[str, Any]) -> Dict[str, List[float]]:
    """
    Extract the invariant signature φ(WS) for kitchen world.
    
    Args:
        ws: World specification dictionary
        
    Returns:
        Dictionary containing the three invariant signatures as lists
    """
    invariants = ws.get("invariants", {})
    
    # 1. Flow Rate Bounds (LPS) - physics constant
    flow_bounds = invariants.get("flow_rate_bounds_lps", [1.9, 2.3])
    flow_vec = list(flow_bounds)
    
    # 2. Drain Time Maximum (seconds) - contact regime
    drain_time = invariants.get("drain_time_s_max", 120.0)
    drain_vec = [drain_time]
    
    # 3. Penetration Maximum (mm) - object topology/affordances
    penetration = invariants.get("penetration_mm_max", 0.5)
    penetration_vec = [penetration]
    
    return {
        "flow_rate_bounds": flow_vec,
        "drain_time_max": drain_vec, 
        "penetration_max": penetration_vec
    }

def phi_kitchen_alignment(phi_true: Dict[str, List[float]], 
                         phi_hat: Dict[str, List[float]]) -> float:
    """
    Compute alignment metric between two kitchen φ signatures.
    
    Args:
        phi_true: True invariant signature
        phi_hat: Predicted invariant signature
        
    Returns:
        Alignment score in [0,1] where 1.0 is perfect alignment
    """
    def safe_norm(a: List[float]) -> float:
        """Safe normalization with small epsilon to avoid division by zero"""
        return sum(x*x for x in a)**0.5 + 1e-9
    
    def bounded_distance(a: List[float], b: List[float], tolerance: float = 0.1) -> float:
        """Compute bounded distance between lists"""
        dist = sum((x-y)**2 for x, y in zip(a, b))**0.5
        return 2.718**(-dist / (safe_norm(a) * tolerance))
    
    # Flow rate bounds alignment (physics constant)
    flow_align = bounded_distance(
        phi_true["flow_rate_bounds"], 
        phi_hat["flow_rate_bounds"], 
        tolerance=0.2
    )
    
    # Drain time alignment (contact regime)
    drain_align = bounded_distance(
        phi_true["drain_time_max"], 
        phi_hat["drain_time_max"], 
        tolerance=0.3
    )
    
    # Penetration alignment (topology/affordances)
    penetration_align = bounded_distance(
        phi_true["penetration_max"], 
        phi_hat["penetration_max"], 
        tolerance=0.1
    )
    
    # Weighted combination (physics constants most important)
    weights = [0.5, 0.3, 0.2]  # flow, drain, penetration
    alignments = [flow_align, drain_align, penetration_align]
    
    return sum(w*a for w, a in zip(weights, alignments))

def phi_kitchen_validation(phi_sig: Dict[str, List[float]]) -> bool:
    """
    Validate that a kitchen φ signature is physically plausible.
    
    Args:
        phi_sig: Kitchen invariant signature
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Check flow rate bounds are positive and ordered
        flow_bounds = phi_sig["flow_rate_bounds"]
        if len(flow_bounds) != 2 or flow_bounds[0] <= 0 or flow_bounds[1] <= 0:
            return False
        if flow_bounds[0] >= flow_bounds[1]:
            return False
            
        # Check drain time is positive and reasonable
        drain_time = phi_sig["drain_time_max"][0]
        if drain_time <= 0 or drain_time > 1000:  # max 1000 seconds
            return False
            
        # Check penetration is positive and reasonable
        penetration = phi_sig["penetration_max"][0]
        if penetration <= 0 or penetration > 10:  # max 10mm
            return False
            
        return True
        
    except (KeyError, IndexError, TypeError):
        return False

# Convenience function for the World's Wish framework
def compute_kitchen_phi(ws: Dict[str, Any]) -> Tuple[Dict[str, List[float]], float]:
    """
    Compute kitchen φ signature and return with validation score.
    
    Args:
        ws: World specification
        
    Returns:
        Tuple of (phi_signature, validation_score)
    """
    phi_sig = phi_kitchen(ws)
    is_valid = phi_kitchen_validation(phi_sig)
    validation_score = 1.0 if is_valid else 0.0
    
    return phi_sig, validation_score