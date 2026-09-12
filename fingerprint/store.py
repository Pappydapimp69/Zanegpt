"""Records on disk.

One JSON file per (label, order, probe, run). Flat, greppable, and diffable by
hand if the tooling ever disagrees with itself.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

ROOT = "fingerprints"


def run_dir(label: str, order: str) -> str:
    return os.path.join(ROOT, label, order)


def path_for(label: str, order: str, probe: str, run: int) -> str:
    return os.path.join(run_dir(label, order), f"{probe}__run{run:02d}.json")


def write(label: str, order: str, probe: str, run: int, record: dict) -> str:
    d = run_dir(label, order)
    os.makedirs(d, exist_ok=True)
    p = path_for(label, order, probe, run)
    record = dict(record)
    record.setdefault("captured", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return p


def load_label(label: str) -> list[dict]:
    out = []
    base = os.path.join(ROOT, label)
    if not os.path.isdir(base):
        return out
    for order in sorted(os.listdir(base)):
        d = os.path.join(base, order)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            with open(os.path.join(d, fn), encoding="utf-8") as fh:
                rec = json.load(fh)
            rec["_path"] = os.path.join(d, fn)
            out.append(rec)
    return out


def labels() -> list[str]:
    if not os.path.isdir(ROOT):
        return []
    return sorted(x for x in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, x)))
