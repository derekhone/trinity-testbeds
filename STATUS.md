# TRINITY — STATUS

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**

---

## TRINITY-2 — The Governed Action — HARDWARE COMPLETE, INDEPENDENTLY VERIFIED

**As of 2026-07-19:** executed on **three live IBM Heron r2 processors** after Derek rotated the
IBM token and authorized the run. Manifest lock (`MANIFEST-TRINITY-2.sha256`) verified intact
before execution. Aggregate verdict **ALLOW** → governed action **AUTHORIZED**; independent
verifier **PASS**.

TRINITY-2 extends TRINITY-1 by binding the fused three-processor verdict to a **simulated
$500,000 payment authorization**, with a preregistered **quorum (≥2 of 3) + substitution /
failover** rule and full **calibration-snapshot hashing**. The payment is simulated — no real
funds, rail, or authority.

### Result (live IBM Heron r2 hardware, 2026-07-19)

| Slot | Backend | S | Verdict | Job |
|---|---|---|---|---|
| D1 | `ibm_kingston`  | 2.7650 | PASS | `d9e7029htsac739dt2mg` |
| D2 | `ibm_fez`       | 2.7235 | PASS | `d9e71lqneu4c739o3otg` |
| D3 | `ibm_marrakesh` | 2.7235 | PASS | `d9e71pcjeosc73fie1r0` |

- Shots: 4 CHSH circuits × 4,000 × 3 devices = **48,000 total**. Classical bound |S| ≤ 2.0 ·
  Tsirelson 2√2 ≈ 2.828.
- Quorum: required **2** of **3** · valid devices **3** · degraded_quorum **False**.
- Aggregate ExecutionProof verdict: **ALLOW** → governed action **AUTHORIZED** ·
  `trinity_certified = True`.
- Fused nonce: `aa527fe2bb3b6d80e3ec78ab1558521a7b744f94235d805623129acf468602b2`
- Record hash: `4f6fa000e2bf3976a1d575267ecf188baf42f1c6caea9e717bf1fc1be6737dd0`
- Chain link → TRINITY-1 record hash
  `8d23accac81791fa10f1dba1be79a132168966c4620fc42d16de656bcf9d688b`.
- **Independent verifier (`trinity2_verify.py`): PASS** — every S, arm verdict,
  `device_witness_hash`, `calibration_snapshot_hash`, quorum, aggregate verdict, the
  governed-action decision, `governed_action_hash`, `fused_nonce`, and `record_hash`
  reconstructed from raw counts with no qiskit dependency; NIST + chain-link provenance OK.

**PUBLISHED:** GitHub `derekhone/trinity-testbeds` + Zenodo — concept DOI
**10.5281/zenodo.21438244** (cite this), version v1 DOI 10.5281/zenodo.21438245 (2026-07-19).

### Simulator validation (retained record — all branches confirmed pre-hardware)

**Simulator validation (three independent noisy aer backends) — all branches confirmed + independently verified:**

| Scenario | Devices | Aggregate verdict | Action decision | Verifier |
|---|---|---|---|---|
| NOMINAL   | 3× PASS | **ALLOW** | AUTHORIZED | PASS |
| DEGRADED  | 2× PASS (1 device down) | **HOLD** | HELD_FOR_HUMAN_CONFIRMATION | PASS |
| DENY      | 2 PASS + 1 dissenting FAIL | **DENY** | DENIED | PASS |
| GATE-STOP | 1 device (sub-quorum) | **GATE-STOP** | DENIED | PASS |
| TAMPER    | flip a raw count post-hoc | (recompute) | — | **FAIL as required** (record_hash mismatch caught) |
| TAMPER    | force decision AUTHORIZED under DENY | (recompute) | — | **FAIL as required** |

- Kill-condition self-check active: harness exits non-zero if it ever emits ALLOW while a device
  is not PASS, under degraded quorum, or with fewer than 3 distinct devices.
- Independent verifier reconstructs every S, arm verdict, `device_witness_hash`,
  `calibration_snapshot_hash`, quorum, aggregate verdict, **the governed-action decision**,
  `governed_action_hash`, `fused_nonce`, and `record_hash` from raw counts — no qiskit.
- Schema `trinity-proofrecord-2.0`. Chain link → TRINITY-1 record hash
  `8d23accac81791fa10f1dba1be79a132168966c4620fc42d16de656bcf9d688b`.

**Next (needs Derek):** approve → rotate IBM token → run `python3 trinity2_harness.py
--authorize-hardware --allow-unrotated` with `IBM_QUANTUM_TOKEN` set → verify → publish.

---

## TRINITY-1 — The Three-Processor Witness — HARDWARE COMPLETE
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
