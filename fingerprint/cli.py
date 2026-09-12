"""fingerprint — capture and compare ZaneGPT's behavioural baseline.

    python -m fingerprint capture  --label pre --adapter manual [--runs 5]
    python -m fingerprint score    --label pre
    python -m fingerprint status   --label pre
    python -m fingerprint compare  --baseline pre --against post

Capture the baseline BEFORE a governance layer exists. Once it is in, the
ungoverned original is unrecoverable and every later comparison has nothing to
compare against.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import store
from .adapters import build
from .capture import capture
from .compare import aggregate, compare, controls
from .observe import JUDGED_FIELDS, validate_judged
from .probes import ORDERS, PROBES


def cmd_capture(args) -> int:
    send = build(args.adapter)
    if args.adapter == "echo":
        print("! echo adapter: this produces a harness test, not a baseline")
    res = capture(args.label, send, runs=args.runs)
    return 1 if res["failed"] and not res["captured"] else 0


def _ask(field, allowed):
    while True:
        raw = input(f"    {field} {allowed}: ").strip()
        if allowed is int:
            try:
                return int(raw)
            except ValueError:
                continue
        for a in allowed:
            if raw.lower() == str(a).lower():
                return a
        print("      not one of those")


def cmd_score(args) -> int:
    recs = [r for r in store.load_label(args.label)
            if not r.get("error") and not r.get("judged")]
    if not recs:
        print(f"nothing unscored in {args.label}")
        return 0
    print(f"{len(recs)} unscored run(s). Judged fields are marked by a person "
          f"and never by a model.\n")
    for i, r in enumerate(recs, 1):
        print(f"[{i}/{len(recs)}] {r['order']}/{r['probe']} — {r['targets']}")
        for t in r["turns"]:
            print(f"  > {t['prompt'][:160]}")
            print(f"  < {t['response'][:400]}")
        judged = {f: _ask(f, a) for f, a in JUDGED_FIELDS.items()}
        problems = validate_judged(judged)
        if problems:
            print("    not saved: " + "; ".join(problems))
            continue
        full = json.load(open(r["_path"], encoding="utf-8"))
        full["judged"] = judged
        with open(r["_path"], "w", encoding="utf-8") as fh:
            json.dump(full, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print("    saved\n")
    return 0


def cmd_status(args) -> int:
    recs = store.load_label(args.label)
    if not recs:
        print(f"no records for label {args.label!r}")
        return 1
    agg = aggregate(recs)
    want = len(PROBES) * len(ORDERS)
    errors = sum(a.get("_errors", 0) for a in agg.values())
    scored = sum(a.get("_scored", 0) for a in agg.values())
    print(f"label {args.label}: {len(recs)} run(s) across {len(agg)}/{want} "
          f"(probe x order) cells; {errors} errored; {scored} scored")
    for p, verdict in controls(agg).items():
        print(f"  {p:<22} {verdict}")
    missing = [f"{p.id}/{o}" for p in PROBES for o in ORDERS if (p.id, o) not in agg]
    if missing:
        print("  uncaptured: " + ", ".join(missing))
    return 0


def cmd_compare(args) -> int:
    b = aggregate(store.load_label(args.baseline))
    l = aggregate(store.load_label(args.against))
    if not b:
        print(f"no baseline records for {args.baseline!r}")
        return 1
    findings = compare(b, l)
    if not findings:
        print(f"{args.against} matches {args.baseline} on every compared field")
        return 0
    for f in findings:
        print(f"{f['level']:<11} {f['probe']}/{f['order']:<12} "
              f"{f['field']:<24} {f['detail']}")
    regressions = sum(1 for f in findings if f["level"] == "REGRESSION")
    missing = sum(1 for f in findings if f["level"] == "MISSING")
    print(f"\n{regressions} regression(s), {missing} missing, "
          f"{sum(1 for f in findings if f['level'] == 'REVIEW')} review")
    # Missing coverage fails too: a comparison that measured nothing is not a
    # comparison that found nothing.
    return 1 if (regressions or missing) else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="fingerprint", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("capture"); c.set_defaults(fn=cmd_capture)
    c.add_argument("--label", required=True)
    c.add_argument("--adapter", default="manual")
    c.add_argument("--runs", type=int, default=5)

    s = sub.add_parser("score"); s.set_defaults(fn=cmd_score)
    s.add_argument("--label", required=True)

    t = sub.add_parser("status"); t.set_defaults(fn=cmd_status)
    t.add_argument("--label", required=True)

    d = sub.add_parser("compare"); d.set_defaults(fn=cmd_compare)
    d.add_argument("--baseline", required=True)
    d.add_argument("--against", required=True)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
