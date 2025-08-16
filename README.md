Minimal scaffold for the "World's Wish" fixed-point architecture:
- **WS-IR** (World Spec intermediate representation) + invariants + content hash
- **Deterministic Simulator** with named RNG ledger (stub)
- **Agent** with world-absent generation and plan sealing (stubs)
- **Evaluator** implementing WAR/BS/GC and WFI
- **CI** workflows: determinism & WFI gate (thresholds are placeholders)

> This is a **teaching** scaffold: signatures & sim are simple, deterministic, and auditable.
""")

# pyproject and requirements
write("pyproject.toml", """
[project]
name = "worlds-wish"
version = "0.0.1"
description = "Starter scaffold for the World's Wish architecture"
requires-python = ">=3.10"
dependencies = [
  "numpy>=1.24.0",
  "networkx>=3.2",
  "pytest>=8.0.0"
]

[tool.pytest.ini_options]
pythonpath = ["."]
addopts = "-q"
""")

write("requirements-dev.txt", """
numpy>=1.24.0
networkx>=3.2
pytest>=8.0.0
""")

# WS-IR schema (simplified)
write("ws_ir/schema.json", json.dumps({
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "World Spec IR (starter)",
  "type": "object",
  "required": ["version", "rng", "physics", "objects", "invariants"],
  "properties": {
    "version": {"type":"string"},
    "rng": {
      "type":"object",
      "properties": {
        "physics_noise":{"type":"integer"},
        "sensor_noise":{"type":"integer"},
        "actuator_noise":{"type":"integer"}
      },
      "required":["physics_noise","sensor_noise","actuator_noise"]
    },
    "physics": {
      "type":"object",
      "properties": {
        "g": {"type":"array","items":{"type":"number"},"minItems":3,"maxItems":3},
        "dt":{"type":"number"},
        "restitution":{"type":"number"},
        "fluid_viscosity":{"type":"number"}
      },
      "required":["g","dt","restitution","fluid_viscosity"]
    },
    "objects": {
      "type":"array",
      "items":{
        "type":"object",
        "required":["id","mat","pose"],
        "properties":{
          "id":{"type":"string"},
          "mesh":{"type":"string"},
          "type":{"type":"string"},
          "mat":{"type":"string"},
          "afford":{"type":"array","items":{"type":"string"}},
          "pose":{"type":"array","items":{"type":"number"}}
        }
      }
    },
    "constraints":{"type":"array","items":{"type":"object"}},
    "sensors":{"type":"array","items":{"type":"object"}},
    "actuators":{"type":"array","items":{"type":"object"}},
    "invariants":{"type":"object"}
  }
}, indent=2))

# Example worlds
kitchen = {
  "version": "wsir-0.3.2",
  "rng": {"physics_noise": 123, "sensor_noise": 7, "actuator_noise": 5},
  "physics": {"g":[0,-9.81,0], "dt":0.01, "restitution":0.28, "fluid_viscosity":1.0e-3},
  "objects":[
    {"id":"sink","mesh":"rect_basin","mat":"ceramic","afford":["container"],"pose":[0,0,0]},
    {"id":"faucet","type":"spout","mat":"steel","afford":["spout"],"pose":[0,0.5,0]},
    {"id":"key","mesh":"flat_key","mat":"brass","afford":["graspable"],"pose":[0.1,0.9,0]}
  ],
  "constraints":[{"type":"attach","a":"faucet","b":"sink"}],
  "sensors":[{"id":"rgb_cam","pose":[-1,1,1]}],
  "actuators":[{"id":"hand","dofs":6}],
  "invariants":{
    "flow_rate_bounds_lps":[1.9,2.3],
    "drain_time_s_max":120.0,
    "penetration_mm_max":0.5
  }
}
maze = {
  "version": "wsir-0.3.2",
  "rng": {"physics_noise": 321, "sensor_noise": 9, "actuator_noise": 8},
  "physics": {"g":[0,-9.81,0], "dt":0.02, "restitution":0.15, "fluid_viscosity":1.0e-3},
  "objects":[
    {"id":"agent","mat":"plastic","afford":["move"],"pose":[0,0,0]},
    {"id":"goal","mat":"plastic","afford":["target"],"pose":[10,0,0]}
  ],
  "constraints":[{"type":"maze","size":[10,10]}],
  "sensors":[{"id":"rgb_cam","pose":[0,1,0]}],
  "actuators":[{"id":"wheels","dofs":2}],
  "invariants":{"maze_solvable": True}
}
puddle = {
  "version": "wsir-0.3.2",
  "rng": {"physics_noise": 42, "sensor_noise": 2, "actuator_noise": 11},
  "physics": {"g":[0,-9.81,0], "dt":0.005, "restitution":0.05, "fluid_viscosity":2.0e-3},
  "objects":[
    {"id":"tray","mat":"aluminum","afford":["container"],"pose":[0,0,0]},
    {"id":"droplet","mat":"water","afford":["fluid"],"pose":[0.05,0.1,0]}
  ],
  "constraints":[],
  "sensors":[{"id":"top_cam","pose":[0,2,0]}],
  "actuators":[{"id":"nudge","dofs":2}],
  "invariants":{"droplet_mass_bounds":[0.9,1.1]}
}
write("ws_ir/examples/kitchen.json", json.dumps(kitchen, indent=2))
write("ws_ir/examples/maze.json", json.dumps(maze, indent=2))
write("ws_ir/examples/puddle.json", json.dumps(puddle, indent=2))

# Sim: RNGLedger and stub simulator
write("sim/ledger.py", """
from __future__ import annotations
import numpy as np
import hashlib

