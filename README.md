> **Repository Role:** Preregistered Experiment Series — Three-Processor CHSH Fusion (TRINITY) · Part of the [Remnant Fieldworks](https://remnantfieldworks.com) research and product ecosystem

**Where this fits:** This repository is part of the Remnant Fieldworks quantum witness research program — a high-adversity test environment for provenance and execution integrity that informs the [ExecutionProof](https://executionproof.io) governance architecture. The quantum series tests whether nonclassical entropy sources, Bell-inequality violations, and tamper-evident records can serve as authorization evidence components in ProofRecords. TRINITY executes one Bell-CHSH witness independently across three separate physical quantum processors and fuses the results.

---

# TRINITY — The Three-Processor Witness

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**

One nonclassicality witness (Bell–CHSH), executed **independently on three separate physical
quantum processors** (`ibm_kingston`, `ibm_fez`, `ibm_marrakesh` — all Heron r2, 156q), each
evaluated on its own against the classical bound, and all three device records **fused into a
single chain-linked, independently reconstructable ExecutionProof record**.

- **TRINITY-1 — The Three-Processor Witness** (cross-device evidence fusion)
- **TRINITY-2 — The Governed Action** (three-root quorum → **simulated** high-value authorization)

## Status — HARDWARE COMPLETE, INDEPENDENTLY VERIFIED, PUBLISHED

Both experiments have been executed on real IBM Quantum hardware, independently verified, and
published to Zenodo. All six runtime jobs are confirmed `Completed` on IBM's own records.

| Experiment | Verdict | Devices (S) | Zenodo | GitHub |
|---|---|---|---|---|
| **TRINITY-1** | **ALLOW** | kingston 2.7360 · fez 2.5785 · marrakesh 2.7410 | concept **10.5281/zenodo.21436793** (v1.0 21436794) | this repo |
| **TRINITY-2** | **ALLOW** → simulated action AUTHORIZED | kingston 2.7650 · fez 2.7235 · marrakesh 2.7235 | concept **10.5281/zenodo.21438244** (v1 21438245) | this repo |

- **TRINITY-1 jobs:** `d9e46lcjeosc73fiaj00` (kingston) · `d9e46pcjeosc73fiaj50` (fez) · `d9e4a5sinv1c73apq1pg` (marrakesh) — 2026-07-19.
- **TRINITY-2 jobs:** `d9e7029htsac739dt2mg` (kingston) · `d9e71lqneu4c739o3otg` (fez) · `d9e71pcjeosc73fie1r0` (marrakesh) — 2026-07-19. Quorum 3/3, not degraded.
- Independent verifier (`trinity_verify.py` / `trinity2_verify.py`) **PASS** for both — every S, witness hash, calibration hash, quorum, aggregate verdict, fused nonce, and record hash reconstructed from raw counts with **no qiskit dependency**.
- **TRINITY-2 chain-links to TRINITY-1** (record_hash `8d23accac81791fa10f1dba1be79a132168966c4620fc42d16de656bcf9d688b`).

## Public claim (kept narrow)

> To our knowledge, TRINITY-1 is an **unusual** preregistered demonstration in which one
> Bell–CHSH nonclassicality witness is independently evaluated on **three distinct physical
> quantum processors under a common provider environment (IBM)**, and the three device-level
> records are cryptographically fused — with external entropy and a prior-record chain link —
> into a single tamper-evident, independently reconstructable, ExecutionProof-**governed
> evidence record**. TRINITY-2 extends this by passing the fused verdict through a preregistered
> quorum rule to govern a **simulated** high-value payment authorization.

**Wording, deliberately:** we say "unusual," not "first" — no historical-priority claim is made
pending a formal literature/patent/standards review (see `TRINITY-1-CLARIFICATIONS.md`). The
three processors are **distinct physical devices under one provider** — independent devices, but
**not** independent vendors or independent trust domains.

**TRINITY-2's $500,000 payment is SIMULATED.** No funds moved, no live payment rail was accessed,
and no real institutional authorization was exercised. This is enterprise-*relevant* pilot
evidence, not an enterprise-ready deployment (no external customer integration, no production
security/compliance review).

**This is a robustness + multi-root-provenance demonstration — NOT** a device-independence
claim, NOT a loophole closure, NOT entanglement between processors, NOT three-vendor
independence, NOT a security or randomness-certification proof. Locality and detection loopholes
remain open on every device.

## Verdict logic (preregistered, frozen)

| Verdict | Condition |
|---------|-----------|
| **ALLOW** | all three devices S ≥ 2.2, reconstruction agrees, provenance valid |
| **HOLD** | ≥3 devices, provenance valid, any device inconclusive (2.0 ≤ S < 2.2) |
| **DENY** | provenance invalid, reconstruction mismatch, tampering, or any device S < 2.0 |
| **GATE-STOP** | fewer than three distinct devices returned valid data, or NIST unavailable |

Precedence: **DENY > GATE-STOP > HOLD > ALLOW**. A dissenting device is never averaged away.
TRINITY-2 adds a preregistered **quorum (≥2 of 3)** rule with substitution/failover and full
calibration-snapshot hashing.

## Files

- `TRINITY-1-preregistration.md`, `TRINITY-2-preregistration.md` — full preregistered designs (locked).
- `TRINITY-1-CLARIFICATIONS.md` — seven post-execution design-review points (documentation layer).
- `trinity_harness.py`, `trinity2_harness.py` — build the CHSH witness, run three devices, assemble the
  `trinity-proofrecord-*.json` record, compute the aggregate verdict, write the report.
- `trinity_verify.py`, `trinity2_verify.py` — independent verifiers: reconstruct every S, hash, nonce,
  quorum, and verdict from raw counts with **no qiskit dependency**.
- `MANIFEST.sha256`, `MANIFEST-TRINITY-2.sha256` — SHA-256 preregistration locks, committed before each run.
- `zenodo_metadata_trinity2.json`, `zenodo_publish_trinity2.py` — publication pipeline.
- `results/` — reports and ProofRecord JSON for both experiments.

## Run

```bash
pip install -r requirements.txt

# Simulator validation (default; no token needed) — three independent noisy backends
python3 trinity_harness.py
python3 trinity2_harness.py

# Exercise the governance branches on the simulator
python3 trinity2_harness.py --scenario hold    # one device inconclusive -> HOLD
python3 trinity2_harness.py --scenario deny     # one device below classical -> DENY

# Independent verification
python3 trinity_verify.py
python3 trinity2_verify.py
```

## Hardware execution — COMPLETE (2026-07-19)

**TRINITY-1 executed on three live IBM Heron r2 processors.** Aggregate ExecutionProof verdict **ALLOW**; independent verifier **PASS**.

| Slot | Backend | S | nσ | Verdict | Job |
|---|---|---|---|---|---|
| D1 | `ibm_kingston` | 2.736 | 23.27 | VALID_ABOVE | `d9e46lcjeosc73fiaj00` |
| D2 | `ibm_fez` | 2.5785 | 18.29 | VALID_ABOVE | `d9e46pcjeosc73fiaj50` |
| D3 | `ibm_marrakesh` | 2.741 | 23.43 | VALID_ABOVE | `d9e4a5sinv1c73apq1pg` |

- **Shots:** 4 CHSH circuits × 4,000 shots/circuit × 3 devices = **48,000 total**
- **Classical bound:** |S| ≤ 2.0  ·  **Certification threshold:** S ≥ 2.2  ·  **Tsirelson bound:** 2√2 ≈ 2.828
- **Cross-device spread (descriptive):** S_min 2.5785, S_max 2.741, mean 2.685, range 0.163, pop_std 0.076
- **All three devices independently passed** — no device averaged away; aggregate verdict **ALLOW** (`trinity_certified = True`)
- **Independent verification:** `trinity_verify.py` PASS (reconstructed all S values, verdicts, hashes, nonce, and record_hash from raw counts with no qiskit dependency)
- **trinity_nonce:** `508f0ad692a7bd3a1d1a069aa02f4dc2519560153f646220f2150bbe47270e2f`
- **record_hash:** `8d23accac81791fa10f1dba1be79a132168966c4620fc42d16de656bcf9d688b`

See `results/TRINITY-1-report.md` and `results/TRINITY-1-proofrecord.json` for full details.

## Scope & honesty

Device-dependent. Results apply only within the tested circuit model, backends, physical
qubits, calibration, shot counts, and harness. Cross-device agreement demonstrates
reproducibility and multi-root provenance, not device independence. σ is binomial shot noise
only. TRINITY-2's payment is simulated. Experimental evidence + governance demonstration — not
a universal proof.

*Proof Before Power · Verification Before Execution · claims kept narrower than the evidence.*

### License scope

See [LICENSE-SCOPE.md](LICENSE-SCOPE.md). No new blanket grant is made; existing permissions are preserved.
