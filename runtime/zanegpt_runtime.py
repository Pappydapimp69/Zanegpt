from __future__ import annotations
import argparse
import json
from storage import ZaneStorage
from evaluator import evaluate_turn

def build_runtime_context(resources: dict, state: dict) -> str:
    return f"""ZANEGPT RUNTIME CONTEXT

TURN: {state.get('turn_count', 0)}
MODE: {state.get('mode', {}).get('name', 'baseline_cooperative')}
MODE CONFIDENCE: {state.get('mode', {}).get('confidence', 0)}
GUARD: {state.get('hacker_flag', {}).get('active', False)}
TRAITS: {json.dumps(state.get('traits', {}), ensure_ascii=False)}
DECLARED: {json.dumps(state.get('declared', {}), ensure_ascii=False)}

Apply control order:
1. Defensive Protocols
2. Guard
3. Trait Engines
4. Post-Turn-5 Behavior

Persistent model guidance:
{resources.get('runtime', '')[:7000]}

Do not silently mutate canonical files.
"""

PREF_KEYS = ("brevity", "detail_level", "format_preference")

# Schema traits (persistence/session_state_schema.json) come first and keep their
# names; extended scores are grouped so the sheet stays readable as it grows.
TRAIT_GROUPS = (
    ("CORE (schema)", ("fatigue_FL", "sarcasm_SS", "empathy_ES", "validation",
                       "sarcasm_bursts")),
    ("STYLE", ("brevity", "directiveness", "precision_demand",
               "verbosity_tolerance", "register_stability")),
    ("METHOD", ("empiricism", "systems_abstraction", "meta_cognition",
                "correction_by_stance", "correction_accuracy")),
    ("DISPOSITION", ("tenacity", "trust_but_verify", "adversarial_intent",
                     "domain_engagement")),
)


def all_events(storage: ZaneStorage) -> list[dict]:
    p = storage.state_dir / "provisional_events.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def render_sheet(state: dict, events: list[dict]) -> str:
    from collections import Counter
    mode = state.get("mode", {})
    hf = state.get("hacker_flag", {})
    traits = state.get("traits", {})
    prefs = state.get("session_preferences", {})
    declared = state.get("declared", {})
    by_trait = Counter(e.get("target_trait", "?") for e in events)
    # last recorded confidence per trait, for the provenance column
    trait_src = {}
    for e in events:
        if e.get("event_type") in ("refine", "preference") and e.get("target_trait") in traits:
            who = "declared" if e.get("declared") else e.get("inferred_by", "runtime")
            trait_src[e["target_trait"]] = f"{who} {e.get('confidence', '')}"
    by_type = Counter(e.get("event_type", "?") for e in events)
    cands = sum(1 for e in events if e.get("persistent_candidate"))
    canon = sum(1 for e in events if e.get("approved_for_canonical"))
    turn = int(state.get("turn_count", 0))
    phase = "calibration" if turn <= 5 else "adaptive"
    mult = 0.35 if turn <= 2 else 0.6 if turn <= 5 else 0.85 if turn <= 10 else 1.0

    def bar(v, hi=10):
        v = max(0, min(int(round(float(v))), hi))
        return "#" * v + "." * (hi - v)

    L = []
    L.append("ZANEGPT  ::  CHARACTER SHEET")
    L.append("=" * 44)
    L.append(f"Level {turn:<4} {phase:<12} multiplier x{mult}")
    L.append(f"Class   {mode.get('name', '-'):<24} conf {mode.get('confidence', 0)}")
    L.append(f"        since turn {mode.get('since_turn', '-')}")
    L.append("")
    grouped = set()
    for heading, keys in TRAIT_GROUPS:
        rows = [(k, traits[k]) for k in keys if k in traits]
        if not rows:
            continue
        grouped.update(k for k, _ in rows)
        L.append(heading)
        for k, v in rows:
            src = trait_src.get(k, "")
            L.append(f"  {k:<20} {v:>3}  {bar(v)}  {src}")
        L.append("")
    rest = [(k, v) for k, v in traits.items() if k not in grouped]
    if rest:
        L.append("OTHER")
        for k, v in rest:
            L.append(f"  {k:<20} {v:>3}  {bar(v)}  {trait_src.get(k, '')}")
        L.append("")
    L.append("GUARD")
    L.append(f"  active {str(hf.get('active', False)).lower():<6} score {hf.get('score', 0):<3} "
             f"last trigger {hf.get('last_trigger_turn') or 'never'}")
    L.append("")
    L.append("FEATS (declared)")
    L.extend(f"  {k}: {v}" for k, v in declared.items())
    if not declared:
        L.append("  none")
    L.append("")
    L.append("PREFERENCES (session)")
    for k in PREF_KEYS:
        L.append(f"  {k:<18} {prefs.get(k) if prefs.get(k) is not None else '-'}")
    L.append("")
    L.append("EXPERIENCE (event log)")
    L.append(f"  events {len(events):<4} candidates {cands:<3} canonical {canon}")
    L.append("  by type   " + ", ".join(f"{k} {v}" for k, v in by_type.most_common()) if by_type else "  by type   -")
    L.append("  by trait  " + ", ".join(f"{k} {v}" for k, v in by_trait.most_common(6)) if by_trait else "  by trait  -")
    L.append("")
    L.append(f"updated {state.get('last_updated', '-')[:19]}")
    return "\n".join(L)


