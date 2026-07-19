#!/usr/bin/env python3
"""
TRINITY-2 independent verifier.

Reconstructs — from the released raw counts in results/TRINITY-2-proofrecord.json, with NO
qiskit / harness dependency (standard library only) — every device CHSH S, arm verdict
(PASS/FAIL/INDETERMINATE with the preregistered k-sigma margin), device_witness_hash,
calibration_snapshot_hash, the quorum decision, the fused governed-action verdict, the
governed-action DECISION, the governed_action_hash, the fused_nonce, and the record_hash.

Exits 0 iff everything reconstructs and agrees (including that the action decision follows the
verdict), else 1.

Usage: python3 trinity2_verify.py
"""

import hashlib
import json
import os
import sys

# Preregistered constants (hard-coded so the verifier is independent of the harness)
CHSH_CLASSICAL = 2.0
K_MARGIN = 2
QUORUM_REQUIRED = 2
FULL_QUORUM = 3
LIGO_GW150914_HASH = "66c4b196"
PREVIOUS_RECORD_HASH = "8d23accac81791fa10f1dba1be79a132168966c4620fc42d16de656bcf9d688b"

DECISION_MAP = {
    "ALLOW": "AUTHORIZED",
    "HOLD": "HELD_FOR_HUMAN_CONFIRMATION",
    "DENY": "DENIED",
    "GATE-STOP": "DENIED",
}

HERE = os.path.dirname(os.path.abspath(__file__))
RECORD_PATH = os.path.join(HERE, "results", "TRINITY-2-proofrecord.json")


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


def recompute_sigma(raw_counts):
    # shots per setting = total counts / 4 settings, matching harness
    total = sum(sum(raw_counts[k].values()) for k in ["a0b0", "a0b1", "a1b0", "a1b1"])
    shots = total // 4 if total else 1
    return (4.0 / max(shots, 1)) ** 0.5


def arm_verdict(S, sigma):
    if S - K_MARGIN * sigma > CHSH_CLASSICAL:
        return "PASS"
    if S + K_MARGIN * sigma <= CHSH_CLASSICAL:
        return "FAIL"
    return "INDETERMINATE"


def governed_verdict(verdicts_by_backend, provenance_ok, reconstructs):
    """verdicts_by_backend: list of (backend, verdict). Mirrors harness precedence."""
    if not provenance_ok or not reconstructs:
        return "GATE-STOP", False
    definite = [(b, v) for (b, v) in verdicts_by_backend if v in ("PASS", "FAIL")]
    distinct_definite = len({b for (b, _) in definite})
    if distinct_definite < QUORUM_REQUIRED:
        return "GATE-STOP", False
    if any(v == "FAIL" for (_, v) in definite):
        return "DENY", (distinct_definite < FULL_QUORUM)
    distinct_pass = len({b for (b, v) in definite if v == "PASS"})
    if distinct_pass >= FULL_QUORUM:
        return "ALLOW", False
    return "HOLD", True


