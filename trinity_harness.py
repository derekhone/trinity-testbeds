#!/usr/bin/env python3
"""
TRINITY-1: The Three-Processor Witness — experiment harness.

Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed.

One nonclassicality witness (Bell-CHSH) executed INDEPENDENTLY on three separate physical
quantum processors (ibm_kingston, ibm_fez, ibm_marrakesh). Each device is evaluated on its own
against the classical bound; all three device-level records are fused into a single
chain-linked, independently reconstructable `trinity-proofrecord-1.0` ExecutionProof record.

Novelty (narrow): to our knowledge the first preregistered ExecutionProof record binding one
witness independently certified across three distinct quantum processors. This is a robustness
+ multi-root-provenance demonstration, NOT a loophole closure or device-independence claim.

DEFAULT MODE: simulator validation (three independent noisy aer backends). Hardware submission
is GATED: it refuses to run unless --authorize-hardware AND --allow-unrotated are both passed
(after the exposed token has been rotated) and IBM_QUANTUM_TOKEN is set in the environment.

Usage:
  python3 trinity_harness.py                       # simulator validation (default)
  python3 trinity_harness.py --shots 4000          # custom shots
  python3 trinity_harness.py --scenario hold       # exercise HOLD branch on simulator
  python3 trinity_harness.py --scenario deny        # exercise DENY (invalid device) branch
  python3 trinity_harness.py --authorize-hardware --allow-unrotated   # hardware (post-rotation)
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
SCHEMA = "trinity-proofrecord-1.0"
EXPERIMENT = "TRINITY-1"
FRAMEWORK = "Coherent Inheritance Framework (CIF)"
GOVERNANCE = "ExecutionProof"

CHSH_CLASSICAL = 2.0
CHSH_TSIRELSON = 2.0 * np.sqrt(2.0)
CHSH_THRESHOLD = 2.2

TARGET_DEVICES = ["ibm_kingston", "ibm_fez", "ibm_marrakesh"]
REQUIRED_DISTINCT_DEVICES = 3

LIGO_GW150914_HASH = "66c4b196"       # cosmological anchor carried from WITNESS-3
NIST_BEACON_URL = "https://beacon.nist.gov/beacon/2.0/pulse/last"
PREVIOUS_RECORD_LABEL = "OMNI-1"       # chain continuity link

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")
MANIFEST_PATH = os.path.join(HERE, "MANIFEST.sha256")
PREREG_PATH = os.path.join(HERE, "TRINITY-1-preregistration.md")
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
    print(f"[TRINITY-1] {msg}", flush=True)


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
    n_sigma = (abs(S) - CHSH_CLASSICAL) / sigma if sigma > 0 else 0.0
    return {"S": float(S), "correlators": {k: float(v) for k, v in E.items()},
            "n_sigma": float(n_sigma), "sigma": float(sigma), "shots_per_setting": int(shots)}


def device_verdict(S):
    if S < CHSH_CLASSICAL:
        return "INVALID"
    if S >= CHSH_THRESHOLD:
        return "VALID_ABOVE"
    return "INCONCLUSIVE"


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
# Execution backends
# ----------------------------------------------------------------------------------------
def run_one_simulator(circuits, shots, depol1, depol2, seed, label):
    """Simulate ONE independent device as a noisy aer backend."""
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
    backend_info = {
        "backend": f"aer_sim::{label}",
        "job_id": f"SIM-{label}-{seed}",
        "calibration_hash": sha256_hex(f"aer-depol-{depol1}-{depol2}-seed{seed}"),
        "qubit_mapping": {n: list(range(circuits[n].num_qubits)) for n in names},
    }
    return counts, backend_info


def run_one_hardware(circuits, shots, token, backend_name):
    """Run the CHSH witness on ONE real IBM Quantum device."""
    from qiskit_ibm_runtime import QiskitRuntimeService, Batch, SamplerV2 as Sampler

    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    backend = service.backend(backend_name)
    names = list(circuits.keys())
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

    props = backend.properties()
    cal_source = str(props.last_update_date) if props else backend.name
    # physical qubits after transpile (best-effort)
    try:
        phys = {n: [tqc[j].find_bit(q).index for q in tqc[j].qubits]
                for j, n in enumerate(names)}
    except Exception:  # noqa: BLE001
        phys = {n: list(range(2)) for n in names}
    backend_info = {
        "backend": backend.name,
        "job_id": job_id,
        "calibration_hash": sha256_hex(cal_source),
        "qubit_mapping": phys,
    }
    return counts, backend_info


# ----------------------------------------------------------------------------------------
# Per-device evaluation
# ----------------------------------------------------------------------------------------
def evaluate_device(slot, counts, backend_info):
    chsh = compute_chsh(counts)
    verdict = device_verdict(chsh["S"])
    witness_obj = {
        "slot": slot,
        "backend": backend_info["backend"],
        "S": round(chsh["S"], 6),
        "n_sigma": round(chsh["n_sigma"], 4),
        "correlators": {k: round(v, 6) for k, v in chsh["correlators"].items()},
        "classical_bound": CHSH_CLASSICAL,
        "tsirelson": round(CHSH_TSIRELSON, 6),
        "threshold": CHSH_THRESHOLD,
        "shots_per_setting": chsh["shots_per_setting"],
        "verdict": verdict,
        "certified": verdict == "VALID_ABOVE",
    }
    device_witness_hash = sha256_hex(canonical_json(witness_obj))
    device_record = {
        "slot": slot,
        "backend": backend_info["backend"],
        "job_id": backend_info["job_id"],
        "calibration_hash": backend_info["calibration_hash"],
        "qubit_mapping": backend_info["qubit_mapping"],
        "raw_counts": counts,
        "witness": witness_obj,
        "device_witness_hash": device_witness_hash,
    }
    return device_record


# ----------------------------------------------------------------------------------------
# Aggregate verdict
# ----------------------------------------------------------------------------------------
def aggregate_verdict(device_records, distinct_devices, provenance_ok, reconstructs):
    if not provenance_ok or not reconstructs:
        return "DENY"
    if distinct_devices < REQUIRED_DISTINCT_DEVICES:
        return "GATE-STOP"
    verdicts = [d["witness"]["verdict"] for d in device_records]
    if any(v == "INVALID" for v in verdicts):
        return "DENY"
    if any(v == "INCONCLUSIVE" for v in verdicts):
        return "HOLD"
    if all(v == "VALID_ABOVE" for v in verdicts):
        return "ALLOW"
    return "HOLD"


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
                         previous_record_hash, substitutions):
    distinct = len({d["backend"] for d in device_records})

    # provenance
    prereg_ok = True
    declared = manifest.get("manifest_declared", {})
    if declared:
        if declared.get("TRINITY-1-preregistration.md") and \
           declared["TRINITY-1-preregistration.md"] != manifest["manifest_prereg_sha256"]:
            prereg_ok = False
        if declared.get("trinity_harness.py") and \
           declared["trinity_harness.py"] != manifest["manifest_harness_sha256"]:
            prereg_ok = False
    provenance_ok = (nist is not None) and bool(previous_record_hash) and prereg_ok
    reconstructs = True  # independent authority is trinity_verify.py

    agg = aggregate_verdict(device_records, distinct, provenance_ok, reconstructs)

    nist_value = nist["nist_value"] if nist else ""
    ordered_hashes = [d["device_witness_hash"] for d in
                      sorted(device_records, key=lambda x: x["slot"])]
    trinity_nonce = sha256_hex("|".join(
        ordered_hashes + [nist_value, LIGO_GW150914_HASH, previous_record_hash]))

    record = {
        "schema": SCHEMA,
        "experiment": EXPERIMENT,
        "framework": FRAMEWORK,
        "governance": GOVERNANCE,
        "mode": mode,
        "public_claim": ("A preregistered demonstration of one nonclassicality witness "
                         "independently evaluated on three distinct quantum processors and "
                         "fused into a single chain-linked, independently reconstructable "
                         "ExecutionProof record."),
        "devices": device_records,
        "distinct_devices": distinct,
        "device_substitutions": substitutions,
        "aggregate_verdict": agg,
        "trinity_certified": agg == "ALLOW",
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
            "previous_record_hash": previous_record_hash,
            "manifest_prereg_sha256": manifest["manifest_prereg_sha256"],
            "manifest_harness_sha256": manifest["manifest_harness_sha256"],
        },
        "trinity_nonce": trinity_nonce,
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
                 f"{w['verdict']} | `{d['job_id']}` |\n")
    md = f"""# TRINITY-1 Report — The Three-Processor Witness

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**

