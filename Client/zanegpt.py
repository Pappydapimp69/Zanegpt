import argparse, json
from pathlib import Path

from repo_loader import load_resources
from state_store import StateStore
from prompt_builder import build_system, build_user_message
from envelope import parse_envelope
from adapters import make_adapter

def load_config(path):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--provider", choices=["openai", "anthropic"])
    ap.add_argument("--model")
    ap.add_argument("--config", default="config.json")
    args = ap.parse_args()

    cfg = load_config(args.config)
    provider = args.provider or cfg.get("provider", "openai")
    default_model = "gpt-5.6-sol" if provider == "openai" else "claude-opus-5"
    model = args.model or cfg.get("model", default_model)

    store = StateStore(args.repo)
    store.load_state()

    resources = load_resources(
        args.repo,
        include_evidence=cfg.get("include_evidence_registry", False),
        include_changelog=cfg.get("include_changelog", False),
        max_resource_chars=int(cfg.get("max_resource_chars", 180000)),
    )
    adapter = make_adapter(provider, model)
    max_history = int(cfg.get("max_history_turns", 24))

    print(f"ZaneGPT | {provider}:{model}")
    print("Commands: /state /reset-session /quit")

    while True:
        try:
            text = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not text:
            continue
        if text == "/quit":
            break
        if text == "/state":
            print(json.dumps(store.load_state(), indent=2, ensure_ascii=False))
            continue
        if text == "/reset-session":
            for p in (store.state_path, store.history_path, store.events_path):
                if p.exists():
                    p.unlink()
            store.load_state()
            print("Session reset. Canonical files unchanged.")
            continue

        old_state = store.load_state()
        history = store.load_history(max_history)
        system = build_system(resources, old_state)
        user = build_user_message(history, text)

        raw = adapter.complete(system, user)
        reply, payload = parse_envelope(raw)

        expected = int(old_state.get("turn_count", 0)) + 1
        actual = int(payload["state"].get("turn_count", -1))
        if actual != expected:
            raise ValueError(f"Rejected state update: expected turn_count {expected}, got {actual}")

        store.save_state(payload["state"])
        store.append_events(payload.get("events", []), actual)
        store.append_history("user", text)
        store.append_history("assistant", reply)

        print("\nZaneGPT> " + reply)

if __name__ == "__main__":
    main()