class RNGLedger:
    def __init__(self, seeds: dict[str,int]):
        self.streams = {k: np.random.default_rng(v) for k,v in seeds.items()}
        self.counters = {k: 0 for k in seeds}
    def sample(self, name: str, *args, **kwargs):
        val = self.streams[name].random(*args, **kwargs)
        self.counters[name] += 1
        return val
    def audit_state_hash(self) -> str:
        # Hash stream states + counters for deterministic audit
        h = hashlib.sha256()
        for k in sorted(self.streams.keys()):
            st = str(self.streams[k].bit_generator.state).encode()
            h.update(k.encode()+b'|'+st+b'|'+str(self.counters[k]).encode())
        return h.hexdigest()
""")

write("sim/sim.py", """
from __future__ import annotations
import json, hashlib
from dataclasses import dataclass
from sim.ledger import RNGLedger

@dataclass
class SimState:
    t: int
    ws_hash: str
    rng_audit: str

class Simulator:
    def __init__(self, ws: dict):
        self.ws = ws
        seeds = ws.get("rng", {})
        self.rng = RNGLedger(seeds)
        self.ticks = 0
        self.ws_hash = hashlib.sha256(json.dumps(ws, sort_keys=True).encode()).hexdigest()
    def step(self, n=1):
        # Stub deterministic evolution: advance ticks and consume RNG in a named way
        for _ in range(n):
            _ = self.rng.sample("physics_noise")  # consume one sample for physics per tick
            self.ticks += 1
    def snapshot(self) -> SimState:
        return SimState(t=self.ticks, ws_hash=self.ws_hash, rng_audit=self.rng.audit_state_hash())
""")

# Invariants & hashing
write("invariants/core.py", """
from __future__ import annotations

def pass_all(ws: dict) -> bool:
    inv = ws.get("invariants", {})
    # Trivial starter checks
    if "penetration_mm_max" in inv and inv["penetration_mm_max"] < 0: return False
    if "drain_time_s_max" in inv and inv["drain_time_s_max"] <= 0: return False
    return True
""")

write("ws_ir/hash.py", """
import hashlib, json
def hash_world_spec(ws: dict, versions: dict|None=None) -> str:
    payload = {"ws": ws, "versions": versions or {}}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