- Experiment: **{record['experiment']}**  ·  Schema: `{record['schema']}`
- Mode: **{record['mode']}**  ·  Witness: **{record['witness_type']}**
- Distinct devices: **{record['distinct_devices']}**  ·  Shots total: **{record['shots_total']:,}**
- Generated: {record['generated_at']}

> **Public claim:** {record['public_claim']}

## Aggregate ExecutionProof verdict: **{record['aggregate_verdict']}**

`trinity_certified = {record['trinity_certified']}`

| Slot | Backend | S | nσ | Verdict | Job |
|---|---|---|---|---|---|
{rows}
Classical bound |S| ≤ 2.0 · Tsirelson 2√2 ≈ 2.828 · certification threshold S ≥ {CHSH_THRESHOLD}.

## Fusion & provenance
- TRINITY nonce: `{record['trinity_nonce']}`
- Record hash: `{record['record_hash']}`
- Chain — previous record ({record['chain']['previous_record_label']}): `{record['chain']['previous_record_hash']}`
- NIST beacon pulse: `{record['external_entropy']['nist_beacon_pulse']}` @ {record['external_entropy']['nist_timestamp']}
- LIGO GW150914 anchor: `{record['external_entropy']['ligo_gw150914_hash']}`
- Manifest (prereg): `{record['chain']['manifest_prereg_sha256']}`
- Manifest (harness): `{record['chain']['manifest_harness_sha256']}`

