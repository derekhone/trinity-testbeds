#!/usr/bin/env python3
"""
TRINITY-2: The Governed Action — experiment harness.

Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed.

Extends TRINITY-1 (one Bell-CHSH witness independently evaluated on three IBM Quantum
processors, fused into one record) with the pilot-grade product claim:

  * a SIMULATED high-impact action (authorize a $500,000 payment) is ALLOWED / HELD / DENIED
    strictly by the fused multi-processor verdict;
  * a preregistered QUORUM (>=2 distinct valid devices) with SUBSTITUTION / FAILOVER governs
    behavior when a processor is unavailable;
  * a full CALIBRATION SNAPSHOT is captured per device and hashed into the record.

The payment is SIMULATED — no real funds, rail, or authority. Standard nonclassicality
loopholes remain open; this is a governance demonstration, not a security/physics proof.

DEFAULT MODE: simulator validation (three independent noisy aer backends). Hardware submission
is GATED: it refuses to run unless --authorize-hardware AND --allow-unrotated are both passed
(after the exposed IBM token has been ROTATED and Derek authorizes) and IBM_QUANTUM_TOKEN is set.

Usage:
  python3 trinity2_harness.py                      # simulator validation, nominal -> ALLOW
  python3 trinity2_harness.py --scenario degraded  # one device down  -> HOLD (degraded quorum)
  python3 trinity2_harness.py --scenario deny       # dissenting device -> DENY
  python3 trinity2_harness.py --scenario gatestop   # sub-quorum       -> GATE-STOP
  python3 trinity2_harness.py --authorize-hardware --allow-unrotated   # hardware (post-rotation)
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import requests

from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dumps as qasm3_dumps

# ----------------------------------------------------------------------------------------
# Preregistered constants
# ----------------------------------------------------------------------------------------
SCHEMA = "trinity-proofrecord-2.0"
EXPERIMENT = "TRINITY-2"
FRAMEWORK = "Coherent Inheritance Framework (CIF)"
GOVERNANCE = "ExecutionProof"

CHSH_CLASSICAL = 2.0
CHSH_TSIRELSON = 2.0 * np.sqrt(2.0)
K_MARGIN = 2  # sigma margin above/below classical bound for PASS/FAIL decision

TARGET_DEVICES = ["ibm_kingston", "ibm_fez", "ibm_marrakesh"]
QUORUM_REQUIRED = 2          # >=2 distinct valid devices needed to proceed
FULL_QUORUM = 3              # all three distinct devices -> ALLOW

LIGO_GW150914_HASH = "66c4b196"
NIST_BEACON_URL = "https://beacon.nist.gov/beacon/2.0/pulse/last"
PREVIOUS_RECORD_LABEL = "TRINITY-1"
# TRINITY-1 record_hash (public chain link)
PREVIOUS_RECORD_HASH = "8d23accac81791fa10f1dba1be79a132168966c4620fc42d16de656bcf9d688b"

# Simulated governed action (no real funds / rail / authority)
GOVERNED_ACTION_TEMPLATE = {
    "action_type": "payment_authorization",
    "amount": 500000,
    "currency": "USD",
    "payee_ref": "SIMULATED-PAYEE-0001",
    "policy_ref": "RF-100/multi-root-quorum-v1",
    "simulated": True,
}

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")
MANIFEST_PATH = os.path.join(HERE, "MANIFEST-TRINITY-2.sha256")
PREREG_PATH = os.path.join(HERE, "TRINITY-2-preregistration.md")
HARNESS_PATH = os.path.abspath(__file__)

CHSH_SETTINGS = {
    "a0b0": (0.0, np.pi / 8),
    "a0b1": (0.0, 3 * np.pi / 8),
    "a1b0": (np.pi / 4, np.pi / 8),
    "a1b1": (np.pi / 4, 3 * np.pi / 8),
}


# ----------------------------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------------------------
def sha256_hex(data) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def log(msg):
    print(f"[TRINITY-2] {msg}", flush=True)


# ----------------------------------------------------------------------------------------
# CHSH circuit + witness
# ----------------------------------------------------------------------------------------
def build_chsh_circuit(theta_a, theta_b, name):
    qc = QuantumCircuit(2, 2, name=name)
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()
    qc.ry(-2.0 * theta_a, 0)
    qc.ry(-2.0 * theta_b, 1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc


def build_chsh_circuits():
    return {name: build_chsh_circuit(ta, tb, f"chsh_{name}")
            for name, (ta, tb) in CHSH_SETTINGS.items()}


def correlator_from_counts(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0, 0
    e = 0
    for bitstr, c in counts.items():
        bits = bitstr.replace(" ", "")[-2:]
        parity = 1 if bits.count("1") % 2 == 0 else -1
        e += parity * c
    return e / total, total


def compute_chsh(counts_by_setting):
    E, n_total = {}, 0
    for name in ["a0b0", "a0b1", "a1b0", "a1b1"]:
        e, n = correlator_from_counts(counts_by_setting[name])
        E[name] = e
        n_total += n
    S = E["a0b0"] - E["a0b1"] + E["a1b0"] + E["a1b1"]
    shots = n_total // 4 if n_total else 1
    sigma = np.sqrt(4.0 / max(shots, 1))
    return {"S": float(S), "correlators": {k: float(v) for k, v in E.items()},
            "sigma": float(sigma), "shots_per_setting": int(shots)}


def arm_verdict(S, sigma):
    """PASS / FAIL / INDETERMINATE with a k-sigma margin (preregistered)."""
    if S - K_MARGIN * sigma > CHSH_CLASSICAL:
        return "PASS"
    if S + K_MARGIN * sigma <= CHSH_CLASSICAL:
        return "FAIL"
    return "INDETERMINATE"


# ----------------------------------------------------------------------------------------
# NIST beacon + manifest
# ----------------------------------------------------------------------------------------
def fetch_nist_beacon(timeout=15):
    try:
        r = requests.get(NIST_BEACON_URL, timeout=timeout)
        r.raise_for_status()
        pulse = r.json().get("pulse", {})
        return {
            "nist_beacon_pulse": int(pulse.get("pulseIndex", 0)),
            "nist_value": str(pulse.get("outputValue", "")),
            "nist_timestamp": str(pulse.get("timeStamp", "")),
        }
    except Exception as e:  # noqa: BLE001
        log(f"WARNING: NIST beacon fetch failed: {e}")
        return None


def read_manifest_hashes():
    prereg_hash = sha256_file(PREREG_PATH) if os.path.exists(PREREG_PATH) else ""
    harness_hash = sha256_file(HARNESS_PATH)
    declared = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    declared[os.path.basename(parts[-1])] = parts[0]
    return {"manifest_prereg_sha256": prereg_hash,
            "manifest_harness_sha256": harness_hash,
            "manifest_declared": declared}


# ----------------------------------------------------------------------------------------
# Calibration snapshot (hardened — new in TRINITY-2)
# ----------------------------------------------------------------------------------------
def simulator_calibration_snapshot(label, depol1, depol2, seed, n_qubits=2):
    """Deterministic synthetic calibration snapshot for a simulated device."""
    rng = np.random.default_rng(seed)
    qubits = []
    for q in range(n_qubits):
        qubits.append({
            "qubit": q,
            "T1_us": round(float(80 + rng.uniform(-20, 40)), 3),
            "T2_us": round(float(60 + rng.uniform(-15, 30)), 3),
            "readout_error": round(float(0.01 + rng.uniform(0, 0.02)), 5),
            "frequency_ghz": round(float(4.8 + rng.uniform(-0.2, 0.2)), 5),
        })
    snapshot = {
        "backend_name": f"aer_sim::{label}",
        "backend_version": "aer-sim-1",
        "n_qubits": n_qubits,
        "coupling_map_fingerprint": sha256_hex(f"linear-{n_qubits}-{label}"),
        "basis_gates": ["ry", "h", "cx", "measure"],
        "single_qubit_depolarizing": depol1,
        "two_qubit_depolarizing": depol2,
        "qubits": qubits,
    }
    return snapshot


def hardware_calibration_snapshot(backend):
    """Full calibration snapshot captured from a real IBM backend at submission time."""
    props = backend.properties()
    conf = backend.configuration()
    n = conf.n_qubits
    qubits = []
    for q in range(n):
        try:
            qubits.append({
                "qubit": q,
                "T1_us": round(float(props.t1(q) * 1e6), 3),
                "T2_us": round(float(props.t2(q) * 1e6), 3),
                "readout_error": round(float(props.readout_error(q)), 6),
                "frequency_ghz": round(float(props.frequency(q) / 1e9), 6),
            })
        except Exception:  # noqa: BLE001
            qubits.append({"qubit": q, "T1_us": None, "T2_us": None,
                           "readout_error": None, "frequency_ghz": None})
    try:
        cmap = sorted([list(map(int, e)) for e in conf.coupling_map]) if conf.coupling_map else []
    except Exception:  # noqa: BLE001
        cmap = []
    snapshot = {
        "backend_name": backend.name,
        "backend_version": str(getattr(backend, "version", conf.backend_version)),
        "n_qubits": n,
        "coupling_map_fingerprint": sha256_hex(canonical_json(cmap)),
        "basis_gates": list(conf.basis_gates),
        "last_update_date": str(props.last_update_date) if props else "",
        "qubits": qubits,
    }
    return snapshot


# ----------------------------------------------------------------------------------------
# Execution backends
# ----------------------------------------------------------------------------------------
def run_one_simulator(circuits, shots, depol1, depol2, seed, label):
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(depol1, 1), ["ry", "h", "x", "sx"])
    nm.add_all_qubit_quantum_error(depolarizing_error(depol2, 2), ["cx", "cz"])
    backend = AerSimulator(noise_model=nm, seed_simulator=seed)

    names = list(circuits.keys())
    tqc = transpile([circuits[n] for n in names], backend, optimization_level=3)
    result = backend.run(tqc, shots=shots).result()
    counts = {n: {k.replace(" ", ""): v for k, v in result.get_counts(i).items()}
              for i, n in enumerate(names)}
    snapshot = simulator_calibration_snapshot(label, depol1, depol2, seed)
    backend_info = {
        "backend": f"aer_sim::{label}",
        "job_id": f"SIM-{label}-{seed}",
        "calibration_snapshot": snapshot,
        "calibration_snapshot_hash": sha256_hex(canonical_json(snapshot)),
        "qubit_mapping": {n: list(range(circuits[n].num_qubits)) for n in names},
    }
    return counts, backend_info


def run_one_hardware(circuits, shots, token, backend_name):
    from qiskit_ibm_runtime import QiskitRuntimeService, Batch, SamplerV2 as Sampler

    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    backend = service.backend(backend_name)
    names = list(circuits.keys())
    # capture calibration BEFORE running so the snapshot reflects submission-time state
    snapshot = hardware_calibration_snapshot(backend)
    tqc = transpile([circuits[n] for n in names], backend, optimization_level=3)

    counts, job_id = {}, None
    with Batch(backend=backend) as batch:
        sampler = Sampler(mode=batch)
        job = sampler.run(tqc, shots=shots)
        job_id = job.job_id()
        log(f"  [{backend_name}] submitted job {job_id}; polling...")
        res = job.result()
    for i, n in enumerate(names):
        data = res[i].data
        creg = list(data.__dict__.keys())[0] if hasattr(data, "__dict__") else "c"
        counts[n] = {k.replace(" ", ""): v for k, v in getattr(data, creg).get_counts().items()}

    phys = {}
    for j, n in enumerate(names):
        try:
            layout = tqc[j].layout
            phys[n] = ([int(q) for q in layout.final_index_layout(filter_ancillas=True)]
                       if layout is not None else list(range(circuits[n].num_qubits)))
        except Exception:  # noqa: BLE001
            phys[n] = list(range(circuits[n].num_qubits))
    backend_info = {
        "backend": backend.name,
        "job_id": job_id,
        "calibration_snapshot": snapshot,
        "calibration_snapshot_hash": sha256_hex(canonical_json(snapshot)),
        "qubit_mapping": phys,
    }
    return counts, backend_info


# ----------------------------------------------------------------------------------------
# Per-device evaluation
# ----------------------------------------------------------------------------------------
def evaluate_device(slot, counts, backend_info):
    chsh = compute_chsh(counts)
    verdict = arm_verdict(chsh["S"], chsh["sigma"])
    n_sigma = (abs(chsh["S"]) - CHSH_CLASSICAL) / chsh["sigma"] if chsh["sigma"] > 0 else 0.0
    witness_obj = {
        "slot": slot,
        "backend": backend_info["backend"],
        "S": round(chsh["S"], 6),
        "n_sigma": round(float(n_sigma), 4),
        "correlators": {k: round(v, 6) for k, v in chsh["correlators"].items()},
        "classical_bound": CHSH_CLASSICAL,
        "tsirelson": round(CHSH_TSIRELSON, 6),
        "k_margin": K_MARGIN,
        "sigma": round(chsh["sigma"], 6),
        "shots_per_setting": chsh["shots_per_setting"],
        "verdict": verdict,
        "pass": verdict == "PASS",
    }
    device_witness_hash = sha256_hex(canonical_json(witness_obj))
    device_record = {
        "slot": slot,
        "backend": backend_info["backend"],
        "job_id": backend_info["job_id"],
        "calibration_snapshot": backend_info["calibration_snapshot"],
        "calibration_snapshot_hash": backend_info["calibration_snapshot_hash"],
        "qubit_mapping": backend_info["qubit_mapping"],
        "raw_counts": counts,
        "witness": witness_obj,
        "device_witness_hash": device_witness_hash,
    }
    return device_record


# ----------------------------------------------------------------------------------------
# Fused governed-action verdict (preregistered precedence)
# ----------------------------------------------------------------------------------------
def governed_verdict(device_records, provenance_ok, reconstructs):
    """
    Precedence (TRINITY-2 prereg §6):
      1. GATE-STOP — integrity/provenance failure, OR fewer than QUORUM distinct devices with a
         definite (PASS/FAIL) result.  Action DENIED.
      2. DENY      — quorum of definite devices present but not all PASS (a dissenting device).
                     Action DENIED.
      3. HOLD      — quorum met and all definite-PASS, but fewer than FULL_QUORUM distinct
                     devices (degraded quorum).  Action HELD for human confirmation.
      4. ALLOW     — all FULL_QUORUM distinct devices PASS.  Action AUTHORIZED.
    """
    if not provenance_ok or not reconstructs:
        return "GATE-STOP", False
    definite = [d for d in device_records if d["witness"]["verdict"] in ("PASS", "FAIL")]
    distinct_definite = len({d["backend"] for d in definite})
    if distinct_definite < QUORUM_REQUIRED:
        return "GATE-STOP", False
    fails = [d for d in definite if d["witness"]["verdict"] == "FAIL"]
    if fails:
        return "DENY", (distinct_definite < FULL_QUORUM)
    # all definite devices PASS
    distinct_pass = len({d["backend"] for d in definite if d["witness"]["verdict"] == "PASS"})
    if distinct_pass >= FULL_QUORUM:
        return "ALLOW", False
    return "HOLD", True  # degraded quorum (e.g. 2 of 3)


def decision_for(verdict):
    return {
        "ALLOW": "AUTHORIZED",
        "HOLD": "HELD_FOR_HUMAN_CONFIRMATION",
        "DENY": "DENIED",
        "GATE-STOP": "DENIED",
    }[verdict]


# ----------------------------------------------------------------------------------------
# ProofRecord assembly
# ----------------------------------------------------------------------------------------
def circuit_qasm_hashes(circuits):
    out = {}
    for n, qc in circuits.items():
        try:
            q = qasm3_dumps(qc)
        except Exception:  # noqa: BLE001
            q = repr(qc)
        out[n] = {"qasm_sha256": sha256_hex(q), "n_qubits": qc.num_qubits}
    return out


def assemble_proofrecord(device_records, circuits, nist, manifest, mode, shots,
                         substitutions):
    distinct = len({d["backend"] for d in device_records})

    prereg_ok = True
    declared = manifest.get("manifest_declared", {})
    if declared:
        if declared.get("TRINITY-2-preregistration.md") and \
           declared["TRINITY-2-preregistration.md"] != manifest["manifest_prereg_sha256"]:
            prereg_ok = False
        if declared.get("trinity2_harness.py") and \
           declared["trinity2_harness.py"] != manifest["manifest_harness_sha256"]:
            prereg_ok = False
    provenance_ok = (nist is not None) and bool(PREVIOUS_RECORD_HASH) and prereg_ok
    reconstructs = True  # independent authority is trinity2_verify.py

    verdict, degraded = governed_verdict(device_records, provenance_ok, reconstructs)
    decision = decision_for(verdict)

    nist_value = nist["nist_value"] if nist else ""
    ordered = sorted(device_records, key=lambda x: x["slot"])
    fusion_tokens = [f"{d['device_witness_hash']}:{d['calibration_snapshot_hash']}"
                     for d in ordered]

    governed_action = dict(GOVERNED_ACTION_TEMPLATE)
    governed_action["decision"] = decision
    governed_action["decided_at"] = datetime.now(timezone.utc).isoformat()
    governed_action["governed_by_verdict"] = verdict
    governed_action_hash = sha256_hex(canonical_json(governed_action))

    fused_nonce = sha256_hex("|".join(
        fusion_tokens + [nist_value, LIGO_GW150914_HASH, PREVIOUS_RECORD_HASH,
                         governed_action_hash]))

    valid_devices = len({d["backend"] for d in device_records
                         if d["witness"]["verdict"] in ("PASS", "FAIL")})

    record = {
        "schema": SCHEMA,
        "experiment": EXPERIMENT,
        "framework": FRAMEWORK,
        "governance": GOVERNANCE,
        "mode": mode,
        "public_claim": ("A preregistered demonstration in which a simulated high-impact action "
                         "is allowed, held, or denied by a Bell-CHSH witness independently "
                         "evaluated on three quantum processors and fused into one chain-linked, "
                         "independently reconstructable ExecutionProof record, with a quorum + "
                         "substitution rule governing processor unavailability."),
        "devices": device_records,
        "distinct_devices": distinct,
        "device_substitutions": substitutions,
        "quorum": {
            "required": QUORUM_REQUIRED,
            "full": FULL_QUORUM,
            "valid_devices": valid_devices,
            "degraded_quorum": bool(degraded),
        },
        "governed_action": governed_action,
        "aggregate_verdict": verdict,
        "action_decision": decision,
        "trinity_certified": verdict == "ALLOW",
        "witness_type": "Bell-CHSH",
        "circuits": circuit_qasm_hashes(circuits),
        "shots_per_circuit": shots,
        "shots_total": shots * 4 * len(device_records),
        "external_entropy": {
            "nist_beacon_pulse": nist["nist_beacon_pulse"] if nist else 0,
            "nist_value": nist_value,
            "nist_timestamp": nist["nist_timestamp"] if nist else "",
            "ligo_gw150914_hash": LIGO_GW150914_HASH,
        },
        "chain": {
            "previous_record_label": PREVIOUS_RECORD_LABEL,
            "previous_record_hash": PREVIOUS_RECORD_HASH,
            "manifest_prereg_sha256": manifest["manifest_prereg_sha256"],
            "manifest_harness_sha256": manifest["manifest_harness_sha256"],
        },
        "governed_action_hash": governed_action_hash,
        "fused_nonce": fused_nonce,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    record["record_hash"] = sha256_hex(canonical_json(record))
    return record


# ----------------------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------------------
def write_report(record):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    rows = ""
    for d in sorted(record["devices"], key=lambda x: x["slot"]):
        w = d["witness"]
        rows += (f"| {d['slot']} | `{d['backend']}` | {w['S']} | {w['n_sigma']} | "
                 f"{w['verdict']} | `{d['calibration_snapshot_hash'][:12]}…` | `{d['job_id']}` |\n")
    subs = "\n".join(f"- {s}" for s in record["device_substitutions"]) or "- none"
    ga = record["governed_action"]
    md = f"""# TRINITY-2 Report — The Governed Action

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**

