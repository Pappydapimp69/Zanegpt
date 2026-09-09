# Zanegpt

ZaneGPT is a stateful behavior layer. The runtime owns the state; the host model
applies it.

## Do not read the spec files into context
`persistence/`, `knowledge/`, `runtime/evaluator.py`, and `Client/` are consumed
by the runtime, not by you. Reading them fills the session with control-layer
vocabulary that makes tool-permission classifiers stricter for the rest of the
session. Treat them like Brain's node repos: go through the CLI.

- Session state: `python3 runtime/zanegpt_runtime.py --repo . --state`
- Ingest a turn: `python3 runtime/zanegpt_runtime.py --repo . --ingest "<text>"`
- Preferred: a `UserPromptSubmit` hook runs `--hook` for you and returns the
  context block automatically. Snippet to merge into settings is in
  `README.md` under "UserPromptSubmit hook".

## Skill
`.claude/skills/zanegpt/SKILL.md` — invoke with `/zanegpt`. Install to
`~/.claude/skills/zanegpt/` for a session-wide copy.

## Never
- write to `knowledge/` directly (promotion requires explicit user approval)
- commit `.zanegpt/` (gitignored session state)
