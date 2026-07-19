# TRINITY-1 — STATUS

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**
**As of:** hardware run **COMPLETE**, independently verified, aggregate verdict **ALLOW**.

## Result (live IBM Heron r2 hardware)

One preregistered Bell-CHSH nonclassicality witness, evaluated independently on three
distinct quantum processors and fused into a single chain-linked ExecutionProof record.

| Slot | Backend | S | nσ | Verdict | Job |
|---|---|---|---|---|---|
| D1 | `ibm_kingston` | 2.7360 | 23.27 | VALID_ABOVE | `d9e46lcjeosc73fiaj00` |
| D2 | `ibm_fez` | 2.5785 | 18.29 | VALID_ABOVE | `d9e46pcjeosc73fiaj50` |
| D3 | `ibm_marrakesh` | 2.7410 | 23.43 | VALID_ABOVE | `d9e4a5sinv1c73apq1pg` |

- Classical bound |S| ≤ 2.0 · Tsirelson 2√2 ≈ 2.828 · certification threshold S ≥ 2.2.
- Aggregate ExecutionProof verdict: **ALLOW** · `trinity_certified = True`
- TRINITY nonce: `508f0ad692a7bd3a1d1a069aa02f4dc2519560153f646220f2150bbe47270e2f`
- Record hash: `8d23accac81791fa10f1dba1be79a132168966c4620fc42d16de656bcf9d688b`
- Chain — previous record (OMNI-1): `22ffb2ba137c89c2846225c6d5a11fb2a4dc6aaa6a0ba1dfe6864bc50393bb0c`
- NIST beacon pulse: `1865761` @ 2026-07-19T03:21:00.000Z
- Shots: 4,000 per circuit × 4 circuits × 3 devices = **48,000** total (matches prereg + locked
  harness `--shots` default; OMNI shot-count-consistency lesson honored).
- **Independent verifier: PASS** (recomputes every S, verdict, witness hash, nonce, record
  hash, and the aggregate verdict from raw counts — no qiskit).

## Completed

- [x] **Preregistration** (`TRINITY-1-preregistration.md`) — three-processor design, identical
      CHSH witness, per-device + aggregate verdict logic (ALLOW/HOLD/DENY/GATE-STOP), fused
      `trinity_nonce`, kill condition, hardware gate, scope/honesty caveats, purpose gate.
- [x] **Harness** (`trinity_harness.py`) — builds the CHSH witness, runs three independent
      devices (simulator or hardware), assembles the `trinity-proofrecord-1.0` record, computes
      the aggregate ExecutionProof verdict, writes report + JSON. Records the **actual physical
      qubits** used after transpilation per circuit (post-layout).
- [x] **Independent verifier** (`trinity_verify.py`) — reconstructs every device S, verdict,
      `device_witness_hash`, `trinity_nonce`, and `record_hash` from raw counts, no qiskit.
- [x] **Preregistration + harness lock** (`MANIFEST.sha256`) — SHA-256, re-verified `OK`.
- [x] **Simulator validation** — three independent noisy aer backends:
  - **NOMINAL** → all three VALID_ABOVE → **ALLOW**; verifier **PASS**.
  - **HOLD** scenario → device 3 driven to INCONCLUSIVE → aggregate **HOLD**.
  - **DENY** scenario → device 3 driven below classical (INVALID) → aggregate **DENY**.
  - **Tamper test** → altering one raw count without recomputing the hash → verifier recomputes
    **DENY** and reports **FAIL** (record_hash mismatch caught).
  - **Manifest-lock test** → editing the harness after locking broke the declared hash →
    provenance invalid → **DENY** (the lock works).
- [x] **Hardware run** on `ibm_kingston` + `ibm_fez` + `ibm_marrakesh` — genuine CHSH
      violation on all three, aggregate **ALLOW**, verifier **PASS**.

## Scope & honesty (unchanged from preregistration)

- This is a **device-dependent** demonstration of nonclassicality reproduced across three
  processors and cryptographically fused into one governance record. It is **not**
  device-independent, does **not** close the detection or locality loopholes, and does **not**
  entangle the three processors with one another. Each device is a separate, self-contained
  CHSH experiment; TRINITY is the reproduction + fusion claim, nothing more.

## Provenance / reproducibility

```bash
cd /home/ubuntu/trinity-testbeds
sha256sum -c MANIFEST.sha256          # confirm prereg + harness lock intact
python3 trinity_verify.py             # independent reconstruction from raw counts → PASS
```

## Security note

The IBM Quantum token used for this run was pasted in chat and is therefore considered
**compromised** — rotate it at https://quantum.cloud.ibm.com. The harness only reads the token
from the `IBM_QUANTUM_TOKEN` environment variable — never hard-coded, never committed
(`.gitignore` excludes `.env`).
