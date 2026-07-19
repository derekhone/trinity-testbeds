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

## Hardware run — how it was executed (reproducibility)

The hardware runs were performed after the IBM Quantum token was rotated and the run explicitly
authorized (preregistration §8). To reproduce on your own account:

```bash
export IBM_QUANTUM_TOKEN="your-token"     # never commit or paste in chat
python3 trinity2_harness.py --authorize-hardware
python3 trinity2_verify.py
```

## Scope & honesty

Device-dependent. Results apply only within the tested circuit model, backends, physical
qubits, calibration, shot counts, and harness. Cross-device agreement demonstrates
reproducibility and multi-root provenance, not device independence. σ is binomial shot noise
only. TRINITY-2's payment is simulated. Experimental evidence + governance demonstration — not
a universal proof.

*Proof Before Power · Verification Before Execution · claims kept narrower than the evidence.*