def main():
    if not os.path.exists(RECORD_PATH):
        print(f"[VERIFY] ProofRecord not found: {RECORD_PATH}")
        return 1
    with open(RECORD_PATH) as f:
        rec = json.load(f)

    print("=" * 78)
    print("TRINITY-2 INDEPENDENT VERIFICATION — The Governed Action")
    print("=" * 78)

    ok = True
    ordered = sorted(rec["devices"], key=lambda x: x["slot"])
    verdicts_by_backend = []

    for d in ordered:
        S, _ = recompute_S(d["raw_counts"])
        sigma = recompute_sigma(d["raw_counts"])
        recorded_S = d["witness"]["S"]
        dS = abs(S - recorded_S)
        v = arm_verdict(S, sigma)
        verdicts_by_backend.append((d["backend"], v))

        s_match = "OK" if dS < 1e-3 else "MISMATCH"
        if dS >= 1e-3:
            ok = False
        wh = sha256_hex(canonical_json(d["witness"]))
        wh_match = "OK" if wh == d["device_witness_hash"] else "MISMATCH"
        if wh != d["device_witness_hash"]:
            ok = False
        ch = sha256_hex(canonical_json(d["calibration_snapshot"]))
        ch_match = "OK" if ch == d["calibration_snapshot_hash"] else "MISMATCH"
        if ch != d["calibration_snapshot_hash"]:
            ok = False
        vmatch = "OK" if v == d["witness"]["verdict"] else "MISMATCH"
        if v != d["witness"]["verdict"]:
            ok = False
        print(f"{d['slot']} {d['backend']:26s} S={S:.4f}(rec {recorded_S:.4f})[{s_match}] "
              f"arm={v}[{vmatch}] witness_hash[{wh_match}] calib_hash[{ch_match}]")

    distinct = len({d["backend"] for d in ordered})
    print(f"\nDistinct devices: {distinct}")

    # provenance
    nist_value = rec["external_entropy"]["nist_value"]
    prev_hash = rec["chain"]["previous_record_hash"]
    provenance_ok = bool(nist_value) and (prev_hash == PREVIOUS_RECORD_HASH)
    print(f"provenance (NIST + correct chain link): {'OK' if provenance_ok else 'FAIL'}")
    if prev_hash != PREVIOUS_RECORD_HASH:
        print(f"  chain link MISMATCH: expected {PREVIOUS_RECORD_HASH}")
        ok = False

    # governed-action decision must follow verdict
    verdict, degraded = governed_verdict(verdicts_by_backend, provenance_ok, ok)
    v_match = "OK" if verdict == rec["aggregate_verdict"] else "MISMATCH"
    if verdict != rec["aggregate_verdict"]:
        ok = False
    print(f"aggregate verdict recomputed: {verdict} (rec {rec['aggregate_verdict']}) [{v_match}]")

    expected_decision = DECISION_MAP[verdict]
    dec_match = "OK" if expected_decision == rec["action_decision"] else "MISMATCH"
    if expected_decision != rec["action_decision"]:
        ok = False
    if rec["governed_action"]["decision"] != rec["action_decision"]:
        ok = False
        dec_match = "MISMATCH"
    print(f"governed-action decision: {expected_decision} (rec {rec['action_decision']}) [{dec_match}]")

    # degraded_quorum consistency
    dq_match = "OK" if bool(degraded) == bool(rec["quorum"]["degraded_quorum"]) else "MISMATCH"
    if bool(degraded) != bool(rec["quorum"]["degraded_quorum"]):
        ok = False
    print(f"degraded_quorum: {degraded} (rec {rec['quorum']['degraded_quorum']}) [{dq_match}]")

    # governed_action_hash
    gah = sha256_hex(canonical_json(rec["governed_action"]))
    gah_match = "OK" if gah == rec["governed_action_hash"] else "MISMATCH"
    if gah != rec["governed_action_hash"]:
        ok = False
    print(f"governed_action_hash [{gah_match}]")

    # fused_nonce
    fusion_tokens = [f"{d['device_witness_hash']}:{d['calibration_snapshot_hash']}"
                     for d in ordered]
    nonce = sha256_hex("|".join(
        fusion_tokens + [nist_value, LIGO_GW150914_HASH, PREVIOUS_RECORD_HASH,
                         rec["governed_action_hash"]]))
    nonce_match = "OK" if nonce == rec["fused_nonce"] else "MISMATCH"
    if nonce != rec["fused_nonce"]:
        ok = False
    print(f"fused_nonce [{nonce_match}]")

    # record_hash
    rec_copy = dict(rec)
    stored_hash = rec_copy.pop("record_hash", None)
    rh = sha256_hex(canonical_json(rec_copy))
    rh_match = "OK" if rh == stored_hash else "MISMATCH"
    if rh != stored_hash:
        ok = False
    print(f"record_hash [{rh_match}]")

    # hard safety invariant: ALLOW must never coexist with a non-PASS arm or degraded quorum
    if rec["aggregate_verdict"] == "ALLOW":
        if any(v != "PASS" for (_, v) in verdicts_by_backend) or rec["quorum"]["degraded_quorum"] \
                or distinct < FULL_QUORUM:
            print("SAFETY INVARIANT VIOLATED: ALLOW with non-PASS / degraded / sub-quorum")
            ok = False

    print("=" * 78)
    print("VERIFICATION RESULT:", "PASS" if ok else "FAIL")
    print("=" * 78)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