""")

# Signatures & evaluator
write("eval/signature.py", """
from __future__ import annotations
import numpy as np, networkx as nx

def compute_world_signature(ws: dict) -> dict:
    # Physics vector
    p = ws.get("physics", {})
    physics_vec = np.array([p.get("g",[0,0,0])[1], p.get("dt",0.01), p.get("restitution",0.0), p.get("fluid_viscosity",0.0)], dtype=float)

    # Topology graph from constraints
    G = nx.Graph()
    for obj in ws.get("objects", []):
        G.add_node(obj["id"])
    for c in ws.get("constraints", []):
        a, b = c.get("a"), c.get("b")
        if a and b: G.add_edge(a,b)
    if len(G) == 0: G.add_node("∅")

    # Spectrum (fixed size with padding)
    spec = np.zeros(8, dtype=float)
    lambdas = sorted(nx.normalized_laplacian_spectrum(G))
    spec[:min(8, len(lambdas))] = lambdas[:8]

    # Affordance bag
    afford = sorted({a for o in ws.get("objects", []) for a in o.get("afford", [])})
    afford_hash = hash(tuple(afford)) % (10**6)

    return {"physics_vec": physics_vec, "spec": spec, "afford_hash": afford_hash}

def signature_alignment_metric(sig_true: dict, sig_hat: dict) -> float:
    # Simple normalized distances
    def norm(a): return np.linalg.norm(a) + 1e-9
    ap = np.exp(-np.linalg.norm(sig_true["physics_vec"]-sig_hat["physics_vec"]) / (norm(sig_true["physics_vec"])*0.5))
    aspec = 1.0 - min(1.0, np.linalg.norm(sig_true["spec"]-sig_hat["spec"]))
    aaff = 1.0 if sig_true["afford_hash"] == sig_hat["afford_hash"] else 0.0
    return float(0.5*ap + 0.4*aspec + 0.1*aaff)
""")

write("eval/wish_eval.py", """
from __future__ import annotations
from eval.signature import compute_world_signature, signature_alignment_metric

class WorldWishEvaluator:
    def __init__(self, world_spec: dict, world_generator, weights=(1/3,1/3,1/3)):
        self.ws = world_spec
        self.wgen = world_generator
        self.weights = weights
        self.true_sig = compute_world_signature(self.ws)

    def evaluate(self, agent):
        # WAR
        ws_hat = agent.generate_world_model(from_internal_model=True)
        WAR = signature_alignment_metric(self.true_sig, compute_world_signature(ws_hat))

        # BS
        plan = agent.plan_without_world_access().seal()
        BS = float(execute_plan_on_reveal(plan, self.ws))  # stub: 1.0 = success

        # GC
        GC = float(self.wgen.get_likelihood(ws_hat))       # stub: [0,1]

        WFI = sum(w*m for w,m in zip(self.weights, [WAR, BS, GC]))
        return {"WAR": WAR, "BS": BS, "GC": GC, "WFI": WFI}

# --- Stubs for demo ---
class DummyPlan:
    def __init__(self, steps=5): self.steps=steps; self._sealed=False
    def seal(self): self._sealed=True; return self

def execute_plan_on_reveal(plan: DummyPlan, ws: dict) -> float:
    # Deterministic: succeeds if sealed and small number of steps
    return 1.0 if getattr(plan, "_sealed", False) and plan.steps <= 10 else 0.0
""")

# Tiny agent & world generator stubs
write("agent/agent.py", """
from __future__ import annotations
import copy
from eval.signature import compute_world_signature

class Agent:
    def __init__(self, internal_ws: dict):
        # Internal model starts as a (possibly noisy) copy
        self.internal_ws = copy.deepcopy(internal_ws)

    def generate_world_model(self, from_internal_model=True) -> dict:
        # Return internal model (no leakage at eval time)
        return copy.deepcopy(self.internal_ws)

    class _Plan:
        def __init__(self): self._sealed=False
        def seal(self): self._sealed=True; return self
        @property
        def sealed(self): return self._sealed

    def plan_without_world_access(self):
        return self._Plan()

    def experience(self, ws: dict):
        # Update internal model signature drift downward (stub)
        pass