- Experiment: **{record['experiment']}**  ·  Schema: `{record['schema']}`
- Mode: **{record['mode']}**  ·  Witness: **{record['witness_type']}**
- Distinct devices: **{record['distinct_devices']}**  ·  Shots total: **{record['shots_total']:,}**
- Generated: {record['generated_at']}

> **Public claim:** {record['public_claim']}

## Governed action (SIMULATED)

| Field | Value |
|---|---|
| Action | {ga['action_type']} |
| Amount | {ga['amount']:,} {ga['currency']} |
| Payee ref | `{ga['payee_ref']}` |
| Policy ref | `{ga['policy_ref']}` |
| **Decision** | **{ga['decision']}** |
| Governed by verdict | {ga['governed_by_verdict']} |
| Simulated | {ga['simulated']} |

## Aggregate ExecutionProof verdict: **{record['aggregate_verdict']}**  →  action **{record['action_decision']}**

`trinity_certified = {record['trinity_certified']}`

Quorum: required **{record['quorum']['required']}** of **{record['quorum']['full']}** · valid devices **{record['quorum']['valid_devices']}** · degraded_quorum **{record['quorum']['degraded_quorum']}**

| Slot | Backend | S | nσ | Arm | Calib snapshot | Job |
|---|---|---|---|---|---|---|
{rows}
Classical bound |S| ≤ 2.0 · Tsirelson 2√2 ≈ 2.828 · PASS iff S − {K_MARGIN}σ > 2.0 · FAIL iff S + {K_MARGIN}σ ≤ 2.0 · else INDETERMINATE.

