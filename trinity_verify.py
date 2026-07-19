#!/usr/bin/env python3
"""
TRINITY-1 independent verifier.

Reconstructs every device's CHSH S, the per-device verdict, each device_witness_hash, the
fused trinity_nonce, the record_hash, and the aggregate ExecutionProof verdict DIRECTLY from
the released raw counts in results/TRINITY-1-proofrecord.json — with NO qiskit / harness
dependency (standard library + nothing else). Emits its own governance verdict and exits 0 iff
everything reconstructs and agrees, else 1.

Usage: python3 trinity_verify.py
"""

import hashlib
import json
import math
import os
import sys

# Preregistered constants (hard-coded here so the verifier is independent of the harness)
CHSH_CLASSICAL = 2.0
CHSH_THRESHOLD = 2.2
REQUIRED_DISTINCT_DEVICES = 3
LIGO_GW150914_HASH = "66c4b196"
TOL = 1e-6

HERE = os.path.dirname(os.path.abspath(__file__))
RECORD_PATH = os.path.join(HERE, "results", "TRINITY-1-proofrecord.json")


def sha256_hex(data) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def correlator(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0
    e = 0
    for bitstr, c in counts.items():
        bits = bitstr.replace(" ", "")[-2:]
        parity = 1 if bits.count("1") % 2 == 0 else -1
        e += parity * c
    return e / total


def recompute_S(raw_counts):
    E = {k: correlator(raw_counts[k]) for k in ["a0b0", "a0b1", "a1b0", "a1b1"]}
    return E["a0b0"] - E["a0b1"] + E["a1b0"] + E["a1b1"], E


def device_verdict(S):
    if S < CHSH_CLASSICAL:
        return "INVALID"
    if S >= CHSH_THRESHOLD:
        return "VALID_ABOVE"
    return "INCONCLUSIVE"


def aggregate(verdicts, distinct, provenance_ok, reconstructs):
    if not provenance_ok or not reconstructs:
        return "DENY"
    if distinct < REQUIRED_DISTINCT_DEVICES:
        return "GATE-STOP"
    if any(v == "INVALID" for v in verdicts):
        return "DENY"
    if any(v == "INCONCLUSIVE" for v in verdicts):
        return "HOLD"
    if all(v == "VALID_ABOVE" for v in verdicts):
        return "ALLOW"
    return "HOLD"


def main():
    if not os.path.exists(RECORD_PATH):
        print(f"[VERIFY] ProofRecord not found: {RECORD_PATH}")
        return 1
    with open(RECORD_PATH) as f:
        rec = json.load(f)

    print("=" * 78)
    print("TRINITY-1 INDEPENDENT VERIFICATION")
    print("=" * 78)

    ok = True
    recomputed_verdicts = []
    ordered = sorted(rec["devices"], key=lambda x: x["slot"])

    for d in ordered:
        S, E = recompute_S(d["raw_counts"])
        recorded_S = d["witness"]["S"]
        dS = abs(S - recorded_S)
        v = device_verdict(S)
        recomputed_verdicts.append(v)
        match = "OK" if dS < 1e-3 else "MISMATCH"
        if dS >= 1e-3:
            ok = False
        # per-device witness hash reconstruction
        wh = sha256_hex(canonical_json(d["witness"]))
        wh_match = "OK" if wh == d["device_witness_hash"] else "MISMATCH"
        if wh != d["device_witness_hash"]:
            ok = False
        vmatch = "OK" if v == d["witness"]["verdict"] else "MISMATCH"
        if v != d["witness"]["verdict"]:
            ok = False
        print(f"{d['slot']} {d['backend']:26s} "
              f"S_recomputed={S:.4f} recorded={recorded_S:.4f} [{match}] "
              f"verdict={v}[{vmatch}] witness_hash[{wh_match}]")

    # distinct devices
    distinct = len({d["backend"] for d in ordered})
    print(f"\nDistinct devices: {distinct} (required {REQUIRED_DISTINCT_DEVICES})")

    # trinity_nonce reconstruction
    ordered_hashes = [d["device_witness_hash"] for d in ordered]
    nist_value = rec["external_entropy"]["nist_value"]
    prev_hash = rec["chain"]["previous_record_hash"]
    nonce = sha256_hex("|".join(ordered_hashes + [nist_value, LIGO_GW150914_HASH, prev_hash]))
    nonce_match = "OK" if nonce == rec["trinity_nonce"] else "MISMATCH"
    if nonce != rec["trinity_nonce"]:
        ok = False
    print(f"trinity_nonce  [{nonce_match}]")

    # record_hash reconstruction
    rec_copy = dict(rec)
    stored_hash = rec_copy.pop("record_hash", None)
    rh = sha256_hex(canonical_json(rec_copy))
    rh_match = "OK" if rh == stored_hash else "MISMATCH"
    if rh != stored_hash:
        ok = False
    print(f"record_hash    [{rh_match}]")

    # provenance
    provenance_ok = bool(nist_value) and bool(prev_hash)
    print(f"provenance (NIST + chain present): {'OK' if provenance_ok else 'FAIL'}")

    # aggregate verdict reconstruction
    agg = aggregate(recomputed_verdicts, distinct, provenance_ok, ok)
    agg_match = "OK" if agg == rec["aggregate_verdict"] else "MISMATCH"
    if agg != rec["aggregate_verdict"]:
        ok = False
    print(f"\nAggregate verdict recomputed: {agg} (recorded {rec['aggregate_verdict']}) [{agg_match}]")
    print("=" * 78)
    print("VERIFICATION RESULT:", "PASS" if ok else "FAIL")
    print("=" * 78)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