""")

write("worldgen/worldgen.py", """
from __future__ import annotations
from ws_ir.hash import hash_world_spec

class WorldGenerator:
    def __init__(self, versions=None): self.versions = versions or {}
    def get_likelihood(self, ws: dict) -> float:
        # Deterministic pseudo-likelihood in [0,1] from content hash prefix (stub)
        h = hash_world_spec(ws, self.versions)
        return int(h[:2], 16) / 255.0
""")

# Eval runner
write("eval/run_wfi_gate.py", """
import json, pathlib
from agent.agent import Agent
from worldgen.worldgen import WorldGenerator
from eval.wish_eval import WorldWishEvaluator

def load_ws(name):
    p = pathlib.Path("ws_ir/examples") / f"{name}.json"
    return json.loads(p.read_text())

def main():
    wgen = WorldGenerator({"sim":"refcpu-0.1"})
    results = {}
    for name in ["kitchen", "maze", "puddle"]:
        ws = load_ws(name)
        agent = Agent(ws)               # start with matched internal model (best-case)
        evaluator = WorldWishEvaluator(ws, wgen, weights=(0.34, 0.33, 0.33))
        results[name] = evaluator.evaluate(agent)
    # Simple composite
    WFI = sum(r["WFI"] for r in results.values()) / len(results)
    print("WFI:", round(WFI, 3))
    for k,v in results.items(): print(k, {m: round(v[m],3) for m in v})

if __name__ == "__main__":
    main()
""")

# Tests
write("tests/test_invariants.py", """
import json, pathlib
from invariants.core import pass_all

def test_examples_pass_invariants():
    dirp = pathlib.Path("ws_ir/examples")
    for p in dirp.glob("*.json"):
        ws = json.loads(p.read_text())
        assert pass_all(ws), f"Invariants failed for {p}"
""")

write("tests/test_determinism.py", """
import json, pathlib
from sim.sim import Simulator

def test_rng_ledger_and_snapshot():
    ws = json.loads((pathlib.Path("ws_ir/examples")/"kitchen.json").read_text())
    sim1 = Simulator(ws)
    sim2 = Simulator(ws)
    sim1.step(10)
    sim2.step(10)
    s1, s2 = sim1.snapshot(), sim2.snapshot()
    assert s1.t == s2.t and s1.ws_hash == s2.ws_hash and s1.rng_audit == s2.rng_audit
""")

# GitHub Actions workflows
write(".github/workflows/determinism.yml", """
name: determinism
on: [push, pull_request]
jobs:
  determinism:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -e .
      - name: Run tests (determinism & invariants)
        run: python -m pytest -q tests/test_invariants.py tests/test_determinism.py
""")

write(".github/workflows/wfi_gate.yml", """
name: wfi_gate
on:
  pull_request:
    branches: [ main, master ]
jobs:
  wfi:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -e .
      - name: Run WFI gate
        run: |
          python eval/run_wfi_gate.py | tee wfi.out
          WFI=$(python - <<'PY'
from pathlib import Path
txt = Path("wfi.out").read_text()
import re
m = re.search(r"WFI:\s*([0-9.]+)", txt)
print(m.group(1) if m else "0.0")
PY
)
          echo "WFI=$WFI"
          python - <<'PY'
import os, sys
wfi = float(os.environ.get("WFI","0"))
THRESH = 0.75
sys.exit(0 if wfi >= THRESH else 1)
PY
""")

# Zip the scaffold
zip_path = "/mnt/data/worlds_wish_starter.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(base):
        for f in files:
            fp = os.path.join(root, f)
            z.write(fp, os.path.relpath(fp, base))

zip_path
