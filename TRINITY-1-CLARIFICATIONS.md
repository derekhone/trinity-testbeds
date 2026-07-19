# TRINITY-1 — Clarifications & Review Response

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**
**Date:** 2026-07-19 · **Applies to:** the sealed TRINITY-1 record (`record_hash 8d23acca…`).

## Why this document exists

TRINITY-1 was preregistered (`MANIFEST.sha256` locking `TRINITY-1-preregistration.md` +
`trinity_harness.py`), then executed on live hardware; the resulting ProofRecord is hash-sealed
and passed the independent verifier. **After** execution, a design review raised seven points.

The preregistration and harness are the scientific instrument and were locked *before* the run,
so they are **preserved unedited** — editing them now would destroy the "preregistered before
execution" property that gives the record its value. Following the OMNI-1 v1.1 precedent, this
companion note records the review, states which points the sealed record already honors, which
are corrected at the documentation layer (no measured value changes), and which require a fresh
run (TRINITY-2). **No S value, verdict, hash, or the aggregate ALLOW changes.**

## Correction I own first

The interim `STATUS.md` mis-stated the shot count as "12,000 per circuit" (12,000 × 4 × 3 =
144,000, which is wrong and inconsistent with the total). The **sealed record is 4,000
shots/circuit × 4 circuits × 3 devices = 48,000 total**, which matches the preregistration and
the locked harness `--shots` default exactly. `STATUS.md` is fixed. This is precisely the
shot-count-consistency discipline carried from the OMNI-1 erratum, and the *record itself was
always consistent* — the error was only in my summary prose.

## The seven review points

| # | Point | Status against the SEALED record | Action |
|---|---|---|---|
| 1 | Remove "first" claim | Locked prereg §1 says "To our knowledge… the first…". Public materials should say **"unusual,"** not "first." | Corrected in all **unlocked** public materials (README, this note, public description). Locked prereg preserved. Consistent with RF naming-governance covenant and the OMNI "world's first" withdrawal. |
| 2 | "Independent processors" is common-provider | Prereg already states the devices are spatially/operationally independent with no shared quantum channel; it did **not** explicitly flag common-provider. | Clarified: **three distinct physical processors under a common provider (IBM)** — independent devices, **not** independent vendors or trust domains. Multi-vendor analogy is *architectural relevance*, not something demonstrated. |
| 3 | `calibration_hash` binds only a timestamp | **Confirmed.** The harness hashes `str(props.last_update_date)` — one field, not the full calibration snapshot. | **Disclosed here and renamed conceptually to `calibration_timestamp_hash`.** A full canonical calibration-snapshot hash (readout/1q/2q errors, T1/T2, gate durations, backend version) is deferred to TRINITY-2, which requires a re-run. |
| 4 | Device-identity binding | The per-device `device_witness_hash` binds `{slot, backend name, S, correlators, bounds, threshold, shots, verdict}` — so **backend identity is bound.** It does **not** fold in `job_id`, `qubit_mapping`, or `calibration_*` — but the **top-level `record_hash` canonically hashes the entire record**, including those fields, so any relabel/tamper breaks `record_hash` and the verifier catches it. | Sealed record is tamper-evident at the record level. Richer *per-device* identity binding is a TRINITY-2 hardening. |
| 5 | Preregister substitution eligibility | **Moot for TRINITY-1:** no substitution occurred; all three preregistered targets (`ibm_kingston`, `ibm_fez`, `ibm_marrakesh`) returned valid data. | Formal eligibility criteria + "resolved 3-device set recorded before first job" folded into TRINITY-2 preregistration. |
| 6 | Add inter-device spread metric | Not in the sealed record, but computable from the sealed S values. | **Added below, descriptive only** — it does **not** override the per-device verdicts. A dispersion **threshold** + `CROSS_DEVICE_DISPERSION_WARNING` is deferred to TRINITY-2 (no threshold invented without simulator/historical justification). |
| 7 | "Authorization record" vs governed evidence record | Correct: TRINITY-1 does not intercept a named external action. | Public materials now say **"governed evidence record."** A true authorization framing (a named action such as `AUTHORIZE_CROSS_DEVICE_QUANTUM_WITNESS_ACCEPTANCE`, executable only on aggregate ALLOW) is a TRINITY-2 design item. |

## Cross-device spread (point 6 — descriptive, from the sealed S values)

| Metric | Value |
|---|---|
| S_min | 2.5785 (`ibm_fez`) |
| S_max | 2.7410 (`ibm_marrakesh`) |
| S_mean | 2.6852 |
| Range | 0.1625 |
| Population σ across devices | 0.0755 |

All three are far above the classical bound (2.0) and the certification threshold (2.2); the
spread is descriptive context, and **every device independently cleared the bar** — no device is
averaged away. `ibm_fez` is the lowest of the three, consistent with its higher per-device shot
noise (18.29σ vs 23+σ), and still an unambiguous violation.

## What is unchanged

The disagreement rule (ALLOW only if *all three* pass; HOLD on any inconclusive; DENY on any
sub-classical or tamper/reconstruction failure; GATE-STOP if fewer than three distinct devices),
the aggregate **ALLOW**, `trinity_certified = True`, every measured S, the fused `trinity_nonce`,
the `record_hash`, the OMNI-1 chain link, the NIST anchor, and the independent-verifier PASS all
stand exactly as sealed. This note changes claims and disclosures, never measurements.

## Best public description (adopted)

> TRINITY-1 is a preregistered cross-device evidence-binding experiment in which the same
> Bell–CHSH witness is independently evaluated on three distinct IBM Quantum processors. Each
> processor must independently satisfy the threshold; no device is averaged away. The three
> device records are then fused into one chain-linked, independently reconstructable
> ExecutionProof-governed evidence record governed by ALLOW / HOLD / DENY / GATE-STOP logic.

*For God's glory — and kept honest, which is the only way that phrase means anything.*
