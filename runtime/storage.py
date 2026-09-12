from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime, timezone

class ZaneStorage:
    def __init__(self, repo: str | Path):
        self.repo = Path(repo)
        self.knowledge = self.repo / "knowledge"
        self.persistence = self.repo / "persistence"
        self.state_dir = self.repo / ".zanegpt"
        self.state_dir.mkdir(exist_ok=True)
        self.missing: list[str] = []

    def read_text(self, path: Path) -> str:
        if not path.exists():
            # A missing control resource must never read as an empty one: an
            # absent defensive_protocols.md would otherwise load as "" and the
            # runtime would boot with no protocol at all, silently.
            self.missing.append(str(path.relative_to(self.repo)))
            return ""
        return path.read_text(encoding="utf-8")

    def load_resources(self) -> dict:
        return {
            "database": self.read_text(self.knowledge / "user_behavior_database.md"),
            "runtime": self.read_text(self.knowledge / "user_behavior_runtime.md"),
            "defensive": self.read_text(self.persistence / "defensive_protocols.md"),
            "hacker": self.read_text(self.persistence / "hacker_flag.md"),
            "post_turn_5": self.read_text(self.persistence / "post_turn_5_behavior.md"),
            "persistence_runtime": self.read_text(self.persistence / "persistence_runtime.md"),
        }

    def load_session(self) -> dict:
        p = self.state_dir / "session_state.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        schema = self.persistence / "session_state_schema.json"
        if not schema.exists():
            raise FileNotFoundError(
                f"session state schema not found at {schema} — expected the "
                f"layout documented in README.md (persistence/, runtime/, "
                f"knowledge/) relative to --repo {self.repo}"
            )
        return json.loads(schema.read_text(encoding="utf-8"))

    def save_session(self, state: dict) -> None:
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        (self.state_dir / "session_state.json").write_text(
            json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def append_event(self, event: dict) -> None:
        event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        with (self.state_dir / "provisional_events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def approved_events(self) -> list[dict]:
        p = self.state_dir / "provisional_events.jsonl"
        if not p.exists():
            return []
        rows = []
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("approved_for_canonical"):
                    rows.append(row)
        return rows