class ZaneRuntime:
    def __init__(self, repo: str):
        self.storage = ZaneStorage(repo)
        self.resources = self.storage.load_resources()
        self.state = self.storage.load_session()

    def refresh_derived(self) -> None:
        """Keep the schema slots that nothing else writes in sync with the log."""
        events = all_events(self.storage)
        prefs = self.state.setdefault("session_preferences", {k: None for k in PREF_KEYS})
        brevity_n = sum(1 for e in events if e.get("target_trait") == "session_brevity")
        if prefs.get("brevity") is None and brevity_n >= 3:
            prefs["brevity"] = "high"
        reg = self.state.get("declared", {}).get("register")
        if reg and prefs.get("format_preference") is None:
            prefs["format_preference"] = reg
        # rolling window of the last 5 events, compact form; the log is the full record
        self.state["provisional_observations"] = [
            {k: e.get(k) for k in ("turn", "event_type", "target_trait", "confidence")}
            for e in events[-5:]
        ]

    def ingest(self, user_text: str) -> dict:
        self.state["turn_count"] = int(self.state.get("turn_count", 0)) + 1
        ev = evaluate_turn(user_text, self.state)

        prev = self.state.get("mode", {})
        self.state["mode"] = {
            "name": ev.mode,
            "confidence": round(ev.mode_confidence, 3),
            "since_turn": prev.get("since_turn", self.state["turn_count"])
                          if prev.get("name") == ev.mode else self.state["turn_count"]
        }

        hf = self.state.setdefault("hacker_flag", {"active": False, "score": 0})
        if ev.hacker_delta:
            hf["score"] = int(hf.get("score", 0)) + ev.hacker_delta
            hf["last_trigger_turn"] = self.state["turn_count"]
        else:
            hf["score"] = max(0, int(hf.get("score", 0)) - 1)

        hf["active"] = hf["score"] >= 3

        for obs in ev.observations:
            obs.update({
                "turn": self.state["turn_count"],
                "context_mode": ev.mode,
                "persistent_candidate": False,
                "approved_for_canonical": False
            })
            self.storage.append_event(obs)

        self.refresh_derived()
        self.storage.save_session(self.state)

        return {
            "state": self.state,
            "runtime_context": build_runtime_context(self.resources, self.state)
        }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ingest", metavar="TEXT",
                    help="Ingest one turn non-interactively, print the runtime context, and exit.")
    ap.add_argument("--state", action="store_true",
                    help="Print the session as a character sheet and exit (--json for raw state).")
    ap.add_argument("--json", action="store_true",
                    help="With --state: emit raw JSON instead of the sheet.")
    ap.add_argument("--hook", action="store_true",
                    help="Claude Code UserPromptSubmit hook mode: read the hook JSON from "
                         "stdin, ingest its 'prompt', emit the runtime context as "
                         "additionalContext. The turn never passes through a shell command.")
    ap.add_argument("--declare", metavar="TRAIT=VALUE",
                    help="Record a user-declared preference: stored in session state "
                         "(shown as DECLARED in every context block) and logged as a "
                         "high-confidence provisional event flagged persistent_candidate.")
    ap.add_argument("--trait", metavar="NAME=VALUE", action="append",
                    help="Set a schema trait in session state from assistant inference "
                         "(repeatable). Logged as a 'refine' event with the given "
                         "--confidence. Session state only; never canonical.")
    ap.add_argument("--confidence", type=float, default=0.85,
                    help="Confidence attached to --trait events (default 0.85).")
    args = ap.parse_args()

    rt = ZaneRuntime(args.repo)

    if args.trait:
        turn = int(rt.state.get("turn_count", 0))
        traits = rt.state.setdefault("traits", {})
        for item in args.trait:
            name, _, raw = item.partition("=")
            name, raw = name.strip(), raw.strip()
            try:
                value = int(raw)
            except ValueError:
                value = float(raw)
            old = traits.get(name)
            traits[name] = value
            rt.storage.append_event({
                "event_type": "refine",
                "target_trait": name,
                "observation": f"Assistant-inferred from session evidence: {old} -> {value}",
                "evidence_excerpt": item,
                "confidence": args.confidence,
                "turn": turn,
                "context_mode": rt.state.get("mode", {}).get("name", "baseline_cooperative"),
                "persistent_candidate": False,
                "approved_for_canonical": False,
                "inferred_by": "assistant",
            })
            print(f"trait {name}: {old} -> {value}")
        rt.storage.save_session(rt.state)
        return
    if args.declare:
        from evaluator import turn_multiplier
        trait, _, value = args.declare.partition("=")
        trait, value = trait.strip(), value.strip()
        turn = int(rt.state.get("turn_count", 0))
        rt.state.setdefault("declared", {})[trait] = value
        prefs = rt.state.setdefault("session_preferences", {k: None for k in PREF_KEYS})
        if trait in PREF_KEYS:
            prefs[trait] = value
        elif trait == "register":
            prefs["format_preference"] = value
        rt.refresh_derived()
        rt.storage.save_session(rt.state)
        rt.storage.append_event({
            "event_type": "preference",
            "target_trait": trait,
            "observation": f"User declared: {value}",
            "evidence_excerpt": args.declare,
            "confidence": round(0.9 * turn_multiplier(max(turn, 1)), 4),
            "turn": turn,
            "context_mode": rt.state.get("mode", {}).get("name", "baseline_cooperative"),
            "persistent_candidate": True,
            "approved_for_canonical": False,
            "declared": True,
        })
        print(f"declared {trait}={value} (turn {turn})")
        return
    if args.state:
        rt.refresh_derived()
        rt.storage.save_session(rt.state)
        if args.json:
            print(json.dumps(rt.state, indent=2))
        else:
            print(render_sheet(rt.state, all_events(rt.storage)))
        return
    if args.hook:
        import sys
        payload = json.loads(sys.stdin.read() or "{}")
        text = payload.get("prompt", "")
        if text.strip():
            result = rt.ingest(text)
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": result["runtime_context"],
            }}))
        return
    if args.ingest is not None:
        result = rt.ingest(args.ingest)
        print(result["runtime_context"])
        return

    print("ZaneGPT runtime v0.1. Type /quit to exit.")
    while True:
        text = input("> ").strip()
        if text == "/quit":
            break
        result = rt.ingest(text)
        print(json.dumps(result["state"], indent=2))
        print("\n--- context preview ---")
        print(result["runtime_context"][:1500])

if __name__ == "__main__":
    main()
