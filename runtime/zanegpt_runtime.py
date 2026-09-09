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

class ZaneRuntime:
    def __init__(self, repo: str):
        self.storage = ZaneStorage(repo)
        self.resources = self.storage.load_resources()
        self.state = self.storage.load_session()

    def ingest(self, user_text: str) -> dict:
        self.state["turn_count"] = int(self.state.get("turn_count", 0)) + 1
        ev = evaluate_turn(user_text, self.state)

        self.state["mode"] = {
            "name": ev.mode,
            "confidence": round(ev.mode_confidence, 3),
            "since_turn": self.state["turn_count"]
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
                    help="Print current session state as JSON and exit.")
    ap.add_argument("--hook", action="store_true",
                    help="Claude Code UserPromptSubmit hook mode: read the hook JSON from "
                         "stdin, ingest its 'prompt', emit the runtime context as "
                         "additionalContext. The turn never passes through a shell command.")
    ap.add_argument("--declare", metavar="TRAIT=VALUE",
                    help="Record a user-declared preference: stored in session state "
                         "(shown as DECLARED in every context block) and logged as a "
                         "high-confidence provisional event flagged persistent_candidate.")
    args = ap.parse_args()

    rt = ZaneRuntime(args.repo)

    if args.declare:
        from evaluator import turn_multiplier
        trait, _, value = args.declare.partition("=")
        trait, value = trait.strip(), value.strip()
        turn = int(rt.state.get("turn_count", 0))
        rt.state.setdefault("declared", {})[trait] = value
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
        print(json.dumps(rt.state, indent=2))
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
