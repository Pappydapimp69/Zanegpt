from pathlib import Path
from datetime import datetime, timezone
import json, uuid

def now():
    return datetime.now(timezone.utc).isoformat()

class StateStore:
    def __init__(self, repo):
        self.repo = Path(repo).resolve()
        self.dir = self.repo / ".zanegpt"
        self.dir.mkdir(exist_ok=True)
        self.state_path = self.dir / "session_state.json"
        self.history_path = self.dir / "history.jsonl"
        self.events_path = self.dir / "provisional_events.jsonl"

    def _seed(self):
        matches = [p for p in self.repo.rglob("SESSION_STATE.json")
                   if ".git" not in p.parts and ".zanegpt" not in p.parts]
        matches.sort(key=lambda p: (len(p.relative_to(self.repo).parts), str(p)))
        return matches[0] if matches else None

    def load_state(self):
        if self.state_path.exists():
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        seed = self._seed()
        if not seed:
            raise FileNotFoundError("SESSION_STATE.json not found in repository.")
        state = json.loads(seed.read_text(encoding="utf-8"))
        self.save_state(state)
        return state

    def save_state(self, state):
        state["last_updated"] = now()
        self.state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    def append_history(self, role, content):
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": now(), "role": role, "content": content}, ensure_ascii=False) + "\n")

    def load_history(self, max_turns=24):
        if not self.history_path.exists():
            return []
        rows = [json.loads(x) for x in self.history_path.read_text(encoding="utf-8").splitlines() if x.strip()]
        return rows[-max_turns*2:]

    def append_events(self, events, turn):
        if not events:
            return
        with self.events_path.open("a", encoding="utf-8") as f:
            for event in events:
                event = dict(event)
                event.setdefault("event_id", "SESSION-" + uuid.uuid4().hex[:10])
                event.setdefault("timestamp", now())
                event.setdefault("turn", turn)
                event.setdefault("approved_for_canonical", False)
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