### Device substitutions / failover
{subs}

## Fusion & provenance
- Fused nonce: `{record['fused_nonce']}`
- Governed-action hash: `{record['governed_action_hash']}`
- Record hash: `{record['record_hash']}`
- Chain — previous record ({record['chain']['previous_record_label']}): `{record['chain']['previous_record_hash']}`
- NIST beacon pulse: `{record['external_entropy']['nist_beacon_pulse']}` @ {record['external_entropy']['nist_timestamp']}
- LIGO GW150914 anchor: `{record['external_entropy']['ligo_gw150914_hash']}`
- Manifest (prereg): `{record['chain']['manifest_prereg_sha256']}`
- Manifest (harness): `{record['chain']['manifest_harness_sha256']}`

## Verdict logic (preregistered, precedence DENY-side first)
- **GATE-STOP** → action DENIED — integrity/provenance failure, or fewer than {QUORUM_REQUIRED} distinct devices with a definite (PASS/FAIL) result.
- **DENY** → action DENIED — quorum of definite devices present but not all PASS (a dissenting device is never averaged away).
- **HOLD** → action HELD for human confirmation — quorum met and all-PASS but degraded (fewer than {FULL_QUORUM} distinct devices).
- **ALLOW** → action AUTHORIZED — all {FULL_QUORUM} distinct devices PASS.

