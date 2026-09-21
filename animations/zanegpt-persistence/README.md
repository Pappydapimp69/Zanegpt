# ZaneGPT Approval Gate

A 3D view of the persistence runtime: what the session has observed, how close
each trait is to canonical promotion, and what is stopping it.

The structure is the policy. The core is the canonical model. The amber shell
is `config.json → promotion.require_user_approval`. Traits orbit at a distance
set by how far they are from promotion; when one satisfies
`min_supporting_events` and `min_contexts` it moves to the gate and **stops
there**, pulsing, until somebody decides. Contrary evidence (`weaken`,
`contradict`) is drawn in rose and kept in orbit — the policy says update
confidence, not overwrite history, so nothing is ever removed.

The session traits drive the core itself: mode sets its colour, fatigue slows
its rotation, and an active hacker flag lights the defensive shell around it.

## Why this is the interesting object

`persistence_runtime.md` describes a pipeline — observe, record provisional
event, classify, require repeated support, promote — that is worth being able
to *see*, because the failure mode is invisible by construction. An evidence
registry that quietly promotes without asking looks exactly like one that
doesn't, right up until it tells you something you never taught it.

That is the subject of the companion piece in `../put-me-to-sleep/`: the same
loop with the approval gate removed and the evidence pool shared across users.
This visualiser is the instrument; that one is the cautionary tale.

## Running it

```bash
python animations/zanegpt-persistence/export_state.py            # real runtime
python animations/zanegpt-persistence/export_state.py --demo \
    --out snapshot-schema.json                                   # full vocabulary
```

`export_state.py` drives the real `ZaneRuntime` over a replayed session, then
applies the promotion policy from `config.json` verbatim
(`min_supporting_events`, `min_contexts`, `require_user_approval`) to work out
each trait's status. Open `index.html` and it renders the embedded snapshots;
the **Load your own snapshot** panel takes any `export_state.py` output.

### Two datasets, and why

- **Runtime session** — genuine output of `zanegpt_runtime.ZaneRuntime`. It has
  one trait, because `evaluator.py` is explicitly a deterministic shell that
  only ever emits `session_brevity`. Its own docstring says an LLM classifier
  should replace it.
- **Schema vocabulary** — the full `event_type` set from
  `persistence_event_schema.json` (`confirm` / `strengthen` / `weaken` /
  `contradict` / `refine` / `new` / `preference`) through the *same* promotion
  policy, so the gate, the thresholds and the preserved contrary evidence can
  all be seen working. Every row is marked `"synthetic": true` and the page
  banners it.

## Notes

- `storage.ZaneStorage` expects `persistence/` and `knowledge/` subdirectories,
  but the repo currently keeps those files at its root. `export_state.py`
  stages a view of the repo in a temp directory rather than restructuring
  anything.
- **Approve for canonical** changes the view only. It does not write to
  `.zanegpt/`, and it does not touch canonical files — per the README's own
  "does not silently rewrite canonical behavior files".
- Dependencies: three.js `0.147.0` (UMD, cdnjs) and two Google Fonts faces.
  A three.js failure is reported on the page instead of leaving it blank.
