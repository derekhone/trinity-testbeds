# TRINITY-1 — The Three-Processor Witness

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**

One nonclassicality witness (Bell–CHSH), executed **independently on three separate physical
quantum processors** (`ibm_kingston`, `ibm_fez`, `ibm_marrakesh` — all Heron r2, 156q), each
evaluated on its own against the classical bound, and all three device records **fused into a
single chain-linked, independently reconstructable ExecutionProof record**.

## Public claim (kept narrow)

> To our knowledge, TRINITY-1 is an **unusual** preregistered demonstration in which one
> Bell–CHSH nonclassicality witness is independently evaluated on **three distinct physical
> quantum processors under a common provider environment (IBM)**, and the three device-level
> records are cryptographically fused — with external entropy and a prior-record chain link —
> into a single tamper-evident, independently reconstructable, ExecutionProof-**governed
> evidence record**.

**Wording, deliberately:** we say "unusual," not "first" — no historical-priority claim is made
pending a formal literature/patent/standards review (see `TRINITY-1-CLARIFICATIONS.md`). The
three processors are **distinct physical devices under one provider** — independent devices, but
**not** independent vendors or independent trust domains. We call the output a **governed
evidence record** (not an "authorization record") because TRINITY-1 produces evidence governed
by ALLOW/HOLD/DENY/GATE-STOP logic; it does not yet intercept a named external action.

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

## Files

- `TRINITY-1-preregistration.md` — full preregistered design (locked).
- `trinity_harness.py` — builds the CHSH witness, runs three devices, assembles the
  `trinity-proofrecord-1.0` record, computes the aggregate verdict, writes the report.
- `trinity_verify.py` — independent verifier: reconstructs every S, hash, nonce, and verdict
  from raw counts with **no qiskit dependency**.
- `MANIFEST.sha256` — SHA-256 preregistration lock (prereg + harness), committed before any run.
- `results/TRINITY-1-report.md`, `results/TRINITY-1-proofrecord.json` — outputs.

## Run

```bash
pip install -r requirements.txt

# Simulator validation (default; no token needed) — three independent noisy backends
python3 trinity_harness.py

# Exercise the governance branches on the simulator
python3 trinity_harness.py --scenario hold    # one device inconclusive -> HOLD
python3 trinity_harness.py --scenario deny     # one device below classical -> DENY

# Independent verification
python3 trinity_verify.py
```

## Hardware run — GATED (withheld)

Per preregistration §8, the hardware run is withheld until **both** (a) the exposed IBM Quantum
token has been **rotated** and (b) the run is **explicitly authorized**. When both are met:

```bash
export IBM_QUANTUM_TOKEN="your-rotated-token"     # never commit or paste in chat
python3 trinity_harness.py --authorize-hardware --allow-unrotated
python3 trinity_verify.py
```

## Scope & honesty

Device-dependent. Results apply only within the tested circuit model, backends, physical
qubits, calibration, shot counts, and harness. Cross-device agreement demonstrates
reproducibility and multi-root provenance, not device independence. σ is binomial shot noise
only. Experimental evidence + governance demonstration — not a universal proof.

*Proof Before Power · Verification Before Execution · claims kept narrower than the evidence.*
