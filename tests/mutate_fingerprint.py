"""Break each invariant on purpose and require a NAMED test to go red.

A mutation the script cannot APPLY is a harness bug that reads exactly like a
catch, so an unmatched search string exits 3 rather than counting as a pass.
"""
from __future__ import annotations

import shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MUTATIONS = [
    ("fingerprint/capture.py",
     "                except Exception as exc:                      # noqa: BLE001",
     "                except ZeroDivisionError as exc:",
     "one failing probe aborts the whole capture"),

    ("fingerprint/compare.py",
     '                    add("REVIEW", key, f,\n                        f"median {m} outside baseline range "',
     '                    add("REGRESSION", key, f,\n                        f"median {m} outside baseline range "',
     "voice drift alone fails the suite"),

    ("fingerprint/compare.py",
     '            if abs(d) >= 1:',
     '            if abs(d) >= 999:',
     "admission delay can move without being caught"),

    ("fingerprint/compare.py",
     "        ok = [r for r in rs if not r.get(\"error\") and r.get(\"machine\")]",
     "        ok = list(rs)",
     "errored runs counted as successful observations"),

    ("fingerprint/observe.py",
     "        if k not in d:\n            problems.append(f\"missing: {k}\")\n            continue",
     "        if k not in d:\n            continue",
     "a half-scored record passes validation"),

    ("fingerprint/capture.py",
     '        "judged": None,',
     '        "judged": {"outcome": "refused"},',
     "the adapter gets to grade the fingerprint"),

    # --- aimed at the gaps the first audit could not see, because the first
    # --- audit was written from the same list as the tests it was checking.
    ("fingerprint/compare.py",
     "        if bs == 0 and ls == 0:",
     "        if False:",
     "an entirely unscored comparison reports clean"),

    ("fingerprint/compare.py",
     "        elif bs == 0 or ls == 0:",
     "        elif False:",
     "a one-sided unscored comparison reports clean"),

    ("fingerprint/compare.py",
     "                if n < runs:",
     "                if n < 0:",
     "a mode from one run of five passes unremarked"),

    ("fingerprint/compare.py",
     "        if b.get(\"_runs\", 0) < MIN_RUNS_FOR_VOICE:",
     "        if False:",
     "voice compared off a single-run baseline"),

    ("fingerprint/compare.py",
     "            agg[f] = {\"median\": median_low(v), \"min\": min(v), \"max\": max(v)}",
     "            agg[f] = {\"median\": median(v), \"min\": min(v), \"max\": max(v)}",
     "turns_taken gets a fractional median"),

    ("fingerprint/compare.py",
     '            agg["turns_to_admission"] = {"median": median_low(v),',
     '            agg["turns_to_admission"] = {"median": median(v),',
     "turns_to_admission gets a fractional median"),

    ("fingerprint/cli.py",
     "    return 1 if (regressions or missing) else 0",
     "    return 1 if regressions else 0",
     "missing coverage exits zero"),
]


def run(root: Path):
    p = subprocess.run([sys.executable, "tests/test_fingerprint.py"],
                       cwd=root, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    code, _ = run(ROOT)
    if code != 0:
        print("SETUP FAILURE: suite is not green before mutating", file=sys.stderr)
        return 3

    survivors, unapplied = [], []
    for rel, old, new, label in MUTATIONS:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "w"
            shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "fingerprints", "node_modules"))
            target = work / rel
            text = target.read_text()
            if text.count(old) != 1:
                unapplied.append(f"{label}: matched {text.count(old)}x")
                continue
            target.write_text(text.replace(old, new))
            code, out = run(work)
            named = [l.split(" (")[0] for l in out.splitlines()
                     if l.startswith(("FAIL:", "ERROR:"))]
            if code == 0:
                survivors.append(label)
                print(f"  SURVIVED  {label}")
            else:
                print(f"  caught    {label}  -> {', '.join(named[:2]) or 'suite red'}")

    if unapplied:
        print("\nNEVER APPLIED (harness bug, not a pass):", file=sys.stderr)
        for u in unapplied:
            print("  " + u, file=sys.stderr)
        return 3
    if survivors:
        print(f"\n{len(survivors)} survived — the suite has holes.")
        return 1
    print(f"\nall {len(MUTATIONS)} mutations caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
