# TRINITY-2 Report — The Governed Action

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**

- Experiment: **TRINITY-2**  ·  Schema: `trinity-proofrecord-2.0`
- Mode: **SIMULATOR**  ·  Witness: **Bell-CHSH**
- Distinct devices: **3**  ·  Shots total: **48,000**
- Generated: 2026-07-19T05:08:15.839976+00:00

> **Public claim:** A preregistered demonstration in which a simulated high-impact action is allowed, held, or denied by a Bell-CHSH witness independently evaluated on three quantum processors and fused into one chain-linked, independently reconstructable ExecutionProof record, with a quorum + substitution rule governing processor unavailability.

## Governed action (SIMULATED)

| Field | Value |
|---|---|
| Action | payment_authorization |
| Amount | 500,000 USD |
| Payee ref | `SIMULATED-PAYEE-0001` |
| Policy ref | `RF-100/multi-root-quorum-v1` |
| **Decision** | **AUTHORIZED** |
| Governed by verdict | ALLOW |
| Simulated | True |

## Aggregate ExecutionProof verdict: **ALLOW**  →  action **AUTHORIZED**

`trinity_certified = True`

Quorum: required **2** of **3** · valid devices **3** · degraded_quorum **False**

| Slot | Backend | S | nσ | Arm | Calib snapshot | Job |
|---|---|---|---|---|---|---|
| D1 | `aer_sim::kingston-sim` | 2.786 | 24.8555 | PASS | `4b51b3156dcd…` | `SIM-kingston-sim-101` |
| D2 | `aer_sim::fez-sim` | 2.759 | 24.0017 | PASS | `edbbcdb503b4…` | `SIM-fez-sim-202` |
| D3 | `aer_sim::marrakesh-sim` | 2.7825 | 24.7448 | PASS | `a06d43caaaa6…` | `SIM-marrakesh-sim-303` |

Classical bound |S| ≤ 2.0 · Tsirelson 2√2 ≈ 2.828 · PASS iff S − 2σ > 2.0 · FAIL iff S + 2σ ≤ 2.0 · else INDETERMINATE.

### Device substitutions / failover
- none

## Fusion & provenance
- Fused nonce: `9096f8fb3e76f99befd21b2c3c52b03e91348550555510eaf52021f2b73b749b`
- Governed-action hash: `715925f018666e72189135553020f162c30d7fd17fd6f9d3c08a1db53ad3a7de`
- Record hash: `a5be2a817b5c8e706aadf92a500805ad3e32e7c009087b0006cf7af605da99f9`
- Chain — previous record (TRINITY-1): `8d23accac81791fa10f1dba1be79a132168966c4620fc42d16de656bcf9d688b`
- NIST beacon pulse: `1865865` @ 2026-07-19T05:05:00.000Z
- LIGO GW150914 anchor: `66c4b196`
- Manifest (prereg): `8a887fba2558b25e51e39af6a6800da59accc16371961baa9b7ce42520c4e7c0`
- Manifest (harness): `eb55459658127b9720b5692d6e2e502fef4ebecb43b3f7c4f7ef17046251a1bc`

## Verdict logic (preregistered, precedence DENY-side first)
- **GATE-STOP** → action DENIED — integrity/provenance failure, or fewer than 2 distinct devices with a definite (PASS/FAIL) result.
- **DENY** → action DENIED — quorum of definite devices present but not all PASS (a dissenting device is never averaged away).
- **HOLD** → action HELD for human confirmation — quorum met and all-PASS but degraded (fewer than 3 distinct devices).
- **ALLOW** → action AUTHORIZED — all 3 distinct devices PASS.

## Scope & honesty
The payment is **simulated** — no real funds, rail, customer authority, or entitlement. The
quantum result is **device-dependent**; Bell locality and detection loopholes remain **open**.
Cross-device agreement demonstrates **reproducibility and multi-root provenance with failover**,
not device independence or loophole closure. No entanglement exists between processors. This is
an **experimental governance demonstration**, not a security proof, randomness-certification, or
production certification. σ is binomial shot noise only.

*Proof Before Power · Verification Before Execution · claims kept narrower than the evidence.*
