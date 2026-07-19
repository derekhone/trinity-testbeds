# TRINITY-2 Report — The Governed Action

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**

- Experiment: **TRINITY-2**  ·  Schema: `trinity-proofrecord-2.0`
- Mode: **HARDWARE**  ·  Witness: **Bell-CHSH**
- Distinct devices: **3**  ·  Shots total: **48,000**
- Generated: 2026-07-19T06:38:39.732244+00:00

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
| D1 | `ibm_kingston` | 2.765 | 24.1914 | PASS | `8dfb225a36de…` | `d9e7029htsac739dt2mg` |
| D2 | `ibm_fez` | 2.7235 | 22.8791 | PASS | `d92954bcb872…` | `d9e71lqneu4c739o3otg` |
| D3 | `ibm_marrakesh` | 2.7235 | 22.8791 | PASS | `6e27bdb1c24b…` | `d9e71pcjeosc73fie1r0` |

Classical bound |S| ≤ 2.0 · Tsirelson 2√2 ≈ 2.828 · PASS iff S − 2σ > 2.0 · FAIL iff S + 2σ ≤ 2.0 · else INDETERMINATE.

### Device substitutions / failover
- none

## Fusion & provenance
- Fused nonce: `aa527fe2bb3b6d80e3ec78ab1558521a7b744f94235d805623129acf468602b2`
- Governed-action hash: `f3fb2c32dfe32f67388335b082e606ee6f225b2d1f00611562a9926b9fea3d41`
- Record hash: `4f6fa000e2bf3976a1d575267ecf188baf42f1c6caea9e717bf1fc1be6737dd0`
- Chain — previous record (TRINITY-1): `8d23accac81791fa10f1dba1be79a132168966c4620fc42d16de656bcf9d688b`
- NIST beacon pulse: `1865951` @ 2026-07-19T06:31:00.000Z
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
