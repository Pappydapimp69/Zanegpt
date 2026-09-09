# ZaneGPT Runtime v0.1

Platform-neutral persistence core for the ZaneGPT reconstruction.

## What it does
1. Loads canonical behavior/control resources.
2. Maintains session-only state.
3. Evaluates each turn for mode, trait-state, and persistence events.
4. Produces a compact runtime context block for an LLM.
5. Logs provisional evidence append-only.
6. Requires explicit approval before canonical promotion.

## What it does NOT do
- It does not call OpenAI, Claude, or another LLM yet.
- It does not silently rewrite canonical behavior files.
- It does not fabricate historical ZaneGPT state.

## Expected repository structure

```text
Zanegpt/
  knowledge/
    user_behavior_database.md
    user_behavior_runtime.md
    user_behavior_evidence.jsonl
    user_behavior_changelog.md
  persistence/
    defensive_protocols.md
    hacker_flag.md
    post_turn_5_behavior.md
    persistence_runtime.md
    session_state_schema.json
    persistence_event_schema.json
  runtime/
    zanegpt_runtime.py
    storage.py
    evaluator.py
    config.json
```

Run locally:

```bash
# interactive loop
python runtime/zanegpt_runtime.py --repo /path/to/Zanegpt

# one turn, non-interactive (for driving from a skill/hook)
python runtime/zanegpt_runtime.py --repo /path/to/Zanegpt --ingest "user text"

# character sheet (level, class, ability scores, guard, feats, experience)
python runtime/zanegpt_runtime.py --repo /path/to/Zanegpt --state

# raw session state as JSON
python runtime/zanegpt_runtime.py --repo /path/to/Zanegpt --state --json

# record a user-declared preference / set inferred trait values
python runtime/zanegpt_runtime.py --repo /path/to/Zanegpt --declare register=terse
python runtime/zanegpt_runtime.py --repo /path/to/Zanegpt --trait empathy_ES=1 --trait validation=2
```

Session state persists in `<repo>/.zanegpt/` (gitignored).

## Claude Code skill

`.claude/skills/zanegpt/SKILL.md` wires the runtime into Claude Code: invoke
`/zanegpt` and each turn is ingested through the runtime, whose context block
governs the reply. No API key is needed — the host model is the LLM.

### UserPromptSubmit hook (recommended)

Merge this into `.claude/settings.json` (project) or `~/.claude/settings.json`
(user). The harness runs the runtime on every prompt and injects the context
block as additional context — the user's words never pass through a shell
command, and the model doesn't have to remember to ingest.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PROJECT_DIR:-.}/runtime/zanegpt_runtime.py\" --repo \"${CLAUDE_PROJECT_DIR:-.}\" --hook 2>/dev/null || true",
            "timeout": 10,
            "statusMessage": "ZaneGPT ingest"
          }
        ]
      }
    ]
  }
}
```

### Keep the spec files out of context

`persistence/`, `knowledge/`, `runtime/evaluator.py`, and `Client/` are read by
the runtime, not by the model. Loading them into a session fills it with
control-layer vocabulary that makes tool-permission classifiers stricter for
everything that follows. `CLAUDE.md` says so; keep it that way.
