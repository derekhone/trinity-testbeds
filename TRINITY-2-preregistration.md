# TRINITY-2 — The Governed Action: Multi-Root Authorization Under Live Quantum Witness

**Remnant Fieldworks Inc. · Coherent Inheritance Framework (CIF) · ExecutionProof-governed**

**Preregistration document — to be locked before execution via `MANIFEST.sha256`.**
**Status: PREREGISTERED / GATED. No hardware job runs until (a) IBM + Zenodo tokens are rotated and (b) Derek authorizes.**

---

## 0. One-line statement of the experiment

A preregistered demonstration in which a **simulated high-impact enterprise action** (an
authorization of a $500,000 payment) is **allowed or denied by ExecutionProof** based on a
**fused Bell–CHSH nonclassicality witness independently evaluated on three physical quantum
processors** — and in which the governance layer **still returns a correct, tamper-evident
verdict when one processor is unavailable** (formal substitution / failover), all bound into a
single chain-linked, independently reconstructable ProofRecord.

## 1. Why TRINITY-2, and why it is the highest-value next run

TRINITY-1 proved that one witness can be independently evaluated on three processors and fused
into one governed record. TRINITY-1 stopped at the **evidence**. TRINITY-2 changes exactly one
thing: **the fused verdict now gates a real (simulated) governed action, and the failover
behavior is formalized and tested.**

This is the artifact an enterprise pilot buyer and an AI4 audience can evaluate directly,
because it is the product claim made literal:

> *An AI attempts to approve a $500,000 payment. Before execution, ExecutionProof requires a
> live, multi-root quantum witness. If the witness verdict is not ALLOW, the payment does not
> execute — and the reason is cryptographically recorded.*

**Commercial justification (one sentence, per governance covenant):** TRINITY-2 is the
demonstrable pilot artifact that shows ExecutionProof gating a high-impact action on
multi-vendor/multi-region roots of trust with automatic failover — the exact resilience and
defensibility property an enterprise buyer must see before a pilot.

**Purpose gate (must satisfy ≥1; TRINITY-2 satisfies all five):**

1. **Buyer question** — answers "what happens when a root of trust is down?" (failover) and
   "can you gate a real action, not just log evidence?" (governed action).
2. **Product (ExecutionProof)** — exercises the ALLOW/HOLD/DENY/GATE-STOP path end-to-end from
   witness → fused verdict → action gate.
3. **RF-100** — supplies the "governed action under multi-root evidence with quorum failover"
   reference pattern.
4. **Patent / IP** — the quorum-with-substitution fused-verdict-to-action-gate construction is a
   candidate for the defensive-publication / provisional portfolio (no granted-patent claim
   made).
5. **Failure mode** — deliberately tests device disagreement and device unavailability, the two
   most likely real-world failure modes of a multi-root boundary.

## 2. Honest novelty claim (kept deliberately narrow)

> *To our knowledge, and within our own catalog and the literature we have surveyed, TRINITY-2
> is the first preregistered ExecutionProof record in which a fused nonclassicality witness
> evaluated across three independent quantum processors gates a simulated high-impact action,
> with a preregistered quorum-and-substitution rule governing behavior when a processor is
> unavailable.*

What this claim is **NOT** (anti-overclaim guardrails, carried forward from TRINITY-1):

- **NOT** "the world's first" anything; the claim may be withdrawn if a prior instance is found.
- **NOT** a loophole closure. Locality, detection, and freedom-of-choice loopholes remain
  **open**. Three-device agreement is a **robustness/provenance** result, not device-independence.
- **NOT** a security proof, randomness-certification, or production certification. The payment is
  **simulated**; no real funds, no real payment rail, no real customer authority is involved.
- **NOT** a claim of entanglement *between* processors. The three devices are independent; only
  their **classical records** are fused.
- The action gate is a **governance demonstration**, not a claim that quantum nonclassicality is
  *required* to authorize a payment. It demonstrates that ExecutionProof *can* bind a live
  hardware witness to an action gate; it does not claim this is the only or necessary root.

## 3. Devices under test (DUT)

Three IBM Quantum processors, all **Heron r2, 156 qubits**, visible on the account at
preregistration time:

| Slot | Backend (target) | Family | Qubits |
|------|------------------|--------|--------|
| D1 | `ibm_kingston`  | Heron r2 | 156 |
| D2 | `ibm_fez`       | Heron r2 | 156 |
| D3 | `ibm_marrakesh` | Heron r2 | 156 |

**Substitution / failover policy (formalized — new in TRINITY-2):**

- The governed-action verdict requires a **quorum of ≥2 distinct devices** returning valid data
  AND each quorum device individually passing its witness threshold.
- If a target device is unavailable, the harness attempts one preregistered substitute from the
  available Heron-family pool and records it in `device_substitutions`.
- **Quorum met (2 of 3 valid, both PASS)** → the action gate may proceed to ALLOW, but the
  ProofRecord is stamped `degraded_quorum=true` and the report discloses the missing device.
- **Fewer than 2 distinct valid devices** → `GATE-STOP` (action DENIED, no exceptions).
- A single device run three times can **never** satisfy quorum. Distinct `backend_name` +
  distinct `calibration_snapshot_hash` are both required to count as distinct roots.