## Scope & honesty
The payment is **simulated** — no real funds, rail, customer authority, or entitlement. The
quantum result is **device-dependent**; Bell locality and detection loopholes remain **open**.
Cross-device agreement demonstrates **reproducibility and multi-root provenance with failover**,
not device independence or loophole closure. No entanglement exists between processors. This is
an **experimental governance demonstration**, not a security proof, randomness-certification, or
production certification. σ is binomial shot noise only.

*Proof Before Power · Verification Before Execution · claims kept narrower than the evidence.*
"""
    with open(os.path.join(RESULTS_DIR, "TRINITY-2-report.md"), "w") as f:
        f.write(md)
    with open(os.path.join(RESULTS_DIR, "TRINITY-2-proofrecord.json"), "w") as f:
        json.dump(record, f, indent=2, sort_keys=True)
    log(f"Report + ProofRecord written to {RESULTS_DIR}")


def resolve_ibm_token():
    tok = os.environ.get("IBM_QUANTUM_TOKEN")
    if tok:
        return tok, "env:IBM_QUANTUM_TOKEN"
    return None, None


# ----------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="TRINITY-2 Governed Action harness")
    ap.add_argument("--shots", type=int, default=4000, help="shots per circuit")
    ap.add_argument("--authorize-hardware", action="store_true",
                    help="attempt IBM Quantum hardware run (GATED)")
    ap.add_argument("--allow-unrotated", action="store_true",
                    help="override rotation gate (only after token rotated + authorized)")
    ap.add_argument("--scenario",
                    choices=["nominal", "degraded", "deny", "gatestop"], default="nominal",
                    help="simulator-only: force a verdict branch to validate governance logic")
    args = ap.parse_args()

    circuits = build_chsh_circuits()
    log(f"Built {len(circuits)} CHSH circuits (identical witness for every device).")

    log("Fetching NIST beacon (fresh not-before anchor)...")
    nist = fetch_nist_beacon()
    if nist:
        log(f"NIST pulse {nist['nist_beacon_pulse']} @ {nist['nist_timestamp']}")
    else:
        log("NIST beacon unavailable — provenance will force GATE-STOP.")

    manifest = read_manifest_hashes()
    substitutions = []
    device_records = []
    mode = "SIMULATOR"

    hardware_ok = False
    if args.authorize_hardware:
        token, src = resolve_ibm_token()
        if not args.allow_unrotated:
            log("=" * 78)
            log("HARDWARE RUN BLOCKED BY PREREGISTERED ROTATION GATE (§9).")
            log("Withheld until (a) exposed IBM token rotated AND (b) Derek authorizes.")
            log("Re-run with --allow-unrotated ONLY after both conditions are met.")
            log("Proceeding with SIMULATOR validation instead.")
            log("=" * 78)
        elif not token:
            log("No IBM_QUANTUM_TOKEN in environment; cannot run hardware. Using simulator.")
        else:
            hardware_ok = True
            mode = "HARDWARE"
            log(f"Authorized hardware run (token from {src}). Running three devices...")
            for i, dev in enumerate(TARGET_DEVICES, start=1):
                slot = f"D{i}"
                try:
                    counts, binfo = run_one_hardware(circuits, args.shots, token, dev)
                    device_records.append(evaluate_device(slot, counts, binfo))
                    w = device_records[-1]["witness"]
                    log(f"  {slot} {dev}: S={w['S']:.4f} ({w['verdict']})")
                except Exception as e:  # noqa: BLE001
                    log(f"  {slot} {dev}: UNAVAILABLE ({e}) — recorded as substitution.")
                    substitutions.append({"slot": slot, "target": dev,
                                          "actual": None, "reason": str(e)})

    if not hardware_ok:
        log(f"Running SIMULATOR validation (scenario={args.scenario}, shots={args.shots})...")
        # three independent devices with distinct noise profiles
        profiles = [
            ("kingston-sim", 0.002, 0.010, 101),
            ("fez-sim",      0.003, 0.014, 202),
            ("marrakesh-sim", 0.004, 0.018, 303),
        ]
        active = profiles
        if args.scenario == "deny":
            # device 3 dissents (classical, no entanglement) -> FAIL -> DENY
            active = profiles[:2] + [("marrakesh-sim-degraded", 0.5, 0.9, 303)]
        elif args.scenario == "degraded":
            # device 3 unavailable -> only 2 devices -> HOLD (degraded quorum)
            active = profiles[:2]
            substitutions.append({"slot": "D3", "target": "ibm_marrakesh",
                                  "actual": None, "reason": "device unavailable at run time"})
        elif args.scenario == "gatestop":
            # devices 2 and 3 unavailable -> sub-quorum -> GATE-STOP
            active = profiles[:1]
            substitutions.append({"slot": "D2", "target": "ibm_fez",
                                  "actual": None, "reason": "device unavailable at run time"})
            substitutions.append({"slot": "D3", "target": "ibm_marrakesh",
                                  "actual": None, "reason": "device unavailable at run time"})
        for i, (label, d1, d2, seed) in enumerate(active, start=1):
            counts, binfo = run_one_simulator(circuits, args.shots, d1, d2, seed, label)
            device_records.append(evaluate_device(f"D{i}", counts, binfo))
            w = device_records[-1]["witness"]
            log(f"  D{i} {label}: S={w['S']:.4f} ({w['n_sigma']:.2f}σ) -> {w['verdict']}")

    record = assemble_proofrecord(device_records, circuits, nist, manifest, mode,
                                  args.shots, substitutions)
    write_report(record)

    # -------- kill-condition self-check (prereg §8) --------
    kc_violation = None
    verdicts = [d["witness"]["verdict"] for d in record["devices"]]
    if record["aggregate_verdict"] == "ALLOW":
        if any(v != "PASS" for v in verdicts):
            kc_violation = "ALLOW emitted while a device did not PASS"
        if record["quorum"]["degraded_quorum"]:
            kc_violation = "ALLOW emitted under degraded quorum"
        if record["distinct_devices"] < FULL_QUORUM:
            kc_violation = "ALLOW emitted with fewer than full quorum of distinct devices"

    log("=" * 78)
    for d in sorted(record["devices"], key=lambda x: x["slot"]):
        w = d["witness"]
        log(f"{d['slot']} {d['backend']:26s} S={w['S']:.4f}  {w['verdict']}")
    log(f"QUORUM valid={record['quorum']['valid_devices']} degraded={record['quorum']['degraded_quorum']}")
    log(f"AGGREGATE EXECUTIONPROOF VERDICT: {record['aggregate_verdict']}")
    log(f"GOVERNED ACTION DECISION:         {record['action_decision']}")
    log(f"trinity_certified = {record['trinity_certified']}")
    log(f"fused_nonce = {record['fused_nonce']}")
    log(f"record_hash = {record['record_hash']}")
    if kc_violation:
        log("!" * 78)
        log(f"KILL CONDITION TRIGGERED: {kc_violation}")
        log("!" * 78)
        return 2
    log("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