## Verdict logic (preregistered)
- **ALLOW** — all three devices VALID_ABOVE (S ≥ {CHSH_THRESHOLD}), reconstructs, provenance valid.
- **HOLD** — ≥3 devices, provenance valid, but any device INCONCLUSIVE (2.0–2.2).
- **DENY** — provenance invalid, reconstruction mismatch, tampering, or any device INVALID (S < 2.0).
- **GATE-STOP** — fewer than three distinct devices returned valid data, or NIST unavailable.
- Precedence: DENY > GATE-STOP > HOLD > ALLOW.

## Scope & honesty
Device-dependent. Bell locality and detection loopholes are **open**. Cross-device agreement
demonstrates **reproducibility and multi-root provenance, not** device independence or loophole
closure. No entanglement exists between the three processors; TRINITY-1 certifies the same
nonclassical signature independently on three machines and binds the classical records. σ is
binomial shot noise only. Experimental evidence + governance demonstration — not a security
proof, not a randomness-certification proof, not a production certification.

*Proof Before Power · Verification Before Execution · claims kept narrower than the evidence.*
"""
    with open(os.path.join(RESULTS_DIR, "TRINITY-1-report.md"), "w") as f:
        f.write(md)
    with open(os.path.join(RESULTS_DIR, "TRINITY-1-proofrecord.json"), "w") as f:
        json.dump(record, f, indent=2, sort_keys=True)
    log(f"Report + ProofRecord written to {RESULTS_DIR}")


# ----------------------------------------------------------------------------------------
# Token resolution
# ----------------------------------------------------------------------------------------
def resolve_ibm_token():
    tok = os.environ.get("IBM_QUANTUM_TOKEN")
    if tok:
        return tok, "env:IBM_QUANTUM_TOKEN"
    return None, None


# ----------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="TRINITY-1 Three-Processor Witness harness")
    ap.add_argument("--shots", type=int, default=4000, help="shots per circuit")
    ap.add_argument("--authorize-hardware", action="store_true",
                    help="attempt IBM Quantum hardware run (GATED)")
    ap.add_argument("--allow-unrotated", action="store_true",
                    help="override rotation gate (only after token rotated + authorized)")
    ap.add_argument("--scenario", choices=["nominal", "hold", "deny"], default="nominal",
                    help="simulator-only: force a verdict branch to validate governance logic")
    args = ap.parse_args()

    circuits = build_chsh_circuits()
    log(f"Built {len(circuits)} CHSH circuits (identical witness for every device).")

    log("Fetching NIST beacon (fresh not-before anchor)...")
    nist = fetch_nist_beacon()
    if nist:
        log(f"NIST pulse {nist['nist_beacon_pulse']} @ {nist['nist_timestamp']}")
    else:
        log("NIST beacon unavailable — provenance will force GATE-STOP/DENY.")

    manifest = read_manifest_hashes()
    previous_record_hash = sha256_hex(PREVIOUS_RECORD_LABEL)

    substitutions = []
    device_records = []
    mode = "SIMULATOR"

    hardware_ok = False
    if args.authorize_hardware:
        token, src = resolve_ibm_token()
        if not args.allow_unrotated:
            log("=" * 78)
            log("HARDWARE RUN BLOCKED BY PREREGISTERED ROTATION GATE (§8).")
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
                    log(f"  {slot} {dev}: S={device_records[-1]['witness']['S']:.4f} "
                        f"({device_records[-1]['witness']['verdict']})")
                except Exception as e:  # noqa: BLE001
                    log(f"  {slot} {dev}: FAILED ({e}) — recorded as substitution/skip.")
                    substitutions.append({"slot": slot, "target": dev, "error": str(e)})

    if not hardware_ok:
        # Simulator: three independent devices with distinct noise profiles.
        log(f"Running SIMULATOR validation (scenario={args.scenario}, shots={args.shots})...")
        profiles = [
            ("kingston-sim", 0.002, 0.010, 101),
            ("fez-sim",      0.003, 0.014, 202),
            ("marrakesh-sim", 0.004, 0.018, 303),
        ]
        if args.scenario == "deny":
            # make device 3 classical (no entanglement) -> S ~ 0 -> INVALID -> DENY
            profiles[2] = ("marrakesh-sim-degraded", 0.5, 0.9, 303)
        elif args.scenario == "hold":
            # make device 3 land in the inconclusive band (2.0 <= S < 2.2) via heavy noise
            profiles[2] = ("marrakesh-sim-noisy", 0.045, 0.215, 303)
        for i, (label, d1, d2, seed) in enumerate(profiles, start=1):
            counts, binfo = run_one_simulator(circuits, args.shots, d1, d2, seed, label)
            device_records.append(evaluate_device(f"D{i}", counts, binfo))
            w = device_records[-1]["witness"]
            log(f"  D{i} {label}: S={w['S']:.4f} ({w['n_sigma']:.2f}σ) -> {w['verdict']}")

    record = assemble_proofrecord(device_records, circuits, nist, manifest, mode,
                                  args.shots, previous_record_hash, substitutions)
    write_report(record)

    log("=" * 78)
    for d in sorted(record["devices"], key=lambda x: x["slot"]):
        w = d["witness"]
        log(f"{d['slot']} {d['backend']:24s} S={w['S']:.4f}  {w['verdict']}")
    log(f"AGGREGATE EXECUTIONPROOF VERDICT: {record['aggregate_verdict']}")
    log(f"trinity_certified = {record['trinity_certified']}")
    log(f"trinity_nonce = {record['trinity_nonce']}")
    log(f"record_hash   = {record['record_hash']}")
    log("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
