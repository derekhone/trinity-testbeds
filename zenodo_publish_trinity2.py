#!/usr/bin/env python3
"""
TRINITY-2 Zenodo publisher.

Reads the Zenodo token from env ZENODO_TOKEN (never hard-coded, never committed),
creates a new deposition, uploads the TRINITY-2 artifact set, applies the
preregistered metadata, and (unless --dry-run) publishes to mint a DOI.

Usage:
  ZENODO_TOKEN=xxxxx python3 zenodo_publish_trinity2.py --dry-run   # validate + upload, do NOT publish
  ZENODO_TOKEN=xxxxx python3 zenodo_publish_trinity2.py             # publish (mints DOI)

Safe to re-run: --dry-run leaves an unpublished draft you can inspect on zenodo.org
before committing. Nothing is published without an explicit non-dry-run invocation.
"""
import argparse
import json
import os
import sys
import time

import requests

BASE = "https://zenodo.org/api"
HERE = os.path.dirname(os.path.abspath(__file__))

# Files to include in the record (relative to repo root). Only existing files are uploaded.
FILES = [
    "TRINITY-2-preregistration.pdf",
    "TRINITY-2-preregistration.md",
    "trinity2_harness.py",
    "trinity2_verify.py",
    "MANIFEST-TRINITY-2.sha256",
    "results/TRINITY-2-proofrecord.json",
    "results/TRINITY-2-report.pdf",
    "results/TRINITY-2-report.md",
    "STATUS.md",
    "README.md",
]

EXPECT_RECORD_HASH = "4f6fa000e2bf3976a1d575267ecf188baf42f1c6caea9e717bf1fc1be6737dd0"


def log(m):
    print(f"[zenodo] {m}", flush=True)


def die(m, code=1):
    log(f"ERROR: {m}")
    sys.exit(code)


def preflight():
    """Verify the proofrecord we are about to publish is the verified hardware record."""
    pr = os.path.join(HERE, "results/TRINITY-2-proofrecord.json")
    if not os.path.exists(pr):
        die("proofrecord not found — run the harness first")
    r = json.load(open(pr))
    if r.get("mode") != "HARDWARE":
        die(f"refusing to publish: proofrecord mode is {r.get('mode')!r}, expected HARDWARE")
    if r.get("record_hash") != EXPECT_RECORD_HASH:
        die(f"refusing to publish: record_hash {r.get('record_hash')} != expected {EXPECT_RECORD_HASH}")
    log(f"preflight OK — HARDWARE record, verdict {r.get('aggregate_verdict')} -> "
        f"{r.get('action_decision')}, record_hash matches.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="create draft + upload files + set metadata, but do NOT publish")
    args = ap.parse_args()

    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        die("ZENODO_TOKEN not set in environment.")

    preflight()

    meta = json.load(open(os.path.join(HERE, "zenodo_metadata_trinity2.json")))
    s = requests.Session()
    s.params = {"access_token": token}

    # sanity: token works
    r = s.get(f"{BASE}/deposit/depositions", params={"access_token": token, "size": 1})
    if r.status_code == 401:
        die("token rejected (401). Rotate/regenerate a Zenodo token with deposit:write + deposit:actions.")
    if r.status_code == 403:
        die("token lacks scope (403). Needs deposit:write + deposit:actions.")
    r.raise_for_status()
    log("token authenticated OK.")

    # 1. create deposition
    r = s.post(f"{BASE}/deposit/depositions", json={}, params={"access_token": token})
    r.raise_for_status()
    dep = r.json()
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]
    log(f"created deposition {dep_id}")

    # 2. upload files (new bucket API)
    uploaded = []
    for rel in FILES:
        path = os.path.join(HERE, rel)
        if not os.path.exists(path):
            log(f"  skip (missing): {rel}")
            continue
        name = os.path.basename(rel)
        with open(path, "rb") as fh:
            ru = s.put(f"{bucket}/{name}", data=fh, params={"access_token": token})
        ru.raise_for_status()
        uploaded.append(name)
        log(f"  uploaded {name}")
    if not uploaded:
        die("no files uploaded — nothing to publish")

    # 3. metadata
    rm = s.put(f"{BASE}/deposit/depositions/{dep_id}",
               json=meta, params={"access_token": token})
    if rm.status_code >= 400:
        die(f"metadata rejected ({rm.status_code}): {rm.text[:500]}")
    log("metadata applied OK.")

    if args.dry_run:
        log(f"DRY RUN complete. Draft {dep_id} ready (NOT published).")
        log(f"  Inspect: https://zenodo.org/deposit/{dep_id}")
        log("  Re-run without --dry-run to publish and mint the DOI.")
        return 0

    # 4. publish
    rp = s.post(f"{BASE}/deposit/depositions/{dep_id}/actions/publish",
                params={"access_token": token})
    if rp.status_code >= 400:
        die(f"publish failed ({rp.status_code}): {rp.text[:500]}")
    pub = rp.json()
    doi = pub.get("doi")
    conceptdoi = pub.get("conceptdoi")
    log("=" * 70)
    log(f"PUBLISHED. version DOI: {doi}")
    log(f"concept DOI (cite this): {conceptdoi}")
    log(f"record: {pub.get('links',{}).get('record_html','')}")
    log("=" * 70)
    # write DOI file
    out = os.path.join(HERE, "ZENODO_DOI_TRINITY2.txt")
    with open(out, "w") as fh:
        fh.write("TRINITY-2 Zenodo Publication\n============================\n\n")
        fh.write(f"CONCEPT DOI (cite this): 10.5281/zenodo.{str(conceptdoi).split('.')[-1]}\n")
        fh.write(f"  https://doi.org/{conceptdoi}\n\n")
        fh.write(f"Version DOI: {doi}\n")
        fh.write(f"Record: {pub.get('links',{}).get('record_html','')}\n")
    log(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
