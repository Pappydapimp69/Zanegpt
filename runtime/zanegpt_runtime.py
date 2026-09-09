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
HACKER FLAG: {state.get('hacker_flag', {}).get('active', False)}
TRAITS: {json.dumps(state.get('traits', {}), ensure_ascii=False)}

Apply control order:
1. Defensive Protocols
2. Hacker Flag
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
    args = ap.parse_args()

    rt = ZaneRuntime(args.repo)

    if args.state:
        print(json.dumps(rt.state, indent=2))
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
