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


## Claude Code plugin

This repository is also a Claude Code plugin marketplace. The reusable ZaneGPT
behaviour — the interaction style, not the persistence runtime above — installs
straight from GitHub:

```
/plugin marketplace add Pappydapimp69/Zanegpt
/plugin install zanegpt@zanegpt
```

- `.claude-plugin/marketplace.json` — the marketplace manifest (repo root).
- `zanegpt-plugin/` — the plugin itself; see its README for the OpenAI/Codex
  import path and for why the skill needs YAML frontmatter.
- `zanegpt-plugin.zip` — generated from `zanegpt-plugin/`, kept for surfaces
  that want an archive. A copy, not the source.

The plugin is independent of the runtime: it ships one skill and no code, and
nothing in `runtime/` is required to use it.

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
python zanegpt_runtime.py --repo /path/to/Zanegpt
```
