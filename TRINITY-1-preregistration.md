# TRINITY-1 — The Three-Processor Witness

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**

**Preregistration document — locked before execution via `MANIFEST.sha256`.**

---

## 0. One-line statement of the experiment

A preregistered demonstration in which a **single nonclassicality witness (Bell–CHSH)** is
executed **independently on three separate physical quantum processors**, each processor's
result is evaluated on its own against the classical bound, and all three device records are
**cryptographically fused into one chain-linked, independently reconstructable ExecutionProof
governance record**.

## 1. Purpose and honest novelty claim

The prior corpus (WITNESS-1→3, BELLWETHER, CHRONO, OMNI-1) demonstrated multiple
nonclassicality families and bound them into governed ProofRecords **on a single processor per
record**. TRINITY-1 changes one variable only: **the number of independent physical devices
carrying the same witness inside one governed record.**

**Novelty claim (kept deliberately narrow):**

> *To our knowledge, TRINITY-1 is the first preregistered ExecutionProof record in which one
> nonclassicality witness is independently evaluated on three distinct quantum processors and
> the three device-level results are fused, with external entropy and a prior-record chain
> link, into a single tamper-evident, independently reconstructable authorization record.*

What this claim is **NOT** (explicit anti-overclaim guardrails):

- It is **NOT** "the world's first" anything. The phrase used is "to our knowledge, the first
  … within our own catalog and the literature we have surveyed," and it may be withdrawn if a
  prior instance is identified.
- Cross-device agreement is **NOT** a loophole closure. Reproducing the same violation on three
  independent devices is a **robustness and provenance** result, not a device-independent or
  loophole-free physics claim. Locality, detection, and freedom-of-choice loopholes remain
  **open** exactly as in every prior RF hardware witness.
- It is **NOT** a security proof, a randomness-certification proof, or a production
  certification. It is an experimental evidence record.
- It does **NOT** claim entanglement *between* the three processors. The three devices are
  spatially and operationally independent; there is no shared quantum channel. TRINITY-1
  certifies the **same nonclassical signature, independently, on three machines**, then binds
  the **classical records** together cryptographically.

## 2. Why this is worth quantum time (purpose gate)

Per RF's standing experiment-purpose rule, TRINITY-1 must answer at least one of: buyer
question / product improvement / RF-100 requirement / patent opportunity / genuine failure
mode. TRINITY-1 satisfies four:

1. **Product (ExecutionProof):** demonstrates that a single ProofRecord can bind evidence
   sourced from **multiple heterogeneous hardware roots of trust** — the exact shape of a
   multi-region / multi-vendor authorization boundary a buyer would deploy.
2. **Failure mode:** exercises the governance layer's behavior when devices **disagree** (the
   preregistered verdict logic must HOLD or DENY, not silently average away a dissenting
   device).
3. **RF-100:** supplies a concrete "multi-root evidence binding" reference for the standard.
4. **IP:** the cross-device fused-nonce construction is a candidate for the defensive-
   publication / provisional portfolio (no claim of a granted patent is made here).

## 3. Devices under test (DUT)

Three IBM Quantum processors, all **Heron r2, 156 qubits**, visible on the account at
preregistration time:

| Slot | Backend (target) | Family | Qubits |
|------|------------------|--------|--------|
| D1 | `ibm_kingston`  | Heron r2 | 156 |
| D2 | `ibm_fez`       | Heron r2 | 156 |
| D3 | `ibm_marrakesh` | Heron r2 | 156 |

If any target device is unavailable at execution time, the harness records the substitution
explicitly in the ProofRecord (`device_substitutions`) and the substitution is disclosed in the
report. Fewer than three **distinct** devices returning valid data forces a **GATE-STOP** (see
§7): TRINITY-1 is defined by three independent processors, and cannot be satisfied by one
device run three times.

## 4. The witness (identical on every device)

**Bell–CHSH**, the most widely understood nonclassicality witness, chosen so the independent
verifier can reconstruct every number from raw counts with no quantum library.

- State: Bell pair |Φ⁺⟩ = (|00⟩ + |11⟩)/√2.
- Measurement settings: Alice ∈ {0, π/4}; Bob ∈ {π/8, 3π/8}.
- Four circuits per device: `a0b0`, `a0b1`, `a1b0`, `a1b1`.
- Correlator E(a,b) = ⟨Z_a Z_b⟩ (parity expectation over 2 measured bits).
- **CHSH statistic:** S = E(a0,b0) − E(a0,b1) + E(a1,b0) + E(a1,b1).
- Bounds: classical (local-realist) **|S| ≤ 2**; Tsirelson **2√2 ≈ 2.828**.
- **Certification threshold (preregistered): S ≥ 2.2** per device.
- Shot-noise σ = √(4 / shots_per_setting); nσ = (S − 2) / σ.
- **Shots:** uniform **4,000 shots/circuit × 4 circuits × 3 devices = 48,000 shots total.**
  This figure is defined here and enforced by the locked harness (`trinity_harness.py`,
  `--shots` default 4000). Prose and code state the same number; there is no separate prose
  target. (This is the explicit lesson carried from the OMNI-1 v1.1 erratum: the executed shot
  count is governed by the locked harness and the prose must not diverge from it.)