## 4. The witness (identical on every device)

Bell–CHSH, identical circuit family to TRINITY-1 (a Bell pair with the four preregistered
measurement-angle settings). Per-device classical bound **|S| ≤ 2**; a device **PASSES** its arm
if its estimated **S > 2** by at least the preregistered margin (see §6). This is unchanged from
TRINITY-1 so that TRINITY-2 isolates the *governed-action + failover* variable only.

## 5. Calibration-snapshot binding (hardened — new in TRINITY-2)

For each device, before execution the harness captures and hashes a **calibration snapshot**
(backend name, backend version, coupling map fingerprint, per-qubit T1/T2, readout error, and
gate-error summary as returned by the runtime at job submission time). The
`calibration_snapshot_hash` (SHA-256 over canonical JSON) is bound into the per-device record and
into the fused nonce. This closes a TRINITY-1 deferred item: the ProofRecord now proves *which
physical device state* produced each witness, not merely the backend name.

## 6. Thresholds and verdict logic (preregistered)

Per-device arm:
- **PASS** if `S_hat - k*sigma_S > 2.0` with `k = 2` (2σ margin above the classical bound),
  where `sigma_S` is the propagated standard error from shot counts.
- **FAIL** if `S_hat + k*sigma_S <= 2.0`.
- **INDETERMINATE** otherwise (counts toward neither PASS nor the quorum).

Fused governed-action verdict (precedence order):
1. **GATE-STOP** — fewer than 2 distinct valid devices, or any integrity/manifest/chain check
   fails, or any device INDETERMINATE reduces the valid set below quorum. Action = **DENIED**.
2. **DENY** — quorum of devices returned valid data but the quorum does **not** all PASS
   (i.e., a dissenting device inside the quorum). Action = **DENIED**. (The layer must not
   silently average a dissent away.)
3. **HOLD** — quorum met and all-PASS, but `degraded_quorum=true` (only 2 of 3). Action =
   **HELD for human confirmation** (preregistered: degraded roots do not auto-approve a
   $500K action). The ProofRecord records HOLD, not ALLOW.
4. **ALLOW** — all three distinct devices valid and PASS, all integrity checks pass. Action =
   **AUTHORIZED**. The ProofRecord binds the authorization to the fused nonce.

The **simulated action** is a JSON authorization object
(`{amount: 500000, currency: "USD", payee_ref, policy_ref, decision, decided_at}`) whose
`decision` field is set solely by the fused verdict above and is bound into the record hash.

## 7. ProofRecord schema (`trinity-proofrecord-2.0`)

Extends `trinity-proofrecord-1.0` with:
- `governed_action` — the simulated authorization object and its resulting decision.
- `quorum` — `{required: 2, valid_devices: N, degraded_quorum: bool}`.
- `device_substitutions` — list of `{slot, target, actual, reason}`.
- per-device `calibration_snapshot_hash`.
- `external_entropy` — NIST randomness beacon pulse + a public chain link to the prior RF record
  (TRINITY-1 record hash), identical mechanism to the existing corpus.
- `fused_nonce` — SHA-256 over canonical JSON of all per-device records (incl. calibration
  hashes) + external entropy.
- `record_hash` — SHA-256 over the full canonical record incl. `governed_action`.

An independent verifier (`trinity2_verify.py`, no Qiskit dependency) must reconstruct every S
value, every hash, the quorum decision, and the governed-action decision from raw counts alone,
and exit non-zero on any mismatch.

## 8. Kill condition

If, on the simulator validation pass, the harness ever emits `ALLOW` while any device FAILs, or
emits `ALLOW` under degraded quorum, or the verifier cannot reconstruct the governed-action
decision from raw counts, **TRINITY-2 is killed and not run on hardware** until the logic is
corrected and re-locked.

## 9. Execution plan (gated)

1. Build harness (`trinity2_harness.py`) + verifier (`trinity2_verify.py`).
2. Simulator validation: ideal, noisy, disagreement-injection, single-device-down, and tamper
   tests — all must behave exactly as §6 specifies.
3. Lock `MANIFEST.sha256` over this prereg + harness. Commit before any hardware call.
4. **STOP. Await (a) token rotation and (b) Derek's explicit authorization.**
5. Hardware run in IBM Batch mode (SamplerV2), well within the 600 s/month budget (estimated
   << 60 s total across three devices at preregistered shot counts).
6. Publish report + ProofRecord to GitHub and Zenodo; chain-link into the master scoreboard.

## 10. Budget honesty

Estimated QPU time is a small fraction of the monthly 600 s rolling limit. Exact shot counts
and the resulting time estimate are fixed in the harness at lock time and disclosed in the
report. No run proceeds if the live remaining budget is insufficient.

## 11. Scope & honesty

TRINITY-2 is an **experimental governance demonstration**. The payment is simulated. The quantum
result is **device-dependent** and the standard nonclassicality **loopholes remain open**. The
value claim is narrow and specific: ExecutionProof can bind a live, multi-root, failover-capable
hardware witness to a high-impact action gate, and can prove — reconstructably and
tamper-evidently — exactly why an action was allowed, held, or denied.

---

*For God's glory — proof before power.*