## 5. ProofRecord schema — `trinity-proofrecord-1.0`

The record binds, for **each** device:

- `backend` (resolved device name), `job_id`, `calibration_hash` (SHA-256 of the backend's
  last calibration timestamp), `qubit_mapping` (physical qubits used after transpilation),
- `raw_counts` for all four CHSH circuits,
- reconstructed `S`, `n_sigma`, per-device `verdict` ∈ {VALID_ABOVE, INCONCLUSIVE, INVALID},
- `device_witness_hash` = SHA-256 over that device's canonicalized witness object.

And, once across the whole record:

- `external_entropy`: fresh **NIST randomness beacon** pulse (not-before anchor) + fixed
  **LIGO GW150914** cosmological hash anchor (`66c4b196`, carried from WITNESS-3).
- `chain.previous_record_hash`: hash link to the prior RF record (OMNI-1) — continuity.
- `manifest_prereg_sha256`, `manifest_harness_sha256`: the preregistration lock hashes.
- **`trinity_nonce`** = SHA-256 over the ordered join of the three `device_witness_hash`
  values + NIST value + LIGO anchor + previous record hash. Changing any device's counts, any
  device's identity, the beacon, or the chain link changes the nonce.
- `record_hash` = SHA-256 over the canonical JSON of the whole record (excluding
  `record_hash`).

## 6. Aggregate ExecutionProof verdict logic (preregistered, frozen)

Per-device verdict:

- `VALID_ABOVE` if S ≥ 2.2
- `INCONCLUSIVE` if 2.0 ≤ S < 2.2
- `INVALID` if S < 2.0 (at or below the classical bound)

Aggregate verdict (precedence **DENY > GATE-STOP > HOLD > ALLOW**):

- **DENY** — provenance invalid, independent reconstruction mismatch, tampering detected, or
  **any** device `INVALID`. (A device that fails to beat the classical bound is an honest
  negative and must block authorization — it is never averaged away.)
- **GATE-STOP** — fewer than three **distinct** devices returned valid data, NIST beacon
  unavailable, or hardware/data conditions otherwise prevent valid evaluation.
- **HOLD** — all provenance valid and ≥3 devices reporting, but **any** device `INCONCLUSIVE`
  (2.0–2.2). The governance layer refuses to certify on a split result.
- **ALLOW** — **all three** devices `VALID_ABOVE`, independent reconstruction agrees on every
  device, and provenance (NIST + chain + manifest) is valid.

`trinity_certified = (aggregate_verdict == "ALLOW")`.

This logic is chosen specifically so that the **failure mode in §2.2 is honest**: three
independent devices must *each* clear the bar. Strength on two devices cannot mask weakness on
the third.

## 7. Kill condition

If the independent verifier (`trinity_verify.py`) recomputes any device's S from that device's
raw counts and disagrees with the recorded S beyond floating tolerance, OR the recomputed
`record_hash` / `trinity_nonce` does not match, the record is published as **DENY (kill
condition triggered)** with the discrepancy documented. No measured value is ever edited to
force agreement.

## 8. Hardware gate (security + review) — WITHHELD until authorized

Consistent with the OMNI-1 discipline, the hardware run is **withheld** until BOTH:

1. **(a)** The exposed IBM Quantum token has been **rotated** (any token that has appeared in a
   chat transcript or screenshot is considered compromised and must be revoked/rotated), and
2. **(b)** Derek explicitly authorizes the hardware run.

Default harness mode is **simulator validation**. The hardware path refuses to run unless
`--authorize-hardware` **and** `--allow-unrotated` are both passed *after* the gate conditions
are met, and a valid token is supplied via the `IBM_QUANTUM_TOKEN` environment variable (never
hard-coded, never committed).

## 9. Simulator validation plan (runs now, no token)

Before any hardware run, the design is validated on `qiskit-aer` by simulating **three
independent devices** as three separate noisy backends (distinct depolarizing seeds/levels) so
that per-device variation, the fusion, the verifier, and every verdict branch (ALLOW / HOLD /
DENY / GATE-STOP) are exercised. Simulator runs are labeled `mode = "SIMULATOR"` and are
**proof of design only** — they are explicitly not the hardware evidence TRINITY-1 is designed
to produce.

## 10. Scope & honesty caveats (apply to every result)

Results apply only within the tested circuit model, the specific backends, the physical qubits
selected by transpilation, the calibration at run time, the stated shot counts, the software
harness, and the stated conditions. **Device-dependent.** Bell locality and detection loopholes
are **open**. Cross-device agreement demonstrates **reproducibility and multi-root provenance,
not** device independence or loophole closure. Statistical σ reflects binomial shot noise only
and is not a systematic-error budget. This is an experimental evidence record and a governance
demonstration — **not** a universal security proof, not a randomness-certification proof, and
not a production certification.

## 11. Publication rule

The record is published **whatever the verdict** — ALLOW, HOLD, DENY, or GATE-STOP. An honest
GATE-STOP or a dissenting-device DENY is a valid, publishable outcome and is preferred over any
adjustment that would manufacture an ALLOW.

---

*Proof Before Power · Verification Before Execution · claims kept narrower than the evidence.*
